from preprocessing import prepare_features
from model import train_model
import pandas as pd
import os

def main():
    # chemin vers le fichier Parquet déjà existant
    local_path = "ex01_data_retrieval/data/raw/yellow_tripdata_2025-01.parquet"

    # vérifier que le fichier existe
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    # charger le parquet
    df = pd.read_parquet(local_path)
    print(f"Data loaded with shape: {df.shape}")

    # préparer les features
    X, y = prepare_features(df)

    # entraîner le modèle
    model, rmse = train_model(X, y)
    print(f"Model trained. RMSE on test set: {rmse:.2f}")


if __name__ == "__main__":
    main()
