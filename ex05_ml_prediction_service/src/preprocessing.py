"""
preprocessing.py
Functions to prepare features for ML.
"""

import pandas as pd
import numpy as np

# Expected datetime column names for NYC Yellow Taxi datasets
DT_PICKUP = "tpep_pickup_datetime"
DT_DROPOFF = "tpep_dropoff_datetime"


def prepare_features(df: pd.DataFrame, target: str = "total_amount"):
    """
    Build X (features) and y (target) for a regression model.

    Notes:
    - This works on a local parquet DataFrame (no SQL query here).
    - We do lightweight cleaning to remove obvious outliers.
    - We return the cleaned df as well to allow time-based splitting later.
    """
    df = df.copy()

    # 1) Target checks
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found in dataframe columns.")

    # 2) Datetime -> time features
    if DT_PICKUP in df.columns:
        df[DT_PICKUP] = pd.to_datetime(df[DT_PICKUP], errors="coerce")
        df["hour"] = df[DT_PICKUP].dt.hour
        df["day_of_week"] = df[DT_PICKUP].dt.dayofweek  # 0=Mon ... 6=Sun
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["month"] = df[DT_PICKUP].dt.month
    else:
        # Fallback if datetime is missing
        df["hour"] = 0
        df["day_of_week"] = 0
        df["is_weekend"] = 0
        df["month"] = 1

    # 3) Trip duration in minutes
    if DT_PICKUP in df.columns and DT_DROPOFF in df.columns:
        df[DT_DROPOFF] = pd.to_datetime(df[DT_DROPOFF], errors="coerce")
        df["trip_duration_min"] = (df[DT_DROPOFF] - df[DT_PICKUP]).dt.total_seconds() / 60.0
    else:
        df["trip_duration_min"] = np.nan

    # 4) Normalize / map alternative column names
    # Different sources may use VendorID vs vendor_id, etc.
    rename_map = {
        "trip_distance": "trip_distance",
        "passenger_count": "passenger_count",
        "PULocationID": "pickup_location_id",
        "DOLocationID": "dropoff_location_id",
        "VendorID": "vendor_id",
        "RatecodeID": "rate_code_id",
        "payment_type": "payment_type_id",
    }

    for c_src, c_dst in rename_map.items():
        if c_src in df.columns and c_dst not in df.columns:
            df[c_dst] = df[c_src]

    # 5) Minimal cleaning (keep only reasonable ranges)
    if "trip_distance" in df.columns:
        df = df[df["trip_distance"].between(0.01, 100)]
    if "passenger_count" in df.columns:
        df = df[df["passenger_count"].between(1, 9)]

    # Target bounds (adjust if needed)
    df = df[df[target].between(0.01, 500)]

    # Duration bounds
    df = df[(df["trip_duration_min"].isna()) | (df["trip_duration_min"].between(1, 300))]

    # Speed feature (mph) if duration is valid
    df["speed_mph"] = np.where(
        df["trip_duration_min"] > 0,
        df.get("trip_distance", np.nan) / (df["trip_duration_min"] / 60.0),
        np.nan,
        )
    df = df[(df["speed_mph"].isna()) | (df["speed_mph"].between(0.5, 80))]

    # 6) Build X / y
    feature_cols_num = [
        "trip_distance",
        "passenger_count",
        "trip_duration_min",
        "speed_mph",
        "hour",
        "day_of_week",
        "is_weekend",
        "month",
    ]
    feature_cols_cat = [
        "pickup_location_id",
        "dropoff_location_id",
        "vendor_id",
        "rate_code_id",
        "payment_type_id",
    ]

    # Keep only columns that exist in the current dataset
    feature_cols_num = [c for c in feature_cols_num if c in df.columns]
    feature_cols_cat = [c for c in feature_cols_cat if c in df.columns]

    X = df[feature_cols_num + feature_cols_cat].copy()
    y = df[target].copy()

    # Ensure categorical columns are treated as strings for clean one-hot encoding
    for c in feature_cols_cat:
        X[c] = X[c].astype("Int64").astype("string")

    return X, y, df
