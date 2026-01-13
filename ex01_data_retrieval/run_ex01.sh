#!/bin/bash
set -e

BUCKET_NAME="nyc-raw"
MINIO_ALIAS="localminio"

echo "======================================="
echo " NYC Taxi Big Data – Exercise 1 Runner "
echo "======================================="

echo "[1/4] Starting MinIO infrastructure..."
docker compose up -d

echo "[2/4] Waiting for MinIO to be ready..."
sleep 5

echo "[3/4] Configuring MinIO client..."
mc alias set ${MINIO_ALIAS} http://localhost:9000 minio minio123
mc ls ${MINIO_ALIAS}

echo "[4/4] Creating bucket if not exists..."
mc mb ${MINIO_ALIAS}/${BUCKET_NAME} || true
mc ls ${MINIO_ALIAS}

echo "[5/5] Running Spark ingestion job..."
sbt run

echo "======================================="
echo " Exercise 1 completed successfully "
echo "======================================="
