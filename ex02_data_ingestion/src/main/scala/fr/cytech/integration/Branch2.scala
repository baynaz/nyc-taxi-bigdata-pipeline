import org.apache.spark.sql.{DataFrame, SaveMode, SparkSession}
import org.apache.spark.sql.functions._
import java.util.Properties
import org.slf4j.LoggerFactory

object Branch2Production {
  private val logger = LoggerFactory.getLogger(this.getClass)

  def main(args: Array[String]): Unit = {
    if (args.length < 1) {
      logger.error("Usage: Branch2Production <parquet_path> [jdbc_url] [db_user] [db_password]")
      System.exit(1)
    }

    val parquetPath = args(0)
    val jdbcUrl     = if (args.length > 1) args(1) else "jdbc:postgresql://localhost:5432/taxidb"
    val dbUser      = if (args.length > 2) args(2) else "postgres"
    val dbPassword  = if (args.length > 3) args(3) else "postgres"

    val spark = SparkSession.builder()
      .appName("NYC Taxi - Branch 2 - Production Ingestion")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    val props = new Properties()
    props.put("user", dbUser)
    props.put("password", dbPassword)
    props.put("driver", "org.postgresql.Driver")

    try {
      logger.info(s"=== Starting ingestion from: $parquetPath ===")

      verifyDatabaseConnection(spark, jdbcUrl, props)
      verifyDimensionTables(spark, jdbcUrl, props)

      val rawDf = spark.read.parquet(parquetPath)
      val total = rawDf.count()
      logger.info(s"Total records read: $total")

      // cleaning + ajout year_month
      val cleanedDf = cleanAndValidateData(rawDf)
        .withColumn("year_month", date_format(col("tpep_pickup_datetime").cast("timestamp"), "yyyy-MM"))
        .withColumn("month", col("year_month")) // pour remplir Trips.month

      val valid = cleanedDf.count()
      logger.info(s"Valid records after cleaning: $valid (rejected: ${total - valid})")

      // 1) Upsert TimeDimension sur year_month (idempotent)
      val timeDimDf = buildTimeDimensionByMonth(cleanedDf)
      upsertTimeDimensionByMonth(spark, jdbcUrl, props, timeDimDf)

      // 2) Reload TimeDimension + join sur year_month
      val timeDbDf = spark.read.jdbc(jdbcUrl, "TimeDimension", props)
        .select(col("time_id"), col("year_month"))

      val enrichedTripsDf = cleanedDf
        .join(timeDbDf, Seq("year_month"), "left")
        .withColumn("time_id", col("time_id"))

      // 3) Trips dataframe final
      val tripsDf = prepareTripsData(enrichedTripsDf)

      logger.info("Inserting into Trips...")
      val start = System.currentTimeMillis()

      tripsDf.write
        .mode(SaveMode.Append)
        .option("batchsize", "10000")
        .option("isolationLevel", "READ_COMMITTED")
        .option("numPartitions", "8")
        .jdbc(jdbcUrl, "Trips", props)

      val end = System.currentTimeMillis()
      val dur = (end - start) / 1000.0

      logger.info(s"=== Ingestion DONE ===")
      logger.info(s"Inserted: ${tripsDf.count()} rows")
      logger.info(f"Duration: $dur%.2f sec")

    } finally {
      spark.stop()
    }
  }

  def verifyDatabaseConnection(spark: SparkSession, jdbcUrl: String, props: Properties): Unit = {
    val testQuery = "(SELECT 1 as test) AS test_query"
    spark.read.jdbc(jdbcUrl, testQuery, props).collect()
    logger.info("✓ PostgreSQL OK")
  }

  def verifyDimensionTables(spark: SparkSession, jdbcUrl: String, props: Properties): Unit = {
    val requiredTables = List("Vendor", "RateCode", "Payment", "Borough", "Location_table", "TimeDimension", "Trips")
    val missing = requiredTables.filter { t =>
      try {
        val q = s"(SELECT 1 FROM $t LIMIT 1) AS chk"
        spark.read.jdbc(jdbcUrl, q, props).count()
        false
      } catch { case _: Exception => true }
    }
    if (missing.nonEmpty) throw new RuntimeException(s"Missing tables: ${missing.mkString(", ")} (run Exercise 3 SQL)")
    logger.info("✓ Dimension tables OK")
  }

  def cleanAndValidateData(df: DataFrame): DataFrame = {
    df.filter(
      col("trip_distance") >= 0 &&
        col("fare_amount") >= 0 &&
        col("total_amount") >= 0 &&
        col("passenger_count") > 0 &&
        col("passenger_count") <= 9 &&
        col("tpep_pickup_datetime").isNotNull &&
        col("tpep_dropoff_datetime").isNotNull &&
        col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime")
    )
  }

  // construit une TimeDimension au niveau mois (year_month)
  def buildTimeDimensionByMonth(df: DataFrame): DataFrame = {
    df.select(col("year_month")).distinct()
      .withColumn("year", substring(col("year_month"), 1, 4).cast("int"))
      .withColumn("month", substring(col("year_month"), 6, 2).cast("int"))
      .withColumn("month_name",
        date_format(to_date(concat(col("year_month"), lit("-01"))), "MMMM")
      )
      .select("year", "month", "month_name", "year_month")
  }

  // upsert idempotent (insert seulement les nouveaux year_month)
  def upsertTimeDimensionByMonth(spark: SparkSession, jdbcUrl: String, props: Properties, timeDf: DataFrame): Unit = {
    val existing = spark.read.jdbc(jdbcUrl, "TimeDimension", props).select("year_month").distinct()
    val toInsert = timeDf.join(existing, Seq("year_month"), "left_anti")
    val nb = toInsert.count()
    logger.info(s"TimeDimension new months to insert: $nb")
    if (nb > 0) {
      toInsert.write.mode(SaveMode.Append).jdbc(jdbcUrl, "TimeDimension", props)
    }
  }

  def prepareTripsData(df: DataFrame): DataFrame = {
    df.select(
      coalesce(col("VendorID").cast("integer"), lit(0)).as("vendor_id"),
      coalesce(col("RatecodeID").cast("integer"), lit(99)).as("rate_code_id"),
      coalesce(col("payment_type").cast("integer"), lit(5)).as("payment_type_id"),
      coalesce(col("PULocationID").cast("integer"), lit(264)).as("pickup_location_id"),
      coalesce(col("DOLocationID").cast("integer"), lit(264)).as("dropoff_location_id"),

      col("tpep_pickup_datetime").cast("timestamp").as("pickup_datetime"),
      col("tpep_dropoff_datetime").cast("timestamp").as("dropoff_datetime"),

      col("time_id").cast("integer").as("time_id"),
      col("month").cast("string").as("month"),

      coalesce(col("passenger_count").cast("integer"), lit(1)).as("passenger_count"),
      col("trip_distance").cast("float").as("trip_distance"),
      col("fare_amount").cast("float").as("fare_amount"),
      coalesce(col("extra").cast("float"), lit(0.0)).as("extra"),
      coalesce(col("mta_tax").cast("float"), lit(0.0)).as("mta_tax"),
      coalesce(col("tip_amount").cast("float"), lit(0.0)).as("tip_amount"),
      coalesce(col("tolls_amount").cast("float"), lit(0.0)).as("tolls_amount"),
      coalesce(col("improvement_surcharge").cast("float"), lit(0.0)).as("improvement_surcharge"),
      col("total_amount").cast("float").as("total_amount"),
      coalesce(col("congestion_surcharge").cast("float"), lit(0.0)).as("congestion_surcharge"),
      coalesce(col("airport_fee").cast("float"), lit(0.0)).as("airport_fee")
    )
  }
}
