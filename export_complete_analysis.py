"""
COMPLETE ANALYSIS EXPORT
========================

Export ALL analyzed data to comprehensive CSV:
- All stars picks (all tiers, not just T1-ELITE)
- Market edge percentages
- Matchup data (O/U, ML, favorable/unfavorable)
- PrizePicks available lines
- Recommendations (bet/skip)

Usage:
    python export_complete_analysis.py [date]
"""

import sqlite3
import csv
from datetime import datetime
from typing import List, Dict
import sys


DB_PATH = "database/nhl_predictions.db"


class ComprehensiveAnalysisExporter:
    """Export complete betting analysis to CSV"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

        # Import stars list
        from stars_only_filter import STARS
        self.stars = STARS

        # Favorable matchup criteria
        self.FAVORABLE_CRITERIA = {
            "min_over_under": 5.5,
            "max_favorite_ml": -175,
            "min_underdog_ml": +150
        }

    def get_all_stars_predictions(self, game_date: str) -> List[Dict]:
        """Get ALL predictions for stars (not just T1-ELITE)"""

        cursor = self.conn.cursor()

        # Get all predictions for stars (all tiers)
        placeholders = ",".join(["?" for _ in self.stars])
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
                reasoning,
                model_version
            FROM predictions
            WHERE game_date = ?
            AND player_name IN ({placeholders})
            ORDER BY probability DESC, player_name
        """

        params = [game_date] + self.stars
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
                "reasoning": row[8],
                "model_version": row[9]
            })

        return predictions

    def get_betting_lines(self, game_date: str) -> Dict:
        """Get betting lines (O/U, ML) for games"""

        cursor = self.conn.cursor()

        # Get betting lines
        cursor.execute("""
            SELECT
                home_team,
                away_team,
                over_under,
                home_ml,
                away_ml
            FROM game_betting_lines
            WHERE game_date = ?
        """, (game_date,))

        lines = {}
        for row in cursor.fetchall():
            home_team, away_team, over_under, home_ml, away_ml = row

            # Store by team
            lines[home_team] = {
                "opponent": away_team,
                "over_under": over_under,
                "moneyline": home_ml,
                "is_home": True
            }
            lines[away_team] = {
                "opponent": home_team,
                "over_under": over_under,
                "moneyline": away_ml,
                "is_home": False
            }

        return lines

    def get_prizepicks_lines(self, game_date: str) -> Dict:
        """Get PrizePicks lines (multiple per prop)"""

        cursor = self.conn.cursor()

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

            lines[player_name][prop_type].append(line)

        return lines

    def is_favorable_matchup(self, over_under: float, moneyline: int) -> tuple:
        """
        Check if matchup is favorable

        Returns:
            (is_favorable: bool, reason: str)
        """
        if over_under is None or moneyline is None:
            return False, "No betting data"

        # Check O/U
        if over_under < self.FAVORABLE_CRITERIA["min_over_under"]:
            return False, f"Low scoring (O/U={over_under})"

        # Check ML
        if moneyline < 0:  # Favorite
            if moneyline < self.FAVORABLE_CRITERIA["max_favorite_ml"]:
                return False, f"Heavy favorite (ML={moneyline})"
        else:  # Underdog
            if moneyline > self.FAVORABLE_CRITERIA["min_underdog_ml"]:
                return False, f"Heavy underdog (ML=+{moneyline})"

        return True, "Favorable"

    def calculate_market_edge(self, model_prob: float, model_line: float,
                             prizepicks_lines: List[float]) -> tuple:
        """
        Calculate edge vs PrizePicks market

        Returns:
            (edge_pct: float, closest_line: float, market_prob: float)
        """
        if not prizepicks_lines:
            return None, None, None

        # Find closest line
        closest_line = min(prizepicks_lines, key=lambda x: abs(x - model_line))

        # Calculate market implied probability (2x multiplier ~47.5%)
        market_prob = 0.475  # Standard PrizePicks 2x multiplier

        # Calculate edge
        edge = model_prob - market_prob
        edge_pct = edge * 100

        return edge_pct, closest_line, market_prob

    def get_recommendation(self, tier: str, is_favorable: bool, edge_pct: float = None) -> str:
        """
        Get betting recommendation

        Priority:
        1. Picks in both lists (stars + edge) = BET - HIGHEST CONFIDENCE
        2. Edge >=20% = BET - HUGE EDGE
        3. Edge >=10% = BET - STRONG EDGE
        4. Stars + Favorable + T2-STRONG or better = BET - FAVORABLE MATCHUP
        5. Edge 5-9% = CONSIDER - SMALL EDGE
        6. Stars + Unfavorable = SKIP - UNFAVORABLE MATCHUP
        7. Edge <5% = SKIP - NO EDGE
        """

        # Check edge first
        if edge_pct is not None:
            if edge_pct >= 20:
                return "BET - HUGE EDGE (>=20%)"
            elif edge_pct >= 10:
                return "BET - STRONG EDGE (>=10%)"
            elif edge_pct >= 5:
                if is_favorable and tier in ("T1-ELITE", "T2-STRONG"):
                    return "BET - HIGHEST CONFIDENCE (Stars + Edge + Favorable)"
                else:
                    return "CONSIDER - SMALL EDGE (5-10%)"
            else:
                return "SKIP - NO EDGE (<5%)"

        # No edge data, use stars criteria
        if is_favorable and tier in ("T1-ELITE", "T2-STRONG"):
            return "BET - FAVORABLE MATCHUP (Stars Only)"
        elif not is_favorable:
            return "SKIP - UNFAVORABLE MATCHUP"
        else:
            return "SKIP - LOW CONFIDENCE (<T2-STRONG)"

    def export_to_csv(self, game_date: str, output_file: str = None):
        """Export complete analysis to CSV"""

        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%I%M%p')
            output_file = f"COMPLETE_ANALYSIS_{timestamp}.csv"

        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE BETTING ANALYSIS EXPORT")
        print(f"{'='*80}\n")
        print(f"Date: {game_date}")
        print(f"Output: {output_file}\n")

        # Get all data
        print("Fetching predictions...")
        predictions = self.get_all_stars_predictions(game_date)
        print(f"  Found {len(predictions)} predictions for {len(self.stars)} stars")

        print("Fetching betting lines...")
        betting_lines = self.get_betting_lines(game_date)
        print(f"  Found {len(betting_lines)} teams with betting data")

        print("Fetching PrizePicks lines...")
        prizepicks_lines = self.get_prizepicks_lines(game_date)
        print(f"  Found {len(prizepicks_lines)} players with PrizePicks lines")

        print("\nAnalyzing and exporting...\n")

        # Build comprehensive records
        records = []

        bet_count = 0
        consider_count = 0
        skip_count = 0

        for pred in predictions:
            player = pred["player"]
            team = pred["team"]
            prop = pred["prop_type"]

            # Get betting lines
            betting_data = betting_lines.get(team, {})
            over_under = betting_data.get("over_under")
            moneyline = betting_data.get("moneyline")

            # Check if favorable
            is_favorable, matchup_reason = self.is_favorable_matchup(over_under, moneyline)

            # Get PrizePicks lines
            pp_lines = None
            pp_lines_str = "Not available"
            edge_pct = None
            closest_pp_line = None
            market_prob = None

            if player in prizepicks_lines and prop in prizepicks_lines[player]:
                pp_lines = prizepicks_lines[player][prop]
                pp_lines_str = ", ".join([str(l) for l in sorted(pp_lines)])

                # Calculate edge
                edge_pct, closest_pp_line, market_prob = self.calculate_market_edge(
                    pred["model_prob"],
                    pred["line"],
                    pp_lines
                )

            # Get recommendation
            recommendation = self.get_recommendation(
                pred["tier"],
                is_favorable,
                edge_pct
            )

            # Count recommendations
            if recommendation.startswith("BET"):
                bet_count += 1
            elif recommendation.startswith("CONSIDER"):
                consider_count += 1
            else:
                skip_count += 1

            # Build record
            record = {
                "Recommendation": recommendation,
                "Player": player,
                "Team": team,
                "Opponent": pred["opponent"],
                "Prop": prop.upper(),
                "Direction": pred["prediction"].upper(),
                "Line": pred["line"],
                "Model Probability (%)": f"{pred['model_prob']*100:.1f}",
                "Confidence Tier": pred["tier"],
                "Model Version": pred["model_version"],
                "Reasoning": pred["reasoning"],

                # Market data
                "PrizePicks Lines Available": pp_lines_str,
                "Closest PrizePicks Line": closest_pp_line if closest_pp_line else "N/A",
                "Market Probability (%)": f"{market_prob*100:.1f}" if market_prob else "N/A",
                "Edge vs Market (%)": f"{edge_pct:+.1f}" if edge_pct is not None else "N/A",

                # Matchup data
                "Over/Under": over_under if over_under else "N/A",
                "Moneyline": moneyline if moneyline else "N/A",
                "Favorable Matchup": "YES" if is_favorable else "NO",
                "Matchup Notes": matchup_reason,
            }

            records.append(record)

        # Sort by recommendation priority
        priority = {
            "BET - HIGHEST CONFIDENCE (Stars + Edge + Favorable)": 1,
            "BET - HUGE EDGE (>=20%)": 2,
            "BET - STRONG EDGE (>=10%)": 3,
            "BET - FAVORABLE MATCHUP (Stars Only)": 4,
            "CONSIDER - SMALL EDGE (5-10%)": 5,
            "SKIP - NO EDGE (<5%)": 6,
            "SKIP - UNFAVORABLE MATCHUP": 7,
            "SKIP - LOW CONFIDENCE (<T2-STRONG)": 8,
        }

        records.sort(key=lambda x: (priority.get(x["Recommendation"], 99), -float(x["Model Probability (%)"])))

        # Write CSV
        if records:
            fieldnames = list(records[0].keys())

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

            print(f"{'='*80}")
            print(f"EXPORT COMPLETE")
            print(f"{'='*80}\n")
            print(f"Total picks analyzed: {len(records)}")
            print(f"  BET: {bet_count}")
            print(f"  CONSIDER: {consider_count}")
            print(f"  SKIP: {skip_count}")
            print(f"\nFile saved: {output_file}")
            print(f"{'='*80}\n")

            return output_file
        else:
            print("[WARN] No records to export")
            return None

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Export comprehensive analysis"""

    # Get date from command line or use today
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')

    exporter = ComprehensiveAnalysisExporter()
    exporter.export_to_csv(target_date)
    exporter.close()


if __name__ == "__main__":
    main()
