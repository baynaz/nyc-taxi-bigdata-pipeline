package fr.cytech.integration

import org.apache.spark.sql.SparkSession
import java.net.URL
import java.nio.file.{Files, Paths, StandardCopyOption}

object DataInspector {

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("NYC Taxi - Data Inspection")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    println("Lecture des données depuis minio")

    val data = spark.read.parquet("s3a://nyc-raw/yellow_tripdata_2025-01")

    println("Voici le schéma des données : ")
    data.printSchema()

    println("Aperçu des données.")
    data.show(10, truncate=false)
    spark.stop()



  }

}
