"""
model.py
Functions to train and evaluate ML models.
"""

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd


def train_model(X: pd.DataFrame, y: pd.Series):
    """
    Train a linear regression model and calculate RMSE.

    Returns
    -------
    model: trained model
    rmse: float
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)

    return model, rmse
