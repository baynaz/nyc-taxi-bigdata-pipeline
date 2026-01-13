package fr.cytech.integration

import org.apache.spark.sql.SparkSession
import java.net.URL
import java.nio.file.{Files, Paths, StandardCopyOption}

object Main {

  def main(args: Array[String]): Unit = {

    // 1. Téléchargement automatique du fichier parquet
    val parquetUrl =
      "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-06.parquet"

    val localDir = "data/raw"
    val localPath = s"$localDir/yellow_tripdata_2025-06.parquet"

    Files.createDirectories(Paths.get(localDir))
    new URL(parquetUrl).openStream()
      .pipe(in => Files.copy(in, Paths.get(localPath), StandardCopyOption.REPLACE_EXISTING))

    // 2. SparkSession + configuration MinIO
    val spark = SparkSession.builder()
      .appName("NYC Taxi - Automated Ingestion")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    // 3. Lecture locale du parquet
    val df = spark.read.parquet(localPath)

    // 4. Écriture vers MinIO
    df.write
      .mode("overwrite")
      .parquet("s3a://nyc-raw/yellow_tripdata_2025-06")

    spark.stop()
  }

  // Petit helper pour gérsber le stream proprement
  implicit class AutoClose[A <: AutoCloseable](resource: A) {
    def pipe[B](f: A => B): B =
      try f(resource) finally resource.close()
  }
}
