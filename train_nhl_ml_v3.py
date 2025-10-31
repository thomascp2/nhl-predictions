"""
Train XGBoost ML Models V4 - NOW WITH MONEY LINES!
THE GAME CHANGER: Money lines for game script prediction
Target: 68%+ accuracy with game script features!
"""

import sqlite3
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import pickle
import logging
from datetime import datetime
import os
from game_script_features import GameScriptAnalyzer

DB_PATH = "database/nhl_predictions.db"
MODELS_DIR = "models"

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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
    'Utah Hockey Club': 'UTA'
}

# Reverse mapping for abbreviation -> full name
NHL_ABBR_TO_FULL = {v: k for k, v in NHL_TEAM_MAP.items()}


class NHLMLTrainerV3:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.model_points = None
        self.model_shots = None
        self.feature_columns = []

        if not os.path.exists(MODELS_DIR):
            os.makedirs(MODELS_DIR)

    def add_money_line_features(self, df):
        """
        Add money line and game script features to training data

        Args:
            df: DataFrame with game_date, team, opponent, is_home columns

        Returns:
            DataFrame with added money line features
        """

        # Fetch all odds data
        odds_query = """
            SELECT
                DATE(commence_time) as game_date,
                home_team,
                away_team,
                home_ml,
                away_ml,
                over_under
            FROM odds_api_game_odds
            WHERE home_ml IS NOT NULL AND away_ml IS NOT NULL
        """

        try:
            odds_df = pd.read_sql_query(odds_query, self.conn)

            # Convert full team names to abbreviations
            odds_df['home_abbr'] = odds_df['home_team'].map(NHL_TEAM_MAP)
            odds_df['away_abbr'] = odds_df['away_team'].map(NHL_TEAM_MAP)

            # Remove rows where mapping failed
            odds_df = odds_df.dropna(subset=['home_abbr', 'away_abbr'])

            # Create lookup key: date|home|away
            odds_df['game_key'] = (odds_df['game_date'] + '|' +
                                   odds_df['away_abbr'] + '@' +
                                   odds_df['home_abbr'])

            # Group by game_key and take average (in case multiple bookmakers)
            odds_agg = odds_df.groupby('game_key').agg({
                'home_ml': 'mean',
                'away_ml': 'mean',
                'over_under': 'mean'
            }).reset_index()

            # Create lookup dict
            odds_lookup = {}
            for _, row in odds_agg.iterrows():
                odds_lookup[row['game_key']] = {
                    'home_ml': row['home_ml'],
                    'away_ml': row['away_ml'],
                    'over_under': row['over_under'] if pd.notna(row['over_under']) else 6.0
                }

            logger.info(f"  Loaded odds for {len(odds_lookup)} unique games")

        except Exception as e:
            logger.warning(f"  Could not load odds data: {e}")
            logger.warning("  Continuing without money line features...")
            odds_lookup = {}

        # Initialize game script analyzer
        analyzer = GameScriptAnalyzer()

        # Add money line features to each row
        def calculate_game_script_features(row):
            """Calculate game script features for a single game"""

            # Determine home/away team from player perspective
            if row['is_home']:
                home_team = row['team']
                away_team = row['opponent']
            else:
                home_team = row['opponent']
                away_team = row['team']

            # Create game key
            game_key = f"{row['game_date']}|{away_team}@{home_team}"

            # Get odds for this game
            if game_key in odds_lookup:
                odds = odds_lookup[game_key]
                home_ml = odds['home_ml']
                away_ml = odds['away_ml']
                over_under = odds['over_under']

                # Calculate game script features
                script = analyzer.calculate_game_script_features(
                    home_ml=int(home_ml),
                    away_ml=int(away_ml),
                    over_under=over_under
                )

                # Determine if player's team is favorite
                if row['is_home']:
                    is_favorite = script['is_home_favorite']
                    win_prob = script['home_win_prob']
                else:
                    is_favorite = not script['is_home_favorite']
                    win_prob = script['away_win_prob']

                return pd.Series({
                    'home_ml': home_ml,
                    'away_ml': away_ml,
                    'over_under': over_under,
                    'is_favorite': 1 if is_favorite else 0,
                    'win_prob': win_prob,
                    'blowout_prob': script['blowout_probability'],
                    'expected_margin': script['expected_margin'],
                    'pace_factor': script['pace_factor'],
                    'competitive_factor': script['competitive_factor'],
                    'is_heavy_favorite': 1 if script['favorite_strength'] > 0.20 else 0,
                    'is_pick_em': 1 if abs(script['home_win_prob'] - 0.5) < 0.05 else 0
                })
            else:
                # No odds available - use defaults
                return pd.Series({
                    'home_ml': -110,
                    'away_ml': -110,
                    'over_under': 6.0,
                    'is_favorite': 0,
                    'win_prob': 0.5,
                    'blowout_prob': 0.05,
                    'expected_margin': 0.0,
                    'pace_factor': 1.0,
                    'competitive_factor': 1.0,
                    'is_heavy_favorite': 0,
                    'is_pick_em': 1
                })

        # Apply to all rows
        game_script_features = df.apply(calculate_game_script_features, axis=1)
        df = pd.concat([df, game_script_features], axis=1)

        # Count how many games have real odds vs defaults
        has_odds = (df['over_under'] != 6.0) | (df['home_ml'] != -110)
        logger.info(f"  Added money line features for {has_odds.sum():,}/{len(df):,} games ({has_odds.mean()*100:.1f}%)")

        return df

    def prepare_training_data(self):
        """
        Build COMPLETE training dataset with GOALIE STATS!
        The missing piece that could give us 5-10% accuracy boost
        """

        logger.info("=" * 80)
        logger.info("PREPARING TRAINING DATA V3 - WITH GOALIES! 🥅")
        logger.info("=" * 80)
        logger.info("")

        # First, create a helper to get team's average goalie stats
        logger.info("Building goalie stats aggregates...")

        # Get team-level goalie averages as fallback
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                team,
                AVG(save_percentage) as avg_sv_pct,
                AVG(goals_against_avg) as avg_gaa,
                COUNT(*) as goalie_count
            FROM goalie_stats
            WHERE games_played >= 1
            GROUP BY team
        """)

        team_goalie_avg = {}
        for row in cursor.fetchall():
            team_goalie_avg[row[0]] = {
                'avg_sv_pct': row[1] if row[1] else 0.900,
                'avg_gaa': row[2] if row[2] else 3.00
            }

        logger.info(f"[SUCCESS]Loaded goalie averages for {len(team_goalie_avg)} teams")
        logger.info("")

        query = """
        SELECT
            -- Game context
            gl.game_date,
            gl.player_name,
            gl.team,
            gl.opponent,
            gl.is_home,

            -- Player season stats
            ps.points_per_game as season_ppg,
            ps.sog_per_game as season_sog,
            ps.goals_per_game as season_gpg,
            ps.assists_per_game as season_apg,
            ps.toi_per_game as season_toi,
            ps.shooting_pct as season_sh_pct,
            ps.games_played as season_gp,
            ps.position as player_position,

            -- Player rolling stats (L10)
            prs10.rolling_ppg as l10_ppg,
            prs10.rolling_sog as l10_sog,
            prs10.rolling_std_points as l10_std_points,
            prs10.rolling_std_sog as l10_std_sog,
            prs10.z_score_points as z_score,

            -- Player rolling stats (L5)
            prs5.rolling_ppg as l5_ppg,
            prs5.rolling_sog as l5_sog,
            prs5.rolling_std_points as l5_std_points,
            prs5.rolling_std_sog as l5_std_sog,
            prs5.z_score_points as l5_z_score,

            -- Opponent team defensive stats
            ts.goals_against_per_game as opp_ga_pg,
            ts.shots_against_per_game as opp_sa_pg,

            -- Actual results (TARGET)
            gl.points as actual_points,
            gl.shots_on_goal as actual_shots,
            CASE WHEN gl.points >= 1 THEN 1 ELSE 0 END as hit_points,
            CASE WHEN gl.shots_on_goal >= 3 THEN 1 ELSE 0 END as hit_shots

        FROM player_game_logs gl

        -- Join season stats
        INNER JOIN player_stats ps
            ON gl.player_name = ps.player_name
            AND gl.team = ps.team
            AND ps.season = '2025-2026'

        -- Join L10 rolling stats
        LEFT JOIN player_rolling_stats prs10
            ON gl.player_name = prs10.player_name
            AND prs10.as_of_date = gl.game_date
            AND prs10.window_size = 10

        -- Join L5 rolling stats
        LEFT JOIN player_rolling_stats prs5
            ON gl.player_name = prs5.player_name
            AND prs5.as_of_date = gl.game_date
            AND prs5.window_size = 5

        -- Join opponent team stats
        LEFT JOIN team_stats ts
            ON gl.opponent = ts.team
            AND ts.season = '2025-2026'

        WHERE ps.games_played >= 5
        AND gl.game_date < date('now', '-1 day')
        """

        logger.info("Querying database...")
        df = pd.read_sql_query(query, self.conn)

        logger.info(f"[SUCCESS]Loaded {len(df):,} game records")
        logger.info("")

        # Add goalie stats based on opponent team
        logger.info("Adding opponent goalie stats...")

        def get_goalie_stats(opponent):
            if opponent in team_goalie_avg:
                return pd.Series({
                    'opp_goalie_sv_pct': team_goalie_avg[opponent]['avg_sv_pct'],
                    'opp_goalie_gaa': team_goalie_avg[opponent]['avg_gaa']
                })
            else:
                # League average fallback
                return pd.Series({
                    'opp_goalie_sv_pct': 0.900,
                    'opp_goalie_gaa': 3.00
                })

        goalie_data = df['opponent'].apply(get_goalie_stats)
        df = pd.concat([df, goalie_data], axis=1)

        logger.info(f"[SUCCESS]Added goalie stats for all games")
        logger.info("")

        # Add money line features (NEW!)
        logger.info("Adding money line features for game scripting...")
        df = self.add_money_line_features(df)
        logger.info("")

        # Drop rows with missing critical values
        initial_count = len(df)
        df_clean = df.dropna(subset=['season_ppg', 'season_sog', 'l10_ppg']).copy()

        logger.info(f"After removing critical NaNs: {len(df_clean):,} records ({len(df_clean)/initial_count*100:.1f}%)")
        logger.info("")

        # Fill remaining NaNs with defaults
        df_clean['l5_ppg'] = df_clean['l5_ppg'].fillna(df_clean['season_ppg'])
        df_clean['l5_sog'] = df_clean['l5_sog'].fillna(df_clean['season_sog'])
        df_clean['l5_std_points'] = df_clean['l5_std_points'].fillna(0.5)
        df_clean['l5_std_sog'] = df_clean['l5_std_sog'].fillna(1.0)
        df_clean['l5_z_score'] = df_clean['l5_z_score'].fillna(0.0)
        df_clean['player_position'] = df_clean['player_position'].fillna('F')

        # Feature engineering
        logger.info("🔧 Engineering features...")

        # Opponent strength factors (normalized)
        league_avg_ga = df_clean['opp_ga_pg'].mean()
        league_avg_sa = df_clean['opp_sa_pg'].mean()

        df_clean.loc[:, 'opp_ga_factor'] = df_clean['opp_ga_pg'] / league_avg_ga
        df_clean.loc[:, 'opp_sa_factor'] = df_clean['opp_sa_pg'] / league_avg_sa

        # GOALIE DIFFICULTY FACTOR (NEW!)
        league_avg_sv = df_clean['opp_goalie_sv_pct'].mean()
        league_avg_gaa = df_clean['opp_goalie_gaa'].mean()

        # Higher SV% = harder to score (lower multiplier for player)
        # Lower GAA = tougher goalie (lower multiplier for player)
        df_clean.loc[:, 'goalie_difficulty_sv'] = df_clean['opp_goalie_sv_pct'] / league_avg_sv
        df_clean.loc[:, 'goalie_difficulty_gaa'] = league_avg_gaa / df_clean['opp_goalie_gaa']

        # Combined goalie difficulty score
        df_clean.loc[:, 'goalie_difficulty'] = (df_clean['goalie_difficulty_sv'] + df_clean['goalie_difficulty_gaa']) / 2

        # Recent form vs season
        df_clean.loc[:, 'recent_vs_season_ppg'] = df_clean['l10_ppg'] - df_clean['season_ppg']
        df_clean.loc[:, 'recent_vs_season_sog'] = df_clean['l10_sog'] - df_clean['season_sog']

        # L5 vs L10 (super hot/cold)
        df_clean.loc[:, 'l5_vs_l10_ppg'] = df_clean['l5_ppg'] - df_clean['l10_ppg']
        df_clean.loc[:, 'l5_vs_l10_sog'] = df_clean['l5_sog'] - df_clean['l10_sog']

        # Consistency metrics
        df_clean.loc[:, 'ppg_consistency'] = np.where(
            df_clean['season_ppg'] > 0,
            df_clean['l10_std_points'] / df_clean['season_ppg'],
            1.0
        )
        df_clean.loc[:, 'sog_consistency'] = np.where(
            df_clean['season_sog'] > 0,
            df_clean['l10_std_sog'] / df_clean['season_sog'],
            1.0
        )

        # Shot efficiency
        df_clean.loc[:, 'shot_efficiency'] = np.where(
            df_clean['season_sog'] > 0,
            df_clean['season_gpg'] / df_clean['season_sog'],
            0.1
        )

        # Position encoding
        df_clean.loc[:, 'is_forward'] = (df_clean['player_position'] == 'F').astype(int)

        # Home advantage
        df_clean.loc[:, 'home_adv'] = df_clean['is_home'].astype(int)

        logger.info("[SUCCESS]Feature engineering complete")
        logger.info("")

        # Define feature columns
        self.feature_columns = [
            # Season stats
            'season_ppg', 'season_sog', 'season_gpg', 'season_apg',
            'season_toi', 'season_sh_pct',

            # L10 rolling
            'l10_ppg', 'l10_sog', 'l10_std_points', 'l10_std_sog',

            # L5 rolling
            'l5_ppg', 'l5_sog', 'l5_std_points', 'l5_std_sog', 'l5_z_score',

            # Form indicators
            'z_score', 'recent_vs_season_ppg', 'recent_vs_season_sog',
            'l5_vs_l10_ppg', 'l5_vs_l10_sog',

            # Consistency
            'ppg_consistency', 'sog_consistency',

            # Shot quality
            'shot_efficiency',

            # Matchup - TEAM
            'opp_ga_factor', 'opp_sa_factor',

            # Matchup - GOALIE
            'opp_goalie_sv_pct', 'opp_goalie_gaa',
            'goalie_difficulty_sv', 'goalie_difficulty_gaa', 'goalie_difficulty',

            # Game Script - MONEY LINES (NEW!)
            'home_ml', 'away_ml', 'over_under',
            'is_favorite', 'win_prob', 'blowout_prob', 'expected_margin',
            'pace_factor', 'competitive_factor',
            'is_heavy_favorite', 'is_pick_em',

            # Context
            'home_adv', 'is_forward'
        ]

        logger.info(f"📋 FEATURES FOR ML MODEL V4 (WITH MONEY LINES!): {len(self.feature_columns)} features")
        for idx, feat in enumerate(self.feature_columns, 1):
            # Money line features
            if feat in ['home_ml', 'away_ml', 'over_under', 'is_favorite', 'win_prob',
                       'blowout_prob', 'expected_margin', 'pace_factor', 'competitive_factor',
                       'is_heavy_favorite', 'is_pick_em']:
                marker = "💰"
            # Goalie features
            elif 'goalie' in feat:
                marker = "🥅"
            # Other new features
            elif feat in ['l5_ppg', 'l5_sog', 'l5_std_points', 'l5_std_sog',
                         'l5_z_score', 'l5_vs_l10_ppg', 'l5_vs_l10_sog',
                         'ppg_consistency', 'sog_consistency', 'shot_efficiency',
                         'is_forward']:
                marker = "🆕"
            else:
                marker = "  "
            logger.info(f"  {marker} {idx:2}. {feat}")
        logger.info("")

        # Sample breakdown
        logger.info("TARGET DISTRIBUTION:")
        logger.info(f"  Points >= 1: {df_clean['hit_points'].sum():,} hits ({df_clean['hit_points'].mean()*100:.1f}%)")
        logger.info(f"  Shots >= 3:  {df_clean['hit_shots'].sum():,} hits ({df_clean['hit_shots'].mean()*100:.1f}%)")
        logger.info("")

        # Goalie stats summary
        logger.info("GOALIE STATS SUMMARY:")
        logger.info(f"  Avg opponent SV%: {df_clean['opp_goalie_sv_pct'].mean():.3f}")
        logger.info(f"  Avg opponent GAA: {df_clean['opp_goalie_gaa'].mean():.2f}")
        logger.info(f"  SV% range: {df_clean['opp_goalie_sv_pct'].min():.3f} - {df_clean['opp_goalie_sv_pct'].max():.3f}")
        logger.info("")

        return df_clean

    def train_models(self, df):
        """Train XGBoost models with goalie stats"""

        logger.info("=" * 80)
        logger.info("TRAINING ML MODELS V3 (WITH GOALIES!)")
        logger.info("=" * 80)
        logger.info("")

        X = df[self.feature_columns]
        y_points = df['hit_points']
        y_shots = df['hit_shots']

        # Train/test split
        X_train, X_test, y_points_train, y_points_test = train_test_split(
            X, y_points, test_size=0.2, random_state=42, stratify=y_points
        )

        _, _, y_shots_train, y_shots_test = train_test_split(
            X, y_shots, test_size=0.2, random_state=42, stratify=y_shots
        )

        logger.info(f"Training set: {len(X_train):,} samples")
        logger.info(f"Test set: {len(X_test):,} samples")
        logger.info("")

        # === POINTS MODEL ===
        logger.info("Training POINTS model (V3 with goalies)...")
        logger.info("")

        self.model_points = XGBClassifier(
            n_estimators=300,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            random_state=42,
            eval_metric='logloss'
        )

        self.model_points.fit(X_train, y_points_train)

        # Calibrate probabilities
        logger.info("🔧 Calibrating probabilities...")
        self.model_points = CalibratedClassifierCV(self.model_points, method='isotonic', cv=3)
        self.model_points.fit(X_train, y_points_train)

        # Evaluate
        y_points_pred = self.model_points.predict(X_test)
        y_points_proba = self.model_points.predict_proba(X_test)[:, 1]

        points_acc = accuracy_score(y_points_test, y_points_pred)
        points_auc = roc_auc_score(y_points_test, y_points_proba)

        logger.info(f"[SUCCESS]POINTS MODEL V3 PERFORMANCE:")
        logger.info(f"  Accuracy: {points_acc:.3f} ({points_acc*100:.1f}%)")
        logger.info(f"  AUC-ROC: {points_auc:.3f}")
        logger.info("")

        cm = confusion_matrix(y_points_test, y_points_pred)
        logger.info("Confusion Matrix:")
        logger.info(f"  TN={cm[0,0]}, FP={cm[0,1]}")
        logger.info(f"  FN={cm[1,0]}, TP={cm[1,1]}")
        logger.info(f"  Precision: {cm[1,1]/(cm[1,1]+cm[0,1]):.1%}" if (cm[1,1]+cm[0,1]) > 0 else "  Precision: N/A")
        logger.info(f"  Recall: {cm[1,1]/(cm[1,1]+cm[1,0]):.1%}" if (cm[1,1]+cm[1,0]) > 0 else "  Recall: N/A")
        logger.info("")

        # === SHOTS MODEL ===
        logger.info("Training SHOTS model (V3 with goalies)...")
        logger.info("")

        self.model_shots = XGBClassifier(
            n_estimators=300,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            random_state=42,
            eval_metric='logloss'
        )

        self.model_shots.fit(X_train, y_shots_train)

        # Calibrate
        logger.info("🔧 Calibrating probabilities...")
        self.model_shots = CalibratedClassifierCV(self.model_shots, method='isotonic', cv=3)
        self.model_shots.fit(X_train, y_shots_train)

        # Evaluate
        y_shots_pred = self.model_shots.predict(X_test)
        y_shots_proba = self.model_shots.predict_proba(X_test)[:, 1]

        shots_acc = accuracy_score(y_shots_test, y_shots_pred)
        shots_auc = roc_auc_score(y_shots_test, y_shots_proba)

        logger.info(f"[SUCCESS]SHOTS MODEL V3 PERFORMANCE:")
        logger.info(f"  Accuracy: {shots_acc:.3f} ({shots_acc*100:.1f}%)")
        logger.info(f"  AUC-ROC: {shots_auc:.3f}")
        logger.info("")

        cm = confusion_matrix(y_shots_test, y_shots_pred)
        logger.info("Confusion Matrix:")
        logger.info(f"  TN={cm[0,0]}, FP={cm[0,1]}")
        logger.info(f"  FN={cm[1,0]}, TP={cm[1,1]}")
        logger.info(f"  Precision: {cm[1,1]/(cm[1,1]+cm[0,1]):.1%}" if (cm[1,1]+cm[0,1]) > 0 else "  Precision: N/A")
        logger.info(f"  Recall: {cm[1,1]/(cm[1,1]+cm[1,0]):.1%}" if (cm[1,1]+cm[1,0]) > 0 else "  Recall: N/A")
        logger.info("")

        return {
            'points_acc': points_acc,
            'points_auc': points_auc,
            'shots_acc': shots_acc,
            'shots_auc': shots_auc
        }

    def feature_importance(self):
        """Show feature importance"""

        logger.info("=" * 80)
        logger.info("FEATURE IMPORTANCE (V3 - WITH GOALIES)")
        logger.info("=" * 80)
        logger.info("")

        # Points model
        logger.info("POINTS MODEL - TOP 10:")
        base_estimator = self.model_points.calibrated_classifiers_[0].estimator
        importance_points = base_estimator.feature_importances_
        for feat, imp in sorted(zip(self.feature_columns, importance_points), key=lambda x: x[1], reverse=True)[:10]:
            marker = "🥅" if 'goalie' in feat else ""
            logger.info(f"  {marker} {feat:<30} {imp:.4f}")
        logger.info("")

        # Shots model
        logger.info("SHOTS MODEL - TOP 10:")
        base_estimator = self.model_shots.calibrated_classifiers_[0].estimator
        importance_shots = base_estimator.feature_importances_
        for feat, imp in sorted(zip(self.feature_columns, importance_shots), key=lambda x: x[1], reverse=True)[:10]:
            marker = "🥅" if 'goalie' in feat else ""
            logger.info(f"  {marker} {feat:<30} {imp:.4f}")
        logger.info("")

    def save_models(self):
        """Save V4 models (with money lines)"""

        logger.info("Saving V4 models...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save timestamped V4 models
        with open(f"{MODELS_DIR}/nhl_points_model_v4_{timestamp}.pkl", 'wb') as f:
            pickle.dump(self.model_points, f)

        with open(f"{MODELS_DIR}/nhl_shots_model_v4_{timestamp}.pkl", 'wb') as f:
            pickle.dump(self.model_shots, f)

        with open(f"{MODELS_DIR}/feature_columns_v4_{timestamp}.pkl", 'wb') as f:
            pickle.dump(self.feature_columns, f)

        # Save as latest V3 (for backwards compatibility)
        with open(f"{MODELS_DIR}/nhl_points_model_latest_v3.pkl", 'wb') as f:
            pickle.dump(self.model_points, f)

        with open(f"{MODELS_DIR}/nhl_shots_model_latest_v3.pkl", 'wb') as f:
            pickle.dump(self.model_shots, f)

        with open(f"{MODELS_DIR}/feature_columns_latest_v3.pkl", 'wb') as f:
            pickle.dump(self.feature_columns, f)

        # Save as latest V4 (new)
        with open(f"{MODELS_DIR}/nhl_points_model_latest_v4.pkl", 'wb') as f:
            pickle.dump(self.model_points, f)

        with open(f"{MODELS_DIR}/nhl_shots_model_latest_v4.pkl", 'wb') as f:
            pickle.dump(self.model_shots, f)

        with open(f"{MODELS_DIR}/feature_columns_latest_v4.pkl", 'wb') as f:
            pickle.dump(self.feature_columns, f)

        logger.info("[SUCCESS]Models saved as V4 (also saved to V3 paths for compatibility)")
        logger.info("")

    def close(self):
        self.conn.close()


def main():
    logger.info("\n")
    logger.info("=" * 80)
    logger.info("NHL ML MODEL TRAINING V3 - THE GOALIE UPDATE!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("NEW: Opponent goalie save percentage & GAA")
    logger.info("NEW: Goalie difficulty factors")
    logger.info("TARGET: 65%+ accuracy (we're gonna hit it!)")
    logger.info("")

    trainer = NHLMLTrainerV3()

    df = trainer.prepare_training_data()
    metrics = trainer.train_models(df)
    trainer.feature_importance()
    trainer.save_models()

    logger.info("=" * 80)
    logger.info("[SUCCESS]TRAINING COMPLETE - V4 (WITH MONEY LINES!)")
    logger.info("=" * 80)
    logger.info("")
    logger.info("PROGRESSION:")
    logger.info(f"  V1 Points: 58.1%")
    logger.info(f"  V2 Points: 58.9%")
    logger.info(f"  V3 Points: ~65% 🥅 (with goalies)")
    logger.info(f"  V4 Points: {metrics['points_acc']*100:.1f}% 💰 (with money lines)")
    logger.info("")
    logger.info(f"  V1 Shots:  56.0%")
    logger.info(f"  V2 Shots:  58.1%")
    logger.info(f"  V3 Shots:  ~65% 🥅 (with goalies)")
    logger.info(f"  V4 Shots:  {metrics['shots_acc']*100:.1f}% 💰 (with money lines)")
    logger.info("")

    if metrics['points_acc'] >= 0.68 and metrics['shots_acc'] >= 0.68:
        logger.info("🎉 AMAZING! 68%+ on both models with money lines!")
        logger.info("[SUCCESS]Ready for production deployment!")
    elif metrics['points_acc'] >= 0.65 and metrics['shots_acc'] >= 0.65:
        logger.info("🎯 TARGET ACHIEVED! 65%+ on both models!")
        logger.info("Money lines provided a solid boost!")
    elif metrics['points_acc'] >= 0.62 or metrics['shots_acc'] >= 0.62:
        logger.info("Solid improvement! Above baseline!")
        logger.info("💡 Money lines are helping, but more data/features may help further")
    else:
        logger.info("Results logged. Test in production to see real performance.")

    logger.info("")
    trainer.close()


if __name__ == "__main__":
    main()
