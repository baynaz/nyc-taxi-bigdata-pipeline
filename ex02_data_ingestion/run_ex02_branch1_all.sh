#!/bin/bash
set -e

MONTH="${1:-ALL}"
CLEAN_BUCKET="nyc-clean"
MINIO_ALIAS="localminio"

echo "======================================="
echo " NYC Taxi Big Data – Exercice 2 - Branch 1"
echo "======================================="
echo "Month: ${MONTH}"
echo "[1/4] Starting infrastructure..."
docker compose up -d

echo "[2/4] Waiting for MinIO..."
sleep 5

echo "[3/4] Configuring MinIO client..."
mc alias set ${MINIO_ALIAS} http://localhost:9000 minio minio123

echo "[4/4] Creating clean bucket if not exists..."
mc mb ${MINIO_ALIAS}/${CLEAN_BUCKET} 2>/dev/null || true

echo "[5/5] Running Spark cleaning job (Branch1 only)..."
sbt "runMain fr.cytech.integration.Main ${MONTH}"

echo "======================================="
echo " Exercise 2 - Branch 1 completed"
echo "======================================="
