"""
Enhanced NHL Predictions - FIXED FOR 2025-26
Now with GAME SCRIPT INTEGRATION using money lines!

Features:
- Season averages (no rolling stats)
- Game total factor (scoring environment)
- Money line game scripting (blowout/competitive adjustments)
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats as scipy_stats
from game_script_features import GameScriptAnalyzer

DB_PATH = "database/nhl_predictions.db"

# NHL Team Name Mapping: Full Name -> Abbreviation
NHL_TEAM_MAP = {
    'Anaheim Ducks': 'ANA',
    'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF',
    'Calgary Flames': 'CGY',
    'Carolina Hurricanes': 'CAR',
    'Chicago Blackhawks': 'CHI',
    'Colorado Avalanche': 'COL',
    'Columbus Blue Jackets': 'CBJ',
    'Dallas Stars': 'DAL',
    'Detroit Red Wings': 'DET',
    'Edmonton Oilers': 'EDM',
    'Florida Panthers': 'FLA',
    'Los Angeles Kings': 'LAK',
    'Minnesota Wild': 'MIN',
    'Montreal Canadiens': 'MTL',
    'Nashville Predators': 'NSH',
    'New Jersey Devils': 'NJD',
    'New York Islanders': 'NYI',
    'New York Rangers': 'NYR',
    'Ottawa Senators': 'OTT',
    'Philadelphia Flyers': 'PHI',
    'Pittsburgh Penguins': 'PIT',
    'San Jose Sharks': 'SJS',
    'Seattle Kraken': 'SEA',
    'St Louis Blues': 'STL',
    'Tampa Bay Lightning': 'TBL',
    'Toronto Maple Leafs': 'TOR',
    'Vancouver Canucks': 'VAN',
    'Vegas Golden Knights': 'VGK',
    'Washington Capitals': 'WSH',
    'Winnipeg Jets': 'WPG',
    'Utah Hockey Club': 'UTA'  # Formerly Arizona Coyotes
}

class EnhancedPredictionEngine:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.predictions = []
    
    def get_player_features(self, player_name, team, opponent, is_home, game_ou_total=None,
                           home_ml=None, away_ml=None):
        """
        Get player features from 2025-26 season data with GAME SCRIPT integration

        Args:
            player_name: Player name
            team: Player's team
            opponent: Opponent team
            is_home: Is player at home?
            game_ou_total: Game over/under total
            home_ml: Home team money line (e.g., -150, +120)
            away_ml: Away team money line

        Returns:
            Dictionary with player features and expected values
        """

        base_query = """
            SELECT
                points_per_game, sog_per_game, toi_per_game,
                games_played, shooting_pct
            FROM player_stats
            WHERE player_name = ? AND team = ? AND season = '2025-2026'
        """
        base_df = pd.read_sql_query(base_query, self.conn, params=(player_name, team))

        if len(base_df) == 0:
            return None

        base = base_df.iloc[0]

        ppg_recent = base['points_per_game']
        sog_recent = base['sog_per_game']

        home_away_factor = 1.05 if is_home else 0.95

        # GAME SCRIPT INTEGRATION (NEW!)
        # Uses money lines to predict blowouts, competitive games, etc.
        game_script_factor = 1.0
        pace_factor = 1.0
        game_script_info = None

        if home_ml and away_ml:
            # Analyze game script using money lines
            analyzer = GameScriptAnalyzer()
            script = analyzer.calculate_game_script_features(
                home_ml=home_ml,
                away_ml=away_ml,
                over_under=game_ou_total if game_ou_total else 6.0
            )

            # Determine if player's team is favorite or underdog
            if is_home:
                is_favorite = script['is_home_favorite']
            else:
                is_favorite = not script['is_home_favorite']

            # Apply appropriate game script adjustment
            if is_favorite:
                game_script_factor = script['toi_adjustment_favorite']
            else:
                game_script_factor = script['toi_adjustment_underdog']

            # Use pace factor from game script (already accounts for O/U)
            pace_factor = script['pace_factor']

            game_script_info = {
                'is_favorite': is_favorite,
                'blowout_prob': script['blowout_probability'],
                'competitiveness': script['competitiveness'],
                'game_script_factor': game_script_factor
            }

        else:
            # Fallback to old O/U-only logic if no money lines
            if game_ou_total:
                if game_ou_total >= 7.0:
                    pace_factor = 1.15  # High scoring game
                elif game_ou_total >= 6.5:
                    pace_factor = 1.08
                elif game_ou_total >= 6.0:
                    pace_factor = 1.0   # Neutral
                elif game_ou_total >= 5.5:
                    pace_factor = 0.92
                else:
                    pace_factor = 0.85  # Low scoring game
            else:
                pace_factor = 1.0  # No data, assume neutral

        features = {
            'player_name': player_name,
            'team': team,
            'opponent': opponent,
            'is_home': is_home,
            'ppg_season': ppg_recent,
            'sog_season': sog_recent,
            'games_played': base['games_played'],
            'shooting_pct': base['shooting_pct'] if pd.notna(base['shooting_pct']) else 10.0,
            'home_away_factor': home_away_factor,
            'pace_factor': pace_factor,
            'game_script_factor': game_script_factor,  # NEW!
            'game_ou_total': game_ou_total if game_ou_total else 6.0,
            'home_ml': home_ml,  # NEW! Store for reference
            'away_ml': away_ml,  # NEW! Store for reference
            'game_script_info': game_script_info,  # NEW! Full game script details
            # Apply ALL factors to expected values
            'expected_points': ppg_recent * home_away_factor * pace_factor * game_script_factor,
            'expected_shots': sog_recent * home_away_factor * pace_factor * game_script_factor,
        }

        return features
    
    def predict_shots(self, features):
        """Predict shots probability"""
        expected = features['expected_shots']
        std_dev = max(expected * 0.40, 0.5)
        prob = 1 - scipy_stats.norm.cdf(2.5, expected, std_dev)
        
        return {
            'probability': prob,
            'expected': expected,
            'line': 2.5,
            'prop_type': 'shots'
        }
    
    def predict_points(self, features):
        """Predict points probability"""
        ppg = features['expected_points']
        
        if ppg >= 1.5:
            prob = 0.95
        elif ppg >= 1.0:
            prob = 0.70 + (ppg - 1.0) * 0.5
        elif ppg >= 0.5:
            prob = 0.50 + (ppg - 0.5) * 0.4
        else:
            prob = ppg * 1.0
        
        prob = min(0.95, max(0.05, prob))
        
        return {
            'probability': prob,
            'expected': ppg,
            'line': 0.5,
            'prop_type': 'points'
        }
    
    def generate_predictions(self, game_date):
        """Generate predictions for a date"""

        print("=" * 80)
        print(f"ENHANCED NHL PREDICTIONS - {game_date}")
        print("=" * 80)
        print()

        games_query = """
            SELECT away_team, home_team, game_ou_total
            FROM games
            WHERE game_date = ?
        """
        games_df = pd.read_sql_query(games_query, self.conn, params=(game_date,))

        print(f"Found {len(games_df)} games")
        print()

        # FETCH MONEY LINES FROM ODDS API (NEW!)
        odds_query = """
            SELECT home_team, away_team, home_ml, away_ml, over_under
            FROM odds_api_game_odds
            WHERE DATE(commence_time) = ?
            GROUP BY home_team, away_team
        """
        try:
            odds_df = pd.read_sql_query(odds_query, self.conn, params=(game_date,))

            # Create lookup dictionary, converting full names to abbreviations
            game_odds = {}
            for _, row in odds_df.iterrows():
                # Convert full team names to abbreviations
                home_full = row['home_team']
                away_full = row['away_team']
                home_abbr = NHL_TEAM_MAP.get(home_full, home_full)  # Fallback to full name if not found
                away_abbr = NHL_TEAM_MAP.get(away_full, away_full)

                key = f"{away_abbr}@{home_abbr}"
                game_odds[key] = {
                    'home_ml': row['home_ml'] if pd.notna(row['home_ml']) else None,
                    'away_ml': row['away_ml'] if pd.notna(row['away_ml']) else None,
                    'over_under': row['over_under'] if pd.notna(row['over_under']) else None
                }

            print(f"Loaded money lines for {len(game_odds)} games (with team name conversion)")
            print()
        except Exception as e:
            print(f"⚠️  Could not load money lines: {e}")
            print("Continuing with game total-only predictions...")
            game_odds = {}
            print()

        predictions = []

        for _, game in games_df.iterrows():
            away = game['away_team']
            home = game['home_team']
            game_ou = game['game_ou_total'] if pd.notna(game['game_ou_total']) else None

            # GET MONEY LINES FOR THIS GAME (NEW!)
            game_key = f"{away}@{home}"
            odds = game_odds.get(game_key, {})
            home_ml = odds.get('home_ml', None)
            away_ml = odds.get('away_ml', None)

            # Use O/U from odds if not in games table
            if not game_ou and odds.get('over_under'):
                game_ou = odds.get('over_under')

            # Display game info with money lines for transparency
            if home_ml and away_ml:
                print(f"{away} @ {home} - ML: {int(away_ml):+d}/{int(home_ml):+d}, O/U: {game_ou if game_ou else 'N/A'}")
            elif game_ou:
                print(f"{away} @ {home} - O/U {game_ou}")

            for team, opponent, is_home in [(away, home, False), (home, away, True)]:
                players_query = """
                    SELECT DISTINCT player_name
                    FROM player_stats
                    WHERE team = ? AND season = '2025-2026'
                    AND games_played >= 5
                    ORDER BY points_per_game DESC
                    LIMIT 10
                """
                players = pd.read_sql_query(players_query, self.conn, params=(team,))

                for player_name in players['player_name']:
                    # PASS MONEY LINES TO get_player_features (NEW!)
                    features = self.get_player_features(
                        player_name, team, opponent, is_home, game_ou,
                        home_ml=home_ml,
                        away_ml=away_ml
                    )
                    
                    if features is None:
                        continue
                    
                    shot_pred = self.predict_shots(features)

                    # Build reasoning with game script info
                    shot_reasoning = f"{features['sog_season']:.1f} SOG/G"
                    if features.get('game_script_info'):
                        gs_info = features['game_script_info']
                        if gs_info['is_favorite']:
                            shot_reasoning += f" | Favorite (GS: {features['game_script_factor']:.2f}x)"
                        else:
                            shot_reasoning += f" | Underdog (GS: {features['game_script_factor']:.2f}x)"

                    predictions.append({
                        'player': player_name,
                        'team': team,
                        'opponent': opponent,
                        'home_away': 'HOME' if is_home else 'AWAY',
                        'prop': f"SOG OVER {shot_pred['line']}",
                        'probability': shot_pred['probability'],
                        'expected': shot_pred['expected'],
                        'confidence': (shot_pred['probability'] - 0.5) * 100,
                        'reasoning': shot_reasoning
                    })

                    # QUALITY FILTER: Skip points props in low-scoring games (O/U <= 5.5)
                    # Defensive battles = limited scoring, even for elite players
                    if game_ou and game_ou <= 5.5:
                        # Skip points prop for this player
                        continue

                    point_pred = self.predict_points(features)

                    # Build reasoning with game script info
                    point_reasoning = f"{features['ppg_season']:.2f} PPG"
                    if features.get('game_script_info'):
                        gs_info = features['game_script_info']
                        if gs_info['is_favorite']:
                            point_reasoning += f" | Favorite (GS: {features['game_script_factor']:.2f}x)"
                        else:
                            point_reasoning += f" | Underdog (GS: {features['game_script_factor']:.2f}x)"

                    predictions.append({
                        'player': player_name,
                        'team': team,
                        'opponent': opponent,
                        'home_away': 'HOME' if is_home else 'AWAY',
                        'prop': f"Points OVER {point_pred['line']}",
                        'probability': point_pred['probability'],
                        'expected': point_pred['expected'],
                        'confidence': (point_pred['probability'] - 0.5) * 100,
                        'reasoning': point_reasoning
                    })
        
        predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
        
        print("=" * 80)
        print(f"TOP PREDICTIONS ({len(predictions)} total)")
        print("=" * 80)
        print()
        
        for i, pred in enumerate(predictions[:20], 1):
            print(f"{i:2}. {pred['player']:25} ({pred['team']}) {pred['home_away']} vs {pred['opponent']}")
            print(f"    {pred['prop']}")
            print(f"    Prob: {pred['probability']*100:.1f}% | Expected: {pred['expected']:.2f}")
            print(f"    {pred['reasoning']}")
            print()
        
        self.predictions = predictions
        print(f"[SUCCESS] Generated {len(predictions)} predictions")
        print()
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    engine = EnhancedPredictionEngine()
    engine.generate_predictions(datetime.now().strftime('%Y-%m-%d'))
    engine.close()