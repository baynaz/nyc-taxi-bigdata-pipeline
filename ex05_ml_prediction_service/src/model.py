"""model.py
Functions to train and evaluate ML models.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
from sklearn.ensemble import HistGradientBoostingRegressor


def mape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-6) -> float:
    """Mean Absolute Percentage Error (in %) with epsilon to avoid division by zero."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.maximum(np.abs(y_true), eps)
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


@dataclass
class TrainResult:
    pipeline: Pipeline
    rmse: float
    mae: float
    r2: float
    mape_pct: float


def train_model(
        X: pd.DataFrame,
        y: pd.Series,
        df_for_time_split: pd.DataFrame | None = None
) -> TrainResult:
    """Train a full pipeline (preprocess + model).
    Uses a time-based split if df_for_time_split contains 'tpep_pickup_datetime'.
    """

    # Numeric vs categorical columns
    num_cols = [c for c in X.columns if X[c].dtype != "object" and str(X[c].dtype) != "string"]
    cat_cols = [c for c in X.columns if c not in num_cols]

    preprocess = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]), num_cols),
            ("cat", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    model = HistGradientBoostingRegressor(
        learning_rate=0.08,
        max_depth=8,
        max_iter=200,
        random_state=42,
    )

    pipeline = Pipeline(steps=[
        ("preprocess", preprocess),
        ("model", model),
    ])

    # ---- Split strategy ----
    if df_for_time_split is not None and "tpep_pickup_datetime" in df_for_time_split.columns:
        tmp = df_for_time_split.copy()
        tmp["__idx__"] = np.arange(len(tmp))
        tmp["tpep_pickup_datetime"] = pd.to_datetime(tmp["tpep_pickup_datetime"], errors="coerce")
        tmp = tmp.sort_values("tpep_pickup_datetime")

        split = int(len(tmp) * 0.8)
        train_idx = tmp["__idx__"].iloc[:split].values
        test_idx = tmp["__idx__"].iloc[split:].values

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae = float(mean_absolute_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))
    mape_pct = mape(y_test.to_numpy(), preds)

    return TrainResult(pipeline=pipeline, rmse=rmse, mae=mae, r2=r2, mape_pct=mape_pct)
