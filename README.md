## NYC Taxi Big Data Pipeline

Big Data Project 
This project aims to deploy a Big Data architecture to collect, ingest, process and exploit NYC Yellow Taxi data.

---

## Data collection and data integration

- **Data source**: NYC Taxi & Limousine Commission (Parquet files) https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Processing engine**: Apache Spark (Scala)
- **Data Lake**: MinIO (S3-compatible storage)
- **Local orchestration**: Docker Compose

Data flow:
NYC Website → Automated Download → Spark → MinIO (Data Lake)

## Requirements (manual setup)

- **Java 11**
- **Docker**
- **Docker Compose**
- **sbt**
- **Git**
- **IntelliJ IDEA + Scala plugin** (Pour le plugin, dans Intellij :Settings → Plugins → Marketplace → Scala → Install)

Quick checks:
```bash
java -version
docker --version
docker compose version
sbt --version
```
---
Run Exercise 1
```bash
git clone <REPOSITORY_URL>
cd nyc-taxi-bigdata-pipeline/ex01_data_retrieval
chmod +x run_exo1.sh
./run_exo1.sh
```





