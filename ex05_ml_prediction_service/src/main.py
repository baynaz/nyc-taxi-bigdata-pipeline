import os
import glob
import pandas as pd
from joblib import dump
import json
import platform
import sklearn
import numpy as np

from .preprocessing import prepare_features
from .model import train_model


def load_parquets(parquet_paths: list[str], max_rows: int | None = None) -> pd.DataFrame:
    """Load multiple parquet files and optionally limit the total number of rows."""
    dfs = []
    total = 0

    for path in parquet_paths:
        df_part = pd.read_parquet(path)

        if max_rows is not None:
            remaining = max_rows - total
            if remaining <= 0:
                break
            df_part = df_part.head(remaining)

        dfs.append(df_part)
        total += len(df_part)

    if not dfs:
        raise FileNotFoundError("No parquet files found to load.")

    return pd.concat(dfs, ignore_index=True)


def main():
    # IMPORTANT: when running from ex05_ml_prediction_service/, raw data is one level above
    default_raw_dir = os.path.join("..", "ex01_data_retrieval", "data", "raw")
    raw_dir = os.getenv("RAW_PARQUET_DIR", default_raw_dir)

    # Default: Jan -> Jun 2025
    patterns = [
        os.path.join(raw_dir, "yellow_tripdata_2025-01.parquet"),
        os.path.join(raw_dir, "yellow_tripdata_2025-02.parquet"),
        os.path.join(raw_dir, "yellow_tripdata_2025-03.parquet"),
        os.path.join(raw_dir, "yellow_tripdata_2025-04.parquet"),
        os.path.join(raw_dir, "yellow_tripdata_2025-05.parquet"),
        os.path.join(raw_dir, "yellow_tripdata_2025-06.parquet"),
    ]

    parquet_paths: list[str] = []
    for p in patterns:
        parquet_paths.extend(glob.glob(p))

    parquet_paths = sorted(set(parquet_paths))
    if not parquet_paths:
        raise FileNotFoundError(f"No parquet files found. RAW_PARQUET_DIR={raw_dir}")

    max_rows_env = os.getenv("MAX_ROWS")
    max_rows = int(max_rows_env) if max_rows_env else None

    df = load_parquets(parquet_paths, max_rows=max_rows)
    print(f"Loaded {len(df):,} rows from {len(parquet_paths)} parquet file(s).")

    # Preprocessing
    X, y, df_clean = prepare_features(df, target="total_amount")
    print(f"After preprocessing: X={X.shape}, y={y.shape}")

    # Training (time split if pickup datetime exists)
    result = train_model(X, y, df_for_time_split=df_clean)

    print(f"Model trained. RMSE={result.rmse:.2f} | MAE={result.mae:.2f} | R2={result.r2:.3f} | MAPE={result.mape_pct:.2f}%")

    # Save metrics
    metrics_path = os.getenv("METRICS_PATH", "artifacts/metrics.json")
    metrics = {
        "rows_loaded": int(len(df)),
        "rows_after_cleaning": int(len(df_clean)),
        "n_features": int(X.shape[1]),
        "rmse": result.rmse,
        "mae": result.mae,
        "r2": result.r2,
        "mape_pct": result.mape_pct,
        "max_rows_env": os.getenv("MAX_ROWS"),
        "python": platform.python_version(),
        "sklearn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }

    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to: {metrics_path}")


# Save pipeline
    out_path = os.getenv("MODEL_PATH", "artifacts/model.joblib")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    dump(result.pipeline, out_path)
    print(f"Saved model to: {out_path}")


if __name__ == "__main__":
    main()
