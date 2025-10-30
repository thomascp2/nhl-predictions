"""
Test the parlay logger with the user's actual observation
"""

from log_parlay import log_parlay_quick
from prizepicks_odds_scraper import PrizePicksOddsDatabase
import sqlite3
import pandas as pd

print("="*80)
print("TESTING PARLAY LOGGER")
print("="*80)
print()

# Test with user's actual parlay observation
picks = [
    {'player_name': 'Auston Matthews', 'prop_type': 'shots', 'line': 3.5},
    {'player_name': 'Kirill Marchenko', 'prop_type': 'shots', 'line': 2.5}
]

print("Logging test parlay:")
print(f"  Matthews SHOTS O3.5 + Marchenko SHOTS O2.5")
print(f"  Actual payout: 2.25x")
print()

log_parlay_quick(picks, 2.25, '2025-10-29')

print()
print("="*80)
print("VERIFYING DATABASE ENTRIES")
print("="*80)
print()

conn = sqlite3.connect('database/nhl_predictions.db')

# Check parlay observations table
print("Parlay Observations:")
df_parlays = pd.read_sql("""
    SELECT date, num_legs, actual_payout, created_at
    FROM prizepicks_parlay_observations
    ORDER BY created_at DESC
    LIMIT 5
""", conn)
print(df_parlays.to_string(index=False))
print()

# Check observed odds table
print("Observed Individual Odds:")
df_odds = pd.read_sql("""
    SELECT player_name, prop_type, line, implied_multiplier, confidence, observations
    FROM prizepicks_observed_odds
    WHERE date = '2025-10-29'
    ORDER BY confidence DESC, observations DESC
""", conn)
print(df_odds.to_string(index=False))
print()

conn.close()

print("="*80)
print("TEST VERIFICATION")
print("="*80)
print()

# Verify the calculation
db = PrizePicksOddsDatabase()

for pick in picks:
    mult, conf = db.get_implied_odds(
        pick['player_name'],
        pick['prop_type'],
        pick['line'],
        '2025-10-29'
    )
    print(f"{pick['player_name']} {pick['prop_type'].upper()} O{pick['line']}")
    print(f"  Implied multiplier: {mult:.2f}x")
    print(f"  Confidence: {conf:.0%}")

    # Verify calculation
    import numpy as np
    expected_mult = np.sqrt(2.25)
    if abs(mult - expected_mult) < 0.01:
        print(f"  [PASS] Calculation correct (sqrt(2.25) = {expected_mult:.2f})")
    else:
        print(f"  [FAIL] Expected {expected_mult:.2f}, got {mult:.2f}")
    print()

db.close()

print("="*80)
print("[SUCCESS] Parlay logger test complete!")
print("="*80)
