#!/bin/bash
# run_branch2.sh

# Check if parquet path is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <parquet_path>"
    echo "Example: $0 s3a://nyc-clean/yellow_tripdata_2025-01-clean"
    exit 1
fi

PARQUET_PATH="$1"

echo "========================================"
echo "NYC Taxi - Branch 2 Ingestion"
echo "========================================"
echo "Parquet path: ${PARQUET_PATH}"
echo "========================================"
echo ""

# Run with sbt (automatically compiles and executes)
sbt "runMain Branch2Production ${PARQUET_PATH} jdbc:postgresql://localhost:5432/taxidb postgres postgres"