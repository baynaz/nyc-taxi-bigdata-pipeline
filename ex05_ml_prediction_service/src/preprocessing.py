"""
preprocessing.py
Functions to prepare features for ML.
"""

import pandas as pd


def prepare_features(df: pd.DataFrame):
    """
    Clean and prepare features for ML model.

    Returns
    -------
    X : pd.DataFrame
        Features
    y : pd.Series
        Target
    """
    # Drop rows with missing critical values
    df = df.dropna(subset=['fare_amount', 'trip_distance', 'passenger_count'])

    # Target variable
    y = df['fare_amount']

    # Feature selection
    X = df[['trip_distance', 'passenger_count']]

    return X, y
