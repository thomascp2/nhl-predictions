-- ============================================================================
-- NHL PREDICTION SYSTEM - ENHANCED DATABASE SCHEMA
-- Complete automation: Data collection → Predictions → Grading → Analysis
-- Version: 2.0
-- Date: October 23, 2025
-- ============================================================================

-- ============================================================================
-- GAME SCHEDULE & METADATA
-- ============================================================================
CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    game_date TEXT NOT NULL,
    game_time TEXT,
    season TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_team TEXT NOT NULL,
    venue TEXT,
    
    -- Game betting context
    game_ou_total REAL,
    spread REAL,
    
    -- Game results (populated after game)
    away_score INTEGER,
    home_score INTEGER,
    game_status TEXT DEFAULT 'scheduled', -- scheduled, in_progress, final
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(game_date, away_team, home_team)
);

CREATE INDEX IF NOT EXISTS idx_games_date ON games(game_date);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(game_status);
CREATE INDEX IF NOT EXISTS idx_games_teams ON games(away_team, home_team);

-- ============================================================================
-- GOALIE MATCHUPS (Enhanced)
-- ============================================================================
CREATE TABLE IF NOT EXISTS goalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    game_date TEXT NOT NULL,
    
    -- Team info
    away_team TEXT NOT NULL,
    home_team TEXT NOT NULL,
    
    -- Goalie assignments
    away_goalie TEXT NOT NULL,
    home_goalie TEXT NOT NULL,
    
    -- Season stats
    away_sv_pct REAL NOT NULL,
    home_sv_pct REAL NOT NULL,
    away_gaa REAL,
    home_gaa REAL,
    
    -- Recent form (last 5 games)
    away_l5_sv_pct REAL,
    home_l5_sv_pct REAL,
    
    -- Confirmation
    confirmation_status TEXT DEFAULT 'PREDICTED', -- CONFIRMED, PREDICTED, PROBABLE
    confidence_score REAL DEFAULT 0.5,
    prediction_method TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    UNIQUE(game_date, away_team, home_team)
);

CREATE INDEX IF NOT EXISTS idx_goalies_game ON goalies(game_id);
CREATE INDEX IF NOT EXISTS idx_goalies_date ON goalies(game_date);

-- ============================================================================
-- PLAYER BASE STATS (Season-level)
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    team TEXT NOT NULL,
    position TEXT,
    season TEXT NOT NULL,
    
    -- Basic counting stats
    games_played INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    shots_on_goal INTEGER DEFAULT 0,
    
    -- Per-game averages
    points_per_game REAL DEFAULT 0.0,
    sog_per_game REAL DEFAULT 0.0,
    goals_per_game REAL DEFAULT 0.0,
    assists_per_game REAL DEFAULT 0.0,
    
    -- Ice time
    toi_per_game REAL DEFAULT 0.0,
    pp_toi_per_game REAL DEFAULT 0.0,
    
    -- Advanced metrics
    xg_share REAL,
    ixg_per_game REAL,
    shooting_pct REAL,
    
    -- Statistical measures
    std_dev_points REAL,
    std_dev_sog REAL,
    
    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(player_name, team, season)
);

CREATE INDEX IF NOT EXISTS idx_player_stats_name ON player_stats(player_name);
CREATE INDEX IF NOT EXISTS idx_player_stats_team ON player_stats(team);
CREATE INDEX IF NOT EXISTS idx_player_stats_season ON player_stats(season);

-- ============================================================================
-- PLAYER GAME LOGS (Individual game performance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_game_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    game_date TEXT NOT NULL,
    player_name TEXT NOT NULL,
    team TEXT NOT NULL,
    opponent TEXT NOT NULL,
    is_home INTEGER DEFAULT 1,
    
    -- Game stats
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    shots_on_goal INTEGER DEFAULT 0,
    toi REAL DEFAULT 0.0,
    pp_toi REAL DEFAULT 0.0,
    
    -- Advanced
    ixg REAL,
    blocked_shots INTEGER DEFAULT 0,
    hits INTEGER DEFAULT 0,
    
    -- Context
    was_back_to_back INTEGER DEFAULT 0,
    rest_days INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    UNIQUE(game_id, player_name)
);

CREATE INDEX IF NOT EXISTS idx_game_logs_player ON player_game_logs(player_name);
CREATE INDEX IF NOT EXISTS idx_game_logs_date ON player_game_logs(game_date);
CREATE INDEX IF NOT EXISTS idx_game_logs_game ON player_game_logs(game_id);

-- ============================================================================
-- ROLLING STATISTICS (Pre-computed for speed)
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_rolling_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    team TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    window_size INTEGER NOT NULL, -- 5, 10, 20 games
    
    -- Rolling averages
    rolling_ppg REAL,
    rolling_sog REAL,
    rolling_toi REAL,
    
    -- Rolling standard deviations
    rolling_std_points REAL,
    rolling_std_sog REAL,
    
    -- Trends
    points_trend REAL, -- slope of linear regression
    sog_trend REAL,
    
    -- Hot/Cold indicators
    z_score_points REAL,
    z_score_sog REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(player_name, team, as_of_date, window_size)
);

CREATE INDEX IF NOT EXISTS idx_rolling_player_date ON player_rolling_stats(player_name, as_of_date);

-- ============================================================================
-- TEAM STATISTICS
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    season TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    
    -- Basic stats
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    otl INTEGER DEFAULT 0,
    
    -- Scoring
    goals_per_game REAL,
    goals_against_per_game REAL,
    
    -- Shot metrics
    shots_per_game REAL,
    shots_against_per_game REAL,
    
    -- Advanced
    corsi_for_pct REAL,
    fenwick_for_pct REAL,
    xg_per_game REAL,
    xga_per_game REAL,
    
    -- Special teams
    pp_pct REAL,
    pk_pct REAL,
    
    -- Situational
    home_record TEXT,
    away_record TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team, season, as_of_date)
);

CREATE INDEX IF NOT EXISTS idx_team_stats_team ON team_stats(team);
CREATE INDEX IF NOT EXISTS idx_team_stats_date ON team_stats(as_of_date);

-- ============================================================================
-- MATCHUP HISTORY (Head-to-head)
-- ============================================================================
CREATE TABLE IF NOT EXISTS matchup_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    opponent_team TEXT NOT NULL,
    season TEXT NOT NULL,
    
    -- Historical performance vs this opponent
    games_played INTEGER DEFAULT 0,
    avg_points REAL,
    avg_sog REAL,
    total_points INTEGER DEFAULT 0,
    total_sog INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(player_name, opponent_team, season)
);

CREATE INDEX IF NOT EXISTS idx_matchup_player ON matchup_history(player_name);
CREATE INDEX IF NOT EXISTS idx_matchup_opponent ON matchup_history(opponent_team);

-- ============================================================================
-- LINE COMBINATIONS (Linemate effects)
-- ============================================================================
CREATE TABLE IF NOT EXISTS line_combinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    season TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    
    -- Line composition
    line_number INTEGER, -- 1, 2, 3, 4
    center TEXT,
    left_wing TEXT,
    right_wing TEXT,
    
    -- Performance metrics
    games_together INTEGER DEFAULT 0,
    toi_together REAL,
    goals_for INTEGER DEFAULT 0,
    xg_for REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team, season, as_of_date, line_number)
);

CREATE INDEX IF NOT EXISTS idx_lines_team ON line_combinations(team);
CREATE INDEX IF NOT EXISTS idx_lines_player_center ON line_combinations(center);
CREATE INDEX IF NOT EXISTS idx_lines_player_lw ON line_combinations(left_wing);
CREATE INDEX IF NOT EXISTS idx_lines_player_rw ON line_combinations(right_wing);

-- ============================================================================
-- PREDICTIONS (Enhanced)
-- ============================================================================
CREATE TABLE IF NOT EXISTS predictions (
    id TEXT PRIMARY KEY,
    prediction_batch_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    
    -- Game context
    game_id TEXT NOT NULL,
    game_date TEXT NOT NULL,
    game_time TEXT,
    
    -- Player info
    player_name TEXT NOT NULL,
    team TEXT NOT NULL,
    opponent TEXT NOT NULL,
    position TEXT,
    
    -- Prop details
    prop_type TEXT NOT NULL, -- Points, SOG, etc.
    line REAL NOT NULL,
    odds_type TEXT DEFAULT 'STANDARD', -- STANDARD, DEMON, GOBLIN
    
    -- Prediction
    prediction TEXT NOT NULL, -- OVER, UNDER
    probability REAL NOT NULL,
    
    -- Statistical distributions
    expected_value REAL, -- Point estimate
    std_dev REAL, -- Standard deviation
    confidence_low REAL, -- Lower bound (5th percentile)
    confidence_high REAL, -- Upper bound (95th percentile)
    
    -- Distribution parameters (for Beta/Gaussian)
    dist_type TEXT, -- beta, gaussian, poisson
    dist_alpha REAL, -- Beta alpha or Gaussian mean
    dist_beta REAL, -- Beta beta or Gaussian std
    
    -- Scoring
    confidence_tier TEXT, -- T1-ELITE, T2-STRONG, T3-MARGINAL, SKIP
    edge_score REAL, -- Expected Value (EV)
    kelly_score REAL, -- Risk-adjusted Kelly score
    kelly_bet_pct REAL, -- Recommended bet %
    
    -- Feature contributions
    base_probability REAL, -- Before adjustments
    ml_boost REAL, -- ML adjustment
    matchup_adjustment REAL, -- Opponent-specific
    rest_adjustment REAL, -- Rest days
    linemate_adjustment REAL, -- Line combination
    
    -- Context
    goalie_opponent TEXT,
    goalie_sv_pct REAL,
    is_home INTEGER,
    rest_days INTEGER,
    is_back_to_back INTEGER,
    
    -- Reasoning
    reasoning TEXT, -- JSON array of reasoning points
    
    -- Correlation risk
    correlation_risk TEXT, -- LOW, MEDIUM, HIGH
    correlated_picks TEXT, -- JSON array of correlated player IDs
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Grading (populated after game)
    actual_result TEXT, -- HIT, MISS
    actual_stat_value REAL,
    is_correct INTEGER,
    graded_at TIMESTAMP,
    
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE INDEX IF NOT EXISTS idx_predictions_batch ON predictions(prediction_batch_id);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(game_date);
CREATE INDEX IF NOT EXISTS idx_predictions_player ON predictions(player_name);
CREATE INDEX IF NOT EXISTS idx_predictions_tier ON predictions(confidence_tier);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_version);
CREATE INDEX IF NOT EXISTS idx_predictions_ungraded ON predictions(game_date, actual_result) 
    WHERE actual_result IS NULL;

-- ============================================================================
-- PREDICTION BATCHES (Track each prediction run)
-- ============================================================================
CREATE TABLE IF NOT EXISTS prediction_batches (
    batch_id TEXT PRIMARY KEY,
    run_timestamp TIMESTAMP NOT NULL,
    model_version TEXT NOT NULL,
    
    -- Stats about this batch
    total_predictions INTEGER,
    t1_count INTEGER,
    t2_count INTEGER,
    t3_count INTEGER,
    
    avg_probability REAL,
    avg_kelly_score REAL,
    
    -- Configuration used
    config_json TEXT, -- JSON of model parameters
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODEL VERSIONS & PERFORMANCE
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_versions (
    version TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    description TEXT,
    
    -- Model parameters
    feature_weights TEXT, -- JSON
    calibration_factors TEXT, -- JSON
    
    -- Performance metrics (updated as predictions are graded)
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy REAL,
    
    -- By tier
    t1_accuracy REAL,
    t2_accuracy REAL,
    t3_accuracy REAL,
    
    -- Calibration
    calibration_error REAL,
    brier_score REAL,
    log_loss REAL,
    
    -- ROI metrics
    total_ev REAL,
    kelly_roi REAL,
    
    is_active INTEGER DEFAULT 1,
    last_updated TIMESTAMP
);

-- ============================================================================
-- CALIBRATION HISTORY (Track calibration over time)
-- ============================================================================
CREATE TABLE IF NOT EXISTS calibration_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date TEXT NOT NULL,
    model_version TEXT NOT NULL,
    
    -- Overall metrics
    total_predictions INTEGER,
    overall_accuracy REAL,
    avg_predicted_prob REAL,
    calibration_error REAL,
    
    -- By probability bucket
    bucket_50_60_actual REAL,
    bucket_50_60_predicted REAL,
    bucket_50_60_count INTEGER,
    
    bucket_60_70_actual REAL,
    bucket_60_70_predicted REAL,
    bucket_60_70_count INTEGER,
    
    bucket_70_80_actual REAL,
    bucket_70_80_predicted REAL,
    bucket_70_80_count INTEGER,
    
    bucket_80_90_actual REAL,
    bucket_80_90_predicted REAL,
    bucket_80_90_count INTEGER,
    
    -- Recommendations
    recommendations TEXT, -- JSON
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (model_version) REFERENCES model_versions(version)
);

-- ============================================================================
-- FEATURE IMPORTANCE (Track which features matter)
-- ============================================================================
CREATE TABLE IF NOT EXISTS feature_importance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_version TEXT NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    
    -- Feature weights
    feature_name TEXT NOT NULL,
    importance_score REAL NOT NULL,
    
    -- Performance when feature is included vs excluded
    with_feature_accuracy REAL,
    without_feature_accuracy REAL,
    
    UNIQUE(model_version, recorded_at, feature_name)
);

-- ============================================================================
-- DATA COLLECTION LOG (Track automated data fetches)
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_date TEXT NOT NULL,
    data_type TEXT NOT NULL, -- 'player_stats', 'goalies', 'schedule', 'odds'
    source TEXT NOT NULL, -- 'NHL_API', 'Natural_Stat_Trick', 'PrizePicks', etc.
    
    records_collected INTEGER,
    status TEXT, -- SUCCESS, PARTIAL, FAILED
    error_message TEXT,
    
    execution_time_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data_log_date ON data_collection_log(collection_date);
CREATE INDEX IF NOT EXISTS idx_data_log_type ON data_collection_log(data_type);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string', -- string, integer, float, boolean, json
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT OR IGNORE INTO system_config (key, value, value_type, description) VALUES
    ('current_season', '2024-2025', 'string', 'Current NHL season'),
    ('current_model_version', 'v2.0-beta-gaussian', 'string', 'Active prediction model'),
    ('auto_data_collection', 'true', 'boolean', 'Enable automated data collection'),
    ('prediction_time', '10:00', 'string', 'Daily prediction generation time (EST)'),
    ('grading_time', '08:00', 'string', 'Daily grading time (EST)'),
    ('min_games_played', '5', 'integer', 'Minimum games for predictions'),
    ('kelly_fraction', '0.25', 'float', 'Conservative Kelly multiplier'),
    ('confidence_level', '0.90', 'float', 'Confidence interval level'),
    ('calibration_frequency', '7', 'integer', 'Days between calibration runs');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Recent player performance with rolling stats
CREATE VIEW IF NOT EXISTS v_player_current_form AS
SELECT 
    ps.player_name,
    ps.team,
    ps.position,
    ps.games_played,
    ps.points_per_game,
    ps.sog_per_game,
    ps.toi_per_game,
    prs5.rolling_ppg as last_5_ppg,
    prs5.rolling_sog as last_5_sog,
    prs5.z_score_points,
    prs5.z_score_sog,
    ps.xg_share,
    ps.ixg_per_game
FROM player_stats ps
LEFT JOIN player_rolling_stats prs5 ON 
    ps.player_name = prs5.player_name 
    AND ps.team = prs5.team 
    AND prs5.window_size = 5
    AND prs5.as_of_date = (
        SELECT MAX(as_of_date) FROM player_rolling_stats 
        WHERE player_name = ps.player_name
    )
WHERE ps.season = (SELECT value FROM system_config WHERE key = 'current_season');

-- Today's games with goalie matchups
CREATE VIEW IF NOT EXISTS v_todays_games AS
SELECT 
    g.game_id,
    g.game_date,
    g.game_time,
    g.away_team,
    g.home_team,
    g.game_ou_total,
    g.spread,
    gl.away_goalie,
    gl.home_goalie,
    gl.away_sv_pct,
    gl.home_sv_pct,
    gl.confirmation_status
FROM games g
LEFT JOIN goalies gl ON g.game_id = gl.game_id
WHERE g.game_date = date('now')
    AND g.game_status = 'scheduled';

-- Ungraded predictions
CREATE VIEW IF NOT EXISTS v_ungraded_predictions AS
SELECT 
    p.id,
    p.game_date,
    p.player_name,
    p.team,
    p.opponent,
    p.prop_type,
    p.line,
    p.prediction,
    p.probability,
    p.confidence_tier,
    p.expected_value,
    g.game_status
FROM predictions p
JOIN games g ON p.game_id = g.game_id
WHERE p.actual_result IS NULL
    AND g.game_status = 'final'
ORDER BY p.game_date DESC, p.confidence_tier;

-- Model performance dashboard
CREATE VIEW IF NOT EXISTS v_model_performance AS
SELECT 
    mv.version,
    mv.total_predictions,
    mv.accuracy,
    mv.t1_accuracy,
    mv.t2_accuracy,
    mv.t3_accuracy,
    mv.calibration_error,
    mv.kelly_roi,
    mv.last_updated,
    COUNT(DISTINCT pb.batch_id) as prediction_runs
FROM model_versions mv
LEFT JOIN prediction_batches pb ON mv.version = pb.model_version
GROUP BY mv.version
ORDER BY mv.created_at DESC;
