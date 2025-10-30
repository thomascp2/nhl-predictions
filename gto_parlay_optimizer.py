"""
GTO-Style Parlay Optimizer for NHL PrizePicks
Builds +EV parlays using frequency allocation similar to poker solvers.
Ensures proper bankroll distribution and avoids correlated picks.
Uses real PrizePicks payouts based on odds_type.
"""

import sqlite3
import pandas as pd
import numpy as np
import json
from itertools import combinations
from typing import List, Tuple, Dict
from collections import defaultdict
from datetime import datetime
from prizepicks_payouts import PrizePicksPayoutCalculator

DB_PATH = "database/nhl_predictions.db"


class GTOParleyOptimizer:
    """
    Optimizes parlay construction for sports betting picks based on EV.
    Uses GTO-style frequency allocation similar to poker solvers.
    """

    def __init__(self, picks_df: pd.DataFrame, min_profitable_ev: float = 0.0):
        """
        Initialize with picks dataframe.

        Expected columns:
        - player_name: str
        - prop_type: str (shots/points)
        - line: float (e.g., 3.5)
        - odds_american: int (American odds, e.g., -110, +150)
        - model_probability: float (0-1)
        - ev_score: float (individual pick EV)
        - game_id: str (to track correlations)
        - team: str
        - opponent: str

        Args:
            min_profitable_ev: Minimum EV threshold for parlay inclusion (default 0.0 = breakeven)
        """
        self.picks_df = picks_df.copy()
        self.min_profitable_ev = min_profitable_ev
        self.parlays_2leg = []
        self.parlays_3leg = []
        self.parlays_4leg = []
        self.filtered_parlays_2leg = []
        self.filtered_parlays_3leg = []
        self.filtered_parlays_4leg = []
        self.selected_parlays = []

        # Calculate target frequencies for each pick (GTO-style)
        self._calculate_pick_frequencies()

    def _calculate_pick_frequencies(self,
                                    max_frequency: int = 20,
                                    min_frequency: int = 3):
        """
        Calculate target frequency for each pick based on EV (GTO-style).

        Similar to how GTO poker solvers assign action frequencies to hands.
        High EV picks appear more frequently in parlays.

        Args:
            max_frequency: Maximum times a pick can appear in parlays
            min_frequency: Minimum times a pick should appear in parlays
        """
        def frequency_for_ev(ev: float) -> int:
            """Map EV to target frequency using non-linear scaling."""
            if ev >= 0.15:  # Premium picks (like AA/KK in poker)
                return max_frequency
            elif ev >= 0.10:  # Strong picks (like AK/QQ)
                return int(max_frequency * 0.8)
            elif ev >= 0.07:  # Good picks (like JJ/AQ)
                return int(max_frequency * 0.6)
            elif ev >= 0.05:  # Decent picks (like suited broadway)
                return int(max_frequency * 0.4)
            elif ev >= 0.03:  # Marginal picks (like small pairs)
                return int(max_frequency * 0.25)
            else:  # Low EV picks (like suited connectors - mixed strategy)
                return min_frequency

        self.picks_df['target_frequency'] = self.picks_df['ev_score'].apply(frequency_for_ev)
        self.picks_df['actual_frequency'] = 0  # Track actual appearances

        print("\n" + "="*80)
        print("PICK FREQUENCY ALLOCATION (GTO-Style)")
        print("="*80)
        freq_summary = self.picks_df[['player_name', 'prop_type', 'ev_score', 'target_frequency']].copy()
        freq_summary['ev_score'] = freq_summary['ev_score'].apply(lambda x: f"{x:.1%}")
        print(freq_summary.to_string(index=False))
        print()

    def american_to_decimal(self, odds: int) -> float:
        """Convert American odds to decimal odds."""
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1

    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds."""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))

    def calculate_parlay_probability(self, pick_indices: List[int]) -> float:
        """Calculate combined probability for a parlay."""
        probs = self.picks_df.iloc[list(pick_indices)]['model_probability'].values
        return np.prod(probs)

    def calculate_parlay_payout(self, pick_indices: List[int]) -> float:
        """
        Calculate total payout multiplier for a parlay using real PrizePicks payouts.
        Accounts for standard, goblin, and demon odds_types.
        """
        picks = self.picks_df.iloc[list(pick_indices)]
        odds_types = picks['odds_type'].tolist()

        # Use PrizePicks payout calculator with actual odds_types
        payout = PrizePicksPayoutCalculator.calculate_parlay_payout(odds_types)

        return payout

    def calculate_parlay_ev(self, pick_indices: List[int]) -> float:
        """Calculate expected value for a parlay."""
        prob = self.calculate_parlay_probability(pick_indices)
        payout = self.calculate_parlay_payout(pick_indices)
        return (prob * payout) - 1

    def calculate_breakeven_payout(self, pick_indices: List[int]) -> float:
        """Calculate the breakeven payout needed for this parlay."""
        prob = self.calculate_parlay_probability(pick_indices)
        return 1 / prob

    def is_parlay_profitable(self, pick_indices: List[int]) -> bool:
        """
        Check if parlay meets minimum profitability threshold.

        Returns True if actual payout >= breakeven payout (adjusted for min_profitable_ev)
        """
        actual_payout = self.calculate_parlay_payout(pick_indices)
        breakeven_payout = self.calculate_breakeven_payout(pick_indices)

        # Adjust breakeven for minimum EV requirement
        required_payout = breakeven_payout * (1 + self.min_profitable_ev)

        return actual_payout >= required_payout

    def calculate_frequency_score(self, pick_indices: List[int]) -> float:
        """
        Calculate how well this parlay helps achieve target frequencies.

        Similar to GTO solver balancing range frequencies.
        Higher score = better for achieving frequency targets.
        """
        score = 0
        for idx in pick_indices:
            current_freq = self.picks_df.iloc[idx]['actual_frequency']
            target_freq = self.picks_df.iloc[idx]['target_frequency']

            # Reward parlays that help under-represented picks
            if current_freq < target_freq:
                # How much we need this pick (0 to 1 scale)
                need_factor = (target_freq - current_freq) / target_freq
                score += need_factor
            else:
                # Penalize over-represented picks
                over_factor = (current_freq - target_freq) / target_freq
                score -= over_factor * 0.5  # Penalty is less severe

        return score / len(pick_indices)  # Normalize by parlay size

    def is_correlated(self, pick_indices: List[int]) -> bool:
        """
        Check if picks are correlated (same game).
        Correlated parlays reduce true EV.
        """
        picks = self.picks_df.iloc[list(pick_indices)]
        games = picks['game_id'].values
        teams = picks['team'].values

        # Same game = correlated
        if len(set(games)) < len(games):
            return True

        # Same team = correlated
        if len(set(teams)) < len(teams):
            return True

        return False

    def generate_candidate_parlays(self,
                                   num_2leg: int = 100,
                                   num_3leg: int = 100,
                                   num_4leg: int = 50,
                                   min_parlay_ev: float = 0.0):
        """
        Generate candidate parlays.

        Args:
            num_2leg: Max number of 2-leg parlays to consider
            num_3leg: Max number of 3-leg parlays to consider
            num_4leg: Max number of 4-leg parlays to consider
            min_parlay_ev: Minimum EV threshold for parlay inclusion
        """
        n_picks = len(self.picks_df)

        if n_picks < 2:
            print("[WARNING] Need at least 2 picks to generate parlays")
            return

        # Generate 2-leg parlays
        print(f"\n[*] Generating 2-leg parlay candidates...")
        profitable_count = 0

        for combo in combinations(range(n_picks), 2):
            if self.is_correlated(combo):
                continue  # Skip correlated picks

            parlay_ev = self.calculate_parlay_ev(combo)
            actual_payout = self.calculate_parlay_payout(combo)
            breakeven_payout = self.calculate_breakeven_payout(combo)
            is_profitable = self.is_parlay_profitable(combo)

            parlay_data = {
                'picks': combo,
                'pick_names': [self.picks_df.iloc[i]['player_name'] for i in combo],
                'pick_types': [self.picks_df.iloc[i]['prop_type'] for i in combo],
                'pick_lines': [self.picks_df.iloc[i]['line'] for i in combo],
                'pick_evs': [self.picks_df.iloc[i]['ev_score'] for i in combo],
                'ev': parlay_ev,
                'probability': self.calculate_parlay_probability(combo),
                'actual_payout': actual_payout,
                'breakeven_payout': breakeven_payout,
                'is_profitable': is_profitable,
                'frequency_score': 0  # Will calculate during optimization
            }

            self.parlays_2leg.append(parlay_data)

            if is_profitable and parlay_ev >= min_parlay_ev:
                self.filtered_parlays_2leg.append(parlay_data)
                profitable_count += 1

        print(f"  Total 2-leg combinations: {len(self.parlays_2leg)}")
        print(f"  Profitable (EV > {min_parlay_ev:.1%}): {profitable_count}")

        # Generate 3-leg parlays (if enough picks)
        if n_picks >= 3:
            print(f"\n[*] Generating 3-leg parlay candidates...")
            profitable_count = 0

            for combo in combinations(range(n_picks), 3):
                if self.is_correlated(combo):
                    continue

                parlay_ev = self.calculate_parlay_ev(combo)
                actual_payout = self.calculate_parlay_payout(combo)
                breakeven_payout = self.calculate_breakeven_payout(combo)
                is_profitable = self.is_parlay_profitable(combo)

                parlay_data = {
                    'picks': combo,
                    'pick_names': [self.picks_df.iloc[i]['player_name'] for i in combo],
                    'pick_types': [self.picks_df.iloc[i]['prop_type'] for i in combo],
                    'pick_lines': [self.picks_df.iloc[i]['line'] for i in combo],
                    'pick_evs': [self.picks_df.iloc[i]['ev_score'] for i in combo],
                    'ev': parlay_ev,
                    'probability': self.calculate_parlay_probability(combo),
                    'actual_payout': actual_payout,
                    'breakeven_payout': breakeven_payout,
                    'is_profitable': is_profitable,
                    'frequency_score': 0
                }

                self.parlays_3leg.append(parlay_data)

                if is_profitable and parlay_ev >= min_parlay_ev:
                    self.filtered_parlays_3leg.append(parlay_data)
                    profitable_count += 1

            print(f"  Total 3-leg combinations: {len(self.parlays_3leg)}")
            print(f"  Profitable (EV > {min_parlay_ev:.1%}): {profitable_count}")

        # Generate 4-leg parlays (if enough picks)
        if n_picks >= 4:
            print(f"\n[*] Generating 4-leg parlay candidates...")
            profitable_count = 0

            for combo in combinations(range(n_picks), 4):
                if self.is_correlated(combo):
                    continue

                parlay_ev = self.calculate_parlay_ev(combo)
                actual_payout = self.calculate_parlay_payout(combo)
                breakeven_payout = self.calculate_breakeven_payout(combo)
                is_profitable = self.is_parlay_profitable(combo)

                parlay_data = {
                    'picks': combo,
                    'pick_names': [self.picks_df.iloc[i]['player_name'] for i in combo],
                    'pick_types': [self.picks_df.iloc[i]['prop_type'] for i in combo],
                    'pick_lines': [self.picks_df.iloc[i]['line'] for i in combo],
                    'pick_evs': [self.picks_df.iloc[i]['ev_score'] for i in combo],
                    'ev': parlay_ev,
                    'probability': self.calculate_parlay_probability(combo),
                    'actual_payout': actual_payout,
                    'breakeven_payout': breakeven_payout,
                    'is_profitable': is_profitable,
                    'frequency_score': 0
                }

                self.parlays_4leg.append(parlay_data)

                if is_profitable and parlay_ev >= min_parlay_ev:
                    self.filtered_parlays_4leg.append(parlay_data)
                    profitable_count += 1

            print(f"  Total 4-leg combinations: {len(self.parlays_4leg)}")
            print(f"  Profitable (EV > {min_parlay_ev:.1%}): {profitable_count}")

    def optimize_parlay_selection(self,
                                  target_2leg: int = 10,
                                  target_3leg: int = 5,
                                  target_4leg: int = 3):
        """
        Select optimal parlays using GTO-style frequency balancing.

        Iteratively selects parlays that:
        1. Have positive EV
        2. Help balance pick frequencies toward targets
        3. Maximize overall portfolio EV

        Args:
            target_2leg: Number of 2-leg parlays to select
            target_3leg: Number of 3-leg parlays to select
            target_4leg: Number of 4-leg parlays to select
        """
        print("\n" + "="*80)
        print("GTO PARLAY OPTIMIZATION")
        print("="*80)
        print()

        selected = []

        # Select 2-leg parlays
        if self.filtered_parlays_2leg:
            print(f"[*] Selecting {target_2leg} optimal 2-leg parlays...")
            selected_2leg = self._select_parlays_greedy(
                self.filtered_parlays_2leg,
                target_2leg
            )
            selected.extend([{**p, 'legs': 2} for p in selected_2leg])
            print(f"  Selected {len(selected_2leg)} parlays")

        # Select 3-leg parlays
        if self.filtered_parlays_3leg:
            print(f"[*] Selecting {target_3leg} optimal 3-leg parlays...")
            selected_3leg = self._select_parlays_greedy(
                self.filtered_parlays_3leg,
                target_3leg
            )
            selected.extend([{**p, 'legs': 3} for p in selected_3leg])
            print(f"  Selected {len(selected_3leg)} parlays")

        # Select 4-leg parlays
        if self.filtered_parlays_4leg:
            print(f"[*] Selecting {target_4leg} optimal 4-leg parlays...")
            selected_4leg = self._select_parlays_greedy(
                self.filtered_parlays_4leg,
                target_4leg
            )
            selected.extend([{**p, 'legs': 4} for p in selected_4leg])
            print(f"  Selected {len(selected_4leg)} parlays")

        self.selected_parlays = selected

        print(f"\n[SUCCESS] Total parlays selected: {len(selected)}")
        print()

    def _select_parlays_greedy(self, candidates: List[Dict], target_count: int) -> List[Dict]:
        """
        Greedy selection algorithm for parlay optimization.

        Prioritizes:
        1. EV (higher is better)
        2. Frequency balancing (helps under-represented picks)
        """
        if not candidates:
            return []

        selected = []
        remaining = candidates.copy()

        for _ in range(min(target_count, len(remaining))):
            # Calculate frequency score for each remaining parlay
            for parlay in remaining:
                parlay['frequency_score'] = self.calculate_frequency_score(parlay['picks'])

            # Sort by composite score (EV + frequency balance)
            # Weight: 70% EV, 30% frequency balance
            remaining.sort(
                key=lambda p: (p['ev'] * 0.7) + (p['frequency_score'] * 0.3),
                reverse=True
            )

            # Select best parlay
            best = remaining.pop(0)
            selected.append(best)

            # Update actual frequencies
            for idx in best['picks']:
                self.picks_df.at[idx, 'actual_frequency'] += 1

        return selected

    def kelly_criterion(self, prob: float, payout: float, bankroll: float,
                       fraction: float = 0.25) -> float:
        """
        Calculate optimal bet size using Kelly Criterion.

        f* = (bp - q) / b
        where:
            b = decimal payout - 1
            p = win probability
            q = 1 - p

        Args:
            fraction: Fraction of Kelly to use (0.25 = quarter Kelly for safety)
        """
        b = payout - 1
        p = prob
        q = 1 - p

        kelly = (b * p - q) / b
        kelly = max(0, kelly)  # Don't bet if negative

        # Apply fractional Kelly
        kelly_fraction = kelly * fraction

        # Calculate bet size
        bet_size = bankroll * kelly_fraction

        return bet_size

    def generate_betting_recommendations(self, bankroll: float = 1000,
                                        kelly_fraction: float = 0.25):
        """
        Generate betting recommendations with Kelly sizing.

        Args:
            bankroll: Total bankroll in dollars
            kelly_fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
        """
        if not self.selected_parlays:
            print("[WARNING] No parlays selected. Run optimize_parlay_selection() first.")
            return

        print("\n" + "="*80)
        print(f"BETTING RECOMMENDATIONS (Bankroll: ${bankroll:.0f})")
        print("="*80)
        print()

        total_risk = 0

        for i, parlay in enumerate(self.selected_parlays, 1):
            # Calculate Kelly bet size
            bet_size = self.kelly_criterion(
                parlay['probability'],
                parlay['actual_payout'],
                bankroll,
                kelly_fraction
            )

            # Calculate expected profit
            expected_profit = bet_size * parlay['ev']

            total_risk += bet_size

            # Display parlay
            print(f"PARLAY #{i} ({parlay['legs']}-leg)")
            print(f"{'-'*80}")

            for j, idx in enumerate(parlay['picks'], 1):
                pick = self.picks_df.iloc[idx]
                odds_label = f"[{pick['odds_type']}]" if pick['odds_type'] != 'standard' else ""
                print(f"  Leg {j}: {pick['player_name']:20} {pick['prop_type'].upper():7} O{pick['line']:.1f} {odds_label}")

            print(f"\n  Probability: {parlay['probability']:.1%}")
            print(f"  Payout:      {parlay['actual_payout']:.1f}x")
            print(f"  EV:          {parlay['ev']:+.1%}")
            print(f"  Kelly Bet:   ${bet_size:.2f} ({bet_size/bankroll:.1%} of bankroll)")
            print(f"  Expected:    ${expected_profit:+.2f}")
            print()

        print(f"{'='*80}")
        print(f"TOTAL RISK: ${total_risk:.2f} ({total_risk/bankroll:.1%} of bankroll)")
        print(f"{'='*80}")
        print()

    def export_to_csv(self, filename: str = "gto_parlays.csv"):
        """Export selected parlays to CSV for easy reference."""
        if not self.selected_parlays:
            print("[WARNING] No parlays to export")
            return

        rows = []
        for i, parlay in enumerate(self.selected_parlays, 1):
            for j, idx in enumerate(parlay['picks'], 1):
                pick = self.picks_df.iloc[idx]
                rows.append({
                    'Parlay_ID': i,
                    'Legs': parlay['legs'],
                    'Leg_Number': j,
                    'Player': pick['player_name'],
                    'Prop_Type': pick['prop_type'].upper(),
                    'Line': pick['line'],
                    'Team': pick['team'],
                    'Opponent': pick['opponent'],
                    'Parlay_Probability': parlay['probability'],
                    'Parlay_Payout': parlay['actual_payout'],
                    'Parlay_EV': parlay['ev']
                })

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"[SUCCESS] Exported {len(self.selected_parlays)} parlays to {filename}")

    def save_to_database(self, date: str = None):
        """Save selected parlays to database for tracking and grading."""
        if not self.selected_parlays:
            print("[WARNING] No parlays to save")
            return

        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        saved_count = 0

        for i, parlay in enumerate(self.selected_parlays, 1):
            # Build picks JSON
            picks_list = []
            for idx in parlay['picks']:
                pick = self.picks_df.iloc[idx]
                picks_list.append({
                    'player_name': pick['player_name'],
                    'prop_type': pick['prop_type'],
                    'line': float(pick['line']),
                    'team': pick['team'],
                    'opponent': pick['opponent'],
                    'odds_type': pick.get('odds_type', 'standard')
                })

            picks_json = json.dumps(picks_list)
            parlay_id = f"P{i:03d}"

            # Calculate parlay tier based on EV
            if parlay['ev'] >= 0.25:
                tier = 'ELITE'
            elif parlay['ev'] >= 0.15:
                tier = 'T1'
            elif parlay['ev'] >= 0.10:
                tier = 'T2'
            else:
                tier = 'T3'

            # Get Kelly bet sizing if available
            kelly_bet = parlay.get('kelly_bet', 0)
            kelly_fraction = parlay.get('kelly_fraction', 0.25)

            # Insert into database
            insert_query = """
                INSERT OR REPLACE INTO gto_parlays
                (date, parlay_id, num_legs, picks_json, combined_probability,
                 payout_multiplier, expected_value, kelly_fraction,
                 recommended_bet_size, parlay_tier, correlation_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(insert_query, (
                date,
                parlay_id,
                parlay['legs'],
                picks_json,
                parlay['probability'],
                parlay['actual_payout'],
                parlay['ev'],
                kelly_fraction,
                kelly_bet,
                tier,
                0.0,  # correlation_score (placeholder for now)
                datetime.now().isoformat()
            ))

            saved_count += 1

        conn.commit()
        conn.close()

        print(f"[SUCCESS] Saved {saved_count} parlays to database")


def load_picks_from_database(date: str = None, min_edge: float = 0.07) -> pd.DataFrame:
    """
    Load picks from prizepicks_edges table.

    Args:
        date: Date string (YYYY-MM-DD). If None, uses today.
        min_edge: Minimum edge threshold (default 7%)

    Returns:
        DataFrame with required columns for GTO optimizer
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            e.player_name,
            e.team,
            e.opponent,
            e.prop_type,
            e.line,
            e.our_probability as model_probability,
            e.expected_value as ev_score,
            e.edge,
            e.odds_type,
            p.game_id
        FROM prizepicks_edges e
        LEFT JOIN predictions p ON (
            e.player_name = p.player_name AND
            e.prop_type = p.prop_type AND
            e.date = p.game_date
        )
        WHERE e.date = ?
        AND e.edge >= ?
        ORDER BY e.edge DESC
    """

    df = pd.read_sql_query(query, conn, params=(date, min_edge))
    conn.close()

    # Fill missing game_ids with dummy values (team_opponent)
    if 'game_id' in df.columns:
        df['game_id'] = df.apply(
            lambda row: row['game_id'] if pd.notna(row['game_id']) else f"{row['team']}_{row['opponent']}",
            axis=1
        )
    else:
        df['game_id'] = df.apply(lambda row: f"{row['team']}_{row['opponent']}", axis=1)

    # Fill missing odds_type with 'standard'
    if 'odds_type' in df.columns:
        df['odds_type'] = df['odds_type'].fillna('standard')
    else:
        df['odds_type'] = 'standard'

    # Add dummy odds (PrizePicks uses fixed payouts, not individual odds)
    df['odds_american'] = -110  # Standard juice

    return df


def main():
    """Run GTO parlay optimizer"""
    import sys

    print("\n" + "="*80)
    print("GTO PARLAY OPTIMIZER - NHL PRIZEPICKS")
    print("="*80)
    print()

    # Parse arguments
    date = sys.argv[1] if len(sys.argv) > 1 else None
    bankroll = float(sys.argv[2]) if len(sys.argv) > 2 else 1000

    # Load picks from database
    print(f"[*] Loading edge plays from database (7%+ edge)...")
    picks_df = load_picks_from_database(date, min_edge=0.07)

    if len(picks_df) == 0:
        print("[WARNING] No edge plays found with 7%+ edge")
        print("   Try running: python prizepicks_integration_v2.py")
        return

    print(f"[SUCCESS] Loaded {len(picks_df)} edge plays")
    print()

    # Initialize optimizer
    optimizer = GTOParleyOptimizer(picks_df, min_profitable_ev=0.0)

    # Generate candidate parlays
    optimizer.generate_candidate_parlays(
        num_2leg=100,
        num_3leg=50,
        num_4leg=25,
        min_parlay_ev=0.10  # Only parlays with 10%+ EV
    )

    # Optimize selection
    optimizer.optimize_parlay_selection(
        target_2leg=8,
        target_3leg=4,
        target_4leg=2
    )

    # Generate betting recommendations
    optimizer.generate_betting_recommendations(
        bankroll=bankroll,
        kelly_fraction=0.25  # Quarter Kelly for safety
    )

    # Export to CSV
    timestamp = datetime.now().strftime('%Y-%m-%d_%I-%M%p')
    filename = f"GTO_PARLAYS_{timestamp}.csv"
    optimizer.export_to_csv(filename)

    # Save to database
    optimizer.save_to_database(date)

    print("\n" + "="*80)
    print("[SUCCESS] OPTIMIZATION COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print(f"   1. Review recommendations above")
    print(f"   2. Check {filename} for detailed parlay breakdown")
    print(f"   3. Place bets on PrizePicks using recommended sizing")
    print()


if __name__ == "__main__":
    main()
