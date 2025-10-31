"""
Correlation Detection for Parlays

Detects correlated prop types and player relationships to avoid
in parlay construction. Correlated bets reduce true combined probability.

Usage:
    from correlation_detector import CorrelationDetector

    detector = CorrelationDetector()
    is_correlated = detector.are_correlated(leg1, leg2)
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from system_logger import get_logger

logger = get_logger(__name__)

DB_PATH = "database/nhl_predictions.db"


class CorrelationDetector:
    """
    Detects correlated props and players for parlay construction

    Correlation Types:
    1. Same player (always correlated)
    2. Same game (game script correlation)
    3. Same team (team performance correlation)
    4. Prop type correlation (shots → points, etc.)
    5. Linemate correlation (shared ice time)
    6. Opposing goalies (inverse correlation)
    """

    # Known prop correlations (from hockey knowledge)
    PROP_CORRELATIONS = {
        ('points', 'goals'): 0.75,      # Points include goals
        ('points', 'assists'): 0.70,    # Points include assists
        ('points', 'shots'): 0.60,      # More shots → more points
        ('shots', 'goals'): 0.55,       # More shots → more goals
        ('assists', 'points'): 0.70,    # Assists are points
        ('goals', 'points'): 0.75,      # Goals are points
    }

    def __init__(self, db_path: str = DB_PATH):
        """Initialize correlation detector"""
        self.db_path = db_path
        self.linemate_cache = {}  # Cache linemate relationships

    def are_same_player(self, player1: str, player2: str) -> bool:
        """Check if two legs are the same player"""
        return player1.lower() == player2.lower()

    def are_same_game(self, team1: str, opp1: str, team2: str, opp2: str) -> bool:
        """Check if two legs are from the same game"""
        # Same game if:
        # 1. Same team playing same opponent
        # 2. Team1 vs Opp1 is the reverse of Team2 vs Opp2
        if team1 == team2 and opp1 == opp2:
            return True
        if team1 == opp2 and opp1 == team2:
            return True
        return False

    def are_same_team(self, team1: str, team2: str) -> bool:
        """Check if two legs are from the same team"""
        return team1.lower() == team2.lower()

    def are_props_correlated(self, prop1: str, prop2: str, threshold: float = 0.50) -> bool:
        """
        Check if two prop types are correlated

        Args:
            prop1: First prop type (e.g., 'points')
            prop2: Second prop type (e.g., 'shots')
            threshold: Correlation threshold (0.50 = moderate)

        Returns:
            True if correlation > threshold
        """
        # Normalize prop names
        prop1 = prop1.lower().strip()
        prop2 = prop2.lower().strip()

        # Same prop type is always correlated
        if prop1 == prop2:
            return True

        # Check known correlations
        correlation = self.PROP_CORRELATIONS.get((prop1, prop2))
        if correlation is None:
            # Try reverse order
            correlation = self.PROP_CORRELATIONS.get((prop2, prop1))

        if correlation and correlation >= threshold:
            return True

        return False

    def are_linemates(self, player1: str, team1: str, player2: str, team2: str) -> bool:
        """
        Check if two players are linemates (play together)

        For now, returns False (would need line combination data)
        Future: Integrate with NHL API line combinations
        """
        # Same team is required for linemates
        if team1 != team2:
            return False

        # TODO: Fetch line combinations from NHL API
        # For now, conservatively return False
        # In production, would check if players share ice time regularly

        return False

    def get_correlation_score(
        self,
        player1: str, team1: str, opp1: str, prop1: str,
        player2: str, team2: str, opp2: str, prop2: str
    ) -> float:
        """
        Calculate correlation score between two parlay legs

        Returns:
            0.0 = No correlation (independent)
            1.0 = Perfect correlation (avoid!)
        """
        # Same player = perfect correlation
        if self.are_same_player(player1, player2):
            return 1.0

        score = 0.0

        # Same game correlation (moderate)
        if self.are_same_game(team1, opp1, team2, opp2):
            score += 0.30
            logger.debug(f"Same game correlation: {player1} vs {player2}")

        # Same team correlation (low)
        if self.are_same_team(team1, team2):
            score += 0.20
            logger.debug(f"Same team correlation: {player1} vs {player2}")

        # Prop type correlation
        if self.are_props_correlated(prop1, prop2):
            # Only matters if same player (already handled) or linemates
            if self.are_linemates(player1, team1, player2, team2):
                score += 0.40
                logger.debug(f"Linemate + prop correlation: {player1} vs {player2}")

        return min(score, 1.0)  # Cap at 1.0

    def are_correlated(
        self,
        leg1: Dict,
        leg2: Dict,
        threshold: float = 0.30
    ) -> bool:
        """
        Check if two parlay legs are correlated

        Args:
            leg1: Dictionary with player_name, team, opponent, prop_type
            leg2: Dictionary with player_name, team, opponent, prop_type
            threshold: Correlation threshold (0.30 = low/moderate)

        Returns:
            True if correlation score > threshold
        """
        score = self.get_correlation_score(
            leg1['player_name'], leg1['team'], leg1['opponent'], leg1['prop_type'],
            leg2['player_name'], leg2['team'], leg2['opponent'], leg2['prop_type']
        )

        if score > threshold:
            logger.debug(f"Correlation detected ({score:.2f}): {leg1['player_name']} + {leg2['player_name']}")
            return True

        return False

    def filter_uncorrelated_combinations(
        self,
        legs: List[Dict],
        max_correlation: float = 0.30
    ) -> List[List[Dict]]:
        """
        Generate parlay combinations with correlation filtering

        Args:
            legs: List of potential parlay legs
            max_correlation: Maximum allowed correlation

        Returns:
            List of valid parlay combinations (uncorrelated)
        """
        valid_combinations = []

        # Generate 2-leg parlays
        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                if not self.are_correlated(legs[i], legs[j], max_correlation):
                    valid_combinations.append([legs[i], legs[j]])

        # Generate 3-leg parlays
        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                for k in range(j + 1, len(legs)):
                    # Check all pairs
                    if (not self.are_correlated(legs[i], legs[j], max_correlation) and
                        not self.are_correlated(legs[i], legs[k], max_correlation) and
                        not self.are_correlated(legs[j], legs[k], max_correlation)):
                        valid_combinations.append([legs[i], legs[j], legs[k]])

        return valid_combinations


def calculate_prop_correlations_from_data() -> Dict[Tuple[str, str], float]:
    """
    Calculate prop correlations from historical data

    This would analyze actual game results to find empirical correlations.
    For now, returns known hockey correlations.

    Future: Query player_stats to calculate actual correlations
    """
    # TODO: Implement empirical correlation calculation
    # For now, return known hockey correlations
    return CorrelationDetector.PROP_CORRELATIONS


# Example usage and testing
if __name__ == "__main__":
    print("Testing Correlation Detection...")
    print()

    detector = CorrelationDetector()

    # Test 1: Same player
    print("[TEST 1] Same player (should be correlated)")
    leg1 = {'player_name': 'Dylan Larkin', 'team': 'DET', 'opponent': 'LAK', 'prop_type': 'points'}
    leg2 = {'player_name': 'Dylan Larkin', 'team': 'DET', 'opponent': 'LAK', 'prop_type': 'shots'}
    corr_score = detector.get_correlation_score(
        leg1['player_name'], leg1['team'], leg1['opponent'], leg1['prop_type'],
        leg2['player_name'], leg2['team'], leg2['opponent'], leg2['prop_type']
    )
    print(f"  Correlation score: {corr_score:.2f} (1.0 = perfect)")
    print(f"  Correlated: {detector.are_correlated(leg1, leg2)}")

    print()

    # Test 2: Same game
    print("[TEST 2] Same game, different players")
    leg1 = {'player_name': 'Dylan Larkin', 'team': 'DET', 'opponent': 'LAK', 'prop_type': 'points'}
    leg2 = {'player_name': 'Adrian Kempe', 'team': 'LAK', 'opponent': 'DET', 'prop_type': 'points'}
    corr_score = detector.get_correlation_score(
        leg1['player_name'], leg1['team'], leg1['opponent'], leg1['prop_type'],
        leg2['player_name'], leg2['team'], leg2['opponent'], leg2['prop_type']
    )
    print(f"  Correlation score: {corr_score:.2f}")
    print(f"  Correlated (threshold 0.30): {detector.are_correlated(leg1, leg2, threshold=0.30)}")

    print()

    # Test 3: Different games, no correlation
    print("[TEST 3] Different games (should NOT be correlated)")
    leg1 = {'player_name': 'Dylan Larkin', 'team': 'DET', 'opponent': 'LAK', 'prop_type': 'points'}
    leg2 = {'player_name': 'Jack Hughes', 'team': 'NJ', 'opponent': 'SJ', 'prop_type': 'points'}
    corr_score = detector.get_correlation_score(
        leg1['player_name'], leg1['team'], leg1['opponent'], leg1['prop_type'],
        leg2['player_name'], leg2['team'], leg2['opponent'], leg2['prop_type']
    )
    print(f"  Correlation score: {corr_score:.2f}")
    print(f"  Correlated: {detector.are_correlated(leg1, leg2)}")

    print()

    # Test 4: Filter combinations
    print("[TEST 4] Filter uncorrelated combinations")
    legs = [
        {'player_name': 'Dylan Larkin', 'team': 'DET', 'opponent': 'LAK', 'prop_type': 'points'},
        {'player_name': 'Adrian Kempe', 'team': 'LAK', 'opponent': 'DET', 'prop_type': 'points'},
        {'player_name': 'Jack Hughes', 'team': 'NJ', 'opponent': 'SJ', 'prop_type': 'points'},
        {'player_name': 'William Eklund', 'team': 'SJ', 'opponent': 'NJ', 'prop_type': 'points'},
    ]

    valid_combos = detector.filter_uncorrelated_combinations(legs, max_correlation=0.30)
    print(f"  Total 2-3 leg combinations: {len(valid_combos)}")
    print(f"  Sample valid parlay:")
    if valid_combos:
        sample = valid_combos[0]
        for leg in sample:
            print(f"    - {leg['player_name']} ({leg['team']}) {leg['prop_type'].upper()}")

    print()
    print("="*60)
    print("Correlation detection ready!")
    print("="*60)
    print()
    print("Usage in gto_parlay_optimizer.py:")
    print("  from correlation_detector import CorrelationDetector")
    print("  detector = CorrelationDetector()")
    print("  if not detector.are_correlated(leg1, leg2):")
    print("      # Include in parlay")
