# NYC Taxi Big Data Pipeline

Big Data Project 
This project aims to deploy a Big Data architecture to collect, ingest, process and exploit NYC Yellow Taxi data. This work is done by :
## Contributors

Special thanks to:
- @baynaz : Zaynab Merimi 
- @tassatig : Tasnim Atig
- @sekou2109 : Sékou Bah
- @hadjuse : Hadj Rabearimanana
- @nousselm : Noussayba El Marrakchi


---

## Table of Contents

1. [Dashboard](#dashboard)
2. [Data Collection and Data Integration](#data-collection-and-data-integration)  
3. [MinIO – Data Lake Configuration](#minio--data-lake-configuration)  
   - [MinIO Services](#minio-services)  
   - [MinIO Bucket](#minio-bucket)  
4. [Requirements (Manual Setup)](#requirements-manual-setup)  
5. [1: Data Collection and Integration](#1-data-collection-and-integration)  
6. [2: Data Cleaning and Multi-Branch Ingestion](#2-data-cleaning-and-multi-branch-ingestion)  
7. [3: Data Warehouse Configuration and Initialization](#3-data-warehouse-configuration-and-initialization)  
8. [4: Data Visualization](#4-data-visualization)  
9. [5: Machine Learning Model Implementation](#5-machine-learning-model-implementation)
10. [6: Airflow Automation](#6-airflow-automation)
---
## Dashboard

At first, we used data of only one month, then scaled it to multiple months.

The dashbord of multiple months looks like this: 
<img width="1791" height="967" alt="image" src="https://github.com/user-attachments/assets/5dea956b-250e-48eb-b977-bf73699676e5" />

The dashbord of one month looks like this after running : 

<img width="1850" height="959" alt="image" src="https://github.com/user-attachments/assets/185faab8-bb81-4b94-a28e-af4afff5684f" />
<img width="1850" height="959" alt="image" src="https://github.com/user-attachments/assets/c66fe89d-6d24-4b4a-9d51-df5ed5c826fb" />

## Video demonstration of our dashboard:
https://github.com/user-attachments/assets/185f5c40-ae4b-43ab-b70d-1c174dc93ccd



---
## Data collection and data integration

- **Data source**: NYC Taxi & Limousine Commission (Parquet files) https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Format**: Parquet
- **Period**:
  - Baseline: January 2025
  - Extended: January → June 2025
- **Scale**:
  - ~20M trips ingested in PostgreSQL
  - ~500k rows sampled for ML training
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
# 1: Data Collection and Integration
1. Create the project in IntelliJ as a Project from Version Control:
   - Go to **File → New → Project from Version Control**
   - Copy and paste this repository URL, then click **Clone**
   - Select the branch **main**
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
   - On intellij interface, go to **ex01_data_retrieval/src/main/scala**,
   - right click, select **Mark Directory as**, select **Sources Root**
5. Run run_ex01.sh for the baseline version (January 2025 only)
```bash
cd nyc-taxi-bigdata-pipeline/ex01_data_retrieval
chmod +x run_ex01.sh
./run_ex01.sh
run
```
6. Run run_ex01_all.sh for the extended version (January to June 2025)
```bash
cd ex01_data_retrieval
./run_ex01_all.sh
```

7. Fixing IllegalAccessError in IntelliJ
If you encounter IllegalAccessError in IntelliJ, you need to add an extra VM option:
- Click on the three vertical dots in your run/debug configuration.
- From the dropdown Modify Options, select Add VM Option.
- Add the following line: (`--add-exports java.base/sun.nio.ch=ALL-UNNAMED`)
This will allow your code to access internal Java modules that would otherwise cause IllegalAccessError.
---

### Expected Result
After successful execution:
- MinIO contains a bucket named nyc-raw
- Spark-generated Parquet files are available in the bucket:
nyc-raw/

---
# 2: Data Cleaning and Multi-Branch Ingestion

Run run_ex02.sh

```bash
cd nyc-taxi-bigdata-pipeline/ex02_data_ingestion
# baseline version: 
chmod +x run_ex02_branch1.sh
./run_ex02_branch1.sh
run

#extended version:
chmod +x run_ex02_branch_all.sh
./run_ex02_branch_all.sh
run
```
You should see a new bucket nyc-clean on your minio session.
### Data ingestion into postgreSQL database
You should execute part 3 bellow before doing this part.
```bash
cd nyc-taxi-bigdata-pipeline/ex02_data_ingestion
chmod +x run_branch2.sh
./run_branch2.sh s3a://nyc-clean/yellow_tripdata_2025-01-clean
run
```
It will put the trips into database.

---
# 3: Data Warehouse Configuration and Initialization

This step details the procedure to connect the IDE (IntelliJ) to the PostgreSQL container and execute the scripts to create and populate the Data Warehouse tables.

## 1. Connecting to the Database (IntelliJ)

1. Open the **Database** tab located on the right vertical panel in IntelliJ.  
2. Click **`+` (New)** > **Data Source** > **PostgreSQL**.  
3. Configure the connection with the parameters defined in `docker-compose.yml`:  
   - **Host**: `localhost`  
   - **Port**: `5432`  
   - **User**: `postgres`  
   - **Password**: `postgres`  
   - **Database**: `taxidb`  
4. Click **Test Connection** (download drivers if prompted).  
5. If the test shows "Succeeded", click **OK**.  

## 2. Executing the SQL Scripts

Interaction with the database is done via a **Query Console**:  
*Right-click* on the connection `taxidb@localhost` > **New** > **Query Console**.  

### Step A: Creating the structure
1. Open the file `ex03_sql_table_creation/creation.sql` and copy its contents.  
2. Paste the SQL code into the IntelliJ console.  
3. Select all text (`Ctrl+A`) and run it using the **Play ▶️** button (or `Ctrl + Enter`).  
4. **Verification**: The "Output" tab should display confirmation that the tables were created.  

### Step B: Inserting reference data
1. Clear the console or open a new one.  
2. Paste the contents of the file `ex03_sql_table_creation/insertion.sql` (which contains static data: Vendors, Boroughs, etc.).  
3. Run the script using the **Play ▶️** button.  
   ![SQL Script Output](https://github.com/user-attachments/assets/1f0d7374-5411-4176-b0e8-f67c8ce43c2b)  
4. **Verification**: Ensure no errors appear in the "Output" tab.  

## 3. Final Verification

To confirm that the Data Warehouse is correctly initialized:  
1. In the **Database** panel, click **Refresh** (🔄).  
2. Navigate through the tree: `taxidb@localhost` > `taxidb` > `public` > `tables`.  
3. The 6 tables should appear (`DVendor`, `Trips`, `Location_table`, etc.).  
4. Double-click a table (e.g., `Vendor`) to confirm it contains the data.


---
# 4:Data visualization

This module provides an interactive dashboard to analyze the NYC Taxi data stored in the PostgreSQL Data Warehouse. It visualizes Key Performance Indicators (KPIs), vendor market shares, payment methods, and top pickup locations.

### Technical Stack
* **Language:** Python 3.10+
* **Framework:** Streamlit
* **Visualization:** Plotly Express
* **Data Manipulation:** Pandas & SQLAlchemy
* **Dependency Manager:** `uv` (for speed and reproducibility)

---

### Installation & Setup

We use **`uv`** to manage Python dependencies strictly and efficiently. This ensures everyone uses the exact same library versions.

#### 1. Install `uv` (if not already installed)
If you don't have `uv` installed on your machine:
```bash
# On Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Install Project Dependencies
```bash
uv sync
```

#### 3. IDE Configuration (IntelliJ IDEA)
To ensure the IDE recognizes the installed libraries (and avoids red underlining), please configure the Python Interpreter:

- Go to **File** > **Project Structure** > **SDKs**.
- Click "**+**" > **Add Python SDK** > **Virtual Environment**.
- Select **Existing environment**.
- In the "**Interpreter**" field, browse and select the python executable located inside your project folder:
```bash
# Linux/Mac:
nyc-taxi-bigdata-pipeline/.venv/bin/python
```
- Click **OK** and **Apply**.

### 4. Running the Dashboard
```bash
cd ex04_dashboard
uv run streamlit run dashboard.py
```
In the streamlit interface, filter month = 2025-01 for the baseline version and months from 2025-01 → 2025-06 for the extended version.

---
# 5:Machine Learning Model Implementation

---
# 6:Airflow Automation

The pipeline performs two main steps:
1.  **Data Cleaning**: Spark cleans raw yellow taxi data.
2.  **Ingestion**: Spark ingests the cleaned data into a PostgreSQL Data Warehouse.

### The Architecture
* **Airflow**: Scheduler & Webserver (Orchestrator).
* **Spark Master/Workers**: Execution engine for heavy processing.
* **PostgreSQL**: Data Warehouse & Airflow Metadata DB.
* **Docker**: All services run in containers.

### Setup & Installation Guide

### 1. Compile the Spark Application
We use `spark-submit` to run the jobs inside Docker. First, you must compile the Scala code on your local machine:
```bash
cd work-dir/ex02_data_ingestion
sbt package
```
#### Success Check
Ensure you see `[success]` and that the file `nyc-taxi-ingestion_2.12-1.0.jar` is created in `target/scala-2.12/`.

### 2. Fix Permissions (Crucial Step)
Airflow runs as a non-root user inside the container.  
You must grant read/write permissions to the logs and configuration folders, and allow Airflow to communicate with the Docker Daemon.  
Run these commands from the project root:
```bash
# 1. Allow Airflow to write logs
sudo chmod -R 777 dags logs plugins
# 2. Allow Airflow to trigger Docker containers (Fixes "Permission Denied" on socket)
sudo chmod 666 /var/run/docker.sock
```
### 3. Start the Infrastructure
Build and start the containers:
```bash
docker compose up -d --build
```
### Running the Pipeline
#### 1. Access the Interface
Open your browser and go to: http://localhost:8080

Username: admin
Password: admin

#### 2. Trigger the DAG
- Find the DAG named **nyc_taxi_pipeline**
- Toggle the switch to Unpause (OFF → ON / Blue)
- Click the Play Button (▷) on the right side of the row → Trigger DAG

#### 3. Monitor Execution
Click on the **nyc_taxi_pipeline** name, then go to the **Graph** tab. You should see the tasks turn Green sequentially:
<img width="138" height="75" alt="image" src="https://github.com/user-attachments/assets/a77954db-0a99-497c-a3b5-999647655481" />


<img width="1842" height="529" alt="image (3)" src="https://github.com/user-attachments/assets/159546f9-0350-434f-89ff-385c2a24c6ab" />
This is the issue we were facing: 
<img width="1837" height="1013" alt="image" src="https://github.com/user-attachments/assets/7b738a62-9561-42ab-9717-606bd6f2fb7a" />
To deal with this issue we prepared this troubleshooting steps:

## Troubleshooting & Robust Installation Guide (Airflow/Spark)
This guide helps resolve common errors encountered when deploying the pipeline on different machines (permission errors, different Scala versions, missing JAR files, Docker API incompatibility).
### Mandatory Prerequisites
Before running the pipeline on your machine, follow these two steps to avoid 99% of errors.
#### 1. Compile the Scala CodeThe Spark container needs the compiled `.jar` file. It does not create it itself; you must generate it locally.
```bash
# Navigate to the ingestion module folder
cd ex02_data_ingestion
# Compile the project (generates the .jar in target/)
sbt package
```
### 2. Fix Docker Permissions (Linux/Mac)
Airflow needs access to your host machine's Docker socket to spin up Spark containers. If you encounter a permission denied error, run:
```Bash
sudo chmod 666 /var/run/docker.sock
```
### 3. DAG Configuration (Universal Solution)
Replace the content o- f the nettoyage (cleaning) and ingestion tasks in your *dags/nyc_taxi_pipeline.py* file with the code below.
This code automatically handles:
- Docker API compatibility (avoids client version is too new errors).
- Automatic detection of the .jar file (regardless of its name or Scala version).
- Injection of S3 dependencies (hadoop-aws) to prevent ClassNotFoundException

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e2a8cc9e-7a5e-4501-97c0-9ad9a2a6136d" />
