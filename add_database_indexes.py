"""Add performance indexes to database tables"""
import sqlite3

DB_PATH = "database/nhl_predictions.db"

def add_indexes():
    """Add indexes to frequently queried columns"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    indexes = [
        # Predictions table indexes
        ("idx_predictions_date_tier",
         "CREATE INDEX IF NOT EXISTS idx_predictions_date_tier ON predictions(game_date, confidence_tier)"),

        ("idx_predictions_date_player",
         "CREATE INDEX IF NOT EXISTS idx_predictions_date_player ON predictions(game_date, player_name)"),

        ("idx_predictions_date_prob",
         "CREATE INDEX IF NOT EXISTS idx_predictions_date_prob ON predictions(game_date, probability DESC)"),

        # Edges table indexes
        ("idx_edges_date_edge",
         "CREATE INDEX IF NOT EXISTS idx_edges_date_edge ON prizepicks_edges(date, edge DESC)"),

        ("idx_edges_date_player",
         "CREATE INDEX IF NOT EXISTS idx_edges_date_player ON prizepicks_edges(date, player_name)"),

        ("idx_edges_date_ev",
         "CREATE INDEX IF NOT EXISTS idx_edges_date_ev ON prizepicks_edges(date, expected_value DESC)"),

        # Parlays table indexes
        ("idx_parlays_date",
         "CREATE INDEX IF NOT EXISTS idx_parlays_date ON gto_parlays(date)"),

        ("idx_parlays_date_id",
         "CREATE INDEX IF NOT EXISTS idx_parlays_date_id ON gto_parlays(date, Parlay_ID)"),

        # Player stats indexes
        ("idx_player_stats_name_season",
         "CREATE INDEX IF NOT EXISTS idx_player_stats_name_season ON player_stats(player_name, season)"),

        ("idx_player_stats_team_season",
         "CREATE INDEX IF NOT EXISTS idx_player_stats_team_season ON player_stats(team, season)"),
    ]

    print("Adding database indexes...")
    print()

    for idx_name, idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            print(f"[+] Created: {idx_name}")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print(f"[=] Exists: {idx_name}")
            else:
                print(f"[!] Failed: {idx_name} - {e}")

    conn.commit()
    conn.close()

    print()
    print("="*60)
    print("Database indexes added successfully!")
    print("="*60)
    print()
    print("Impact:")
    print("  - Faster queries on date + tier/player/probability")
    print("  - Improved dashboard performance")
    print("  - Better performance as data grows")
    print()
    print("Next time you query predictions, edges, or parlays,")
    print("the database will use these indexes automatically.")

if __name__ == "__main__":
    add_indexes()
