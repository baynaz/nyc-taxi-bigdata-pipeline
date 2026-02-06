#!/bin/bash
set -e

MINIO_ALIAS="localminio"
BUCKET_NAME="nyc-raw"
TAXI_TYPE="${1:-yellow}"   # optionnel: yellow/green/fhv

MONTHS=(
  "2025-01"
  "2025-02"
  "2025-03"
  "2025-04"
  "2025-05"
  "2025-06"
)

echo "[1/4] Starting infrastructure..."
docker compose up -d

echo "[2/4] Waiting a bit..."
sleep 5

echo "[3/4] MinIO bucket check..."
mc alias set ${MINIO_ALIAS} http://localhost:9000 minio minio123
mc mb ${MINIO_ALIAS}/${BUCKET_NAME} || true

echo "[4/4] Ingesting months to MinIO..."
for m in "${MONTHS[@]}"; do
  echo "==> Ingesting ${TAXI_TYPE} ${m}"
  sbt "runMain fr.cytech.integration.Main ${m} ${TAXI_TYPE}"
done

echo "Done. Check MinIO bucket: ${BUCKET_NAME}"
