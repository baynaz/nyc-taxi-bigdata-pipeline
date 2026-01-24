#!/bin/bash
set -e

RAW_BUCKET="nyc-raw"
CLEAN_BUCKET="nyc-clean"
MINIO_ALIAS="localminio"

echo "======================================="
echo " NYC Taxi Big Data – Exercise 2 Runner "
echo "======================================="

echo "[1/5] Starting infrastructure..."
docker compose up -d

echo "[2/5] Waiting for MinIO..."
sleep 5

echo "[3/5] Configuring MinIO client..."
mc alias set ${MINIO_ALIAS} http://localhost:9000 minioadmin minioadmin

echo "[4/5] Creating clean bucket if not exists..."
mc mb ${MINIO_ALIAS}/${CLEAN_BUCKET} || true

echo "[5/5] Running Spark cleaning job..."
sbt run

echo "======================================="
echo " Exercise 2 completed successfully "
echo "======================================="
