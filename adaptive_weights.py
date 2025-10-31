"""
Adaptive Model Weights System

Dynamically adjusts ensemble weights based on recent performance.
If statistical model is hitting 75%, increase its weight.
If ML model is struggling, decrease its weight.

Usage:
    from adaptive_weights import get_adaptive_weights

    stat_weight, ml_weight = get_adaptive_weights()
    # Use these weights in ensemble predictions
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Tuple, Dict
from system_logger import get_logger

logger = get_logger(__name__)

DB_PATH = "database/nhl_predictions.db"


def get_model_performance(days_back: int = 7, min_predictions: int = 20) -> Dict:
    """
    Get performance stats for statistical and ML models

    Args:
        days_back: Number of days to look back
        min_predictions: Minimum predictions needed for reliable stats

    Returns:
        Dictionary with performance stats
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    start_date_str = start_date.strftime('%Y-%m-%d')

    # Get graded predictions from last N days
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
            AVG(CASE WHEN is_correct = 1 THEN 1.0 ELSE 0.0 END) as accuracy,
            AVG(base_probability) as avg_base_prob,
            AVG(ml_boost) as avg_ml_boost,
            AVG(probability) as avg_ensemble_prob
        FROM predictions
        WHERE game_date >= ?
        AND is_correct IS NOT NULL
        AND base_probability IS NOT NULL
        AND ml_boost IS NOT NULL
    """, (start_date_str,))

    result = cursor.fetchone()
    conn.close()

    if not result or result[0] < min_predictions:
        logger.warning(f"Not enough graded predictions ({result[0] if result else 0}/{min_predictions})")
        return None

    total, correct, accuracy, avg_base, avg_boost, avg_ensemble = result

    # Estimate individual model performance
    # Statistical model performance ≈ base_probability accuracy
    # ML model performance ≈ how much ml_boost helps

    return {
        'total_predictions': total,
        'correct_predictions': correct,
        'ensemble_accuracy': accuracy,
        'avg_base_probability': avg_base,
        'avg_ml_boost': avg_boost,
        'avg_ensemble_probability': avg_ensemble,
        'days_analyzed': days_back
    }


def calculate_statistical_accuracy(days_back: int = 7) -> float:
    """
    Calculate statistical model accuracy based on base_probability

    We can't directly measure statistical model accuracy since we always
    use ensemble, but we can estimate it by looking at how well
    base_probability correlates with actual results.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    # Get predictions where base_probability is high (>70%)
    # These are mostly driven by statistical model
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            AVG(CASE WHEN is_correct = 1 THEN 1.0 ELSE 0.0 END) as accuracy
        FROM predictions
        WHERE game_date >= ?
        AND is_correct IS NOT NULL
        AND base_probability >= 0.70
        AND base_probability IS NOT NULL
    """, (start_date,))

    result = cursor.fetchone()
    conn.close()

    if not result or result[0] < 10:
        return None

    return result[1]


def calculate_ml_contribution(days_back: int = 7) -> float:
    """
    Calculate how much ML model helps or hurts

    Positive contribution means ML improves accuracy
    Negative contribution means ML hurts accuracy
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    # Compare accuracy when ML boost is positive vs negative
    cursor.execute("""
        SELECT
            CASE WHEN ml_boost > 0 THEN 'positive' ELSE 'negative' END as boost_direction,
            COUNT(*) as total,
            AVG(CASE WHEN is_correct = 1 THEN 1.0 ELSE 0.0 END) as accuracy
        FROM predictions
        WHERE game_date >= ?
        AND is_correct IS NOT NULL
        AND ml_boost IS NOT NULL
        GROUP BY boost_direction
    """, (start_date,))

    results = cursor.fetchall()
    conn.close()

    if len(results) < 2:
        return 0.0

    boost_stats = {row[0]: {'total': row[1], 'accuracy': row[2]} for row in results}

    # If positive boost has higher accuracy, ML is helping
    # If negative boost has higher accuracy, ML is hurting
    positive_acc = boost_stats.get('positive', {}).get('accuracy', 0.5)
    negative_acc = boost_stats.get('negative', {}).get('accuracy', 0.5)

    contribution = positive_acc - negative_acc

    return contribution


def get_adaptive_weights(
    days_back: int = 7,
    min_predictions: int = 20,
    baseline_stat_weight: float = 0.70,
    baseline_ml_weight: float = 0.30,
    max_adjustment: float = 0.20
) -> Tuple[float, float]:
    """
    Calculate adaptive model weights based on recent performance

    Args:
        days_back: Days to look back for performance
        min_predictions: Minimum predictions needed
        baseline_stat_weight: Default statistical weight
        baseline_ml_weight: Default ML weight
        max_adjustment: Maximum adjustment from baseline (±20%)

    Returns:
        (statistical_weight, ml_weight) tuple

    Logic:
        1. If statistical model hitting 75%+, increase weight to 0.80
        2. If statistical model < 65%, decrease weight to 0.60
        3. If ML contribution positive, increase ML weight
        4. If ML contribution negative, decrease ML weight
    """
    # Get performance stats
    performance = get_model_performance(days_back, min_predictions)

    if not performance:
        logger.info("Not enough data for adaptive weights, using baseline (70/30)")
        return (baseline_stat_weight, baseline_ml_weight)

    stat_accuracy = calculate_statistical_accuracy(days_back)
    ml_contribution = calculate_ml_contribution(days_back)

    logger.info(f"Performance analysis ({days_back} days):")
    logger.info(f"  Ensemble accuracy: {performance['ensemble_accuracy']:.1%}")
    logger.info(f"  Statistical accuracy estimate: {stat_accuracy:.1%}" if stat_accuracy else "  Statistical accuracy: Not enough data")
    logger.info(f"  ML contribution: {ml_contribution:+.1%}")

    # Start with baseline
    stat_weight = baseline_stat_weight
    ml_weight = baseline_ml_weight

    # Adjust based on statistical accuracy
    if stat_accuracy:
        if stat_accuracy >= 0.75:
            # Statistical model is performing great, increase weight
            adjustment = min(0.10, max_adjustment)
            stat_weight = min(0.90, baseline_stat_weight + adjustment)
            logger.info(f"  [BOOST] Statistical model strong ({stat_accuracy:.1%}), increasing weight")
        elif stat_accuracy < 0.65:
            # Statistical model struggling, decrease weight
            adjustment = min(0.10, max_adjustment)
            stat_weight = max(0.50, baseline_stat_weight - adjustment)
            logger.info(f"  [REDUCE] Statistical model weak ({stat_accuracy:.1%}), decreasing weight")

    # Adjust based on ML contribution
    if abs(ml_contribution) > 0.05:  # Significant contribution (>5%)
        if ml_contribution > 0:
            # ML is helping, increase ML weight
            adjustment = min(ml_contribution, max_adjustment)
            ml_weight = min(0.50, baseline_ml_weight + adjustment)
            logger.info(f"  [BOOST] ML model helping (+{ml_contribution:.1%}), increasing weight")
        else:
            # ML is hurting, decrease ML weight
            adjustment = min(abs(ml_contribution), max_adjustment)
            ml_weight = max(0.10, baseline_ml_weight - adjustment)
            logger.info(f"  [REDUCE] ML model hurting ({ml_contribution:.1%}), decreasing weight")

    # Ensure weights sum to 1.0
    total = stat_weight + ml_weight
    stat_weight = stat_weight / total
    ml_weight = ml_weight / total

    logger.info(f"  [FINAL] Weights: {stat_weight:.0%} statistical, {ml_weight:.0%} ML")

    return (stat_weight, ml_weight)


def save_weights_to_config(stat_weight: float, ml_weight: float):
    """Save weights to database for tracking"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_weights_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            stat_weight REAL NOT NULL,
            ml_weight REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Insert weights
    cursor.execute("""
        INSERT INTO model_weights_history
        (date, stat_weight, ml_weight, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime('%Y-%m-%d'),
        stat_weight,
        ml_weight,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


# Example usage and testing
if __name__ == "__main__":
    print("Testing Adaptive Model Weights...")
    print()

    # Get performance stats
    print("[TEST 1] Get model performance (last 7 days)")
    performance = get_model_performance(days_back=7)

    if performance:
        print(f"  Total predictions: {performance['total_predictions']}")
        print(f"  Ensemble accuracy: {performance['ensemble_accuracy']:.1%}")
        print(f"  Avg base probability: {performance['avg_base_probability']:.1%}")
        print(f"  Avg ML boost: {performance['avg_ml_boost']:+.1%}")
    else:
        print("  Not enough data yet")

    print()

    # Get adaptive weights
    print("[TEST 2] Calculate adaptive weights")
    stat_weight, ml_weight = get_adaptive_weights(days_back=7)

    print(f"  Statistical weight: {stat_weight:.0%}")
    print(f"  ML weight: {ml_weight:.0%}")
    print(f"  Sum: {stat_weight + ml_weight:.0%}")

    # Save to database
    save_weights_to_config(stat_weight, ml_weight)
    print("  Saved to database")

    print()
    print("="*60)
    print("Adaptive weights system ready!")
    print("="*60)
    print()
    print("Usage in ensemble_predictions.py:")
    print("  from adaptive_weights import get_adaptive_weights")
    print("  stat_weight, ml_weight = get_adaptive_weights()")
    print("  engine = EnsemblePredictionEngine(stat_weight, ml_weight)")
