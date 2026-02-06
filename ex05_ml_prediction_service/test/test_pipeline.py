"""
test_pipeline.py
Unit tests for the ML pipeline modules.
"""

import unittest
import pandas as pd

from src.preprocessing import prepare_features
from src.model import train_model


class TestMLPipeline(unittest.TestCase):
    def test_prepare_features(self):
        df_test = pd.DataFrame({
            "tpep_pickup_datetime": ["2025-01-01 10:00:00", "2025-01-01 11:00:00", "2025-01-01 12:00:00"],
            "tpep_dropoff_datetime": ["2025-01-01 10:10:00", "2025-01-01 11:20:00", "2025-01-01 12:05:00"],
            "total_amount": [10, 20, 30],
            "trip_distance": [1, 2, 3],
            "passenger_count": [1, 2, 1],
        })

        X, y, df_clean = prepare_features(df_test)
        self.assertEqual(y.shape[0], 3)
        self.assertTrue(len(X.columns) >= 2)
        self.assertTrue("trip_duration_min" in df_clean.columns)

    def test_train_model(self):
        X = pd.DataFrame({
            "trip_distance": [1, 2, 3, 4],
            "passenger_count": [1, 2, 1, 3],
            "hour": [10, 11, 12, 13],
        })
        y = pd.Series([10, 20, 30, 40])

        result = train_model(X, y)
        self.assertTrue(result.rmse >= 0)
        self.assertTrue(result.mae >= 0)
        self.assertIsNotNone(result.pipeline)


if __name__ == "__main__":
    unittest.main()
