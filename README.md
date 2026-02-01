# NYC Taxi Big Data Pipeline

Big Data Project 
This project aims to deploy a Big Data architecture to collect, ingest, process and exploit NYC Yellow Taxi data.

---

## Table of Contents

1. [Data Collection and Data Integration](#data-collection-and-data-integration)  
2. [MinIO – Data Lake Configuration](#minio--data-lake-configuration)  
   - [MinIO Services](#minio-services)  
   - [MinIO Bucket](#minio-bucket)  
3. [Requirements (Manual Setup)](#requirements-manual-setup)  
4. [Exercise 1: Data Collection and Integration](#run-exercise-1-data-collection-and-integration)  
5. [Exercise 2: Data Cleaning and Multi-Branch Ingestion](#run-exercise-2-data-cleaning-and-multi-branch-ingestion)  
6. [Exercise 3: Data Warehouse Configuration and Initialization](#exercise-3-data-warehouse-configuration-and-initialization)  
7. [Exercise 4: Data Visualization](#exercise-4-data-visualization)  
8. [Exercise 5: Machine Learning Model Implementation](#exercise-5-machine-learning-model-implementation)  
9. [Exercise 6: Airflow Automation](#exercise-6-airflow-automation)
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
# Run Exercise 1: Data Collection and Integration
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
5. Run run_ex01.sh
```bash
cd nyc-taxi-bigdata-pipeline/ex01_data_retrieval
chmod +x run_exo1.sh
./run_ex01.sh
run
```
6. Fixing IllegalAccessError in IntelliJ
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
# Run Exercise 2: Data Cleaning and Multi-Branch Ingestion

Run run_ex02.sh

```bash
cd nyc-taxi-bigdata-pipeline/ex02_data_ingestion
chmod +x run_ex02.sh
./run_ex02.sh
run
```
You should see a new bucket nyc-clean on your minio session.


---
# Exercise 3: Data Warehouse Configuration and Initialization

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
# Exercise 4:Data visualization
# Exercise 4: Data Visualization

This module provides an interactive dashboard to analyze the NYC Taxi data stored in the PostgreSQL Data Warehouse. It visualizes Key Performance Indicators (KPIs), vendor market shares, payment methods, and top pickup locations.

### 🛠️ Technical Stack
* **Language:** Python 3.10+
* **Framework:** Streamlit
* **Visualization:** Plotly Express
* **Data Manipulation:** Pandas & SQLAlchemy
* **Dependency Manager:** `uv` (for speed and reproducibility)

---

### 🚀 Installation & Setup

We use **`uv`** to manage Python dependencies strictly and efficiently. This ensures everyone uses the exact same library versions.

#### 1. Install `uv` (if not already installed)
If you don't have `uv` installed on your machine:
```bash
# On Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Install Project Dependencies
```bash
uv sync
```


IDE Configuration (IntelliJ IDEA)
To ensure the IDE recognizes the installed libraries (and avoids red underlining), please configure the Python Interpreter:

Go to File > Project Structure > SDKs.

Click + > Add Python SDK > Virtual Environment.

Select Existing environment.```

In the "Interpreter" field, browse and select the python executable located inside your project folder:

Linux/Mac: nyc-taxi-bigdata-pipeline/.venv/bin/python

Windows: nyc-taxi-bigdata-pipeline\.venv\Scripts\python.exe

Click OK and Apply.

###3 Running the Dashboard
uv run streamlit run ex04_dashboard/dashboard.py
---
# Exercise 5:Machine Learning Model Implementation
---
# Exercise 6:Airflow Automation
