"""
Data Cleaner Module
Handles cleaning and preprocessing of games.csv and vgsales.csv.
"""
import re
import pandas as pd


def parse_shorthand(value) -> float:
    """Convert shorthand strings like '17K', '1.2M' to floats."""
    if pd.isna(value):
        return 0.0
    val = str(value).strip().replace(",", "")
    if val == "" or val == "--":
        return 0.0
    multiplier = 1
    if val.upper().endswith("K"):
        multiplier = 1_000
        val = val[:-1]
    elif val.upper().endswith("M"):
        multiplier = 1_000_000
        val = val[:-1]
    try:
        return float(val) * multiplier
    except ValueError:
        return 0.0


def parse_release_year(date_str) -> float:
    """Extract year from various date string formats."""
    if pd.isna(date_str) or str(date_str).strip() == "":
        return float("nan")
    date_str = str(date_str).strip()
    # Try formats: "Jan 21, 2022", "2022", "Jan 2022"
    for pattern in [r"\b(19|20)\d{2}\b"]:
        match = re.search(pattern, date_str)
        if match:
            return float(match.group())
    return float("nan")


def clean_games(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean games.csv:
    - Drop unnamed index column
    - Convert K/M columns to numeric
    - Parse release year from Release Date
    - Normalize Genre list to first genre
    - Fill missing values
    """
    df = df.copy()

    # Drop unnamed index column if present
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    # Convert shorthand numeric columns
    for col in ["Times Listed", "Number of Reviews", "Plays", "Playing", "Backlogs", "Wishlist"]:
        if col in df.columns:
            df[col] = df[col].apply(parse_shorthand)

    # Parse release year
    df["Release Year"] = df["Release Date"].apply(parse_release_year)

    # Fill missing Rating with median
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Rating"] = df["Rating"].fillna(df["Rating"].median())

    # Fill missing Team
    df["Team"] = df["Team"].fillna("Unknown")

    # Fill missing Summary
    if "Summary" in df.columns:
        df["Summary"] = df["Summary"].fillna("")

    # Extract primary genre (first in comma-separated list)
    df["Primary Genre"] = df["Genres"].apply(
        lambda x: str(x).split(",")[0].strip() if pd.notna(x) else "Unknown"
    )

    # Normalize Title for merging
    df["Game"] = df["Title"].str.strip()

    # Drop duplicate titles
    df.drop_duplicates(subset=["Game"], keep="first", inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"[OK] Cleaned games data: {len(df):,} records, {df.shape[1]} columns")
    return df


def clean_vgsales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean vgsales.csv:
    - Fill missing Year with median
    - Fill missing Publisher with 'Unknown'
    - Normalize Name for merging
    """
    df = df.copy()

    # Fill missing Publisher
    df["Publisher"] = df["Publisher"].fillna("Unknown")

    # Fill missing Year with median
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    median_year = df["Year"].median()
    df["Year"] = df["Year"].fillna(median_year).astype("Int64")

    # Normalize Name for merging
    df["Game"] = df["Name"].str.strip()

    print(f"[OK] Cleaned vgsales data: {len(df):,} records, {df.shape[1]} columns")
    return df


def merge_datasets(games_df: pd.DataFrame, vgsales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge games and vgsales on normalized Game name.
    Uses inner join; only games present in both datasets are kept.
    """
    merged = pd.merge(games_df, vgsales_df, on="Game", how="inner")
    print(f"[OK] Merged dataset: {len(merged):,} records")
    return merged


class DataCleaner:
    def __init__(self):
        pass

    def clean_games(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_games(df)

    def clean_vgsales(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_vgsales(df)

    def merge(self, games_df: pd.DataFrame, vgsales_df: pd.DataFrame) -> pd.DataFrame:
        return merge_datasets(games_df, vgsales_df)


# Convenience alias used in older notebooks
def clean_data(df: pd.DataFrame, dataset: str = "games") -> pd.DataFrame:
    if dataset == "games":
        return clean_games(df)
    elif dataset == "vgsales":
        return clean_vgsales(df)
    return df
