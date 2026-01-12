#!/bin/bash
set -e

echo "======================================="
echo " NYC Taxi Big Data – Exercise 1 Runner "
echo "======================================="

echo "[1/2] Starting MinIO infrastructure..."
docker compose up -d

echo "[2/2] Running Spark ingestion job (Exercise 1)..."
sbt run

echo "======================================="
echo " Exercise 1 completed successfully "
echo "======================================="
