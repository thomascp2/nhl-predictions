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

    Enhanced with LINEAR probability model for better calibration.

    PrizePicks offers TOI lines like:
    - O15.5 minutes (bottom-6/bottom-4)
    - O17.5 minutes (middle-6/middle-4)
    - O19.5 minutes (top-6/top-4)
    - O21.5 minutes (elite players)

    Args:
        toi_df: TOI predictions DataFrame
        date: Game date

    Returns:
        List of prediction dictionaries
    """
    predictions = []

    # Expanded TOI lines on PrizePicks
    toi_lines = [13.5, 15.5, 17.5, 19.5, 21.5, 23.5]

    for _, row in toi_df.iterrows():
        player = row['player_name']
        team = row['team']
        opponent = row['opponent']
        predicted_toi = row['predicted_toi_minutes']
        confidence = row['confidence']

        # Estimate standard deviation based on TOI range
        # Elite players (20+ min): More consistent, lower std_dev
        # Middle players (15-20 min): Moderate variance
        # Bottom players (<15 min): Higher variance
        if predicted_toi >= 20:
            std_dev = 1.5  # Elite players: tight distribution
        elif predicted_toi >= 17:
            std_dev = 2.0  # Top-6/Top-4: moderate variance
        elif predicted_toi >= 15:
            std_dev = 2.5  # Middle-6/Middle-4: higher variance
        else:
            std_dev = 3.0  # Bottom-6/Bottom-4: most variance

        # Generate predictions for each line
        for line in toi_lines:
            # Calculate distance from line
            distance = predicted_toi - line

            # LINEAR PROBABILITY MODEL (better than exponential for TOI)
            # Theory: TOI variance is roughly normal, so linear is more accurate
            #
            # P(Over) = 0.5 + (distance / (k * std_dev))
            # where k controls the steepness (we use 4 for gradual slope)
            #
            # Examples:
            # - distance = +2 std_dev → P = 0.5 + 0.5 = 1.0 (clamped to 0.95)
            # - distance = +1 std_dev → P = 0.5 + 0.25 = 0.75
            # - distance = 0 → P = 0.5 (neutral)
            # - distance = -1 std_dev → P = 0.5 - 0.25 = 0.25

            k = 4  # Steepness factor (higher = more gradual)
            linear_prob = 0.50 + (distance / (k * std_dev))

            # Adjust by confidence (high confidence = trust model more)
            # Confidence ranges from 0-100
            confidence_factor = confidence / 100.0  # 0-1

            # Blend with base 0.50 probability based on confidence
            # High confidence = use linear_prob fully
            # Low confidence = regress toward 0.50
            probability = 0.50 + (linear_prob - 0.50) * confidence_factor

            # Clamp to reasonable range
            probability = max(0.25, min(0.95, probability))

            # Only create predictions if probability suggests edge potential
            # Skip extreme mismatches (very low or very high probability)
            if probability < 0.35 or probability > 0.90:
                continue

            # Determine prediction direction
            if probability >= 0.50:
                prediction_direction = 'OVER'
            else:
                prediction_direction = 'UNDER'
                probability = 1.0 - probability  # Flip probability for UNDER

            # Assign confidence tier
            if probability >= 0.75:
                tier = 'T1-ELITE'
            elif probability >= 0.65:
                tier = 'T2-STRONG'
            elif probability >= 0.55:
                tier = 'T3-MARGINAL'
            else:
                tier = 'T4-FADE'

            # Enhanced reasoning
            reasoning = (
                f"TOI model: {predicted_toi:.1f} min (σ={std_dev:.1f}, "
                f"confidence={confidence:.0f}%) | "
                f"Distance: {distance:+.1f} min from {line} line"
            )

            predictions.append({
                'game_date': date,
                'player_name': player,
                'team': team,
                'opponent': opponent,
                'prop_type': 'toi',
                'line': line,
                'prediction': prediction_direction,
                'probability': probability,
                'confidence_tier': tier,
                'reasoning': reasoning,
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
