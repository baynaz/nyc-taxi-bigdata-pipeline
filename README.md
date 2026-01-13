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





