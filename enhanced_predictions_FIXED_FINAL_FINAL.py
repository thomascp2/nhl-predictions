"""
Enhanced NHL Predictions - FIXED FOR 2025-26
No rolling stats, uses season averages only
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats as scipy_stats

DB_PATH = "database/nhl_predictions.db"

class EnhancedPredictionEngine:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.predictions = []
    
    def get_player_features(self, player_name, team, opponent, is_home, game_ou_total=None):
        """Get player features from 2025-26 season data"""

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

        # Calculate game total factor (scoring environment)
        # O/U 6.0 = neutral (1.0x multiplier)
        # O/U 7.0+ = high scoring (1.15x multiplier)
        # O/U 5.5 = low scoring (0.85x multiplier)
        if game_ou_total:
            if game_ou_total >= 7.0:
                game_total_factor = 1.15  # High scoring game
            elif game_ou_total >= 6.5:
                game_total_factor = 1.08
            elif game_ou_total >= 6.0:
                game_total_factor = 1.0   # Neutral
            elif game_ou_total >= 5.5:
                game_total_factor = 0.92
            else:
                game_total_factor = 0.85  # Low scoring game
        else:
            game_total_factor = 1.0  # No data, assume neutral

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
            'game_total_factor': game_total_factor,
            'game_ou_total': game_ou_total if game_ou_total else 6.0,
            'expected_points': ppg_recent * home_away_factor * game_total_factor,
            'expected_shots': sog_recent * home_away_factor * game_total_factor,
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

        predictions = []

        for _, game in games_df.iterrows():
            away = game['away_team']
            home = game['home_team']
            game_ou = game['game_ou_total'] if pd.notna(game['game_ou_total']) else None

            # Display game O/U for transparency
            if game_ou:
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
                    features = self.get_player_features(player_name, team, opponent, is_home, game_ou)
                    
                    if features is None:
                        continue
                    
                    shot_pred = self.predict_shots(features)
                    predictions.append({
                        'player': player_name,
                        'team': team,
                        'opponent': opponent,
                        'home_away': 'HOME' if is_home else 'AWAY',
                        'prop': f"SOG OVER {shot_pred['line']}",
                        'probability': shot_pred['probability'],
                        'expected': shot_pred['expected'],
                        'confidence': (shot_pred['probability'] - 0.5) * 100,
                        'reasoning': f"{features['sog_season']:.1f} SOG/G"
                    })

                    point_pred = self.predict_points(features)
                    predictions.append({
                        'player': player_name,
                        'team': team,
                        'opponent': opponent,
                        'home_away': 'HOME' if is_home else 'AWAY',
                        'prop': f"Points OVER {point_pred['line']}",
                        'probability': point_pred['probability'],
                        'expected': point_pred['expected'],
                        'confidence': (point_pred['probability'] - 0.5) * 100,
                        'reasoning': f"{features['ppg_season']:.2f} PPG"
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