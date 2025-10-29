"""
PrizePicks Payout Calculator
Handles standard, goblin, demon modes and mixed parlays
"""

from typing import List, Dict


class PrizePicksPayoutCalculator:
    """
    Calculate accurate payouts for PrizePicks parlays.

    Based on observed PrizePicks payout structures:
    - Standard picks have full payouts
    - Goblin picks have reduced payouts (easier lines)
    - Demon picks have boosted payouts (harder lines)
    - Mixed parlays have blended payouts
    """

    # Standard Power Play payouts (all standard picks)
    STANDARD_PAYOUTS = {
        2: 3.0,
        3: 5.0,
        4: 10.0,
        5: 20.0,
        6: 25.0
    }

    # Goblin mode multipliers (vs standard)
    # Easier lines = lower payouts
    GOBLIN_FACTORS = {
        2: 0.67,  # 2-pick goblin ~= 2.0x (vs 3.0x standard)
        3: 0.60,  # 3-pick goblin ~= 3.0x (vs 5.0x standard)
        4: 0.50,  # 4-pick goblin ~= 5.0x (vs 10.0x standard)
        5: 0.50,  # 5-pick goblin ~= 10.0x (vs 20.0x standard)
        6: 0.48   # 6-pick goblin ~= 12.0x (vs 25.0x standard)
    }

    # Demon mode multipliers (vs standard)
    # Harder lines = higher payouts
    DEMON_FACTORS = {
        2: 1.33,  # 2-pick demon ~= 4.0x (vs 3.0x standard)
        3: 1.40,  # 3-pick demon ~= 7.0x (vs 5.0x standard)
        4: 1.50,  # 4-pick demon ~= 15.0x (vs 10.0x standard)
        5: 1.50,  # 5-pick demon ~= 30.0x (vs 20.0x standard)
        6: 1.60   # 6-pick demon ~= 40.0x (vs 25.0x standard)
    }

    @classmethod
    def calculate_parlay_payout(cls, odds_types: List[str]) -> float:
        """
        Calculate payout for a parlay given odds_types of each leg.

        Args:
            odds_types: List of odds_type for each pick ('standard', 'goblin', 'demon')

        Returns:
            Payout multiplier (e.g., 3.0 for 2-pick standard)

        Examples:
            ['standard', 'standard'] -> 3.0x
            ['goblin', 'goblin'] -> 2.0x
            ['standard', 'goblin'] -> ~2.5x (blended)
            ['demon', 'demon'] -> 4.0x
        """
        num_picks = len(odds_types)

        if num_picks < 2 or num_picks > 6:
            raise ValueError(f"Invalid number of picks: {num_picks} (must be 2-6)")

        # Get base payout (standard)
        base_payout = cls.STANDARD_PAYOUTS.get(num_picks, 3.0)

        # Count each odds_type
        standard_count = odds_types.count('standard')
        goblin_count = odds_types.count('goblin')
        demon_count = odds_types.count('demon')

        # All standard picks
        if standard_count == num_picks:
            return base_payout

        # All goblin picks
        if goblin_count == num_picks:
            goblin_factor = cls.GOBLIN_FACTORS.get(num_picks, 0.67)
            return base_payout * goblin_factor

        # All demon picks
        if demon_count == num_picks:
            demon_factor = cls.DEMON_FACTORS.get(num_picks, 1.33)
            return base_payout * demon_factor

        # Mixed parlay - calculate weighted average
        # This is an approximation based on observed PrizePicks behavior
        total_weight = 0

        # Standard picks contribute full weight
        total_weight += standard_count * 1.0

        # Goblin picks contribute reduced weight
        goblin_weight = cls.GOBLIN_FACTORS.get(num_picks, 0.67)
        total_weight += goblin_count * goblin_weight

        # Demon picks contribute increased weight
        demon_weight = cls.DEMON_FACTORS.get(num_picks, 1.33)
        total_weight += demon_count * demon_weight

        # Weighted average multiplier
        avg_weight = total_weight / num_picks

        # Apply to base payout
        adjusted_payout = base_payout * avg_weight

        return round(adjusted_payout, 2)

    @classmethod
    def get_payout_for_odds_type(cls, num_picks: int, odds_type: str) -> float:
        """
        Get payout for a uniform parlay (all same odds_type).

        Args:
            num_picks: Number of picks in parlay
            odds_type: 'standard', 'goblin', or 'demon'

        Returns:
            Payout multiplier
        """
        return cls.calculate_parlay_payout([odds_type] * num_picks)

    @classmethod
    def print_payout_table(cls):
        """Print comprehensive payout table for reference"""
        print("\n" + "="*80)
        print("PRIZEPICKS PAYOUT STRUCTURE")
        print("="*80)
        print()

        for num_picks in range(2, 7):
            print(f"{num_picks}-PICK PARLAYS:")
            print(f"  Standard: {cls.get_payout_for_odds_type(num_picks, 'standard'):.2f}x")
            print(f"  Goblin:   {cls.get_payout_for_odds_type(num_picks, 'goblin'):.2f}x")
            print(f"  Demon:    {cls.get_payout_for_odds_type(num_picks, 'demon'):.2f}x")
            print()

        print("MIXED PARLAY EXAMPLES:")
        print(f"  2-pick [standard, goblin]: {cls.calculate_parlay_payout(['standard', 'goblin']):.2f}x")
        print(f"  2-pick [standard, demon]:  {cls.calculate_parlay_payout(['standard', 'demon']):.2f}x")
        print(f"  3-pick [standard×2, goblin]: {cls.calculate_parlay_payout(['standard', 'standard', 'goblin']):.2f}x")
        print(f"  3-pick [demon×2, standard]: {cls.calculate_parlay_payout(['demon', 'demon', 'standard']):.2f}x")
        print()

        print("Note: Mixed parlay payouts are calculated using weighted averages")
        print("      Actual PrizePicks payouts may vary slightly")
        print("="*80)


def test_payout_calculator():
    """Test the payout calculator"""
    calc = PrizePicksPayoutCalculator()

    print("\n" + "="*80)
    print("PAYOUT CALCULATOR TEST")
    print("="*80)
    print()

    test_cases = [
        (['standard', 'standard'], "2-pick standard"),
        (['goblin', 'goblin'], "2-pick goblin"),
        (['demon', 'demon'], "2-pick demon"),
        (['standard', 'goblin'], "2-pick mixed (1 standard, 1 goblin)"),
        (['standard', 'standard', 'standard'], "3-pick standard"),
        (['goblin', 'goblin', 'goblin'], "3-pick goblin"),
        (['demon', 'demon', 'demon'], "3-pick demon"),
        (['standard', 'standard', 'goblin'], "3-pick mixed (2 standard, 1 goblin)"),
        (['standard', 'standard', 'standard', 'standard'], "4-pick standard"),
    ]

    for odds_types, description in test_cases:
        payout = calc.calculate_parlay_payout(odds_types)
        print(f"{description:45} -> {payout:.2f}x")

    print()

    # Print full table
    calc.print_payout_table()


if __name__ == "__main__":
    test_payout_calculator()
