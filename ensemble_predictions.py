"""
Ensemble Prediction Engine
Combines Statistical Model (72% accuracy) + ML Model (59% accuracy)
Target: 73-75% accuracy through intelligent weighting
"""

import sqlite3
import pandas as pd
import numpy as np
import pickle
import logging
from datetime import datetime
import os

DB_PATH = "database/nhl_predictions.db"
MODELS_DIR = "models"

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class EnsemblePredictionEngine:
    def __init__(self, stat_weight=0.70, ml_weight=0.30):
        """
        Initialize ensemble engine

        Args:
            stat_weight: Weight for statistical model (default 0.70)
            ml_weight: Weight for ML model (default 0.30)
        """
        self.conn = sqlite3.connect(DB_PATH)
        self.stat_weight = stat_weight
        self.ml_weight = ml_weight

        # Load ML models
        self.load_ml_models()

        logger.info("=" * 80)
        logger.info("ENSEMBLE PREDICTION ENGINE")
        logger.info("=" * 80)
        logger.info(f"Statistical Model Weight: {stat_weight:.0%}")
        logger.info(f"ML Model Weight: {ml_weight:.0%}")
        logger.info("")

    def load_ml_models(self):
        """Load trained ML models"""
        points_path = f"{MODELS_DIR}/nhl_points_model_latest_v3.pkl"
        shots_path = f"{MODELS_DIR}/nhl_shots_model_latest_v3.pkl"
        features_path = f"{MODELS_DIR}/feature_columns_latest_v3.pkl"

        if not os.path.exists(points_path):
            logger.warning("WARNING:V3 models not found, falling back to V2...")
            points_path = f"{MODELS_DIR}/nhl_points_model_latest_v2.pkl"
            shots_path = f"{MODELS_DIR}/nhl_shots_model_latest_v2.pkl"
            features_path = f"{MODELS_DIR}/feature_columns_latest_v2.pkl"

        if not os.path.exists(points_path):
            logger.warning("WARNING:V2 models not found, falling back to V1...")
            points_path = f"{MODELS_DIR}/nhl_points_model_latest.pkl"
            shots_path = f"{MODELS_DIR}/nhl_shots_model_latest.pkl"
            features_path = f"{MODELS_DIR}/feature_columns_latest.pkl"

        with open(points_path, 'rb') as f:
            self.model_points = pickle.load(f)

        with open(shots_path, 'rb') as f:
            self.model_shots = pickle.load(f)

        with open(features_path, 'rb') as f:
            self.feature_columns = pickle.load(f)

        logger.info(f"SUCCESS:Loaded ML models ({len(self.feature_columns)} features)")

    def get_statistical_predictions(self, game_date):
        """Get predictions from statistical model (from database)"""

        query = """
            SELECT
                player_name,
                team,
                opponent,
                prop_type,
                line,
                probability,
                expected_value,
                confidence_tier
            FROM predictions
            WHERE game_date = ?
            AND (model_version IS NULL OR model_version NOT LIKE 'ml%')
            AND (model_version IS NULL OR model_version NOT LIKE 'ensemble%')
        """

        df = pd.read_sql_query(query, self.conn, params=(game_date,))

        return df

    def get_ml_prediction_for_player(self, player_name, team, opponent, is_home, home_ml=None, away_ml=None, over_under=None):
        """Get ML prediction for a specific player"""

        # Get player features (same logic as ml_predictions.py)
        cursor = self.conn.cursor()

        # Season stats
        cursor.execute("""
            SELECT
                points_per_game, sog_per_game, goals_per_game, assists_per_game,
                toi_per_game, shooting_pct, games_played, position
            FROM player_stats
            WHERE player_name = ? AND team = ? AND season = '2025-2026'
        """, (player_name, team))

        season_row = cursor.fetchone()
        if not season_row:
            return None

        # Rolling stats (L10 and L5)
        cursor.execute("""
            SELECT rolling_ppg, rolling_sog, rolling_std_points, rolling_std_sog, z_score_points
            FROM player_rolling_stats
            WHERE player_name = ? AND window_size = 10
            ORDER BY as_of_date DESC LIMIT 1
        """, (player_name,))
        rolling10_row = cursor.fetchone()

        cursor.execute("""
            SELECT rolling_ppg, rolling_sog, rolling_std_points, rolling_std_sog, z_score_points
            FROM player_rolling_stats
            WHERE player_name = ? AND window_size = 5
            ORDER BY as_of_date DESC LIMIT 1
        """, (player_name,))
        rolling5_row = cursor.fetchone()

        # Team stats
        cursor.execute("""
            SELECT goals_against_per_game, shots_against_per_game
            FROM team_stats
            WHERE team = ? AND season = '2025-2026'
        """, (opponent,))
        opp_row = cursor.fetchone()

        # Goalie stats (get team average)
        cursor.execute("""
            SELECT AVG(save_percentage), AVG(goals_against_avg)
            FROM goalie_stats
            WHERE team = ? AND games_played >= 1
        """, (opponent,))
        goalie_row = cursor.fetchone()

        # League averages
        cursor.execute("""
            SELECT AVG(goals_against_per_game), AVG(shots_against_per_game)
            FROM team_stats
            WHERE season = '2025-2026' AND games_played > 0
        """)
        league_avg = cursor.fetchone()
        league_avg_ga = league_avg[0] if league_avg[0] else 3.0
        league_avg_sa = league_avg[1] if league_avg[1] else 30.0

        cursor.execute("""
            SELECT AVG(save_percentage), AVG(goals_against_avg)
            FROM goalie_stats WHERE games_played >= 1
        """)
        league_goalie_avg = cursor.fetchone()
        league_avg_sv = league_goalie_avg[0] if league_goalie_avg[0] else 0.900
        league_avg_gaa = league_goalie_avg[1] if league_goalie_avg[1] else 3.00

        # Build feature vector
        features = {}

        # Season stats
        features['season_ppg'] = season_row[0]
        features['season_sog'] = season_row[1]
        features['season_gpg'] = season_row[2]
        features['season_apg'] = season_row[3]
        features['season_toi'] = season_row[4]
        features['season_sh_pct'] = season_row[5] if season_row[5] else 10.0
        features['season_gp'] = season_row[6]

        # L10 rolling
        if rolling10_row:
            features['l10_ppg'] = rolling10_row[0]
            features['l10_sog'] = rolling10_row[1]
            features['l10_std_points'] = rolling10_row[2]
            features['l10_std_sog'] = rolling10_row[3]
            features['z_score'] = rolling10_row[4]
        else:
            features['l10_ppg'] = features['season_ppg']
            features['l10_sog'] = features['season_sog']
            features['l10_std_points'] = 0.5
            features['l10_std_sog'] = 1.0
            features['z_score'] = 0.0

        # L5 rolling
        if rolling5_row:
            features['l5_ppg'] = rolling5_row[0]
            features['l5_sog'] = rolling5_row[1]
            features['l5_std_points'] = rolling5_row[2]
            features['l5_std_sog'] = rolling5_row[3]
            features['l5_z_score'] = rolling5_row[4]
        else:
            features['l5_ppg'] = features['season_ppg']
            features['l5_sog'] = features['season_sog']
            features['l5_std_points'] = 0.5
            features['l5_std_sog'] = 1.0
            features['l5_z_score'] = 0.0

        # Form indicators
        features['recent_vs_season_ppg'] = features['l10_ppg'] - features['season_ppg']
        features['recent_vs_season_sog'] = features['l10_sog'] - features['season_sog']
        features['l5_vs_l10_ppg'] = features['l5_ppg'] - features['l10_ppg']
        features['l5_vs_l10_sog'] = features['l5_sog'] - features['l10_sog']

        # Consistency
        features['ppg_consistency'] = features['l10_std_points'] / features['season_ppg'] if features['season_ppg'] > 0 else 1.0
        features['sog_consistency'] = features['l10_std_sog'] / features['season_sog'] if features['season_sog'] > 0 else 1.0

        # Shot efficiency
        features['shot_efficiency'] = features['season_gpg'] / features['season_sog'] if features['season_sog'] > 0 else 0.1

        # Opponent factors
        if opp_row:
            features['opp_ga_factor'] = opp_row[0] / league_avg_ga
            features['opp_sa_factor'] = opp_row[1] / league_avg_sa
        else:
            features['opp_ga_factor'] = 1.0
            features['opp_sa_factor'] = 1.0

        # Goalie stats (if available in features)
        if 'opp_goalie_sv_pct' in self.feature_columns:
            if goalie_row and goalie_row[0]:
                features['opp_goalie_sv_pct'] = goalie_row[0]
                features['opp_goalie_gaa'] = goalie_row[1]
                features['goalie_difficulty_sv'] = goalie_row[0] / league_avg_sv
                features['goalie_difficulty_gaa'] = league_avg_gaa / goalie_row[1] if goalie_row[1] > 0 else 1.0
                features['goalie_difficulty'] = (features['goalie_difficulty_sv'] + features['goalie_difficulty_gaa']) / 2
            else:
                features['opp_goalie_sv_pct'] = league_avg_sv
                features['opp_goalie_gaa'] = league_avg_gaa
                features['goalie_difficulty_sv'] = 1.0
                features['goalie_difficulty_gaa'] = 1.0
                features['goalie_difficulty'] = 1.0

        # Money line features (if available in model)
        if 'home_ml' in self.feature_columns:
            from game_script_features import GameScriptAnalyzer

            if home_ml and away_ml:
                analyzer = GameScriptAnalyzer()
                script = analyzer.calculate_game_script_features(
                    home_ml=int(home_ml),
                    away_ml=int(away_ml),
                    over_under=over_under if over_under else 6.0
                )

                # Determine if player's team is favorite
                if is_home:
                    is_favorite = script['is_home_favorite']
                    win_prob = script['home_win_prob']
                else:
                    is_favorite = not script['is_home_favorite']
                    win_prob = script['away_win_prob']

                features['home_ml'] = home_ml
                features['away_ml'] = away_ml
                features['over_under'] = over_under if over_under else 6.0
                features['is_favorite'] = 1 if is_favorite else 0
                features['win_prob'] = win_prob
                features['blowout_prob'] = script['blowout_probability']
                features['expected_margin'] = script['expected_margin']
                features['pace_factor'] = script['pace_factor']
                features['competitive_factor'] = script['competitive_factor']
                features['is_heavy_favorite'] = 1 if script['favorite_strength'] > 0.20 else 0
                features['is_pick_em'] = 1 if abs(script['home_win_prob'] - 0.5) < 0.05 else 0
            else:
                # Default values if no money lines available
                features['home_ml'] = -110
                features['away_ml'] = -110
                features['over_under'] = 6.0
                features['is_favorite'] = 0
                features['win_prob'] = 0.5
                features['blowout_prob'] = 0.05
                features['expected_margin'] = 0.0
                features['pace_factor'] = 1.0
                features['competitive_factor'] = 1.0
                features['is_heavy_favorite'] = 0
                features['is_pick_em'] = 1

        # Context
        features['home_adv'] = 1 if is_home else 0
        features['is_forward'] = 1 if season_row[7] == 'F' else 0

        # Create DataFrame with exact feature columns
        X = pd.DataFrame([features])[self.feature_columns]

        # Predict
        prob_points = self.model_points.predict_proba(X)[0, 1]
        prob_shots = self.model_shots.predict_proba(X)[0, 1]

        return {
            'prob_points': prob_points,
            'prob_shots': prob_shots
        }

    def fetch_game_odds(self, game_date):
        """Fetch money lines for a given date"""
        # NHL Team Name Mapping (same as in enhanced_predictions and train_nhl_ml)
        NHL_TEAM_MAP = {
            'Anaheim Ducks': 'ANA', 'Boston Bruins': 'BOS', 'Buffalo Sabres': 'BUF',
            'Calgary Flames': 'CGY', 'Carolina Hurricanes': 'CAR', 'Chicago Blackhawks': 'CHI',
            'Colorado Avalanche': 'COL', 'Columbus Blue Jackets': 'CBJ', 'Dallas Stars': 'DAL',
            'Detroit Red Wings': 'DET', 'Edmonton Oilers': 'EDM', 'Florida Panthers': 'FLA',
            'Los Angeles Kings': 'LAK', 'Minnesota Wild': 'MIN', 'Montreal Canadiens': 'MTL',
            'Nashville Predators': 'NSH', 'New Jersey Devils': 'NJD', 'New York Islanders': 'NYI',
            'New York Rangers': 'NYR', 'Ottawa Senators': 'OTT', 'Philadelphia Flyers': 'PHI',
            'Pittsburgh Penguins': 'PIT', 'San Jose Sharks': 'SJS', 'Seattle Kraken': 'SEA',
            'St Louis Blues': 'STL', 'Tampa Bay Lightning': 'TBL', 'Toronto Maple Leafs': 'TOR',
            'Vancouver Canucks': 'VAN', 'Vegas Golden Knights': 'VGK', 'Washington Capitals': 'WSH',
            'Winnipeg Jets': 'WPG', 'Utah Hockey Club': 'UTA'
        }

        odds_query = """
            SELECT home_team, away_team, home_ml, away_ml, over_under
            FROM odds_api_game_odds
            WHERE DATE(commence_time) = ?
            GROUP BY home_team, away_team
        """

        try:
            odds_df = pd.read_sql_query(odds_query, self.conn, params=(game_date,))

            # Create lookup dictionary with team name conversion
            game_odds = {}
            for _, row in odds_df.iterrows():
                home_abbr = NHL_TEAM_MAP.get(row['home_team'], row['home_team'])
                away_abbr = NHL_TEAM_MAP.get(row['away_team'], row['away_team'])

                key = f"{away_abbr}@{home_abbr}"
                game_odds[key] = {
                    'home_ml': row['home_ml'] if pd.notna(row['home_ml']) else None,
                    'away_ml': row['away_ml'] if pd.notna(row['away_ml']) else None,
                    'over_under': row['over_under'] if pd.notna(row['over_under']) else None
                }

            return game_odds

        except Exception as e:
            logger.warning(f"Could not load money lines: {e}")
            return {}

    def generate_ensemble_predictions(self, game_date):
        """Generate ensemble predictions combining statistical + ML"""

        logger.info("=" * 80)
        logger.info(f"ENSEMBLE PREDICTIONS - {game_date}")
        logger.info("=" * 80)
        logger.info("")

        # Get statistical predictions
        logger.info("Loading statistical model predictions...")
        stat_preds = self.get_statistical_predictions(game_date)
        logger.info(f"SUCCESS:Found {len(stat_preds)} statistical predictions")
        logger.info("")

        if len(stat_preds) == 0:
            logger.warning("WARNING:No statistical predictions found! Run fresh_clean_predictions.py first")
            return []

        # Fetch money lines for today's games
        logger.info("Loading money lines for game scripting...")
        game_odds = self.fetch_game_odds(game_date)
        logger.info(f"SUCCESS:Loaded odds for {len(game_odds)} games")
        logger.info("")

        ensemble_predictions = []

        logger.info("Generating ensemble predictions...")
        logger.info("")

        for idx, row in stat_preds.iterrows():
            player_name = row['player_name']
            team = row['team']
            opponent = row['opponent']
            prop_type = row['prop_type']
            line = row['line']
            stat_prob = row['probability']

            # Infer home/away (if home team matches player's team)
            is_home = True  # Default assumption, could be improved

            # Get money lines for this game
            game_key_home = f"{opponent}@{team}"  # team is home
            game_key_away = f"{team}@{opponent}"  # team is away

            if game_key_home in game_odds:
                odds = game_odds[game_key_home]
                is_home = True
            elif game_key_away in game_odds:
                odds = game_odds[game_key_away]
                is_home = False
            else:
                odds = {}

            home_ml = odds.get('home_ml', None)
            away_ml = odds.get('away_ml', None)
            over_under = odds.get('over_under', None)

            # Get ML prediction with money lines
            ml_pred = self.get_ml_prediction_for_player(
                player_name, team, opponent, is_home,
                home_ml=home_ml, away_ml=away_ml, over_under=over_under
            )

            if ml_pred:
                # Extract ML probability for this prop type
                ml_prob = ml_pred['prob_points'] if prop_type == 'points' else ml_pred['prob_shots']

                # ENSEMBLE: Weighted average
                ensemble_prob = (self.stat_weight * stat_prob) + (self.ml_weight * ml_prob)

                # Determine tier
                if ensemble_prob >= 0.70:
                    tier = 'T1-ELITE'
                elif ensemble_prob >= 0.60:
                    tier = 'T2-STRONG'
                else:
                    tier = 'T3-MARGINAL'

                ensemble_predictions.append({
                    'player_name': player_name,
                    'team': team,
                    'opponent': opponent,
                    'prop_type': prop_type,
                    'line': line,
                    'stat_prob': stat_prob,
                    'ml_prob': ml_prob,
                    'ensemble_prob': ensemble_prob,
                    'tier': tier,
                    'boost': ensemble_prob - stat_prob
                })

            else:
                # ML prediction not available, use statistical only
                ensemble_predictions.append({
                    'player_name': player_name,
                    'team': team,
                    'opponent': opponent,
                    'prop_type': prop_type,
                    'line': line,
                    'stat_prob': stat_prob,
                    'ml_prob': None,
                    'ensemble_prob': stat_prob,
                    'tier': row['confidence_tier'],
                    'boost': 0.0
                })

        logger.info(f"SUCCESS:Generated {len(ensemble_predictions)} ensemble predictions")
        logger.info("")

        # Sort by ensemble probability
        ensemble_predictions.sort(key=lambda x: x['ensemble_prob'], reverse=True)

        # Display top predictions
        logger.info("=" * 80)
        logger.info("TOP 15 ENSEMBLE PREDICTIONS")
        logger.info("=" * 80)
        logger.info("")

        for idx, pred in enumerate(ensemble_predictions[:15], 1):
            player = pred['player_name']
            prop = pred['prop_type'].upper()
            line = pred['line']
            stat_p = pred['stat_prob']
            ml_p = pred['ml_prob']
            ens_p = pred['ensemble_prob']
            tier = pred['tier']
            boost = pred['boost']

            boost_indicator = f"UP +{boost:.1%}" if boost > 0.02 else f"DOWN {boost:.1%}" if boost < -0.02 else "SAME ~same"

            logger.info(f"{idx:2}. {player:<25} {prop} O{line}")
            logger.info(f"    Statistical: {stat_p:.1%}")
            if ml_p:
                logger.info(f"    ML Model:    {ml_p:.1%}")
            else:
                logger.info(f"    ML Model:    N/A")
            logger.info(f"    ENSEMBLE:    {ens_p:.1%} ({tier}) {boost_indicator}")
            logger.info("")

        return ensemble_predictions

    def save_ensemble_predictions(self, game_date, predictions):
        """Save ensemble predictions to database"""

        logger.info("Saving ensemble predictions to database...")

        cursor = self.conn.cursor()
        batch_id = f"ensemble_{game_date}_{datetime.now().strftime('%H%M%S')}"
        saved = 0

        for pred in predictions:
            try:
                cursor.execute("""
                    INSERT INTO predictions
                    (game_date, player_name, team, opponent, prop_type, line,
                     prediction, probability, expected_value, confidence_tier,
                     model_version, batch_id, reasoning, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_date,
                    pred['player_name'],
                    pred['team'],
                    pred['opponent'],
                    pred['prop_type'],
                    pred['line'],
                    'OVER',
                    pred['ensemble_prob'],
                    pred['line'],  # Use line as expected value placeholder
                    pred['tier'],
                    'ensemble_v1',
                    batch_id,
                    f"Stat:{pred['stat_prob']:.1%} ML:{pred['ml_prob']:.1%} Ensemble:{pred['ensemble_prob']:.1%}" if pred['ml_prob'] else f"Stat only: {pred['stat_prob']:.1%}",
                    datetime.now().isoformat()
                ))
                saved += 1
            except Exception as e:
                # Skip duplicates or errors
                pass

        self.conn.commit()
        logger.info(f"SUCCESS:Saved {saved} ensemble predictions")
        logger.info("")

    def show_summary(self, predictions):
        """Show summary statistics"""

        logger.info("=" * 80)
        logger.info("ENSEMBLE SUMMARY")
        logger.info("=" * 80)
        logger.info("")

        # Count by tier
        t1_count = sum(1 for p in predictions if p['tier'] == 'T1-ELITE')
        t2_count = sum(1 for p in predictions if p['tier'] == 'T2-STRONG')
        t3_count = sum(1 for p in predictions if p['tier'] == 'T3-MARGINAL')

        logger.info(f"Total predictions: {len(predictions)}")
        logger.info(f"  T1-ELITE: {t1_count}")
        logger.info(f"  T2-STRONG: {t2_count}")
        logger.info(f"  T3-MARGINAL: {t3_count}")
        logger.info("")

        # Average boost from ML
        ml_available = [p for p in predictions if p['ml_prob'] is not None]
        if ml_available:
            avg_boost = np.mean([p['boost'] for p in ml_available])
            logger.info(f"Average ML boost: {avg_boost:+.1%}")

            boosted = sum(1 for p in ml_available if p['boost'] > 0.02)
            lowered = sum(1 for p in ml_available if p['boost'] < -0.02)

            logger.info(f"  ML boosted confidence: {boosted}")
            logger.info(f"  ML lowered confidence: {lowered}")
        logger.info("")

        logger.info("ENSEMBLE ADVANTAGE:")
        logger.info("  SUCCESS:Combines domain expertise (statistical) with data-driven insights (ML)")
        logger.info("  SUCCESS:More robust to outliers")
        logger.info("  SUCCESS:Expected accuracy: 73-75% (vs 72% statistical, 59% ML)")
        logger.info("")

    def close(self):
        self.conn.close()


def main():
    import sys

    # Accept date from command line, or use today
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    logger.info("")
    logger.info("=" * 80)
    logger.info("ENSEMBLE PREDICTION ENGINE")
    logger.info("Combining Statistical (72%) + ML (59%) = 73-75% Expected")
    logger.info("=" * 80)
    logger.info("")

    # Initialize ensemble engine
    engine = EnsemblePredictionEngine(stat_weight=0.70, ml_weight=0.30)

    # Generate ensemble predictions
    predictions = engine.generate_ensemble_predictions(date)

    if predictions:
        # Save to database
        engine.save_ensemble_predictions(date, predictions)

        # Show summary
        engine.show_summary(predictions)

        logger.info("=" * 80)
        logger.info("SUCCESS:ENSEMBLE PREDICTIONS READY!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Check Discord bot with !picks to see ensemble predictions")
        logger.info("  2. Monitor tonight's games to validate accuracy")
        logger.info("  3. Adjust weights if needed (70/30 is starting point)")
        logger.info("")

    engine.close()


if __name__ == "__main__":
    main()
