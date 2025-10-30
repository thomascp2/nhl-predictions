"""
Multi-Line EV Optimizer for PrizePicks
Evaluates ALL available lines for each player/prop and ranks by EV.
Does NOT filter to "best per player" - includes all +EV opportunities.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import requests
import json


DB_PATH = "database/nhl_predictions.db"


class PrizePicksMultiLineClient:
    """Enhanced PrizePicks API client that fetches ALL available lines"""

    LEAGUE_IDS = {'NHL': 8, 'NFL': 9, 'NBA': 7, 'MLB': 2}

    def __init__(self):
        self.base_url = "https://api.prizepicks.com/projections"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://app.prizepicks.com/',
            'Origin': 'https://app.prizepicks.com'
        }

    def get_all_projections(self, sport: str = 'NHL') -> pd.DataFrame:
        """
        Fetch ALL NHL projections from PrizePicks.
        Returns DataFrame with one row per line (not grouped by player).
        """

        league_id = self.LEAGUE_IDS.get(sport.upper(), 8)
        params = {'league_id': league_id, 'per_page': 250, 'single_stat': 'true'}

        print(f"\n[*] Fetching ALL {sport} lines from PrizePicks...")

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()

            api_data = response.json()
            projections = self._parse_to_dataframe(api_data)

            print(f"[+] Fetched {len(projections)} total lines (all players/props/lines)")
            return projections

        except Exception as e:
            print(f"[!] Failed to fetch PrizePicks: {e}")
            return pd.DataFrame()

    def _parse_to_dataframe(self, api_data: Dict) -> pd.DataFrame:
        """Parse PrizePicks API response into flat DataFrame"""

        projections_raw = api_data.get('data', [])
        included = api_data.get('included', [])

        # Build lookups
        players = {}
        games = {}

        for item in included:
            item_type = item.get('type')
            item_id = item.get('id')
            attrs = item.get('attributes', {})

            if item_type == 'new_player':
                players[item_id] = {
                    'name': attrs.get('name', 'Unknown'),
                    'team': attrs.get('team', 'UNK'),
                    'position': attrs.get('position', 'UNK')
                }
            elif item_type == 'game':
                games[item_id] = {
                    'away_team': attrs.get('away_team', 'UNK'),
                    'home_team': attrs.get('home_team', 'UNK'),
                    'game_time': attrs.get('game_time')
                }

        # Parse projections to list
        rows = []

        for proj in projections_raw:
            attrs = proj.get('attributes', {})
            relationships = proj.get('relationships', {})

            # Get player
            player_id = relationships.get('new_player', {}).get('data', {}).get('id')
            player_info = players.get(player_id, {'name': 'Unknown', 'team': 'UNK'})

            # Get game
            game_id = relationships.get('game', {}).get('data', {}).get('id')
            game_info = games.get(game_id, {})

            # Determine opponent
            player_team = player_info['team']
            opponent = 'UNK'
            if game_info:
                if player_team == game_info.get('away_team'):
                    opponent = game_info.get('home_team', 'UNK')
                elif player_team == game_info.get('home_team'):
                    opponent = game_info.get('away_team', 'UNK')

            # Extract projection
            stat_type = attrs.get('stat_type', 'Unknown')
            line_score = attrs.get('line_score')
            odds_type = attrs.get('odds_type', 'standard')

            # Map stat types
            stat_map = {
                'Points': 'points',
                'Shots On Goal': 'shots',
                'SOG': 'shots',
                'Goals': 'goals',
                'Assists': 'assists',
                'Blocked Shots': 'blocks',
                'Hits': 'hits'
            }

            prop_type = stat_map.get(stat_type, stat_type.lower())

            rows.append({
                'player_name': player_info['name'],
                'team': player_team,
                'opponent': opponent,
                'prop_type': prop_type,
                'line': float(line_score) if line_score else None,
                'odds_type': odds_type,
                'stat_type': stat_type
            })

        df = pd.DataFrame(rows)

        # Remove any rows with missing lines
        df = df[df['line'].notna()].reset_index(drop=True)

        return df


class MultiLineEVCalculator:
    """
    Calculates EV for ALL available PrizePicks lines.
    Uses our model's predictions to estimate probability at each line.
    """

    # PrizePicks payout multipliers
    PAYOUT_MULTIPLIERS = {
        'standard': 3.0,   # 2-pick power play
        'goblin': 2.0,     # Easier line, lower payout
        'demon': 4.0       # Harder line, higher payout
    }

    def __init__(self, conn):
        self.conn = conn
        self.predictions_cache = {}

    def load_predictions(self, date: str = None) -> pd.DataFrame:
        """Load our model's predictions for the date"""

        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        query = """
            SELECT
                player_name, team, opponent, prop_type, line,
                probability, expected_value, kelly_score,
                confidence_tier, reasoning
            FROM predictions
            WHERE game_date = ?
            ORDER BY probability DESC
        """

        df = pd.read_sql_query(query, self.conn, params=(date,))

        # Cache predictions by player+prop for faster lookup
        for _, row in df.iterrows():
            key = f"{row['player_name']}_{row['prop_type']}"
            if key not in self.predictions_cache:
                self.predictions_cache[key] = []
            self.predictions_cache[key].append(row)

        return df

    def estimate_probability_at_line(self, player_name: str, prop_type: str,
                                    target_line: float) -> Tuple[float, str]:
        """
        Estimate our model's probability for a specific line.
        Uses interpolation/extrapolation from nearby predictions.

        Returns: (probability, reasoning)
        """

        key = f"{player_name}_{prop_type}"

        if key not in self.predictions_cache:
            return None, "No prediction available"

        preds = self.predictions_cache[key]

        # Find predictions bracketing this line
        lower_preds = [p for p in preds if p['line'] <= target_line]
        upper_preds = [p for p in preds if p['line'] > target_line]

        # Exact match
        exact = [p for p in preds if abs(p['line'] - target_line) < 0.01]
        if exact:
            return exact[0]['probability'], exact[0]['reasoning']

        # Interpolation (between two predictions)
        if lower_preds and upper_preds:
            lower = max(lower_preds, key=lambda x: x['line'])
            upper = min(upper_preds, key=lambda x: x['line'])

            # Linear interpolation
            line_diff = upper['line'] - lower['line']
            target_diff = target_line - lower['line']
            weight = target_diff / line_diff if line_diff > 0 else 0.5

            # Probability decreases as line increases (OVER bets)
            prob = lower['probability'] - (lower['probability'] - upper['probability']) * weight

            reasoning = f"Interpolated between {lower['line']} ({lower['probability']:.1%}) and {upper['line']} ({upper['probability']:.1%})"
            return prob, reasoning

        # Extrapolation (beyond our predictions)
        if lower_preds:
            # Target line is ABOVE all our predictions
            closest = max(lower_preds, key=lambda x: x['line'])

            # Assume probability drops by ~10% per 1.0 line increase
            line_diff = target_line - closest['line']
            prob_drop = line_diff * 0.10  # Conservative estimate
            prob = max(0.05, closest['probability'] - prob_drop)  # Floor at 5%

            reasoning = f"Extrapolated from {closest['line']} ({closest['probability']:.1%}), -{prob_drop:.0%} for +{line_diff:.1f} line"
            return prob, reasoning

        if upper_preds:
            # Target line is BELOW all our predictions
            closest = min(upper_preds, key=lambda x: x['line'])

            # Assume probability increases by ~10% per 1.0 line decrease
            line_diff = closest['line'] - target_line
            prob_increase = line_diff * 0.10
            prob = min(0.95, closest['probability'] + prob_increase)  # Cap at 95%

            reasoning = f"Extrapolated from {closest['line']} ({closest['probability']:.1%}), +{prob_increase:.0%} for -{line_diff:.1f} line"
            return prob, reasoning

        return None, "No prediction available"

    def calculate_edge_for_line(self, player_name: str, team: str, opponent: str,
                                prop_type: str, line: float, odds_type: str) -> Dict:
        """
        Calculate edge and EV for a specific PrizePicks line.
        """

        # Get our probability estimate
        our_prob, reasoning = self.estimate_probability_at_line(player_name, prop_type, line)

        if our_prob is None:
            return None

        # Get payout multiplier
        payout = self.PAYOUT_MULTIPLIERS.get(odds_type, 3.0)

        # Market's implied probability
        pp_implied_prob = 1.0 / payout

        # Calculate edge and EV
        edge = (our_prob - pp_implied_prob) * 100
        ev = (our_prob * payout) - 1.0
        ev_pct = ev * 100

        return {
            'player_name': player_name,
            'team': team,
            'opponent': opponent,
            'prop_type': prop_type,
            'line': line,
            'odds_type': odds_type,
            'our_probability': our_prob,
            'pp_implied_probability': pp_implied_prob,
            'edge': edge,
            'expected_value': ev,
            'ev_pct': ev_pct,
            'payout_multiplier': payout,
            'reasoning': reasoning
        }

    def evaluate_all_prizepicks_lines(self, prizepicks_df: pd.DataFrame,
                                     min_ev: float = 0.05) -> List[Dict]:
        """
        Evaluate EVERY PrizePicks line and return all with +EV.
        Sorted by EV (highest first).
        """

        print("\n" + "="*80)
        print("MULTI-LINE EV OPTIMIZATION")
        print("="*80)
        print()
        print(f"[*] Evaluating {len(prizepicks_df)} PrizePicks lines...")
        print(f"[*] Minimum EV threshold: {min_ev:.1%}")
        print()

        edge_plays = []

        for _, pp_line in prizepicks_df.iterrows():
            edge_data = self.calculate_edge_for_line(
                pp_line['player_name'],
                pp_line['team'],
                pp_line['opponent'],
                pp_line['prop_type'],
                pp_line['line'],
                pp_line['odds_type']
            )

            if edge_data and edge_data['expected_value'] >= min_ev:
                edge_plays.append(edge_data)

        # Sort by EV (highest first)
        edge_plays.sort(key=lambda x: x['expected_value'], reverse=True)

        print(f"[SUCCESS] Found {len(edge_plays)} lines with {min_ev:.0%}+ EV")
        print()

        return edge_plays


def save_multi_line_edges_to_db(edge_plays: List[Dict], date: str = None):
    """Save all edge plays to database"""

    if not edge_plays:
        return

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing edges for this date (fresh start)
    cursor.execute("DELETE FROM prizepicks_edges WHERE date = ?", (date,))

    # Insert all edges
    for play in edge_plays:
        cursor.execute("""
            INSERT INTO prizepicks_edges
            (date, player_name, team, opponent, prop_type, line, odds_type,
             our_probability, pp_implied_probability, edge, expected_value,
             kelly_score, payout_multiplier, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, play['player_name'], play['team'], play['opponent'],
            play['prop_type'], play['line'], play['odds_type'],
            play['our_probability'], play['pp_implied_probability'],
            play['edge'], play['expected_value'],
            0.0,  # Kelly score (placeholder)
            play['payout_multiplier'],
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()

    print(f"[SUCCESS] Saved {len(edge_plays)} edge plays to database")
    print()


def export_to_csv(edge_plays: List[Dict], filename: str = None):
    """Export edge plays to CSV"""

    if not edge_plays:
        return

    if filename is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%I-%M%p')
        filename = f"MULTI_LINE_EDGES_{timestamp}.csv"

    df = pd.DataFrame(edge_plays)

    # Reorder columns for readability
    cols = ['player_name', 'team', 'opponent', 'prop_type', 'line', 'odds_type',
            'our_probability', 'pp_implied_probability', 'edge',
            'expected_value', 'ev_pct', 'payout_multiplier', 'reasoning']

    df = df[[c for c in cols if c in df.columns]]

    # Format percentages
    df['our_probability'] = df['our_probability'].apply(lambda x: f"{x:.1%}")
    df['pp_implied_probability'] = df['pp_implied_probability'].apply(lambda x: f"{x:.1%}")
    df['edge'] = df['edge'].apply(lambda x: f"{x:+.1f}%")
    df['ev_pct'] = df['ev_pct'].apply(lambda x: f"{x:+.1f}%")

    df.to_csv(filename, index=False)
    print(f"[SUCCESS] Exported to {filename}")
    print()


def display_top_edges(edge_plays: List[Dict], top_n: int = 30):
    """Display top edge plays"""

    if not edge_plays:
        print("[WARNING] No edge plays to display")
        return

    print("="*80)
    print(f"TOP {min(top_n, len(edge_plays))} EDGE PLAYS (Sorted by EV)")
    print("="*80)
    print()

    for i, play in enumerate(edge_plays[:top_n], 1):
        odds_label = {
            'standard': '[STD]',
            'goblin': '[GOB]',
            'demon': '[DEM]'
        }.get(play['odds_type'], '[STD]')

        print(f"{i:3}. {play['player_name']:25} ({play['team']}) vs {play['opponent']}")
        print(f"     {play['prop_type'].upper():7} O{play['line']:.1f} {odds_label:5}")
        print(f"     EV: {play['ev_pct']:+6.1f}% | Edge: {play['edge']:+6.1f}% | Prob: {play['our_probability']:.1%} | Payout: {play['payout_multiplier']:.1f}x")
        print(f"     {play['reasoning']}")
        print()


def main():
    """Run multi-line EV optimizer"""
    import sys

    print("\n" + "="*80)
    print("MULTI-LINE EV OPTIMIZER - PRIZEPICKS")
    print("="*80)
    print()

    date = sys.argv[1] if len(sys.argv) > 1 else None
    min_ev = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05  # 5% minimum EV

    # Step 1: Fetch ALL PrizePicks lines
    client = PrizePicksMultiLineClient()
    prizepicks_df = client.get_all_projections('NHL')

    if len(prizepicks_df) == 0:
        print("[ERROR] Failed to fetch PrizePicks lines")
        return

    # Step 2: Load our predictions
    conn = sqlite3.connect(DB_PATH)
    calculator = MultiLineEVCalculator(conn)
    calculator.load_predictions(date)

    if len(calculator.predictions_cache) == 0:
        print("[ERROR] No predictions found. Run prediction generation first.")
        conn.close()
        return

    print(f"[SUCCESS] Loaded predictions for {len(calculator.predictions_cache)} player/prop combos")
    print()

    # Step 3: Evaluate ALL lines
    edge_plays = calculator.evaluate_all_prizepicks_lines(prizepicks_df, min_ev=min_ev)

    conn.close()

    if not edge_plays:
        print("[WARNING] No edge plays found")
        print(f"   Try lowering min_ev threshold (currently {min_ev:.0%})")
        return

    # Step 4: Display results
    display_top_edges(edge_plays, top_n=50)

    # Step 5: Save to database
    save_multi_line_edges_to_db(edge_plays, date)

    # Step 6: Export to CSV
    export_to_csv(edge_plays)

    print("="*80)
    print("[SUCCESS] MULTI-LINE OPTIMIZATION COMPLETE")
    print("="*80)
    print()
    print(f"Total edge plays: {len(edge_plays)}")
    print(f"Average EV: {np.mean([p['ev_pct'] for p in edge_plays]):.1f}%")
    print(f"Median EV: {np.median([p['ev_pct'] for p in edge_plays]):.1f}%")
    print(f"Max EV: {max([p['ev_pct'] for p in edge_plays]):.1f}%")
    print()
    print("Next steps:")
    print("   1. Review edge plays in CSV export")
    print("   2. Run GTO parlay optimizer: python gto_parlay_optimizer.py")
    print()


if __name__ == "__main__":
    main()
