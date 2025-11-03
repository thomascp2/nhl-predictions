"""
MARKET VS MODEL COMPARISON
===========================

Compare your model's predictions to market odds to find edges.

Concept:
  - Market thinks: McDavid Points O/U 0.5 = 52% (from -110 odds)
  - Your model thinks: McDavid Points OVER 0.5 = 91.4%
  - EDGE = 91.4% - 52% = +39.4% ✅ BET THIS!

Only bet when you have a significant edge over the market.

Supports:
  - PrizePicks lines (what you actually bet on)
  - Sportradar API (multiple sportsbooks aggregated)
  - Manual line input
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple

DB_PATH = "database/nhl_predictions.db"


class MarketVsModelAnalyzer:
    """Compare model predictions to market odds"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def american_to_probability(self, american_odds: int) -> float:
        """
        Convert American odds to implied probability

        Examples:
          -110 → 52.4%
          +150 → 40.0%
          -200 → 66.7%
        """
        if american_odds < 0:
            # Favorite: -110 means bet $110 to win $100
            return abs(american_odds) / (abs(american_odds) + 100)
        else:
            # Underdog: +150 means bet $100 to win $150
            return 100 / (american_odds + 100)

    def prizepicks_multiplier_to_probability(self, multiplier: float) -> float:
        """
        Convert PrizePicks multiplier to implied probability

        PrizePicks uses multipliers (2x, 3x, 4x, etc.) instead of odds.
        Higher multiplier = less likely to hit

        Examples:
          2.0x → ~50% (even odds)
          3.0x → ~33% (2:1 against)
          4.0x → ~25% (3:1 against)

        Note: PrizePicks takes juice, so actual probabilities are ~47% for 2x
        """
        # Rough conversion (PrizePicks takes ~5-10% juice)
        raw_prob = 1 / multiplier

        # Adjust for juice (PrizePicks advantage)
        if multiplier <= 2.0:
            return raw_prob * 0.95  # ~5% juice on low multipliers
        elif multiplier <= 3.0:
            return raw_prob * 0.90  # ~10% juice on medium
        else:
            return raw_prob * 0.85  # ~15% juice on high multipliers

    def get_model_predictions(self, game_date: str, stars_only: bool = True) -> List[Dict]:
        """Get predictions from your model"""

        # Optional: Filter to stars only
        stars_filter = ""
        if stars_only:
            from stars_only_filter import STARS
            placeholders = ",".join(["?" for _ in STARS])
            stars_filter = f"AND player_name IN ({placeholders})"
            params = [game_date] + (STARS if stars_only else [])
        else:
            params = [game_date]

        query = f"""
            SELECT
                player_name,
                team,
                opponent,
                prop_type,
                line,
                prediction,
                probability,
                confidence_tier,
                reasoning
            FROM predictions
            WHERE game_date = ?
            {stars_filter}
            AND confidence_tier IN ('T1-ELITE', 'T2-STRONG')
            ORDER BY probability DESC
        """

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "player": row[0],
                "team": row[1],
                "opponent": row[2],
                "prop_type": row[3],
                "line": row[4],
                "prediction": row[5],
                "model_prob": row[6],
                "tier": row[7],
                "reasoning": row[8]
            })

        return predictions

    def get_market_lines(self, game_date: str, source: str = "prizepicks") -> Dict:
        """
        Get market lines from various sources

        Sources:
          - "prizepicks": Fetch from PrizePicks (you already have scraper)
          - "sportradar": Fetch from Sportradar API (requires API key)
          - "manual": Use manually entered lines (for testing)
        """

        if source == "prizepicks":
            return self._get_prizepicks_lines(game_date)
        elif source == "sportradar":
            return self._get_sportradar_lines(game_date)
        elif source == "manual":
            return self._get_manual_lines()
        else:
            return {}

    def _get_prizepicks_lines(self, game_date: str) -> Dict:
        """
        Get lines from PrizePicks database (supports MULTIPLE lines per prop)

        Fetches lines from prizepicks_lines table (populated by fetch_prizepicks_current_lines.py)

        Returns:
            Dict[player][prop] = [list of line dicts with 'line' and 'over_multiplier']
        """

        cursor = self.conn.cursor()

        # Get ALL lines from database (multiple per player/prop combo)
        cursor.execute("""
            SELECT player_name, prop_type, line
            FROM prizepicks_lines
            WHERE date = ?
            ORDER BY player_name, prop_type, line
        """, (game_date,))

        lines = {}
        for row in cursor.fetchall():
            player_name, prop_type, line = row

            if player_name not in lines:
                lines[player_name] = {}

            if prop_type not in lines[player_name]:
                lines[player_name][prop_type] = []

            # Add each line
            # PrizePicks doesn't expose individual pick odds
            # We use standard 2x multiplier (50/50 implied odds)
            lines[player_name][prop_type].append({
                "line": line,
                "over_multiplier": 2.0  # Standard PrizePicks multiplier
            })

        if not lines:
            print(f"[WARN] No PrizePicks lines found for {game_date}")
            print(f"[HINT] Run: python fetch_prizepicks_current_lines.py")

        return lines

    def _get_sportradar_lines(self, game_date: str) -> Dict:
        """
        Get lines from Sportradar API

        Requires API key and subscription
        """
        # TODO: Implement Sportradar API integration
        # For now, return empty
        return {}

    def _get_manual_lines(self) -> Dict:
        """Manually entered lines for testing"""
        return {
            "Connor McDavid": {
                "points": {"line": 0.5, "american_odds": -110},  # Standard odds
                "shots": {"line": 2.5, "american_odds": +150}   # Underdog
            }
        }

    def calculate_edges(self, predictions: List[Dict], market_lines: Dict) -> List[Dict]:
        """
        Compare model predictions to market lines (handles MULTIPLE lines per prop)

        For each prediction, finds the CLOSEST matching market line and calculates edge.

        Example:
            Model: McDavid will score 3.8 shots
            Market Lines: 2.5, 3.5, 4.5
            Best Match: 3.5 (closest to 3.8)
            Compare: Model prob of OVER 3.5 vs Market prob

        Returns list of bets with calculated edges
        """
        edges = []

        for pred in predictions:
            player = pred["player"]
            prop = pred["prop_type"]
            model_line = pred["line"]  # The line our model is predicting

            # Check if we have market lines for this player/prop
            if player not in market_lines:
                continue
            if prop not in market_lines[player]:
                continue

            market_line_list = market_lines[player][prop]

            # Find the CLOSEST market line to our model's line
            # This is the most fair comparison
            closest_market = min(market_line_list, key=lambda x: abs(x["line"] - model_line))

            # Calculate market implied probability for this specific line
            if "over_multiplier" in closest_market:
                # PrizePicks format
                market_prob = self.prizepicks_multiplier_to_probability(closest_market["over_multiplier"])
            elif "american_odds" in closest_market:
                # Standard American odds format
                market_prob = self.american_to_probability(closest_market["american_odds"])
            else:
                continue

            # Calculate edge
            model_prob = pred["model_prob"]
            edge = model_prob - market_prob
            edge_pct = edge * 100

            # Expected value (simplified)
            # EV = (Win Prob × Win Amount) - (Loss Prob × Loss Amount)
            # For PrizePicks 2x multiplier: win $100, lose $100
            multiplier = closest_market.get("over_multiplier", 2.0)
            win_amount = 100 * (multiplier - 1)  # 2x = win $100, 3x = win $200
            loss_amount = 100

            ev = (model_prob * win_amount) - ((1 - model_prob) * loss_amount)

            # Check if our model's line matches the market line
            line_match = abs(closest_market["line"] - model_line) < 0.1

            edges.append({
                **pred,
                "market_prob": market_prob,
                "edge": edge,
                "edge_pct": edge_pct,
                "ev": ev,
                "market_line": closest_market["line"],
                "market_multiplier": closest_market.get("over_multiplier", 2.0),
                "line_match": line_match,
                "all_market_lines": [ml["line"] for ml in market_line_list],
                "market_source": "PrizePicks" if "over_multiplier" in closest_market else "Sportsbook"
            })

        # Sort by edge (highest first)
        edges.sort(key=lambda x: x["edge"], reverse=True)

        return edges

    def display_edges(self, edges: List[Dict], min_edge_pct: float = 5.0):
        """
        Display edges in a readable format

        Args:
            edges: List of edge calculations
            min_edge_pct: Minimum edge % to display (default 5%)
        """

        # Filter to minimum edge
        significant_edges = [e for e in edges if e["edge_pct"] >= min_edge_pct]

        print(f"\n{'='*80}")
        print(f"MARKET VS MODEL ANALYSIS - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print(f"{'='*80}\n")
        print(f"Total predictions analyzed: {len(edges)}")
        print(f"Significant edges (>={min_edge_pct}%): {len(significant_edges)}")
        print(f"\n{'-'*80}\n")

        if not significant_edges:
            print(f"No edges >={min_edge_pct}% found.")
            print(f"Market is efficient today - consider sitting out or lowering threshold.")
            print(f"\n{'='*80}\n")
            return

        for i, edge in enumerate(significant_edges, 1):
            print(f"BET #{i} - {edge['tier']} (Edge: +{edge['edge_pct']:.1f}%)")
            print(f"Player:  {edge['player']} ({edge['team']} vs {edge['opponent']})")
            print(f"Prop:    {edge['prop_type'].upper()} {edge['prediction']} {edge['line']}")
            print(f"")
            print(f"YOUR MODEL:")
            print(f"  Line:        {edge['line']}")
            print(f"  Probability: {edge['model_prob']*100:.1f}%")
            print(f"  Reasoning:   {edge['reasoning']}")
            print(f"")

            # Show all available market lines
            all_lines = edge.get('all_market_lines', [edge['market_line']])
            if len(all_lines) > 1:
                print(f"MARKET ({edge['market_source']}) - AVAILABLE LINES:")
                lines_str = ", ".join([str(l) for l in sorted(all_lines)])
                print(f"  All Lines:   {lines_str}")
                print(f"  Best Match:  {edge['market_line']} ({'EXACT' if edge['line_match'] else 'CLOSEST'})")
            else:
                print(f"MARKET ({edge['market_source']}):")
                print(f"  Line:        {edge['market_line']}")

            print(f"  Probability: {edge['market_prob']*100:.1f}%")
            print(f"  Multiplier:  {edge.get('market_multiplier', 2.0):.1f}x")
            print(f"")
            print(f"EDGE ANALYSIS:")
            print(f"  Your Edge:   +{edge['edge_pct']:.1f}%")
            print(f"  Expected EV: ${edge['ev']:.2f} per $100 bet")

            # Rating
            if edge['edge_pct'] >= 20:
                rating = "HUGE EDGE - MAX BET"
            elif edge['edge_pct'] >= 10:
                rating = "STRONG EDGE - BET THIS"
            elif edge['edge_pct'] >= 5:
                rating = "SMALL EDGE - Consider"
            else:
                rating = "MARGINAL - Skip"

            print(f"  Rating:      {rating}")

            # Line mismatch warning
            if not edge['line_match'] and abs(edge['market_line'] - edge['line']) > 0.5:
                print(f"")
                print(f"  [WARNING] Model line ({edge['line']}) differs from closest market line ({edge['market_line']})")
                print(f"            Edge calculation may be less accurate")

            print(f"{'-'*80}\n")

        print(f"{'='*80}")
        print(f"BETTING STRATEGY:")
        print(f"  - Bet >=20% edges with larger stakes (these are rare!)")
        print(f"  - Bet >=10% edges with standard stakes")
        print(f"  - Consider 5-10% edges (small edge, lower stakes)")
        print(f"  - Skip <5% edges (not enough margin over market)")
        print(f"{'='*80}\n")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Run market vs model analysis"""
    import sys

    # Get date from command line or use today
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')

    print(f"\nMarket vs Model Edge Finder")
    print(f"Target Date: {target_date}\n")

    analyzer = MarketVsModelAnalyzer()

    # Get your model predictions (stars only, high confidence)
    print("Fetching model predictions...")
    predictions = analyzer.get_model_predictions(target_date, stars_only=True)
    print(f"Found {len(predictions)} high-confidence predictions\n")

    # Get market lines (PrizePicks)
    print("Fetching market lines (PrizePicks)...")
    market_lines = analyzer.get_market_lines(target_date, source="prizepicks")
    print(f"Found market lines for {len(market_lines)} players\n")

    # Calculate edges
    print("Calculating edges...")
    edges = analyzer.calculate_edges(predictions, market_lines)

    # Display results
    analyzer.display_edges(edges, min_edge_pct=5.0)

    analyzer.close()


if __name__ == "__main__":
    main()
