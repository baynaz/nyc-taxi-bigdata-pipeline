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
            'fare_amount': [10, 20, 30],
            'trip_distance': [1, 2, 3],
            'passenger_count': [1, 2, 1]
        })
        X, y = prepare_features(df_test)
        self.assertEqual(X.shape, (3, 2))
        self.assertEqual(y.shape[0], 3)

    def test_train_model(self):
        X = pd.DataFrame({'trip_distance': [1, 2, 3, 4], 'passenger_count': [1, 2, 1, 3]})
        y = pd.Series([10, 20, 30, 40])
        model, rmse = train_model(X, y)
        self.assertTrue(rmse >= 0)


if __name__ == "__main__":
    unittest.main()
