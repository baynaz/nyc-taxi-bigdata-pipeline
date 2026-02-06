#!/usr/bin/env bash
set -euo pipefail

# ============================
# Ex05 - ML prediction service
# Reproducible runner
# ============================

# Optional env overrides
MAX_ROWS="${MAX_ROWS:-500000}"
MODEL_PATH="${MODEL_PATH:-artifacts/model.joblib}"
RAW_PARQUET_DIR="${RAW_PARQUET_DIR:-../ex01_data_retrieval/data/raw}"
PREDICT_PARQUET="${PREDICT_PARQUET:-../ex01_data_retrieval/data/raw/yellow_tripdata_2025-02.parquet}"
N_PRED="${N_PRED:-100}"
PRED_OUT="${PRED_OUT:-artifacts/predictions.csv}"

echo "=============================================="
echo "Ex05 - Repro run"
echo "MAX_ROWS=$MAX_ROWS"
echo "RAW_PARQUET_DIR=$RAW_PARQUET_DIR"
echo "MODEL_PATH=$MODEL_PATH"
echo "PREDICT_PARQUET=$PREDICT_PARQUET"
echo "N_PRED=$N_PRED"
echo "PRED_OUT=$PRED_OUT"
echo "=============================================="

mkdir -p artifacts

echo ""
echo ">>> 1) Unit tests"
python -m unittest discover -s test -p "test_*.py"

echo ""
echo ">>> 2) Train model"
RAW_PARQUET_DIR="$RAW_PARQUET_DIR" MAX_ROWS="$MAX_ROWS" MODEL_PATH="$MODEL_PATH" python -m src.main

echo ""
echo ">>> 3) Predict sample"
PREDICT_PARQUET="$PREDICT_PARQUET" N_PRED="$N_PRED" MODEL_PATH="$MODEL_PATH" PRED_OUT="$PRED_OUT" python -m src.predict

echo ""
echo "Done."
