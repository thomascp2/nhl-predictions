"""
Database Setup and Validation
Ensures all required tables exist for the complete NHL betting system
"""

import sqlite3
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"


def create_gto_parlays_table(conn):
    """Create table for storing GTO parlay recommendations"""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gto_parlays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            parlay_id TEXT NOT NULL,
            num_legs INTEGER NOT NULL,
            picks_json TEXT NOT NULL,
            combined_probability REAL,
            payout_multiplier REAL,
            expected_value REAL,
            kelly_fraction REAL,
            recommended_bet_size REAL,
            parlay_tier TEXT,
            correlation_score REAL,
            created_at TEXT,
            result TEXT,
            actual_payout REAL,
            graded_at TEXT,
            UNIQUE(date, parlay_id)
        )
    """)

    print("[SUCCESS] gto_parlays table ready")


def add_grading_columns_to_edges(conn):
    """Add grading columns to prizepicks_edges if they don't exist"""
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(prizepicks_edges)")
    columns = [col[1] for col in cursor.fetchall()]

    columns_to_add = [
        ('result', 'TEXT'),
        ('actual_value', 'REAL'),
        ('graded_at', 'TEXT')
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE prizepicks_edges ADD COLUMN {col_name} {col_type}")
            print(f"[SUCCESS] Added {col_name} column to prizepicks_edges")


def validate_database():
    """Validate all required tables exist"""
    print("="*80)
    print("DATABASE SETUP AND VALIDATION")
    print("="*80)
    print()

    conn = sqlite3.connect(DB_PATH)

    # Create/validate GTO parlays table
    print("Setting up gto_parlays table...")
    create_gto_parlays_table(conn)

    # Add grading columns to edges
    print("Adding grading columns to prizepicks_edges...")
    add_grading_columns_to_edges(conn)

    conn.commit()

    # Validate all expected tables
    print()
    print("Validating tables...")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    required_tables = [
        'predictions',
        'prizepicks_edges',
        'prizepicks_observed_odds',
        'prizepicks_parlay_observations',
        'gto_parlays',
        'player_stats',
        'games'
    ]

    print()
    for table in required_tables:
        if table in tables:
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"[OK] {table:35s} ({count:,} rows)")
        else:
            print(f"[MISSING] {table}")

    conn.close()

    print()
    print("="*80)
    print("DATABASE READY")
    print("="*80)


if __name__ == "__main__":
    validate_database()
