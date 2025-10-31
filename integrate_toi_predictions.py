"""
TOI Predictions Integration

Integrates Time on Ice (TOI) predictions into the main prediction system.
Adds TOI predictions to the predictions table for edge detection.

Usage:
    python integrate_toi_predictions.py 2025-10-30
"""

import sqlite3
import pandas as pd
from datetime import datetime
import sys
from system_logger import get_logger

logger = get_logger(__name__)

DB_PATH = "database/nhl_predictions.db"


def get_toi_predictions(date: str) -> pd.DataFrame:
    """
    Get TOI predictions from TOI system

    Args:
        date: Game date (YYYY-MM-DD)

    Returns:
        DataFrame with TOI predictions
    """
    conn = sqlite3.connect(DB_PATH)

    # Check if toi_predictions table exists
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='toi_predictions'
    """)

    if not cursor.fetchone():
        logger.warning("TOI predictions table doesn't exist yet")
        logger.info("Run: python generate_toi_predictions.py")
        conn.close()
        return pd.DataFrame()

    # Fetch TOI predictions for date
    query = """
        SELECT
            player_name,
            team,
            opponent,
            predicted_toi_minutes,
            confidence,
            game_date
        FROM toi_predictions
        WHERE game_date = ?
        ORDER BY predicted_toi_minutes DESC
    """

    df = pd.read_sql_query(query, conn, params=(date,))
    conn.close()

    return df


def convert_toi_to_predictions(toi_df: pd.DataFrame, date: str) -> list:
    """
    Convert TOI predictions to standard prediction format

    PrizePicks offers TOI lines like:
    - O15.5 minutes
    - O17.5 minutes
    - O19.5 minutes

    Args:
        toi_df: TOI predictions DataFrame
        date: Game date

    Returns:
        List of prediction dictionaries
    """
    predictions = []

    # Common TOI lines on PrizePicks
    toi_lines = [15.5, 17.5, 19.5, 21.5]

    for _, row in toi_df.iterrows():
        player = row['player_name']
        team = row['team']
        opponent = row['opponent']
        predicted_toi = row['predicted_toi_minutes']
        confidence = row['confidence']

        # Generate predictions for each line
        for line in toi_lines:
            if predicted_toi > line:
                # Calculate probability of going over
                # Use confidence and distance from line
                distance = predicted_toi - line
                std_dev = 2.0  # Assume 2 minute standard deviation

                # Simple probability calculation
                # Higher distance = higher probability
                # Higher confidence = higher probability
                base_prob = 0.50 + (distance / (2 * std_dev)) * 0.40

                # Adjust by confidence
                confidence_multiplier = confidence / 100.0  # 0-1
                probability = base_prob * confidence_multiplier

                # Clamp to reasonable range
                probability = max(0.30, min(0.95, probability))

                # Assign confidence tier
                if probability >= 0.75:
                    tier = 'T1-ELITE'
                elif probability >= 0.65:
                    tier = 'T2-STRONG'
                else:
                    tier = 'T3-MARGINAL'

                predictions.append({
                    'game_date': date,
                    'player_name': player,
                    'team': team,
                    'opponent': opponent,
                    'prop_type': 'toi',
                    'line': line,
                    'prediction': 'OVER',
                    'probability': probability,
                    'confidence_tier': tier,
                    'reasoning': f"TOI model predicts {predicted_toi:.1f} min (confidence: {confidence:.0f}%)",
                    'base_probability': probability * 0.95,  # Mostly TOI model
                    'ml_boost': probability * 0.05,  # Small ML component
                })

    return predictions


def add_toi_to_predictions_table(predictions: list):
    """
    Add TOI predictions to main predictions table

    Args:
        predictions: List of prediction dictionaries
    """
    if not predictions:
        logger.info("No TOI predictions to add")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added_count = 0

    for pred in predictions:
        # Check if prediction already exists
        cursor.execute("""
            SELECT id FROM predictions
            WHERE game_date = ? AND player_name = ?
            AND prop_type = 'toi' AND line = ?
        """, (pred['game_date'], pred['player_name'], pred['line']))

        if cursor.fetchone():
            # Already exists, skip
            continue

        # Insert prediction
        cursor.execute("""
            INSERT INTO predictions
            (game_date, player_name, team, opponent, prop_type, line,
             prediction, probability, confidence_tier, reasoning,
             base_probability, ml_boost, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred['game_date'],
            pred['player_name'],
            pred['team'],
            pred['opponent'],
            pred['prop_type'],
            pred['line'],
            pred['prediction'],
            pred['probability'],
            pred['confidence_tier'],
            pred['reasoning'],
            pred['base_probability'],
            pred['ml_boost'],
            datetime.now().isoformat()
        ))

        added_count += 1

    conn.commit()
    conn.close()

    logger.info(f"Added {added_count} TOI predictions to database")


def main(date: str = None):
    """
    Main integration function

    Args:
        date: Game date (YYYY-MM-DD), defaults to today
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    logger.info("="*80)
    logger.info("TOI PREDICTIONS INTEGRATION")
    logger.info("="*80)
    logger.info(f"Date: {date}")
    logger.info("")

    # Step 1: Get TOI predictions
    logger.info("[STEP 1] Fetching TOI predictions...")
    toi_df = get_toi_predictions(date)

    if toi_df.empty:
        logger.warning("No TOI predictions found")
        logger.info("Generate TOI predictions first:")
        logger.info("  python generate_toi_predictions.py")
        return

    logger.info(f"Found {len(toi_df)} TOI predictions")

    # Step 2: Convert to standard format
    logger.info("[STEP 2] Converting to prediction format...")
    predictions = convert_toi_to_predictions(toi_df, date)
    logger.info(f"Generated {len(predictions)} TOI line predictions")

    # Step 3: Add to predictions table
    logger.info("[STEP 3] Adding to predictions table...")
    add_toi_to_predictions_table(predictions)

    logger.info("")
    logger.info("="*80)
    logger.info("TOI INTEGRATION COMPLETE")
    logger.info("="*80)
    logger.info("")
    logger.info(f"Total TOI predictions added: {len(predictions)}")
    logger.info(f"Players covered: {len(toi_df)}")
    logger.info("")
    logger.info("These TOI predictions will now be included in:")
    logger.info("  1. Edge detection (prizepicks_multi_line_optimizer.py)")
    logger.info("  2. GTO parlay optimization (gto_parlay_optimizer.py)")
    logger.info("  3. Dashboard views (app.py)")


if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else None
    main(date)
