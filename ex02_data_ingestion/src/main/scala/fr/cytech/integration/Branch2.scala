import org.apache.spark.sql.{SaveMode, SparkSession}
import org.apache.spark.sql.functions._
import java.util.Properties
import org.slf4j.LoggerFactory
import org.postgresql.Driver
object Branch2Production {

  private val logger = LoggerFactory.getLogger(this.getClass)

  def main(args: Array[String]): Unit = {
    // Validate arguments
    if (args.length < 1) {
      logger.error("Usage: Branch2Production <parquet_path> [jdbc_url] [db_user] [db_password]")
      System.exit(1)
    }

    val parquetPath = args(0)
    val jdbcUrl = if (args.length > 1) args(1) else "jdbc:postgresql://localhost:5432/taxidb"
    val dbUser = if (args.length > 2) args(2) else "postgres"
    val dbPassword = if (args.length > 3) args(3) else "postgres"

    val spark = SparkSession.builder()
      .appName("NYC Taxi - Branch 2 - Production Ingestion")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    import spark.implicits._
    spark.sparkContext.setLogLevel("WARN")

    try {
      // JDBC configuration
      val connectionProperties = new Properties()
      connectionProperties.put("user", dbUser)
      connectionProperties.put("password", dbPassword)
      connectionProperties.put("driver", "org.postgresql.Driver")

      logger.info(s"=== Starting ingestion from $parquetPath ===")

      // Verify PostgreSQL connectivity
      verifyDatabaseConnection(spark, jdbcUrl, connectionProperties)

      // Verify that dimension tables exist
      verifyDimensionTables(spark, jdbcUrl, connectionProperties)

      // Read Parquet file
      logger.info("Reading Parquet file...")
      val rawDf = spark.read.parquet(parquetPath)
      val totalRecords = rawDf.count()
      logger.info(s"Total records to ingest: $totalRecords")

      // Clean and validate data
      val cleanedDf = cleanAndValidateData(rawDf)
      val validRecords = cleanedDf.count()
      logger.info(s"Valid records after cleaning: $validRecords (${totalRecords - validRecords} records rejected)")

      // Transform for Trips table
      val tripsDf = prepareTripsData(cleanedDf)

      // Insert into PostgreSQL
      logger.info("Starting PostgreSQL insertion...")
      val startTime = System.currentTimeMillis()

      tripsDf.write
        .mode(SaveMode.Append)
        .option("batchsize", "10000")
        .option("isolationLevel", "READ_COMMITTED")
        .option("numPartitions", "8") // Parallelization
        .jdbc(jdbcUrl, "Trips", connectionProperties)

      val endTime = System.currentTimeMillis()
      val durationSeconds = (endTime - startTime) / 1000.0

      logger.info(s"=== Ingestion completed successfully ===")
      logger.info(s"Records inserted: $validRecords")
      logger.info(s"Duration: $durationSeconds seconds")
      logger.info(s"Throughput: ${validRecords / durationSeconds} records/sec")

    } catch {
      case e: Exception =>
        logger.error("Error during ingestion", e)
        throw e
    } finally {
      spark.stop()
    }
  }

  /**
   * Verifies PostgreSQL database connection
   */
  def verifyDatabaseConnection(spark: SparkSession, jdbcUrl: String, props: Properties): Unit = {
    try {
      logger.info("Verifying PostgreSQL connection...")
      val testQuery = "(SELECT 1 as test) AS test_query"
      spark.read.jdbc(jdbcUrl, testQuery, props).collect()
      logger.info("✓ PostgreSQL connection established successfully")
    } catch {
      case e: Exception =>
        logger.error("✗ Unable to connect to PostgreSQL", e)
        throw new RuntimeException("Database connection failed", e)
    }
  }

  /**
   * Verifies that all required dimension tables exist
   */
  def verifyDimensionTables(spark: SparkSession, jdbcUrl: String, props: Properties): Unit = {
    logger.info("Verifying existence of dimension tables...")

    val requiredTables = List("Vendor", "RateCode", "Payment", "Borough", "Location_table")
    val missingTables = scala.collection.mutable.ListBuffer[String]()

    requiredTables.foreach { table =>
      try {
        val query = s"(SELECT COUNT(*) as cnt FROM $table LIMIT 1) AS check_$table"
        val count = spark.read.jdbc(jdbcUrl, query, props).first().getLong(0)
        logger.info(s"Table $table exists with $count records")

        if (count == 0) {
          logger.warn(s" WARNING: Table $table is empty!")
        }
      } catch {
        case e: Exception =>
          logger.error(s"✗ Table $table does not exist or is inaccessible")
          missingTables += table
      }
    }

    if (missingTables.nonEmpty) {
      val errorMsg = s"Missing tables: ${missingTables.mkString(", ")}. " +
        "Please run the table creation script (Exercise 3) before launching the ingestion."
      logger.error(errorMsg)
      throw new RuntimeException(errorMsg)
    }

    logger.info("All dimension tables are present")
  }

  /**
   * Cleans and validates raw data
   */
  def cleanAndValidateData(df: org.apache.spark.sql.DataFrame): org.apache.spark.sql.DataFrame = {
    logger.info("Cleaning and validating data...")

    df.filter(
      // Filter out outliers
      col("trip_distance") >= 0 &&
        col("fare_amount") >= 0 &&
        col("total_amount") >= 0 &&
        col("passenger_count") > 0 &&
        col("passenger_count") <= 9 && // Reasonable maximum
        col("tpep_pickup_datetime").isNotNull &&
        col("tpep_dropoff_datetime").isNotNull &&
        col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime") // Dropoff after pickup
    )
  }

  /**
   * Prepares data for insertion into Trips table
   */
  def prepareTripsData(df: org.apache.spark.sql.DataFrame): org.apache.spark.sql.DataFrame = {
    logger.info("Preparing data for Trips table...")

    df.select(
      // Foreign keys
      coalesce(col("VendorID").cast("integer"), lit(0)).as("vendor_id"),
      coalesce(col("RatecodeID").cast("integer"), lit(99)).as("rate_code_id"),
      coalesce(col("payment_type").cast("integer"), lit(5)).as("payment_type_id"),
      coalesce(col("PULocationID").cast("integer"), lit(264)).as("pickup_location_id"),
      coalesce(col("DOLocationID").cast("integer"), lit(264)).as("dropoff_location_id"),

      // Timestamps
      col("tpep_pickup_datetime").cast("timestamp").as("pickup_datetime"),
      col("tpep_dropoff_datetime").cast("timestamp").as("dropoff_datetime"),

      // Measures
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