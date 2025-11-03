"""
Clear and Resave Today's Predictions
"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"

# Get target date from command line or use today
target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')

# Step 1: Clear ALL predictions for target date
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

today = target_date  # Keep variable name for compatibility

cursor.execute("DELETE FROM predictions WHERE game_date = ?", (today,))
deleted = cursor.rowcount
conn.commit()
conn.close()

print(f"[SUCCESS] Deleted {deleted} old predictions")
print()

# Step 2: Generate and save fresh predictions
print("Generating fresh predictions...")

from enhanced_predictions_FIXED_FINAL_FINAL import EnhancedPredictionEngine

engine = EnhancedPredictionEngine()
engine.generate_predictions(today)

# Step 3: Save to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

batch_id = f"batch_{today}_{datetime.now().strftime('%H%M%S')}"
saved = 0

for pred in engine.predictions:
    try:
        if 'Points' in pred['prop']:
            prop_type = 'points'
            line = 0.5
        else:
            prop_type = 'shots'
            line = 2.5
        
        prob = pred['probability']
        # Recalibrated tiers (2025-10-31) - was hitting only 40.9% at T1-ELITE
        if prob >= 0.85:
            tier = 'T1-ELITE'       # Should hit ~65-70%
        elif prob >= 0.75:
            tier = 'T2-STRONG'      # Should hit ~60-65%
        elif prob >= 0.65:
            tier = 'T3-SOLID'       # Should hit ~55-60%
        elif prob >= 0.55:
            tier = 'T4-DECENT'      # Should hit ~50-55%
        else:
            tier = 'T5-FADE'        # Skip these picks
        
        cursor.execute("""
            INSERT INTO predictions
            (game_date, player_name, team, opponent, prop_type, line,
             prediction, probability, expected_value, kelly_score, confidence_tier,
             reasoning, batch_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            pred['player'],
            pred['team'],
            pred['opponent'],
            prop_type,
            line,
            'OVER',  # Points/Shots predictions are always OVER
            pred['probability'],
            pred['expected'],
            pred['confidence'],
            tier,
            pred['reasoning'],
            batch_id,
            datetime.now().isoformat()
        ))
        
        saved += 1
        
    except Exception as e:
        print(f"Error: {e}")

conn.commit()
conn.close()

print(f"\n[SUCCESS] Saved {saved} fresh predictions")
print()

# Verify
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT player_name, prop_type, expected_value, probability
    FROM predictions
    WHERE game_date = ?
    ORDER BY probability DESC
    LIMIT 5
""", (today,))

print("Top 5 predictions in database:")
print("-" * 80)
for player, prop, expected, prob in cursor.fetchall():
    print(f"{player:25} {prop} - {prob*100:.1f}% prob, {expected:.2f} expected")

conn.close()

print()
print("=" * 80)
print("[SUCCESS] ALL DONE!")
print("=" * 80)
print()
print("Now try in Discord:")
print("  !count")
print("  !picks")

engine.close()