"""
Data Loader Module
Handles loading of games.csv and vgsales.csv datasets.
"""
import os
import pandas as pd


class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_games(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, "games.csv")
        print(f"Loading {path}...")
        df = pd.read_csv(path, index_col=0)
        print(f"[OK] Loaded {len(df):,} records from games.csv")
        return df

    def load_vgsales(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, "vgsales.csv")
        print(f"Loading {path}...")
        df = pd.read_csv(path)
        print(f"[OK] Loaded {len(df):,} records from vgsales.csv")
        return df


def load_games(data_dir: str) -> pd.DataFrame:
    return DataLoader(data_dir).load_games()


def load_vgsales(data_dir: str) -> pd.DataFrame:
    return DataLoader(data_dir).load_vgsales()
