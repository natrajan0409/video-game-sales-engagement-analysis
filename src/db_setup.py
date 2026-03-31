"""
Database Setup Module
Creates a SQLite database with normalized tables for video game data.
Supports both SQLite (local) and MySQL (optional).
"""
import os
import sqlite3
import pandas as pd


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "videogames.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection):
    """Create normalized tables."""
    cursor = conn.cursor()

    cursor.executescript("""
        -- Platforms dimension
        CREATE TABLE IF NOT EXISTS platforms (
            platform_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT    NOT NULL UNIQUE
        );

        -- Genres dimension
        CREATE TABLE IF NOT EXISTS genres (
            genre_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_name TEXT    NOT NULL UNIQUE
        );

        -- Publishers dimension
        CREATE TABLE IF NOT EXISTS publishers (
            publisher_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            publisher_name TEXT    NOT NULL UNIQUE
        );

        -- Developers (Teams) dimension
        CREATE TABLE IF NOT EXISTS developers (
            developer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            developer_name TEXT    NOT NULL UNIQUE
        );

        -- Core games table (from games.csv - engagement data)
        CREATE TABLE IF NOT EXISTS games (
            game_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT    NOT NULL UNIQUE,
            developer_id     INTEGER REFERENCES developers(developer_id),
            release_year     INTEGER,
            rating           REAL,
            times_listed     INTEGER DEFAULT 0,
            num_reviews      INTEGER DEFAULT 0,
            plays            INTEGER DEFAULT 0,
            playing          INTEGER DEFAULT 0,
            backlogs         INTEGER DEFAULT 0,
            wishlist         INTEGER DEFAULT 0,
            primary_genre_id INTEGER REFERENCES genres(genre_id)
        );

        -- Sales records (from vgsales.csv)
        CREATE TABLE IF NOT EXISTS sales (
            sale_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            game_title   TEXT    NOT NULL,
            platform_id  INTEGER REFERENCES platforms(platform_id),
            publisher_id INTEGER REFERENCES publishers(publisher_id),
            genre_id     INTEGER REFERENCES genres(genre_id),
            release_year INTEGER,
            na_sales     REAL    DEFAULT 0,
            eu_sales     REAL    DEFAULT 0,
            jp_sales     REAL    DEFAULT 0,
            other_sales  REAL    DEFAULT 0,
            global_sales REAL    DEFAULT 0
        );

        -- Merged view reference table
        CREATE TABLE IF NOT EXISTS merged_games (
            merged_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id      INTEGER REFERENCES games(game_id),
            sale_id      INTEGER REFERENCES sales(sale_id)
        );
    """)
    conn.commit()
    print("[OK] Schema created")


def _get_or_insert(cursor, table: str, id_col: str, name_col: str, name: str) -> int:
    cursor.execute(f"SELECT {id_col} FROM {table} WHERE {name_col} = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"INSERT INTO {table} ({name_col}) VALUES (?)", (name,))
    return cursor.lastrowid


def load_games_to_db(conn: sqlite3.Connection, games_df: pd.DataFrame):
    cursor = conn.cursor()
    inserted = 0
    for _, row in games_df.iterrows():
        dev_id = _get_or_insert(cursor, "developers", "developer_id", "developer_name",
                                 str(row.get("Team", "Unknown")))
        genre_id = _get_or_insert(cursor, "genres", "genre_id", "genre_name",
                                   str(row.get("Primary Genre", "Unknown")))
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO games
                    (title, developer_id, release_year, rating, times_listed,
                     num_reviews, plays, playing, backlogs, wishlist, primary_genre_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                str(row.get("Title", row.get("Game", ""))),
                dev_id,
                int(row["Release Year"]) if pd.notna(row.get("Release Year")) else None,
                float(row.get("Rating", 0)),
                int(row.get("Times Listed", 0)),
                int(row.get("Number of Reviews", 0)),
                int(row.get("Plays", 0)),
                int(row.get("Playing", 0)),
                int(row.get("Backlogs", 0)),
                int(row.get("Wishlist", 0)),
                genre_id,
            ))
            inserted += 1
        except Exception:
            pass
    conn.commit()
    print(f"[OK] Inserted {inserted:,} games into DB")


def load_sales_to_db(conn: sqlite3.Connection, sales_df: pd.DataFrame):
    cursor = conn.cursor()
    inserted = 0
    for _, row in sales_df.iterrows():
        platform_id = _get_or_insert(cursor, "platforms", "platform_id", "platform_name",
                                      str(row.get("Platform", "Unknown")))
        publisher_id = _get_or_insert(cursor, "publishers", "publisher_id", "publisher_name",
                                       str(row.get("Publisher", "Unknown")))
        genre_id = _get_or_insert(cursor, "genres", "genre_id", "genre_name",
                                   str(row.get("Genre", "Unknown")))
        try:
            cursor.execute("""
                INSERT INTO sales
                    (game_title, platform_id, publisher_id, genre_id, release_year,
                     na_sales, eu_sales, jp_sales, other_sales, global_sales)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                str(row.get("Name", row.get("Game", ""))),
                platform_id,
                publisher_id,
                genre_id,
                int(row.get("Year", 0)) if pd.notna(row.get("Year")) else None,
                float(row.get("NA_Sales", 0)),
                float(row.get("EU_Sales", 0)),
                float(row.get("JP_Sales", 0)),
                float(row.get("Other_Sales", 0)),
                float(row.get("Global_Sales", 0)),
            ))
            inserted += 1
        except Exception:
            pass
    conn.commit()
    print(f"[OK] Inserted {inserted:,} sales records into DB")


def setup_database(games_df: pd.DataFrame, sales_df: pd.DataFrame,
                   db_path: str = DB_PATH) -> sqlite3.Connection:
    """Full pipeline: create schema and load both datasets."""
    # Remove old DB to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = get_connection(db_path)
    create_schema(conn)
    load_games_to_db(conn, games_df)
    load_sales_to_db(conn, sales_df)
    print(f"[OK] Database ready at: {os.path.abspath(db_path)}")
    return conn
