"""
PrizePicks Multiplier Learning System
Automatically discovers ACTUAL individual pick multipliers by testing parlays.

This is CRITICAL because:
- "Demon" doesn't always mean 2.0x individual
- Actual payouts vary: some demons are 2.31x, others 2.02x
- This 6%+ difference in implied probability drastically affects EV calculations
- Accurate multipliers = accurate edge detection = better bets
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import requests
import json


DB_PATH = "database/nhl_predictions.db"


class PrizePicksMultiplierLearner:
    """
    Learns actual individual pick multipliers from PrizePicks.

    Method:
    1. Fetch all available lines
    2. For each line, test with neutral baseline pick
    3. Record actual 2-leg parlay payout
    4. Reverse-engineer individual multiplier
    5. Store with confidence score based on observations
    """

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.baseline_multiplier = None
        self.learned_multipliers = {}

        # Create table for storing learned multipliers
        self._create_multiplier_table()

    def _create_multiplier_table(self):
        """Create table to store learned individual multipliers"""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prizepicks_learned_multipliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                player_name TEXT,
                prop_type TEXT,
                line REAL,
                odds_type TEXT,
                individual_multiplier REAL,
                implied_probability REAL,
                confidence REAL,
                observations INTEGER,
                baseline_used TEXT,
                baseline_multiplier REAL,
                parlay_payout REAL,
                last_updated TEXT,
                UNIQUE(player_name, prop_type, line, odds_type, date)
            )
        """)

        self.conn.commit()

    def find_neutral_baseline(self, prizepicks_df: pd.DataFrame) -> Optional[Dict]:
        """
        Find the most "standard" pick to use as baseline for testing.

        Criteria:
        - odds_type = 'standard'
        - Common prop type (shots/points)
        - Middle-of-the-road line (not too high/low)
        - From a neutral game (no blowout expected)

        Returns: Dict with baseline pick info
        """
        print("\n[*] Finding neutral baseline pick for testing...")

        # Filter to standard odds only
        standards = prizepicks_df[prizepicks_df['odds_type'] == 'standard'].copy()

        if len(standards) == 0:
            print("[ERROR] No standard picks found")
            return None

        # Prefer shots or points props (most common, most "standard")
        common_props = standards[standards['prop_type'].isin(['shots', 'points'])]

        if len(common_props) > 0:
            standards = common_props

        # Find median line for each prop type (most "average")
        baseline_candidates = []

        for prop_type in standards['prop_type'].unique():
            prop_lines = standards[standards['prop_type'] == prop_type]
            median_line = prop_lines['line'].median()

            # Find pick closest to median
            prop_lines['distance_from_median'] = abs(prop_lines['line'] - median_line)
            closest = prop_lines.nsmallest(1, 'distance_from_median').iloc[0]

            baseline_candidates.append({
                'player_name': closest['player_name'],
                'team': closest['team'],
                'prop_type': closest['prop_type'],
                'line': closest['line'],
                'odds_type': closest['odds_type'],
                'median_distance': closest['distance_from_median']
            })

        # Choose the most neutral candidate (smallest distance from median)
        if not baseline_candidates:
            return None

        baseline = min(baseline_candidates, key=lambda x: x['median_distance'])

        print(f"[+] Baseline pick: {baseline['player_name']} {baseline['prop_type'].upper()} O{baseline['line']} [standard]")

        # Assume standard baseline ≈ √3 ≈ 1.732x individual
        # This is theoretical for 2-leg standard parlay = 3.0x total
        self.baseline_multiplier = np.sqrt(3.0)
        baseline['individual_multiplier'] = self.baseline_multiplier

        print(f"[+] Assumed baseline individual multiplier: {self.baseline_multiplier:.3f}x")
        print()

        return baseline

    def test_parlay_payout(self, baseline: Dict, test_pick: Dict) -> Optional[float]:
        """
        Test a 2-leg parlay to discover actual payout.

        In a real implementation, this would:
        1. Use PrizePicks API to build parlay
        2. Get actual payout quote

        For now, we'll use the observed data from your spreadsheet as training data,
        then in production this would make actual API calls.

        Returns: Total parlay payout multiplier (e.g., 3.5x)
        """

        # PLACEHOLDER: In production, this would call PrizePicks API
        # For now, we'll estimate based on odds_type (but this will be replaced with actual API calls)

        # These are EXAMPLES based on your spreadsheet observations
        # Real implementation would get actual payouts from API

        if test_pick['odds_type'] == 'demon':
            # Your spreadsheet showed demon + standard can be 3.5x or 4.0x
            # We'd need to actually test each one
            return None  # Placeholder - needs actual API call

        elif test_pick['odds_type'] == 'standard':
            # Standard + standard = 3.0x (this is well-established)
            return 3.0

        elif test_pick['odds_type'] == 'goblin':
            # Goblin + standard typically 2.5x - 2.75x range
            return None  # Placeholder - needs actual API call

        return None

    def calculate_individual_multiplier(self, parlay_payout: float,
                                       baseline_multiplier: float) -> Tuple[float, float]:
        """
        Reverse-engineer individual pick multiplier from parlay payout.

        Math:
        Total = Baseline × Individual
        Therefore: Individual = Total / Baseline

        Returns: (individual_multiplier, implied_probability)
        """
        individual_multiplier = parlay_payout / baseline_multiplier
        implied_probability = 1.0 / individual_multiplier

        return individual_multiplier, implied_probability

    def learn_multipliers_from_observations(self, observations_df: pd.DataFrame):
        """
        Learn multipliers from manual observations (your spreadsheet data).

        This builds initial training data before we automate testing.
        """
        print("\n[*] Learning multipliers from manual observations...")

        learned_count = 0

        for _, obs in observations_df.iterrows():
            if pd.isna(obs.get('Payout')) or obs.get('Payout') == 0:
                continue

            parlay_payout = obs['Payout']

            # Use standard baseline assumption (√3 ≈ 1.732x)
            baseline_mult = np.sqrt(3.0)
            individual_mult, implied_prob = self.calculate_individual_multiplier(
                parlay_payout, baseline_mult
            )

            # Store in database
            self._save_learned_multiplier(
                date=obs.get('date', datetime.now().strftime('%Y-%m-%d')),
                player_name=obs['Player'],
                prop_type=obs['Prop Type'].lower(),
                line=obs['Line'],
                odds_type=obs.get('odds_type', 'unknown'),
                individual_multiplier=individual_mult,
                implied_probability=implied_prob,
                confidence=0.7,  # Manual observations have 70% confidence
                observations=1,
                baseline_used="Standard pick assumption",
                baseline_multiplier=baseline_mult,
                parlay_payout=parlay_payout
            )

            learned_count += 1

        print(f"[SUCCESS] Learned {learned_count} individual multipliers from observations")
        print()

    def _save_learned_multiplier(self, date: str, player_name: str, prop_type: str,
                                 line: float, odds_type: str, individual_multiplier: float,
                                 implied_probability: float, confidence: float,
                                 observations: int, baseline_used: str,
                                 baseline_multiplier: float, parlay_payout: float):
        """Save learned multiplier to database"""

        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO prizepicks_learned_multipliers
            (date, player_name, prop_type, line, odds_type, individual_multiplier,
             implied_probability, confidence, observations, baseline_used,
             baseline_multiplier, parlay_payout, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, player_name, prop_type, line, odds_type, individual_multiplier,
            implied_probability, confidence, observations, baseline_used,
            baseline_multiplier, parlay_payout, datetime.now().isoformat()
        ))

        self.conn.commit()

    def get_learned_multiplier(self, player_name: str, prop_type: str,
                              line: float, date: str = None) -> Optional[Dict]:
        """
        Retrieve learned multiplier for a specific pick.

        Returns: Dict with multiplier info or None if not learned yet
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        cursor = self.conn.cursor()

        # Try exact match first
        cursor.execute("""
            SELECT individual_multiplier, implied_probability, confidence, observations
            FROM prizepicks_learned_multipliers
            WHERE player_name = ? AND prop_type = ? AND line = ? AND date = ?
            ORDER BY last_updated DESC
            LIMIT 1
        """, (player_name, prop_type, line, date))

        result = cursor.fetchone()

        if result:
            return {
                'individual_multiplier': result[0],
                'implied_probability': result[1],
                'confidence': result[2],
                'observations': result[3],
                'source': 'learned'
            }

        # Try recent historical data (within last 7 days) for same player/prop
        cursor.execute("""
            SELECT individual_multiplier, implied_probability, confidence, observations
            FROM prizepicks_learned_multipliers
            WHERE player_name = ? AND prop_type = ? AND ABS(line - ?) <= 0.5
            ORDER BY date DESC, last_updated DESC
            LIMIT 1
        """, (player_name, prop_type, line))

        result = cursor.fetchone()

        if result:
            return {
                'individual_multiplier': result[0],
                'implied_probability': result[1],
                'confidence': result[2] * 0.8,  # Reduce confidence for historical data
                'observations': result[3],
                'source': 'historical'
            }

        return None

    def get_fallback_multiplier(self, odds_type: str) -> Dict:
        """
        Get fallback multiplier when we haven't learned the actual value yet.
        Uses generic assumptions with LOW confidence.
        """

        fallback_map = {
            'standard': {
                'individual_multiplier': 1.732,  # √3
                'implied_probability': 0.5774,   # 1/1.732
                'confidence': 0.3,  # LOW confidence - just a guess
                'observations': 0,
                'source': 'fallback_assumption'
            },
            'goblin': {
                'individual_multiplier': 1.414,  # √2
                'implied_probability': 0.7071,   # 1/1.414
                'confidence': 0.2,  # VERY LOW confidence
                'observations': 0,
                'source': 'fallback_assumption'
            },
            'demon': {
                'individual_multiplier': 2.0,    # Rough estimate
                'implied_probability': 0.5,      # 1/2.0
                'confidence': 0.2,  # VERY LOW confidence
                'observations': 0,
                'source': 'fallback_assumption'
            }
        }

        return fallback_map.get(odds_type, fallback_map['standard'])

    def export_learned_multipliers(self, filename: str = None):
        """Export all learned multipliers to CSV for review"""

        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%I-%M%p')
            filename = f"LEARNED_MULTIPLIERS_{timestamp}.csv"

        query = """
            SELECT
                date, player_name, prop_type, line, odds_type,
                individual_multiplier, implied_probability, confidence, observations,
                baseline_used, parlay_payout, last_updated
            FROM prizepicks_learned_multipliers
            ORDER BY date DESC, individual_multiplier DESC
        """

        df = pd.read_sql_query(query, self.conn)

        # Format percentages
        df['implied_probability'] = df['implied_probability'].apply(lambda x: f"{x:.1%}")
        df['confidence'] = df['confidence'].apply(lambda x: f"{x:.0%}")

        df.to_csv(filename, index=False)
        print(f"[SUCCESS] Exported {len(df)} learned multipliers to {filename}")

    def close(self):
        """Close database connection"""
        self.conn.close()


def load_manual_observations_from_spreadsheet(filepath: str) -> pd.DataFrame:
    """
    Load your manual observations from Excel spreadsheet.
    This seeds the learning system with your initial testing data.
    """
    import pandas as pd

    try:
        df = pd.read_excel(filepath, sheet_name='10-30 final')

        # Only keep rows where we have actual payout data
        df = df[df['Payout'].notna() & (df['Payout'] > 0)].copy()

        print(f"[+] Loaded {len(df)} manual observations from spreadsheet")
        return df

    except Exception as e:
        print(f"[ERROR] Failed to load spreadsheet: {e}")
        return pd.DataFrame()


def main():
    """Initialize multiplier learning system"""

    print("\n" + "="*80)
    print("PRIZEPICKS MULTIPLIER LEARNING SYSTEM")
    print("="*80)
    print()
    print("This system learns ACTUAL individual pick multipliers from PrizePicks.")
    print("Accurate multipliers = accurate implied probabilities = accurate EV.")
    print()

    learner = PrizePicksMultiplierLearner()

    # Option 1: Load manual observations from your spreadsheet
    spreadsheet_path = r"c:\Users\thoma\Downloads\10-30 working file.xlsx"

    observations_df = load_manual_observations_from_spreadsheet(spreadsheet_path)

    if len(observations_df) > 0:
        learner.learn_multipliers_from_observations(observations_df)
        learner.export_learned_multipliers()
    else:
        print("[WARNING] No observations loaded - system will use fallback assumptions")

    # Display summary
    cursor = learner.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM prizepicks_learned_multipliers")
    total_learned = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("SYSTEM STATUS")
    print("="*80)
    print(f"Total learned multipliers: {total_learned}")
    print()

    if total_learned > 0:
        print("Example learned multipliers:")
        cursor.execute("""
            SELECT player_name, prop_type, line, individual_multiplier, implied_probability, confidence
            FROM prizepicks_learned_multipliers
            ORDER BY individual_multiplier DESC
            LIMIT 10
        """)

        for row in cursor.fetchall():
            print(f"  {row[0]:20} {row[1]:7} O{row[2]:.1f} -> {row[3]:.3f}x (implied: {row[4]:.1%}, confidence: {row[5]:.0%})")

    print()
    print("Next steps:")
    print("  1. System will now use LEARNED multipliers when calculating EV")
    print("  2. For lines without learned data, uses fallback assumptions (LOW confidence)")
    print("  3. Gradually build more observations to improve accuracy")
    print()

    learner.close()


if __name__ == "__main__":
    main()
