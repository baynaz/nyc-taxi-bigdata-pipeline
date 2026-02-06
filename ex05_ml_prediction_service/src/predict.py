# src/predict.py
import os
import pandas as pd
from joblib import load
from .preprocessing import prepare_features


def main():
    model_path = os.getenv("MODEL_PATH", "artifacts/model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found: {model_path}. Train first with: python -m src.main"
        )

    parquet_path = os.getenv(
        "PREDICT_PARQUET",
        "ex01_data_retrieval/data/raw/yellow_tripdata_2025-06.parquet"
    )
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Prediction parquet not found: {parquet_path}")

    n = int(os.getenv("N_PRED", "20"))
    df = pd.read_parquet(parquet_path).head(n)

    # Ensure the pipeline preprocessing can run (needs a target column name)
    if "total_amount" not in df.columns:
        df = df.copy()
        df["total_amount"] = 1.0  # dummy target (not used in prediction)

    # IMPORTANT: prepare_features() may DROP rows => use df_clean to align with preds
    X, _, df_clean = prepare_features(df, target="total_amount")

    pipeline = load(model_path)
    preds = pipeline.predict(X)

    out = df_clean.copy().reset_index(drop=True)
    out["pred_total_amount"] = preds

    print(f"Input rows read: {len(df):,}")
    print(f"Rows kept after cleaning: {len(df_clean):,}")
    print(out[["pred_total_amount"]].head(min(n, len(out))))

    out_csv = os.getenv("PRED_OUT", "artifacts/predictions.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    out.to_csv(out_csv, index=False)
    print(f"Saved predictions to: {out_csv}")


if __name__ == "__main__":
    main()
