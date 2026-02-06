package fr.cytech.integration

import org.apache.spark.sql.SparkSession
import java.net.URL
import java.nio.file.{Files, Paths, StandardCopyOption}

object Main {
  def main(args: Array[String]): Unit = {

    if (args.length < 1) {
      System.err.println("Usage: Main <YYYY-MM> [yellow|green|fhv]")
      System.exit(1)
    }

    val month = args(0) // ex: 2025-01
    val taxiType = if (args.length > 1) args(1) else "yellow"

    val parquetUrl =
      s"https://d37ci6vzurychx.cloudfront.net/trip-data/${taxiType}_tripdata_${month}.parquet"

    val localDir = "Project/data/raw"
    Files.createDirectories(Paths.get(localDir))
    val localPath = s"$localDir/${taxiType}_tripdata_${month}.parquet"

    new URL(parquetUrl).openStream().pipe { in =>
      Files.copy(in, Paths.get(localPath), StandardCopyOption.REPLACE_EXISTING)
    }

    val spark = SparkSession.builder()
      .appName(s"NYC Taxi - Ex01 Ingestion $taxiType $month")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    val df = spark.read.parquet(localPath)

    // IMPORTANT: garder un chemin stable dans MinIO
    df.write.mode("overwrite").parquet(s"s3a://nyc-raw/${taxiType}_tripdata_${month}")

    spark.stop()
  }

  implicit class AutoClose[A <: AutoCloseable](resource: A) {
    def pipe[B](f: A => B): B = try f(resource) finally resource.close()
  }
}
