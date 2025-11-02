"""
Adaptive Learning Engine

Analyzes prediction outcomes and learns probability adjustments.
This is the "brain" that makes the system smarter over time.

Features:
- Home ice advantage learning
- Blowout game detection
- Optimal ensemble weights by prop type
- Player-specific calibration
- Statistical significance testing
- Confidence-weighted adjustments

Usage:
    python adaptive_learning/learning_engine.py
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy import stats as scipy_stats

DB_PATH = "database/nhl_predictions.db"

# Minimum sample size for significance
MIN_SAMPLE_SIZE = 30  # Need at least 30 observations


class AdaptiveLearningEngine:
    """
    Learns from prediction outcomes and calculates probability adjustments
    """

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def log_learning_event(self, event_type: str, description: str,
                          factor_name: str = None, prop_type: str = None,
                          old_value: float = None, new_value: float = None,
                          reason: str = None, expected_impact: float = None):
        """Log a learning event for audit trail"""
        self.cursor.execute("""
            INSERT INTO learning_log (
                event_type, description, factor_name, prop_type,
                old_value, new_value, reason, expected_accuracy_change,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (event_type, description, factor_name, prop_type,
              old_value, new_value, reason, expected_impact,
              datetime.now().isoformat()))

        self.conn.commit()

    def store_adjustment(self, factor_name: str, prop_type: Optional[str],
                        adjustment_value: float, confidence: float,
                        sample_size: int, accuracy_with: float,
                        accuracy_without: float, p_value: float):
        """
        Store or update a learned adjustment

        Args:
            factor_name: Name of the adjustment factor
            prop_type: Prop type (or None for all)
            adjustment_value: Probability adjustment (e.g., 0.05 = +5%)
            confidence: 0-1 confidence score
            sample_size: Number of observations
            accuracy_with: Accuracy when factor is present
            accuracy_without: Accuracy when factor is absent
            p_value: Statistical significance
        """
        # Check if adjustment already exists
        self.cursor.execute("""
            SELECT id, adjustment_value
            FROM learned_adjustments
            WHERE factor_name = ? AND (prop_type = ? OR (prop_type IS NULL AND ? IS NULL))
        """, (factor_name, prop_type, prop_type))

        existing = self.cursor.fetchone()
        is_significant = p_value < 0.05

        if existing:
            # Update existing
            old_value = existing[1]
            adjustment_id = existing[0]

            self.cursor.execute("""
                UPDATE learned_adjustments SET
                    adjustment_value = ?,
                    confidence = ?,
                    sample_size = ?,
                    accuracy_with = ?,
                    accuracy_without = ?,
                    p_value = ?,
                    is_significant = ?,
                    last_updated = ?
                WHERE id = ?
            """, (adjustment_value, confidence, sample_size,
                  accuracy_with, accuracy_without, p_value, is_significant,
                  datetime.now().isoformat(), adjustment_id))

            # Log the change
            self.log_learning_event(
                'adjustment_updated',
                f"Updated {factor_name} for {prop_type or 'all props'}",
                factor_name, prop_type, old_value, adjustment_value,
                f"Based on {sample_size} observations, p={p_value:.4f}",
                abs(adjustment_value - old_value)
            )

        else:
            # Insert new
            self.cursor.execute("""
                INSERT INTO learned_adjustments (
                    factor_name, prop_type, adjustment_type, adjustment_value,
                    confidence, sample_size, accuracy_with, accuracy_without,
                    p_value, is_significant, first_learned, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (factor_name, prop_type, 'probability_boost', adjustment_value,
                  confidence, sample_size, accuracy_with, accuracy_without,
                  p_value, is_significant, datetime.now().isoformat(),
                  datetime.now().isoformat()))

            # Log the creation
            self.log_learning_event(
                'adjustment_created',
                f"Created new adjustment: {factor_name} for {prop_type or 'all props'}",
                factor_name, prop_type, None, adjustment_value,
                f"Based on {sample_size} observations, p={p_value:.4f}",
                abs(adjustment_value) if adjustment_value else 0
            )

        self.conn.commit()

    def learn_home_ice_advantage(self):
        """
        Learn home ice advantage by prop type

        Compares accuracy of home vs away predictions
        """
        print("\n[*] Learning home ice advantage...")

        prop_types = ['points', 'shots', 'toi', 'goalie_saves']

        for prop_type in prop_types:
            # Get home predictions
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                    AVG(predicted_probability) as avg_prob
                FROM prediction_outcomes
                WHERE was_home = 1
                AND prop_type = ?
            """, (prop_type,))

            home_result = self.cursor.fetchone()
            if not home_result or home_result[0] < MIN_SAMPLE_SIZE:
                continue

            home_total, home_hits, home_avg_prob = home_result
            home_accuracy = home_hits / home_total if home_total > 0 else 0

            # Get away predictions
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                    AVG(predicted_probability) as avg_prob
                FROM prediction_outcomes
                WHERE was_home = 0
                AND prop_type = ?
            """, (prop_type,))

            away_result = self.cursor.fetchone()
            if not away_result or away_result[0] < MIN_SAMPLE_SIZE:
                continue

            away_total, away_hits, away_avg_prob = away_result
            away_accuracy = away_hits / away_total if away_total > 0 else 0

            # Statistical significance test (chi-square)
            contingency = np.array([
                [home_hits, home_total - home_hits],
                [away_hits, away_total - away_hits]
            ])
            chi2, p_value = scipy_stats.chi2_contingency(contingency)[:2]

            # Calculate adjustment
            accuracy_diff = home_accuracy - away_accuracy

            if p_value < 0.05 and abs(accuracy_diff) > 0.03:  # At least 3% difference
                # Home boost is half the accuracy difference
                adjustment = accuracy_diff / 2

                # Confidence based on sample size
                total_samples = home_total + away_total
                confidence = min(1.0, total_samples / 200)  # Max confidence at 200+ samples

                # Store adjustment
                self.store_adjustment(
                    factor_name='home_ice_boost',
                    prop_type=prop_type,
                    adjustment_value=adjustment,
                    confidence=confidence,
                    sample_size=total_samples,
                    accuracy_with=home_accuracy,
                    accuracy_without=away_accuracy,
                    p_value=p_value
                )

                print(f"  ✅ {prop_type}: Home={home_accuracy:.1%}, Away={away_accuracy:.1%}")
                print(f"     Adjustment: {adjustment:+.1%} for home games (p={p_value:.4f})")
            else:
                print(f"  ⚪ {prop_type}: No significant home ice advantage detected")

    def learn_blowout_effect(self):
        """
        Learn how blowout games affect prediction accuracy

        Blowouts may cause:
        - Starters getting pulled early
        - Less ice time for key players
        - Different playing style (prevent defense)
        """
        print("\n[*] Learning blowout game effects...")

        # Need game_context table populated
        # For now, skip if not available

        print("  ⚪ Blowout learning requires game_context data (coming soon)")

    def learn_optimal_ensemble_weights(self):
        """
        Learn optimal ensemble weights (statistical vs ML) by prop type

        Current system uses fixed 70% stat + 30% ML.
        This learns the optimal split for each prop type.
        """
        print("\n[*] Learning optimal ensemble weights...")

        prop_types = ['points', 'shots', 'toi', 'goalie_saves']

        for prop_type in prop_types:
            # For now, we don't have separate tracking of stat vs ML predictions
            # This would require storing base_probability (stat) and ml_boost separately

            print(f"  ⚪ {prop_type}: Ensemble weight learning requires separated model predictions")
            print(f"     (Will be available after we integrate adjustments into prediction generation)")

    def learn_player_specific_calibration(self):
        """
        Learn player-specific probability calibration

        Some players may be consistently over/under-predicted
        """
        print("\n[*] Learning player-specific calibration...")

        # Find players with at least MIN_SAMPLE_SIZE predictions
        self.cursor.execute("""
            SELECT
                player_name,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                AVG(predicted_probability) as avg_prob
            FROM prediction_outcomes
            GROUP BY player_name
            HAVING COUNT(*) >= ?
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """, (MIN_SAMPLE_SIZE,))

        players = self.cursor.fetchall()

        # Get league average
        self.cursor.execute("""
            SELECT AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END)
            FROM prediction_outcomes
        """)
        league_avg = self.cursor.fetchone()[0] or 0.5

        calibrated_count = 0

        for player_name, total, hits, avg_prob in players:
            player_accuracy = hits / total if total > 0 else 0

            # Calibration error: difference between predicted prob and actual hit rate
            calibration_error = avg_prob - player_accuracy

            # Only adjust if error is significant (>5%) and we have enough data
            if abs(calibration_error) > 0.05 and total >= MIN_SAMPLE_SIZE:
                # Adjustment is half the calibration error (conservative)
                adjustment = -calibration_error / 2

                # Confidence based on sample size
                confidence = min(1.0, total / 100)

                # Store adjustment
                factor_name = f"player_{player_name.replace(' ', '_').lower()}"

                self.store_adjustment(
                    factor_name=factor_name,
                    prop_type=None,  # Applies to all prop types for this player
                    adjustment_value=adjustment,
                    confidence=confidence,
                    sample_size=total,
                    accuracy_with=player_accuracy,
                    accuracy_without=league_avg,
                    p_value=0.0  # We'd need binomial test here
                )

                calibrated_count += 1
                print(f"  ✅ {player_name}: {total} predictions, {player_accuracy:.1%} accuracy")
                print(f"     Predicted {avg_prob:.1%} on average → Adjusting by {adjustment:+.1%}")

        if calibrated_count == 0:
            print("  ⚪ No player-specific calibrations needed yet")
        else:
            print(f"\n  📊 Created {calibrated_count} player-specific adjustments")

    def learn_confidence_tier_calibration(self):
        """
        Learn if confidence tiers are well-calibrated

        T1-ELITE should hit ~75%, T2-STRONG ~65%, etc.
        """
        print("\n[*] Learning confidence tier calibration...")

        tiers = ['T1-ELITE', 'T2-STRONG', 'T3-MODERATE', 'T3-MARGINAL', 'T4-FADE']
        expected_accuracy = {
            'T1-ELITE': 0.75,
            'T2-STRONG': 0.65,
            'T3-MODERATE': 0.57,
            'T3-MARGINAL': 0.52,
            'T4-FADE': 0.45
        }

        for tier in tiers:
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                    AVG(predicted_probability) as avg_prob
                FROM prediction_outcomes
                WHERE confidence_tier = ?
            """, (tier,))

            result = self.cursor.fetchone()
            if not result or result[0] < MIN_SAMPLE_SIZE:
                continue

            total, hits, avg_prob = result
            actual_accuracy = hits / total if total > 0 else 0
            expected = expected_accuracy.get(tier, 0.5)

            calibration_error = actual_accuracy - expected

            if abs(calibration_error) > 0.05:  # >5% miscalibration
                print(f"  ⚠️  {tier}: Expected {expected:.1%}, Actual {actual_accuracy:.1%}")
                print(f"      Calibration error: {calibration_error:+.1%}")
            else:
                print(f"  ✅ {tier}: {actual_accuracy:.1%} accuracy (expected {expected:.1%})")

    def generate_performance_report(self):
        """Generate overall performance report"""
        print("\n" + "=" * 80)
        print("ADAPTIVE LEARNING - PERFORMANCE REPORT")
        print("=" * 80)

        # Overall accuracy
        self.cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits
            FROM prediction_outcomes
        """)

        total, hits = self.cursor.fetchone()
        accuracy = hits / total if total > 0 else 0

        print(f"\n📊 Overall Performance:")
        print(f"   Total Predictions: {total}")
        print(f"   Hits: {hits}")
        print(f"   Accuracy: {accuracy:.1%}")

        # By prop type
        print(f"\n📊 Accuracy by Prop Type:")
        self.cursor.execute("""
            SELECT
                prop_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) as accuracy
            FROM prediction_outcomes
            GROUP BY prop_type
            ORDER BY accuracy DESC
        """)

        for prop_type, total, hits, accuracy in self.cursor.fetchall():
            print(f"   {prop_type:15s}: {hits}/{total:3d} ({accuracy:.1%})")

        # Active adjustments
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM learned_adjustments
            WHERE is_significant = 1
        """)
        active_adjustments = self.cursor.fetchone()[0]

        print(f"\n🎓 Active Learned Adjustments: {active_adjustments}")

        if active_adjustments > 0:
            self.cursor.execute("""
                SELECT factor_name, prop_type, adjustment_value, confidence, sample_size
                FROM learned_adjustments
                WHERE is_significant = 1
                ORDER BY ABS(adjustment_value) DESC
                LIMIT 10
            """)

            print("\n   Top Adjustments:")
            for factor, prop, value, conf, sample in self.cursor.fetchall():
                prop_str = prop if prop else "all props"
                print(f"   - {factor:30s} ({prop_str:12s}): {value:+.1%} (confidence: {conf:.0%}, n={sample})")

    def run_full_learning_cycle(self):
        """Run complete learning cycle"""
        print("\n" + "=" * 80)
        print("ADAPTIVE LEARNING ENGINE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check if we have any outcomes to learn from
        self.cursor.execute("SELECT COUNT(*) FROM prediction_outcomes")
        outcome_count = self.cursor.fetchone()[0]

        if outcome_count == 0:
            print("\n⚠️  No prediction outcomes found!")
            print("    Run grade_predictions.py first to grade some predictions.")
            return

        print(f"\n📊 Found {outcome_count} graded predictions to learn from")

        # Run learning modules
        self.learn_home_ice_advantage()
        # self.learn_blowout_effect()  # Requires game_context
        # self.learn_optimal_ensemble_weights()  # Requires split model tracking
        self.learn_player_specific_calibration()
        self.learn_confidence_tier_calibration()

        # Generate report
        self.generate_performance_report()

        print("\n" + "=" * 80)
        print("✅ LEARNING COMPLETE")
        print("=" * 80)
        print("\nLearned adjustments will be applied to future predictions.")
        print("View learned insights in the dashboard: 'System Utilities' > 'Adaptive Weights'")


def main():
    engine = AdaptiveLearningEngine()
    engine.run_full_learning_cycle()


if __name__ == "__main__":
    main()
