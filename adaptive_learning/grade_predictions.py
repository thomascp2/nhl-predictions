"""
Adaptive Learning System - Prediction Grading Script

This script allows you to manually grade predictions after games complete.
The graded outcomes are used by the learning engine to improve future predictions.

Usage:
    python adaptive_learning/grade_predictions.py 2025-10-31

Features:
- Manual entry of actual stats
- Auto-fetches predictions from database
- Bulk grading with skip options
- Can re-grade if you made a mistake
- Progress saving (can quit and resume)
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = "database/nhl_predictions.db"


def get_predictions_to_grade(date: str) -> List[Dict]:
    """
    Fetch predictions for a specific date that need grading

    Args:
        date: Game date (YYYY-MM-DD)

    Returns:
        List of prediction dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT
            p.id,
            p.game_date,
            p.player_name,
            p.team,
            p.opponent,
            p.prop_type,
            p.line,
            p.prediction,
            p.probability,
            p.confidence_tier,
            p.model_version
        FROM predictions p
        WHERE p.game_date = ?
        AND p.id NOT IN (
            SELECT prediction_id FROM prediction_outcomes
            WHERE prediction_id IS NOT NULL
        )
        ORDER BY
            p.prop_type,
            p.player_name,
            p.line
    """

    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    conn.close()

    predictions = []
    for row in rows:
        predictions.append({
            'id': row[0],
            'game_date': row[1],
            'player_name': row[2],
            'team': row[3],
            'opponent': row[4],
            'prop_type': row[5],
            'line': row[6],
            'prediction': row[7],
            'probability': row[8],
            'confidence_tier': row[9],
            'model_version': row[10]
        })

    return predictions


def check_already_graded(date: str) -> int:
    """Check how many predictions are already graded for this date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM prediction_outcomes
        WHERE game_date = ?
    """, (date,))

    count = cursor.fetchone()[0]
    conn.close()
    return count


def save_outcome(prediction: Dict, actual_stat: float, outcome: str):
    """
    Save prediction outcome to database

    Args:
        prediction: Prediction dictionary
        actual_stat: Actual stat value achieved
        outcome: 'HIT' or 'MISS'
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prediction_outcomes (
            prediction_id,
            game_date,
            player_name,
            team,
            opponent,
            prop_type,
            line,
            predicted_direction,
            predicted_probability,
            confidence_tier,
            model_version,
            actual_stat_value,
            outcome,
            graded_at,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prediction['id'],
        prediction['game_date'],
        prediction['player_name'],
        prediction['team'],
        prediction['opponent'],
        prediction['prop_type'],
        prediction['line'],
        prediction['prediction'],
        prediction['probability'],
        prediction['confidence_tier'],
        prediction['model_version'],
        actual_stat,
        outcome,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def grade_prediction(prediction: Dict) -> Optional[Dict]:
    """
    Interactive grading for a single prediction

    Args:
        prediction: Prediction dictionary

    Returns:
        Grading result dict or None if skipped
    """
    print("\n" + "=" * 80)
    print(f"Player: {prediction['player_name']} ({prediction['team']} vs {prediction['opponent']})")
    print(f"Prop: {prediction['prop_type'].upper()} {prediction['prediction']} {prediction['line']}")
    print(f"Our Prediction: {prediction['probability']*100:.1f}% | Tier: {prediction['confidence_tier']}")
    print("=" * 80)

    while True:
        actual_input = input(f"\nActual {prediction['prop_type']}: (or 's' to skip, 'q' to quit): ").strip().lower()

        if actual_input == 'q':
            return 'QUIT'

        if actual_input == 's':
            print("[Skipped]")
            return None

        try:
            actual_stat = float(actual_input)
            break
        except ValueError:
            print("Invalid input. Enter a number (e.g., 2.0), 's' to skip, or 'q' to quit.")

    # Determine outcome
    if prediction['prediction'] == 'OVER':
        hit = actual_stat > prediction['line']
    else:  # UNDER
        hit = actual_stat < prediction['line']

    outcome = 'HIT' if hit else 'MISS'

    # Show result
    if hit:
        print(f"✅ HIT! ({actual_stat} {'>' if prediction['prediction'] == 'OVER' else '<'} {prediction['line']})")
    else:
        print(f"❌ MISS ({actual_stat} {'<=' if prediction['prediction'] == 'OVER' else '>='} {prediction['line']})")

    # Save
    save_outcome(prediction, actual_stat, outcome)

    return {
        'actual_stat': actual_stat,
        'outcome': outcome
    }


def show_summary(date: str):
    """Show grading summary for the date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
            AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) as accuracy
        FROM prediction_outcomes
        WHERE game_date = ?
    """, (date,))

    total, hits, accuracy = cursor.fetchone()

    if total == 0:
        print("\nNo predictions graded yet for this date.")
        conn.close()
        return

    print("\n" + "=" * 80)
    print(f"GRADING SUMMARY FOR {date}")
    print("=" * 80)
    print(f"Total Graded: {total}")
    print(f"Hits: {hits}")
    print(f"Misses: {total - hits}")
    print(f"Accuracy: {accuracy*100:.1f}%")

    # By prop type
    cursor.execute("""
        SELECT
            prop_type,
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
            AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) as accuracy
        FROM prediction_outcomes
        WHERE game_date = ?
        GROUP BY prop_type
        ORDER BY accuracy DESC
    """, (date,))

    print("\nBy Prop Type:")
    print("-" * 80)
    for prop_type, total, hits, accuracy in cursor.fetchall():
        print(f"  {prop_type:15s}: {hits}/{total} ({accuracy*100:.1f}%)")

    # By tier
    cursor.execute("""
        SELECT
            confidence_tier,
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
            AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) as accuracy
        FROM prediction_outcomes
        WHERE game_date = ?
        GROUP BY confidence_tier
        ORDER BY
            CASE confidence_tier
                WHEN 'T1-ELITE' THEN 1
                WHEN 'T2-STRONG' THEN 2
                WHEN 'T3-MODERATE' THEN 3
                WHEN 'T3-MARGINAL' THEN 4
                WHEN 'T4-FADE' THEN 5
                ELSE 6
            END
    """, (date,))

    print("\nBy Confidence Tier:")
    print("-" * 80)
    for tier, total, hits, accuracy in cursor.fetchall():
        print(f"  {tier:15s}: {hits}/{total} ({accuracy*100:.1f}%)")

    print("=" * 80)

    conn.close()


def main():
    print("\n" + "=" * 80)
    print("ADAPTIVE LEARNING - PREDICTION GRADING")
    print("=" * 80)

    # Get date
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        # Default to yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        date = input(f"\nEnter date to grade (YYYY-MM-DD) [default: {yesterday}]: ").strip()
        if not date:
            date = yesterday

    print(f"\nGrading predictions for: {date}")

    # Check if already graded
    already_graded = check_already_graded(date)
    if already_graded > 0:
        print(f"\n⚠️  {already_graded} predictions already graded for this date")
        cont = input("Continue with remaining predictions? (y/n): ").strip().lower()
        if cont != 'y':
            show_summary(date)
            return

    # Load predictions
    predictions = get_predictions_to_grade(date)

    if not predictions:
        print(f"\n✅ All predictions for {date} have been graded!")
        show_summary(date)
        return

    print(f"\nFound {len(predictions)} predictions to grade")
    print("\nInstructions:")
    print("  - Enter actual stat value (e.g., 2.0 for 2 points)")
    print("  - Type 's' to skip a prediction")
    print("  - Type 'q' to quit and resume later")
    print("\n" + "-" * 80)

    # Grade each prediction
    graded_count = 0
    skipped_count = 0

    for i, prediction in enumerate(predictions, 1):
        print(f"\n[{i}/{len(predictions)}]")

        result = grade_prediction(prediction)

        if result == 'QUIT':
            print(f"\n\nQuitting... Graded {graded_count} predictions.")
            print("Run this script again to continue from where you left off.\n")
            show_summary(date)
            return

        if result is None:
            skipped_count += 1
        else:
            graded_count += 1

    # Final summary
    print("\n" + "=" * 80)
    print("GRADING COMPLETE!")
    print("=" * 80)
    print(f"Graded: {graded_count}")
    print(f"Skipped: {skipped_count}")

    show_summary(date)

    print("\n✅ Next step: Run the learning engine to analyze these outcomes")
    print(f"   python adaptive_learning/learning_engine.py")


if __name__ == "__main__":
    main()
