## NYC Taxi Big Data Pipeline

Big Data Project 
This project aims to deploy a Big Data architecture to collect, ingest, process and exploit NYC Yellow Taxi data.

---

## Data collection and data integration

- **Data source**: NYC Taxi & Limousine Commission (Parquet files) https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Processing engine**: Apache Spark (Scala)
- **Data Lake**: MinIO (S3-compatible storage)
- **Local orchestration**: Docker Compose

**Data flow:** NYC Website → Automated Download → Spark → MinIO (Data Lake)

---

## MinIO – Data Lake Configuration

MinIO is used as the **Data Lake** of this project.  
It is an S3-compatible object storage service that allows Spark to store and read
Parquet files in the same way as AWS S3.

### MinIO services

When Docker Compose is started, MinIO exposes:
- **API endpoint**: http://localhost:9000  
- **Web console**: http://localhost:9001  

Default credentials (defined in `docker-compose.yml`):
- Username: `minio`
- Password: `minio123`
The MinIO web interface can be used to visually inspect buckets and uploaded files.

---

### MinIO bucket
- Bucket name used in this project: **`nyc-raw`**
- This bucket stores the **raw NYC Taxi Parquet data**

The script `run_exo1.sh` automatically:
1. Starts the MinIO service using Docker Compose
2. Configures a MinIO client alias
3. Creates the `nyc-raw` bucket if it does not already exist
4. Runs the Spark ingestion job

This ensures that all team members use the **same configuration**
without any manual action.

---

# Requirements (manual setup)

- **Docker**
- **Docker Compose**
- **sbt**
- **Git**
- **IntelliJ IDEA + Scala plugin** (Pour le plugin, dans Intellij :Settings → Plugins → Marketplace → Scala → Install)
  <img width="974" height="573" alt="image" src="https://github.com/user-attachments/assets/a23f2c3d-2cf4-4e19-9723-012ab4c0a647" />

- **Java 11** :files - Project Structure - Modules - Deêndencies - Module SDK: 'Java 11' - apply - ok
  <img width="1018" height="212" alt="image" src="https://github.com/user-attachments/assets/ab16bdaf-b744-4571-8702-8c43dddffb93" />

- **Scala SDK**: files - Project Structure - Librairy - '+' - Scala SDK + select 'SDKMAN! 2.13.17' - download - select 'version 2.13.17' - apply - ok 
  <img width="1021" height="328" alt="image" src="https://github.com/user-attachments/assets/1429cbf4-ad6a-49a6-ac1e-44ed73f7825b" />
  <img width="406" height="591" alt="image" src="https://github.com/user-attachments/assets/641ec5c8-bd34-4c0a-a39d-6f3b8fde234b" />
  
- Installing MinIO client (`mc`) on Linux:
```bash
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

---
# Run Exercise 1
1. Create the project in Intellij as a Project from Version Control :
   1.1. file - new - Project from Version Control
   1.2. Copy paste this repository URL then click on 'clone'
   1.3. select the branch **zaynab** or on terminal write this command :
```bash
git checkout zaynab
```
2. Set the Manual Setup listed above
3. Quick checks:
```bash
java -version
docker --version
docker compose version
sbt --version
mc --version
docker ps
```
4. Mark **ex01_data_retrieval/src/main/scala** as Sources Root:
   4.1. On intellij interface, go to **ex01_data_retrieval/src/main/scala**, right click - select 'Mark Directory as' - select 'Sources Root'
5. Run run_ex01.sh
```bash
cd nyc-taxi-bigdata-pipeline/ex01_data_retrieval
chmod +x run_exo1.sh
./run_exo1.sh
run
```
6. Fixing IllegalAccessError in IntelliJ
If you encounter IllegalAccessError in IntelliJ, you need to add an extra VM option:
- Click on the three vertical dots in your run/debug configuration.
- From the dropdown Modify Options, select Add VM Option.
- Add the following line: (`--add-exports java.base/sun.nio.ch=ALL-UNNAMED`)
This will allow your code to access internal Java modules that would otherwise cause IllegalAccessError.
---

# Expected Result

After successful execution:
- MinIO contains a bucket named nyc-raw
- Spark-generated Parquet files are available in the bucket:
nyc-raw/

 └── yellow_tripdata_2023-01/

      ├── part-*.parquet
  
      └── _SUCCESS





