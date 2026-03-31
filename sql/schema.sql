-- ============================================================
-- Video Game Sales and Engagement Analysis - SQL Schema
-- Database: SQLite (compatible with MySQL with minor adjustments)
-- ============================================================

PRAGMA foreign_keys = ON;

-- Dimension: Platforms
CREATE TABLE IF NOT EXISTS platforms (
    platform_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT    NOT NULL UNIQUE
);

-- Dimension: Genres
CREATE TABLE IF NOT EXISTS genres (
    genre_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT    NOT NULL UNIQUE
);

-- Dimension: Publishers
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher_name TEXT    NOT NULL UNIQUE
);

-- Dimension: Developers / Teams
CREATE TABLE IF NOT EXISTS developers (
    developer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    developer_name TEXT    NOT NULL UNIQUE
);

-- Fact: Games engagement data (from games.csv)
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

-- Fact: Sales records (from vgsales.csv)
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

-- Bridge: Merged game <-> sales relationship
CREATE TABLE IF NOT EXISTS merged_games (
    merged_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id   INTEGER REFERENCES games(game_id),
    sale_id   INTEGER REFERENCES sales(sale_id)
);

-- ============================================================
-- Useful analytical queries
-- ============================================================

-- Q1: Top-rated games
-- SELECT title, rating FROM games ORDER BY rating DESC LIMIT 10;

-- Q2: Top developers by average rating
-- SELECT d.developer_name, AVG(g.rating) AS avg_rating, COUNT(*) AS game_count
-- FROM games g JOIN developers d ON g.developer_id = d.developer_id
-- GROUP BY d.developer_name HAVING game_count >= 2
-- ORDER BY avg_rating DESC LIMIT 10;

-- Q3: Most common genres
-- SELECT genre_name, COUNT(*) AS cnt
-- FROM games g JOIN genres gn ON g.primary_genre_id = gn.genre_id
-- GROUP BY genre_name ORDER BY cnt DESC;

-- Q10: Region with most sales
-- SELECT 'NA' AS region, SUM(na_sales) AS total FROM sales
-- UNION ALL SELECT 'EU', SUM(eu_sales) FROM sales
-- UNION ALL SELECT 'JP', SUM(jp_sales) FROM sales
-- UNION ALL SELECT 'Other', SUM(other_sales) FROM sales
-- ORDER BY total DESC;

-- Q11: Best-selling platforms
-- SELECT p.platform_name, SUM(s.global_sales) AS total_sales
-- FROM sales s JOIN platforms p ON s.platform_id = p.platform_id
-- GROUP BY p.platform_name ORDER BY total_sales DESC LIMIT 10;

-- Q14: Top 10 best-selling games globally
-- SELECT game_title, SUM(global_sales) AS total
-- FROM sales GROUP BY game_title ORDER BY total DESC LIMIT 10;
