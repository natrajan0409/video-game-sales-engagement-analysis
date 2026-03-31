"""
Run this script once to clean data and populate the SQLite database.
Usage: python setup_db.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import DataLoader
from src.data_cleaner import clean_games, clean_vgsales, merge_datasets
from src.db_setup import setup_database

DATA_DIR = os.path.join(os.path.dirname(__file__), "Rawdata")
CLEAN_DIR = os.path.join(os.path.dirname(__file__), "Cleandata")

os.makedirs(CLEAN_DIR, exist_ok=True)

loader    = DataLoader(DATA_DIR)
raw_games = loader.load_games()
raw_sales = loader.load_vgsales()

games_df  = clean_games(raw_games)
sales_df  = clean_vgsales(raw_sales)
merged_df = merge_datasets(games_df, sales_df)

games_df.to_csv(os.path.join(CLEAN_DIR, "games_clean.csv"), index=False)
sales_df.to_csv(os.path.join(CLEAN_DIR, "vgsales_clean.csv"), index=False)
merged_df.to_csv(os.path.join(CLEAN_DIR, "merged_dataset.csv"), index=False)
print(f"Saved cleaned CSVs to {CLEAN_DIR}")

conn = setup_database(games_df, sales_df)
conn.close()
print("Database setup complete: videogames.db")
