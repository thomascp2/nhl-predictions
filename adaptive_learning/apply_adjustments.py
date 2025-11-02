"""
Adjustment Application Module

This module loads learned adjustments from the database and applies them
to predictions. Import this in your prediction generation scripts.

Usage:
    from adaptive_learning.apply_adjustments import AdaptiveAdjuster

    adjuster = AdaptiveAdjuster()
    adjusted_prob = adjuster.apply_adjustments(
        base_probability=0.65,
        player_name='Connor McDavid',
        prop_type='points',
        is_home=True,
        context={}
    )
"""

import sqlite3
from typing import Dict, Optional
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"


class AdaptiveAdjuster:
    """
    Applies learned probability adjustments to predictions
    """

    def __init__(self):
        self.adjustments = {}
        self.load_adjustments()

    def load_adjustments(self):
        """
        Load all active learned adjustments from database
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Load significant adjustments
        cursor.execute("""
            SELECT
                factor_name,
                prop_type,
                adjustment_value,
                confidence
            FROM learned_adjustments
            WHERE is_significant = 1
            ORDER BY confidence DESC
        """)

        for factor_name, prop_type, value, confidence in cursor.fetchall():
            key = (factor_name, prop_type)
            self.adjustments[key] = {
                'value': value,
                'confidence': confidence
            }

        conn.close()

        print(f"[AdaptiveAdjuster] Loaded {len(self.adjustments)} learned adjustments")

    def get_adjustment(self, factor_name: str, prop_type: Optional[str] = None) -> float:
        """
        Get adjustment value for a specific factor

        Args:
            factor_name: Name of the factor (e.g., 'home_ice_boost')
            prop_type: Prop type (or None for global)

        Returns:
            Adjustment value (default 0.0 if not found)
        """
        # Try prop-specific first
        if prop_type:
            key = (factor_name, prop_type)
            if key in self.adjustments:
                adj = self.adjustments[key]
                return adj['value'] * adj['confidence']  # Weight by confidence

        # Try global (prop_type = None)
        key = (factor_name, None)
        if key in self.adjustments:
            adj = self.adjustments[key]
            return adj['value'] * adj['confidence']

        return 0.0

    def apply_adjustments(self,
                         base_probability: float,
                         player_name: str,
                         prop_type: str,
                         is_home: bool = False,
                         context: Dict = None) -> float:
        """
        Apply all learned adjustments to a base probability

        Args:
            base_probability: Initial probability (0.0 to 1.0)
            player_name: Player name
            prop_type: Prop type (points, shots, toi, goalie_saves)
            is_home: Is player at home?
            context: Additional context dict (for future features)

        Returns:
            Adjusted probability (clamped to 0.05-0.95)
        """
        if context is None:
            context = {}

        adjusted_prob = base_probability

        # 1. Home ice advantage
        if is_home:
            home_boost = self.get_adjustment('home_ice_boost', prop_type)
            if home_boost != 0:
                adjusted_prob += home_boost

        # 2. Player-specific calibration
        player_factor = f"player_{player_name.replace(' ', '_').lower()}"
        player_adj = self.get_adjustment(player_factor, prop_type)
        if player_adj != 0:
            adjusted_prob += player_adj

        # 3. Blowout penalty (if available in context)
        if context.get('expected_margin', 0) >= 3:
            blowout_penalty = self.get_adjustment('blowout_penalty', prop_type)
            if blowout_penalty != 0:
                adjusted_prob += blowout_penalty  # Typically negative

        # 4. Additional context-based adjustments
        # (Can add more as we learn them)

        # Clamp to valid probability range
        # Never go below 5% or above 95% (extreme certainty is dangerous)
        adjusted_prob = max(0.05, min(0.95, adjusted_prob))

        return adjusted_prob

    def get_adjustment_reasoning(self,
                                player_name: str,
                                prop_type: str,
                                is_home: bool = False,
                                context: Dict = None) -> str:
        """
        Generate human-readable explanation of adjustments applied

        Args:
            player_name: Player name
            prop_type: Prop type
            is_home: Is player at home?
            context: Additional context

        Returns:
            Reasoning string
        """
        if context is None:
            context = {}

        reasons = []

        # Home ice
        if is_home:
            home_boost = self.get_adjustment('home_ice_boost', prop_type)
            if abs(home_boost) >= 0.01:  # At least 1%
                reasons.append(f"home ice {home_boost:+.1%}")

        # Player-specific
        player_factor = f"player_{player_name.replace(' ', '_').lower()}"
        player_adj = self.get_adjustment(player_factor, prop_type)
        if abs(player_adj) >= 0.01:
            reasons.append(f"player calibration {player_adj:+.1%}")

        # Blowout
        if context.get('expected_margin', 0) >= 3:
            blowout_penalty = self.get_adjustment('blowout_penalty', prop_type)
            if abs(blowout_penalty) >= 0.01:
                reasons.append(f"blowout penalty {blowout_penalty:+.1%}")

        if reasons:
            return " | Adaptive: " + ", ".join(reasons)
        else:
            return ""

    def get_all_adjustments_summary(self) -> Dict:
        """
        Get summary of all active adjustments

        Returns:
            Dictionary with adjustment info
        """
        summary = {
            'total_adjustments': len(self.adjustments),
            'by_type': {},
            'top_adjustments': []
        }

        # Group by factor type
        factor_types = {}
        for (factor_name, prop_type), adj in self.adjustments.items():
            factor_base = factor_name.split('_')[0]  # 'home', 'player', 'blowout', etc.
            if factor_base not in factor_types:
                factor_types[factor_base] = 0
            factor_types[factor_base] += 1

        summary['by_type'] = factor_types

        # Top adjustments by absolute value
        sorted_adj = sorted(
            self.adjustments.items(),
            key=lambda x: abs(x[1]['value']),
            reverse=True
        )[:10]

        for (factor_name, prop_type), adj in sorted_adj:
            summary['top_adjustments'].append({
                'factor': factor_name,
                'prop_type': prop_type,
                'value': adj['value'],
                'confidence': adj['confidence']
            })

        return summary


# Singleton instance for easy importing
_global_adjuster = None


def get_adjuster() -> AdaptiveAdjuster:
    """
    Get global adjuster instance (singleton pattern)

    Returns:
        AdaptiveAdjuster instance
    """
    global _global_adjuster
    if _global_adjuster is None:
        _global_adjuster = AdaptiveAdjuster()
    return _global_adjuster


# Convenience function for direct use
def apply_adaptive_adjustments(base_probability: float,
                               player_name: str,
                               prop_type: str,
                               is_home: bool = False,
                               context: Dict = None) -> float:
    """
    Convenience function to apply adjustments without instantiating class

    Args:
        base_probability: Initial probability
        player_name: Player name
        prop_type: Prop type
        is_home: Is home game?
        context: Additional context

    Returns:
        Adjusted probability
    """
    adjuster = get_adjuster()
    return adjuster.apply_adjustments(
        base_probability, player_name, prop_type, is_home, context
    )


def get_adaptive_reasoning(player_name: str,
                          prop_type: str,
                          is_home: bool = False,
                          context: Dict = None) -> str:
    """
    Convenience function to get adjustment reasoning

    Args:
        player_name: Player name
        prop_type: Prop type
        is_home: Is home game?
        context: Additional context

    Returns:
        Reasoning string
    """
    adjuster = get_adjuster()
    return adjuster.get_adjustment_reasoning(
        player_name, prop_type, is_home, context
    )


if __name__ == "__main__":
    # Test the adjuster
    print("=" * 80)
    print("ADAPTIVE ADJUSTER TEST")
    print("=" * 80)

    adjuster = AdaptiveAdjuster()

    # Test adjustment
    test_prob = 0.65
    adjusted = adjuster.apply_adjustments(
        base_probability=test_prob,
        player_name='Connor McDavid',
        prop_type='points',
        is_home=True
    )

    print(f"\nTest Adjustment:")
    print(f"  Base probability: {test_prob:.1%}")
    print(f"  Adjusted: {adjusted:.1%}")
    print(f"  Change: {adjusted - test_prob:+.1%}")

    reasoning = adjuster.get_adjustment_reasoning(
        player_name='Connor McDavid',
        prop_type='points',
        is_home=True
    )
    print(f"  Reasoning: {reasoning}")

    # Summary
    summary = adjuster.get_all_adjustments_summary()
    print(f"\n📊 Adjustment Summary:")
    print(f"   Total Adjustments: {summary['total_adjustments']}")
    print(f"   By Type: {summary['by_type']}")

    if summary['top_adjustments']:
        print(f"\n   Top Adjustments:")
        for adj in summary['top_adjustments'][:5]:
            prop_str = adj['prop_type'] if adj['prop_type'] else 'all'
            print(f"     - {adj['factor']:30s} ({prop_str:12s}): {adj['value']:+.1%}")
