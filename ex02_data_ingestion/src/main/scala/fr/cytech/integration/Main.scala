package fr.cytech.integration

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object Main {

  def main(args: Array[String]): Unit = {

    val months: Seq[String] =
      if (args.isEmpty) Seq("2025-01")
      else if (args(0).toUpperCase == "ALL")
        Seq("2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06")
      else Seq(args(0))

    val spark = SparkSession.builder()
      .appName("NYC Taxi - Exercice 2 - Branch 1 Cleaning")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    months.foreach { m =>
      val rawPath   = s"s3a://nyc-raw/yellow_tripdata_$m"
      val cleanPath = s"s3a://nyc-clean/yellow_tripdata_$m-clean"

      println(s"\n=== Cleaning month $m ===")
      println(s"Reading  : $rawPath")
      println(s"Writing  : $cleanPath")

      val rawDf = spark.read.parquet(rawPath)

      val cleanDf = rawDf
        .filter(col("passenger_count") >= 1)
        .filter(col("trip_distance") > 0)
        .filter(col("fare_amount") > 0)
        .filter(col("total_amount") > 0)
        .filter(col("tpep_pickup_datetime") < col("tpep_dropoff_datetime"))

      // Optionnel: petit log de contrôle
      val inCount  = rawDf.count()
      val outCount = cleanDf.count()
      println(s"Records in : $inCount")
      println(s"Records out: $outCount (rejected: ${inCount - outCount})")

      cleanDf.write.mode("overwrite").parquet(cleanPath)
    }

    spark.stop()
  }
}
