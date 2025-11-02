-- ============================================================================
-- ADAPTIVE LEARNING SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- This schema extends the existing nhl_predictions.db with tables for
-- tracking outcomes and learning from results.
--
-- Run this once to initialize: sqlite3 database/nhl_predictions.db < adaptive_learning/schema.sql
-- ============================================================================

-- ============================================================================
-- OUTCOME TRACKING
-- ============================================================================

-- Stores actual results of predictions
CREATE TABLE IF NOT EXISTS prediction_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER,  -- Link to predictions.id (optional, for reference)

    -- Prediction details (duplicated for easy querying)
    game_date TEXT NOT NULL,
    player_name TEXT NOT NULL,
    team TEXT,
    opponent TEXT,
    prop_type TEXT NOT NULL,
    line REAL NOT NULL,

    -- Prediction
    predicted_direction TEXT NOT NULL,  -- 'OVER' or 'UNDER'
    predicted_probability REAL NOT NULL,
    confidence_tier TEXT,
    model_version TEXT,

    -- Actual outcome
    actual_stat_value REAL NOT NULL,  -- e.g., player got 2.0 points
    outcome TEXT NOT NULL,  -- 'HIT' or 'MISS'

    -- Context at prediction time
    was_home BOOLEAN,
    vegas_total REAL,  -- over/under for game
    vegas_spread REAL,  -- goal spread

    -- Metadata
    graded_at TEXT NOT NULL,
    created_at TEXT NOT NULL,

    FOREIGN KEY (prediction_id) REFERENCES predictions(id)
);

CREATE INDEX IF NOT EXISTS idx_outcomes_date ON prediction_outcomes(game_date);
CREATE INDEX IF NOT EXISTS idx_outcomes_player ON prediction_outcomes(player_name);
CREATE INDEX IF NOT EXISTS idx_outcomes_prop ON prediction_outcomes(prop_type);
CREATE INDEX IF NOT EXISTS idx_outcomes_tier ON prediction_outcomes(confidence_tier);

-- ============================================================================
-- GAME CONTEXT
-- ============================================================================

-- Stores context about games for learning patterns
CREATE TABLE IF NOT EXISTS game_context (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_date TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,

    -- Final score
    home_score INTEGER,
    away_score INTEGER,
    total_goals INTEGER,
    goal_margin INTEGER,

    -- Game flow
    pace_factor REAL,  -- shots per minute
    total_shots INTEGER,
    home_shots INTEGER,
    away_shots INTEGER,

    -- Context
    game_importance TEXT,  -- 'regular', 'rivalry', 'playoff_race'
    was_overtime BOOLEAN,
    was_shootout BOOLEAN,

    -- Metadata
    created_at TEXT NOT NULL,

    UNIQUE(game_date, home_team, away_team)
);

CREATE INDEX IF NOT EXISTS idx_game_context_date ON game_context(game_date);
CREATE INDEX IF NOT EXISTS idx_game_context_margin ON game_context(goal_margin);

-- ============================================================================
-- LEARNED ADJUSTMENTS
-- ============================================================================

-- Stores learned probability adjustments
CREATE TABLE IF NOT EXISTS learned_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Adjustment identifier
    factor_name TEXT NOT NULL,  -- e.g., 'home_ice_boost', 'blowout_penalty', 'player_mcdavid'
    prop_type TEXT,  -- NULL means applies to all prop types

    -- Adjustment value
    adjustment_type TEXT NOT NULL,  -- 'probability_boost', 'probability_penalty', 'weight_multiplier'
    adjustment_value REAL NOT NULL,  -- e.g., 0.05 = +5% probability boost

    -- Confidence metrics
    confidence REAL NOT NULL,  -- 0.0 to 1.0, based on sample size
    sample_size INTEGER NOT NULL,  -- number of observations
    accuracy_with REAL,  -- accuracy when adjustment is applied
    accuracy_without REAL,  -- accuracy when adjustment is NOT applied

    -- Statistical significance
    p_value REAL,  -- null hypothesis: adjustment has no effect
    is_significant BOOLEAN,  -- p_value < 0.05

    -- Metadata
    first_learned TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    last_validation TEXT,  -- when we last tested this adjustment

    UNIQUE(factor_name, prop_type)
);

CREATE INDEX IF NOT EXISTS idx_adjustments_factor ON learned_adjustments(factor_name);
CREATE INDEX IF NOT EXISTS idx_adjustments_prop ON learned_adjustments(prop_type);
CREATE INDEX IF NOT EXISTS idx_adjustments_significant ON learned_adjustments(is_significant);

-- ============================================================================
-- MODEL PERFORMANCE TRACKING
-- ============================================================================

-- Tracks model accuracy over time
CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Time period
    date_start TEXT NOT NULL,
    date_end TEXT NOT NULL,

    -- Model identifier
    model_name TEXT NOT NULL,  -- 'statistical', 'ml_ensemble', 'adaptive'
    prop_type TEXT NOT NULL,

    -- Performance metrics
    total_predictions INTEGER NOT NULL,
    correct_predictions INTEGER NOT NULL,
    accuracy REAL NOT NULL,

    -- By confidence tier
    t1_accuracy REAL,
    t2_accuracy REAL,
    t3_accuracy REAL,
    t4_accuracy REAL,

    -- Calibration metrics
    mean_predicted_prob REAL,  -- avg probability we predicted
    actual_hit_rate REAL,  -- actual % that hit
    calibration_error REAL,  -- |mean_predicted - actual_hit_rate|

    -- Expected value metrics
    total_ev REAL,  -- sum of all expected values
    realized_roi REAL,  -- actual ROI if we bet everything

    -- Metadata
    created_at TEXT NOT NULL,

    UNIQUE(date_start, date_end, model_name, prop_type)
);

CREATE INDEX IF NOT EXISTS idx_performance_model ON model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_performance_prop ON model_performance(prop_type);
CREATE INDEX IF NOT EXISTS idx_performance_date ON model_performance(date_start, date_end);

-- ============================================================================
-- ENSEMBLE WEIGHTS HISTORY
-- ============================================================================

-- Tracks optimal ensemble weights over time
CREATE TABLE IF NOT EXISTS ensemble_weights_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Date range this weight applies to
    effective_date TEXT NOT NULL,
    prop_type TEXT NOT NULL,

    -- Weight values
    statistical_weight REAL NOT NULL,  -- 0.0 to 1.0
    ml_weight REAL NOT NULL,  -- 0.0 to 1.0 (should sum to 1.0)

    -- Performance with these weights
    validation_accuracy REAL,
    validation_sample_size INTEGER,

    -- Metadata
    created_at TEXT NOT NULL,

    UNIQUE(effective_date, prop_type)
);

CREATE INDEX IF NOT EXISTS idx_weights_date ON ensemble_weights_history(effective_date);
CREATE INDEX IF NOT EXISTS idx_weights_prop ON ensemble_weights_history(prop_type);

-- ============================================================================
-- LEARNING LOG
-- ============================================================================

-- Audit trail of what the system learned and when
CREATE TABLE IF NOT EXISTS learning_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What happened
    event_type TEXT NOT NULL,  -- 'adjustment_created', 'adjustment_updated', 'adjustment_removed', 'weight_changed'
    description TEXT NOT NULL,

    -- Details
    factor_name TEXT,
    prop_type TEXT,
    old_value REAL,
    new_value REAL,
    reason TEXT,  -- why the change was made

    -- Impact
    expected_accuracy_change REAL,  -- predicted impact on accuracy

    -- Metadata
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_learning_log_event ON learning_log(event_type);
CREATE INDEX IF NOT EXISTS idx_learning_log_date ON learning_log(created_at);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- Overall accuracy by prop type
CREATE VIEW IF NOT EXISTS v_accuracy_by_prop AS
SELECT
    prop_type,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as correct,
    CAST(SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as accuracy
FROM prediction_outcomes
GROUP BY prop_type;

-- Accuracy by confidence tier
CREATE VIEW IF NOT EXISTS v_accuracy_by_tier AS
SELECT
    confidence_tier,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as correct,
    CAST(SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as accuracy,
    AVG(predicted_probability) as avg_predicted_prob
FROM prediction_outcomes
GROUP BY confidence_tier
ORDER BY accuracy DESC;

-- Home vs Away accuracy
CREATE VIEW IF NOT EXISTS v_home_away_split AS
SELECT
    CASE WHEN was_home = 1 THEN 'Home' ELSE 'Away' END as location,
    prop_type,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as correct,
    CAST(SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as accuracy
FROM prediction_outcomes
WHERE was_home IS NOT NULL
GROUP BY was_home, prop_type;

-- Recent learning activity
CREATE VIEW IF NOT EXISTS v_recent_learning AS
SELECT
    event_type,
    description,
    factor_name,
    prop_type,
    new_value,
    expected_accuracy_change,
    created_at
FROM learning_log
ORDER BY created_at DESC
LIMIT 50;

-- ============================================================================
-- INITIALIZATION COMPLETE
-- ============================================================================
-- Run: sqlite3 database/nhl_predictions.db < adaptive_learning/schema.sql
-- ============================================================================
