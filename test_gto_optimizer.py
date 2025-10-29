"""
Test GTO Parlay Optimizer with simulated edge plays
Uses today's predictions to create test data
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"

def create_test_edge_plays():
    """Create test edge plays from today's predictions"""

    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime('%Y-%m-%d')

    # Get today's T1-ELITE picks
    query = """
        SELECT
            player_name,
            team,
            opponent,
            prop_type,
            line,
            probability,
            expected_value,
            game_id
        FROM predictions
        WHERE game_date = ?
        AND confidence_tier = 'T1-ELITE'
        ORDER BY probability DESC
    """

    picks = pd.read_sql_query(query, conn, params=(today,))

    if len(picks) == 0:
        print("[WARNING] No T1-ELITE picks for today")
        conn.close()
        return False

    print(f"Found {len(picks)} T1-ELITE picks for today")
    print()

    # Create prizepicks_edges table if not exists
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prizepicks_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            player_name TEXT,
            team TEXT,
            opponent TEXT,
            prop_type TEXT,
            line REAL,
            odds_type TEXT,
            our_probability REAL,
            pp_implied_probability REAL,
            edge REAL,
            expected_value REAL,
            kelly_score REAL,
            payout_multiplier REAL,
            created_at TEXT
        )
    """)

    # Calculate edge for each pick
    # Assume PrizePicks offers standard 3x payout (33.3% implied prob)
    pp_implied_prob = 0.333  # 1/3.0
    payout = 3.0

    for _, pick in picks.iterrows():
        our_prob = pick['probability']
        edge = (our_prob - pp_implied_prob) * 100

        # Calculate Kelly score
        kelly = ((payout - 1) * our_prob - (1 - our_prob)) / (payout - 1)
        kelly = max(0, kelly) * 100  # Convert to percentage

        if edge >= 7.0:  # Only add if 7%+ edge
            cursor.execute("""
                INSERT OR REPLACE INTO prizepicks_edges
                (date, player_name, team, opponent, prop_type, line, odds_type,
                 our_probability, pp_implied_probability, edge, expected_value,
                 kelly_score, payout_multiplier, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                pick['player_name'],
                pick['team'],
                pick['opponent'],
                pick['prop_type'],
                pick['line'],
                'standard',
                our_prob,
                pp_implied_prob,
                edge,
                pick['expected_value'],
                kelly,
                payout,
                datetime.now().isoformat()
            ))

    conn.commit()

    # Verify
    cursor.execute("SELECT COUNT(*) FROM prizepicks_edges WHERE date = ?", (today,))
    count = cursor.fetchone()[0]

    print(f"[SUCCESS] Created {count} test edge plays in database")
    print()

    conn.close()
    return True


def main():
    """Run test workflow"""
    print("\n" + "="*80)
    print("GTO OPTIMIZER TEST")
    print("="*80)
    print()

    # Step 1: Create test edge plays
    print("[1/2] Creating test edge plays from predictions...")
    if not create_test_edge_plays():
        print("[ERROR] Failed to create test data")
        return

    # Step 2: Run GTO optimizer
    print("[2/2] Running GTO optimizer...")
    print()

    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "gto_parlay_optimizer.py"],
        capture_output=False,
        text=True
    )

    if result.returncode == 0:
        print("\n" + "="*80)
        print("[SUCCESS] TEST COMPLETE")
        print("="*80)
        print()
        print("Generated files:")
        print("   - GTO_PARLAYS_*.csv (parlay breakdown)")
        print()
        print("Next steps:")
        print("   1. Review the output above")
        print("   2. Check the CSV file")
        print("   3. Run live: python run_complete_workflow_gto.py")
    else:
        print("\n[ERROR] Test failed - check output above")


if __name__ == "__main__":
    main()
