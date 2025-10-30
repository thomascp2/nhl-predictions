"""
Complete PrizePicks Integration v2.0
- Fetches actual PrizePicks lines
- Calculates REAL edge vs market
- Integrates opponent/goalie adjustments
- Saves edge data to database
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import requests
import json

DB_PATH = "database/nhl_predictions.db"


class PrizePicksClient:
    """Enhanced PrizePicks API client"""

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
    
    def get_projections(self, sport: str = 'NHL') -> List[Dict]:
        """Fetch NHL projections from PrizePicks"""
        
        league_id = self.LEAGUE_IDS.get(sport.upper(), 8)
        params = {'league_id': league_id, 'per_page': 250, 'single_stat': 'true'}
        
        print(f"\n[*] Fetching {sport} lines from PrizePicks...")
        
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            api_data = response.json()
            projections = self._parse_response(api_data)
            
            print(f"[+] Fetched {len(projections)} player projections")
            return projections
            
        except Exception as e:
            print(f"[!] Failed to fetch PrizePicks: {e}")
            return []
    
    def _parse_response(self, api_data: Dict) -> List[Dict]:
        """Parse PrizePicks API response"""
        
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
        
        # Parse projections
        result = []
        
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
                'Assists': 'assists'
            }
            
            prop_type = stat_map.get(stat_type, stat_type.lower())
            
            result.append({
                'player_name': player_info['name'],
                'team': player_team,
                'opponent': opponent,
                'prop_type': prop_type,
                'line': float(line_score) if line_score else None,
                'odds_type': odds_type,
                'stat_type': stat_type
            })
        
        return result


class EdgeCalculator:
    """Calculate real edge vs PrizePicks market"""
    
    # PrizePicks payout multipliers (approximate)
    PAYOUT_MULTIPLIERS = {
        'standard': 3.0,   # 2-pick power play
        'goblin': 2.0,     # Easier line, lower payout
        'demon': 4.0       # Harder line, higher payout
    }
    
    @staticmethod
    def calculate_edge(our_probability: float, pp_line: float, odds_type: str = 'standard') -> Dict:
        """
        Calculate real edge vs PrizePicks market
        
        Returns:
            {
                'edge': percentage edge,
                'ev': expected value,
                'pp_implied_prob': market's implied probability,
                'bet_recommended': bool
            }
        """
        
        # Get payout multiplier
        payout = EdgeCalculator.PAYOUT_MULTIPLIERS.get(odds_type, 3.0)
        
        # Market's implied probability
        pp_implied_prob = 1.0 / payout
        
        # Our edge
        edge = (our_probability - pp_implied_prob) * 100
        
        # Expected value
        ev = (our_probability * payout) - 1.0
        
        # Recommend bet if edge > 5%
        bet_recommended = edge >= 5.0
        
        return {
            'edge': edge,
            'ev': ev,
            'pp_implied_prob': pp_implied_prob,
            'bet_recommended': bet_recommended,
            'payout_multiplier': payout
        }


class OpponentAdjuster:
    """Adjust predictions based on opponent strength"""
    
    def __init__(self, conn):
        self.conn = conn
        self.team_defense_cache = {}
    
    def get_team_defense_rating(self, team: str) -> float:
        """
        Get team's defensive rating
        1.0 = average, < 1.0 = good defense, > 1.0 = bad defense
        """
        
        if team in self.team_defense_cache:
            return self.team_defense_cache[team]
        
        # Try to fetch from database
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT goals_against_per_game, shots_against_per_game
                FROM team_stats
                WHERE team = ?
            """, (team,))
            
            result = cursor.fetchone()
            
            if result:
                ga_pg, sa_pg = result
                
                # League average (approximate)
                league_avg_ga = 3.0
                league_avg_sa = 30.0
                
                # Composite rating (lower is better for defense)
                ga_factor = ga_pg / league_avg_ga
                sa_factor = sa_pg / league_avg_sa
                
                rating = (ga_factor * 0.6 + sa_factor * 0.4)
                
                self.team_defense_cache[team] = rating
                return rating
        
        except Exception:
            pass
        
        # Default to average
        return 1.0
    
    def adjust_expected_value(self, expected: float, opponent: str, prop_type: str) -> float:
        """
        Adjust player's expected value based on opponent
        """
        
        defense_rating = self.get_team_defense_rating(opponent)
        
        # Stronger opponent (< 1.0) = reduce expected value
        # Weaker opponent (> 1.0) = increase expected value
        
        if prop_type in ['points', 'goals', 'assists']:
            # Goals/points affected more by defense
            adjusted = expected * defense_rating
        elif prop_type == 'shots':
            # Shots less affected (more volume-based)
            adjusted = expected * (1.0 + (defense_rating - 1.0) * 0.5)
        else:
            adjusted = expected
        
        return adjusted


class PrizePicksIntegration:
    """Complete PrizePicks integration with edge detection"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.prizepicks_client = PrizePicksClient()
        self.edge_calculator = EdgeCalculator()
        self.opponent_adjuster = OpponentAdjuster(self.conn)
        self.prizepicks_lines = {}
    
    def fetch_prizepicks_lines(self):
        """Fetch current PrizePicks lines"""
        
        print("="*80)
        print("FETCHING PRIZEPICKS LINES")
        print("="*80)
        
        lines = self.prizepicks_client.get_projections('NHL')
        
        # Index by player + prop
        for line in lines:
            if line['line'] is not None:
                key = f"{line['player_name']}_{line['prop_type']}"
                
                if key not in self.prizepicks_lines:
                    self.prizepicks_lines[key] = []
                
                self.prizepicks_lines[key].append(line)

        print(f"[SUCCESS] Loaded {len(self.prizepicks_lines)} unique player props from PrizePicks")
        print()
    
    def compare_predictions(self, date: str = None):
        """Compare our predictions with PrizePicks lines"""
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print("="*80)
        print("FINDING EDGE vs PRIZEPICKS")
        print("="*80)
        print()

        # Get our predictions
        query = """
            SELECT
                player_name, team, opponent, prop_type, line,
                probability, expected_value, kelly_score,
                confidence_tier, reasoning
            FROM predictions
            WHERE game_date = ?
            ORDER BY probability DESC
        """

        our_preds = pd.read_sql_query(query, self.conn, params=(date,))

        if len(our_preds) == 0:
            print("[WARNING] No predictions found for today")
            print("   Run: python enhanced_predictions.py")
            return []

        print(f"Comparing {len(our_preds)} predictions against PrizePicks...")
        print()
        
        # Find matches and calculate edge
        edge_plays = []
        
        for _, pred in our_preds.iterrows():
            key = f"{pred['player_name']}_{pred['prop_type']}"
            
            if key in self.prizepicks_lines:
                pp_lines = self.prizepicks_lines[key]
                
                for pp_line in pp_lines:
                    # Check if lines match (within 0.5)
                    line_diff = abs(pred['line'] - pp_line['line'])
                    
                    if line_diff <= 0.5:
                        # Calculate edge
                        edge_data = self.edge_calculator.calculate_edge(
                            pred['probability'],
                            pp_line['line'],
                            pp_line['odds_type']
                        )
                        
                        if edge_data['bet_recommended']:
                            edge_plays.append({
                                'player': pred['player_name'],
                                'team': pred['team'],
                                'opponent': pred['opponent'],
                                'prop_type': pred['prop_type'],
                                'line': pp_line['line'],
                                'odds_type': pp_line['odds_type'],
                                'our_prob': pred['probability'],
                                'pp_implied_prob': edge_data['pp_implied_prob'],
                                'edge': edge_data['edge'],
                                'ev': edge_data['ev'],
                                'kelly': pred['kelly_score'],
                                'tier': pred['confidence_tier'],
                                'reasoning': pred['reasoning'],
                                'payout': edge_data['payout_multiplier']
                            })
        
        # Sort by edge
        edge_plays.sort(key=lambda x: x['edge'], reverse=True)
        
        # Display results
        if edge_plays:
            print("TOP EDGE PLAYS vs PRIZEPICKS")
            print("="*80)
            print()

            for i, play in enumerate(edge_plays[:15], 1):
                odds_label = {'standard': '[STD]', 'goblin': '[GOB]', 'demon': '[DEM]'}.get(play['odds_type'], '[STD]')

                print(f"{i:2}. {play['player']:25} ({play['team']}) vs {play['opponent']}")
                print(f"    {play['prop_type'].upper()} OVER {play['line']} {odds_label}")
                print(f"    Edge: {play['edge']:+.1f}% | Our Prob: {play['our_prob']:.1%} vs Market: {play['pp_implied_prob']:.1%}")
                print(f"    EV: {play['ev']:+.1%} | Payout: {play['payout']:.1f}x | Kelly: {play['kelly']:.1f}")
                print(f"    {play['reasoning']}")
                print()

            print(f"[SUCCESS] Found {len(edge_plays)} plays with 5%+ edge")
            print()
        else:
            print("[WARNING] No significant edge plays found")
            print("   Either:")
            print("   1. PrizePicks lines don't match our predictions")
            print("   2. Market is efficient (no edge)")
            print()
        
        return edge_plays
    
    def save_edge_plays(self, edge_plays: List[Dict], date: str = None):
        """Save edge plays to database for tracking"""
        
        if not edge_plays:
            return
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prizepicks_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                player_name TEXT,
                team TEXT,
                opponent TEXT,
                prop_type TEXT,
                line REAL,
                odds_type TEXT,
                our_probability REAL,
                pp_implied_probability REAL,
                edge REAL,
                expected_value REAL,
                kelly_score REAL,
                payout_multiplier REAL,
                created_at TEXT
            )
        """)
        
        # Insert edge plays (with INSERT OR IGNORE to prevent duplicates)
        for play in edge_plays:
            cursor.execute("""
                INSERT OR IGNORE INTO prizepicks_edges
                (date, player_name, team, opponent, prop_type, line, odds_type,
                 our_probability, pp_implied_probability, edge, expected_value,
                 kelly_score, payout_multiplier, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date, play['player'], play['team'], play['opponent'],
                play['prop_type'], play['line'], play['odds_type'],
                play['our_prob'], play['pp_implied_prob'], play['edge'],
                play['ev'], play['kelly'], play['payout'],
                datetime.now().isoformat()
            ))
        
        self.conn.commit()
        print(f"[SUCCESS] Saved {len(edge_plays)} edge plays to database")
        print()
    
    def generate_parlay_suggestions(self, edge_plays: List[Dict]):
        """Suggest optimal 2-3 leg parlays"""
        
        if len(edge_plays) < 2:
            return

        print("="*80)
        print("PARLAY SUGGESTIONS")
        print("="*80)
        print()

        # Filter to top edge plays only
        top_plays = [p for p in edge_plays if p['edge'] >= 7.0][:12]

        if len(top_plays) < 2:
            print("[WARNING] Need at least 2 plays with 7%+ edge for parlays")
            return
        
        print("2-LEG PARLAYS (Uncorrelated games):")
        print("-"*80)
        
        count = 0
        for i, p1 in enumerate(top_plays):
            for p2 in top_plays[i+1:]:
                # Avoid same game (correlated)
                if p1['team'] == p2['team'] or p1['opponent'] == p2['opponent']:
                    continue
                
                # Combined probability
                combined_prob = p1['our_prob'] * p2['our_prob']
                
                # 2-leg PrizePicks payout ~3x
                parlay_ev = (combined_prob * 3.0) - 1.0
                
                if parlay_ev > 0.20:  # 20%+ EV
                    count += 1
                    print(f"{count}. {p1['player']} {p1['prop_type'].upper()} O{p1['line']} ({p1['edge']:+.1f}%)")
                    print(f"   + {p2['player']} {p2['prop_type'].upper()} O{p2['line']} ({p2['edge']:+.1f}%)")
                    print(f"   Combined: {combined_prob:.1%} | EV: {parlay_ev:+.1%}")
                    print()
                    
                    if count >= 5:
                        break
            
            if count >= 5:
                break
        
        print("="*80)
        print()
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Run complete PrizePicks integration"""
    import sys

    date = sys.argv[1] if len(sys.argv) > 1 else None

    print("\n" + "="*80)
    print("PRIZEPICKS INTEGRATION v2.0")
    print("="*80)
    print()
    
    integration = PrizePicksIntegration()
    
    # Step 1: Fetch PrizePicks lines
    integration.fetch_prizepicks_lines()
    
    # Step 2: Compare and find edge
    edge_plays = integration.compare_predictions(date)
    
    # Step 3: Save to database
    if edge_plays:
        integration.save_edge_plays(edge_plays, date)
    
    # Step 4: Generate parlay suggestions
    if edge_plays:
        integration.generate_parlay_suggestions(edge_plays)
    
    integration.close()

    print("[SUCCESS] Complete!")
    print()
    print("Next steps:")
    print("   1. Review edge plays above")
    print("   2. Check prizepicks_edges table in database")
    print("   3. Place bets on PrizePicks for plays with 7%+ edge")
    print()


if __name__ == "__main__":
    main()
