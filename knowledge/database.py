import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent.parent / "data" / "brewery_bot.db"


def get_connection():
    """Create a connection to the brewery bot database."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create all brewery bot database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # BEER STYLES
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beer_styles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bjcp_number TEXT UNIQUE,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            country_of_origin TEXT,
            historical_period TEXT,
            history TEXT,
            description TEXT,
            aroma TEXT,
            appearance TEXT,
            flavor TEXT,
            mouthfeel TEXT,
            ingredients TEXT,
            brewing_notes TEXT,
            typical_abv_min REAL,
            typical_abv_max REAL,
            typical_ibu_min REAL,
            typical_ibu_max REAL,
            typical_og_min REAL,
            typical_og_max REAL,
            typical_fg_min REAL,
            typical_fg_max REAL,
            typical_srm_min REAL,
            typical_srm_max REAL,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------------------------------------
    # GENERAL ENCYCLOPEDIA
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS encyclopedia_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------------------------------------
    # VANISH BEERS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brewery_beers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            style TEXT,
            description TEXT,
            notes TEXT
        )
    """)

    # ---------------------------------------------------------
    # BATCH HISTORY
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brewery_beer_id INTEGER,
            batch_number TEXT,
            brew_date TEXT,
            fermenter TEXT,
            original_gravity REAL,
            final_gravity REAL,
            abv REAL,
            notes TEXT,
            source TEXT,
            FOREIGN KEY (brewery_beer_id)
                REFERENCES brewery_beers(id)
        )
    """)

    # ---------------------------------------------------------
    # FERMENTATION READINGS
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fermentation_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER,
            reading_time TEXT,
            gravity REAL,
            temperature REAL,
            ph REAL,
            notes TEXT,
            source TEXT,
            FOREIGN KEY (batch_id)
                REFERENCES batches(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()

    print("Brewery Bot database initialized successfully.")
    print(f"Database: {DATABASE_PATH}")