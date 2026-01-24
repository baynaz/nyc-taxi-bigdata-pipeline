package fr.cytech.integration

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object Main {

  def main(args: Array[String]): Unit = {

    // 1. Création de la SparkSession
    val spark = SparkSession.builder()
      .appName("NYC Taxi - Exercice 2 - Branche 1")
      .master("local[*]")
      .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
      .config("spark.hadoop.fs.s3a.access.key", "minio")
      .config("spark.hadoop.fs.s3a.secret.key", "minio123")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    // 2. Lecture du Parquet brut depuis Minio
    val rawDf = spark.read.parquet(
      "s3a://nyc-raw/yellow_tripdata_2025-06"
    )



    // 3. Nettoyage / validation des données (branche 1)
    val cleanDf = rawDf
      .filter(col("passenger_count") >= 1)
      .filter(col("trip_distance") > 0)
      .filter(col("fare_amount") > 0)
      .filter(col("total_amount") > 0)
      .filter(col("tpep_pickup_datetime") < col("tpep_dropoff_datetime"))

    // 4. Écriture du Parquet nettoyé dans Minio
    cleanDf.write
      .mode("overwrite")
      .parquet(
        "s3a://nyc-clean/yellow_tripdata_2025-06-clean"
      )

    // 5. Arrêt propre de Spark
    spark.stop()
  }
}