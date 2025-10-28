# 🚀 NHL Prediction System - ML Integration Roadmap
## Handoff Document for Claude Code

---

## 📍 **CURRENT STATE: Production-Ready Statistical Model**

### **What's Working:**
✅ Statistical prediction engine generating realistic forecasts
✅ Discord bot integration (`!run`, `!picks`, `!count`)
✅ Daily automated workflow via one command
✅ Database with 100 players, 2025-26 season data
✅ 26 predictions per 2-game night with proper tiers

### **Recent Wins:**
- Fixed season data issue (2024-25 → 2025-26)
- Resolved calculation bug (236 shots → 3.5 realistic)
- Cleared stale rolling stats causing overpredictions
- Cleaned database of duplicate bad predictions

### **Current Performance:**
```
Top Predictions (2025-10-27):
1. Malkin Points O0.5 - 95% prob, 1.63 expected ✅
2. Crosby Points O0.5 - 84% prob, 1.28 expected ✅
3. Pastrnak SOG O2.5 - 76% prob, 3.52 expected ✅
```

---

## 🎯 **MISSION: Upgrade to Machine Learning**

### **Primary Goals:**
1. **Replace statistical model with XGBoost ML models**
2. **Build automated data pipeline (hourly fetching)**
3. **Implement nightly retraining loop**
4. **Achieve 68%+ prediction accuracy (from ~62%)**
5. **Set foundation for multi-sport expansion (NBA, NFL)**

### **Success Metrics:**
- ML model accuracy: 68%+ (vs 62% baseline)
- ROI: 20%+ (vs 10% baseline)
- Fully automated (no manual commands)
- Self-improving (learns from mistakes)

---

## 📁 **CRITICAL FILES TO UNDERSTAND**

### **🔴 MUST PRESERVE (Production Code):**
```
enhanced_predictions_FIXED_FINAL_FINAL.py
```
- **Role:** Core prediction engine
- **Status:** ✅ Working, generates 26 predictions
- **Logic:** Statistical model (logistic for points, normal for shots)
- **DO NOT DELETE** until ML replacement proven better
```
fresh_clean_predictions.py
```
- **Role:** Generate + save predictions to database
- **Status:** ✅ Working
- **Flow:** Deletes old → Generates new → Saves → Verifies
- **Use:** Daily prediction generation
```
discord_bot.py
```
- **Role:** Discord interface
- **Status:** ✅ Working
- **Commands:** !run, !picks, !count, !edge, !dashboard, !grade
- **DO NOT BREAK** this is user-facing
```
fetch_2025_26_stats.py
```
- **Role:** Fetch player stats from NHL API
- **Status:** ✅ Working (fetches 100 players)
- **Endpoint:** `https://api.nhle.com/stats/rest/en/skater/summary`
- **Season:** `cayenneExp: 'seasonId=20252026'`
```
database/nhl_predictions.db
```
- **Role:** SQLite database (all data lives here)
- **Status:** ✅ Clean, 26 current predictions
- **BACKUP BEFORE ANY SCHEMA CHANGES**

---

## 🚧 **GAPS TO FILL (ML Prerequisites)**

### **1. Game Logs (CRITICAL - Missing)**

**Problem:** No game-by-game data for ML training

**Need:** Create `fetch_game_logs.py`
```python
# Fetch from NHL API: 
# https://api-web.nhle.com/v1/player/{playerId}/game-log/20252026/2

# Populate table:
CREATE TABLE player_game_logs (
    player_name TEXT,
    game_date TEXT,
    opponent TEXT,
    is_home BOOLEAN,
    goals INTEGER,
    assists INTEGER,
    points INTEGER,
    shots INTEGER,
    toi REAL,
    UNIQUE(player_name, game_date)
);

# Target: 2 seasons (2023-24, 2024-25) = ~15,000 games
```

**Estimated Time:** 2-3 hours (API calls + parsing)

---

### **2. Rolling Stats Calculator (CRITICAL - Cleared)**

**Problem:** Deleted rolling stats, need to rebuild

**Need:** Create `compute_rolling_stats.py`
```python
# For each player, calculate from game logs:
# - Last 5 games PPG
# - Last 10 games PPG  
# - Last 20 games PPG
# - Last 5 games SOG/G
# - Last 10 games SOG/G
# - Last 20 games SOG/G
# - Z-score (hot/cold streak)

# Populate table:
CREATE TABLE player_rolling_stats (
    player_name TEXT,
    as_of_date TEXT,
    last_5_ppg REAL,
    last_10_ppg REAL,
    last_5_sog REAL,
    last_10_sog REAL,
    z_score REAL,
    UNIQUE(player_name, as_of_date)
);
```

**Estimated Time:** 1-2 hours

---

### **3. Team Defensive Stats (MEDIUM - Empty Table)**

**Problem:** Opponent adjustments always 1.00x

**Need:** Populate `team_stats` table
```python
# Fetch team-level data:
# - Goals against per game
# - Shots against per game  
# - Defensive rating
# - Special teams

# Calculate opponent factor:
# opponent_strength = team_ga_pg / league_avg_ga
```

**Estimated Time:** 1 hour

---

### **4. Goalie Stats (MEDIUM - Empty Table)**

**Problem:** Goalie adjustments always 1.00x

**Need:** Populate `goalie_stats` table
```python
# Fetch goalie data:
# - Save percentage
# - Goals saved above average (GSAA)
# - Games played

# Calculate goalie factor:
# goalie_difficulty = goalie_sv_pct / league_avg_sv_pct
```

**Estimated Time:** 1 hour

---

## 🤖 **ML MODEL IMPLEMENTATION PLAN**

### **Phase 1: Data Preparation (Week 1)**

**Task 1.1:** Build game log fetcher
```bash
# Create: fetch_game_logs.py
# Output: ~15,000 game logs in database
# Time: 2-3 hours
```

**Task 1.2:** Calculate rolling stats
```bash
# Create: compute_rolling_stats.py
# Input: game_logs table
# Output: rolling_stats table
# Time: 1-2 hours
```

**Task 1.3:** Fetch team/goalie stats
```bash
# Create: fetch_team_stats.py
# Create: fetch_goalie_stats.py
# Time: 2 hours total
```

**Deliverable:** Database with complete features for ML

---

### **Phase 2: Model Training (Week 2)**

**Task 2.1:** Create training script
```python
# File: train_nhl_ml.py

from xgboost import XGBClassifier
import pandas as pd

class NHLMLModel:
    def __init__(self):
        self.model_points = XGBClassifier()
        self.model_shots = XGBClassifier()
    
    def prepare_training_data(self):
        """
        Query database for training features:
        - Player season stats (PPG, SOG/G)
        - Rolling averages (L5, L10, L20)
        - Opponent strength
        - Goalie difficulty
        - Home/away
        - Rest days
        
        Target:
        - hit_points (1 if points > 0.5, else 0)
        - hit_shots (1 if shots > 2.5, else 0)
        """
        
        query = """
        SELECT 
            -- Features
            ps.points_per_game,
            pr.last_10_ppg,
            ps.sog_per_game,
            pr.last_10_sog,
            g.is_home,
            ts.goals_against_per_game,
            gs.save_pct,
            
            -- Target (actual result)
            CASE WHEN gl.points > 0.5 THEN 1 ELSE 0 END as hit_points,
            CASE WHEN gl.shots > 2.5 THEN 1 ELSE 0 END as hit_shots
            
        FROM player_game_logs gl
        JOIN player_stats ps ON gl.player_name = ps.player_name
        JOIN player_rolling_stats pr ON gl.player_name = pr.player_name
        JOIN team_stats ts ON gl.opponent = ts.team
        JOIN goalie_stats gs ON gl.opponent_goalie = gs.player_name
        
        WHERE gl.game_date BETWEEN '2023-10-01' AND '2025-10-26'
        """
        
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def train(self):
        df = self.prepare_training_data()
        
        X = df[feature_columns]
        y_points = df['hit_points']
        y_shots = df['hit_shots']
        
        self.model_points.fit(X, y_points)
        self.model_shots.fit(X, y_shots)
        
        # Evaluate
        print(f"Points Accuracy: {self.model_points.score(X_test, y_test):.2%}")
        print(f"Shots Accuracy: {self.model_shots.score(X_test, y_test):.2%}")
```

**Target Accuracy:** 65-70% on test set (vs 62% baseline)

**Deliverable:** Trained models saved as `.pkl` files

---

### **Phase 3: A/B Testing (Week 3)**

**Task 3.1:** Run both models in parallel
```python
# Generate predictions using:
# 1. Statistical model (current)
# 2. ML model (new)

# Save both to database with model_type tag
# Track performance of each
```

**Task 3.2:** Compare after 50+ predictions
```python
# Metrics to compare:
# - Accuracy
# - Calibration (predicted 70% = actual 70%?)
# - ROI
# - Tier performance (T1 vs T2 vs T3)
```

**Decision Criteria:**
- If ML > Statistical by 3%+ accuracy → Full rollout
- If ML ≈ Statistical → More training data needed
- If ML < Statistical → Debug features/model

---

### **Phase 4: Automation (Week 4)**

**Task 4.1:** Create data pipeline
```python
# File: data_pipeline.py

import schedule

def hourly_check():
    """Check for new games every hour"""
    fetch_game_results()
    update_rolling_stats()

def nightly_retrain():
    """Retrain models at 2 AM"""
    grade_predictions()
    retrain_models()
    generate_tomorrows_predictions()

schedule.every().hour.at(":00").do(hourly_check)
schedule.every().day.at("02:00").do(nightly_retrain)

# Run 24/7
while True:
    schedule.run_pending()
    time.sleep(60)
```

**Deliverable:** Self-updating, self-improving system

---

## 🗂️ **FILE ORGANIZATION**

### **Recommended Structure:**
```
PrizePicks-Research-Lab/
│
├── 📂 src/                    # 🆕 Source code
│   ├── models/
│   │   ├── statistical.py     # Current model
│   │   └── ml_model.py        # New XGBoost
│   ├── data/
│   │   ├── fetchers/
│   │   │   ├── game_logs.py
│   │   │   ├── player_stats.py
│   │   │   ├── team_stats.py
│   │   │   └── goalie_stats.py
│   │   └── processors/
│   │       ├── rolling_stats.py
│   │       └── feature_engineering.py
│   ├── prediction/
│   │   ├── engine.py
│   │   └── grader.py
│   └── automation/
│       ├── pipeline.py
│       └── scheduler.py
│
├── 📂 scripts/                # 🆕 Executable scripts
│   ├── daily_run.py
│   ├── train_model.py
│   ├── fetch_data.py
│   └── grade_results.py
│
├── 📂 legacy/                 # 🆕 Archive old code
│   ├── enhanced_predictions.py
│   └── [other old files]
│
├── 📂 database/
│   └── nhl_predictions.db
│
├── 📂 models/                 # 🆕 Trained models
│   ├── nhl_points_v1.pkl
│   └── nhl_shots_v1.pkl
│
├── 📂 logs/                   # 🆕 Logs
│   └── pipeline_2025-10-27.log
│
├── 📂 docs/
│   ├── COMPLETE_SYSTEM_BOOKMARK.md
│   └── CLAUDE_CODE_HANDOFF.md
│
├── discord_bot.py             # Keep at root
└── schema.sql
```

---

## 🎯 **DEVELOPMENT PRIORITIES**

### **Week 1: Data Collection** ⭐⭐⭐ (CRITICAL)
1. ✅ Build `fetch_game_logs.py`
2. ✅ Build `compute_rolling_stats.py`
3. ✅ Populate team_stats
4. ✅ Populate goalie_stats
5. ✅ Verify data quality

**Success:** Database has 15,000+ game logs, complete features

---

### **Week 2: ML Training** ⭐⭐⭐ (CRITICAL)
1. ✅ Create `train_nhl_ml.py`
2. ✅ Train XGBoost models
3. ✅ Achieve 65%+ accuracy
4. ✅ Save trained models
5. ✅ Feature importance analysis

**Success:** Trained models outperform statistical baseline

---

### **Week 3: Integration** ⭐⭐ (HIGH)
1. ✅ Create `ml_predictions.py`
2. ✅ A/B test framework
3. ✅ Compare performance
4. ✅ Gradual rollout
5. ✅ Monitor accuracy

**Success:** ML model running in production

---

### **Week 4: Automation** ⭐⭐ (HIGH)
1. ✅ Build `data_pipeline.py`
2. ✅ Schedule hourly checks
3. ✅ Nightly retraining
4. ✅ Auto-generate predictions
5. ✅ Error handling/logging

**Success:** System runs 24/7 without intervention

---

### **Week 5-6: Optimization** ⭐ (MEDIUM)
1. ⏳ Feature engineering
2. ⏳ Hyperparameter tuning
3. ⏳ Ensemble models
4. ⏳ Calibration improvements
5. ⏳ Performance monitoring

**Success:** 70%+ accuracy, 20%+ ROI

---

## 🧪 **TESTING STRATEGY**

### **Before Deploying ML Model:**
```python
# Test 1: Smoke Test
def test_ml_predictions():
    """Can we generate predictions without errors?"""
    model = NHLMLModel()
    preds = model.predict_today()
    assert len(preds) > 0
    assert all(0 <= p['probability'] <= 1 for p in preds)

# Test 2: Sanity Check
def test_realistic_predictions():
    """Are predictions realistic?"""
    preds = model.predict_today()
    assert all(p['expected_shots'] < 10 for p in preds)
    assert all(p['expected_points'] < 5 for p in preds)

# Test 3: Backtest
def test_historical_accuracy():
    """How would model perform on past data?"""
    accuracy = backtest_model('2024-10-01', '2024-10-26')
    assert accuracy > 0.62  # Must beat baseline
```

---

## ⚠️ **CRITICAL WARNINGS**

### **🚨 DO NOT:**
1. ❌ Delete `enhanced_predictions_FIXED_FINAL_FINAL.py` (working baseline)
2. ❌ Break Discord bot (user-facing, must always work)
3. ❌ Modify database schema without backup
4. ❌ Deploy untested ML models to production
5. ❌ Remove current predictions before ML proven better

### **✅ DO:**
1. ✅ Backup database before schema changes
2. ✅ Test ML predictions on historical data first
3. ✅ Run A/B test for 50+ predictions minimum
4. ✅ Keep statistical model as fallback
5. ✅ Log everything for debugging

---

## 📊 **FEATURE ENGINEERING IDEAS**

### **Current Features (Statistical Model):**
```
- points_per_game
- sog_per_game
- is_home
```

### **Enhanced Features (ML Model):**
```python
features = {
    # Player Performance
    'ppg_season': season_avg,
    'ppg_l5': last_5_games,
    'ppg_l10': last_10_games,
    'sog_season': season_avg_shots,
    'sog_l10': last_10_shots,
    'shooting_pct': goals / shots,
    'toi_avg': time_on_ice,
    
    # Streaks
    'z_score': (recent - season) / std_dev,
    'games_with_point_streak': consecutive_games,
    
    # Matchup
    'opponent_ga_pg': opp_goals_allowed,
    'opponent_def_rank': 1-31,
    'goalie_sv_pct': starter_save_pct,
    'goalie_gsaa': goals_saved_above_avg,
    
    # Situational
    'is_home': 1 or 0,
    'rest_days': days_since_last_game,
    'back_to_back': 1 if b2b else 0,
    
    # Temporal
    'month': 10-4 (Oct-Apr),
    'day_of_week': 0-6,
    
    # Team Context  
    'team_winning_pct': team_record,
    'team_pace': shots_per_game,
}
```

---

## 🔮 **FUTURE ENHANCEMENTS (Post-ML)**

### **Advanced Features:**
- xG (expected goals)
- Corsi/Fenwick (shot attempts)
- Zone starts (offensive zone %)
- Line combinations
- Power play time
- Injury reports

### **Multi-Sport Expansion:**
```
Phase 1: NHL (Current)
Phase 2: NBA (Similar to NHL)
Phase 3: NFL (Weekly, different approach)
```

### **Portfolio Optimization:**
- Kelly Criterion for bet sizing
- Correlation analysis for parlays
- Bankroll management
- Risk-adjusted returns

---

## 📞 **KEY RESOURCES**

### **APIs:**
- NHL Stats: `https://api.nhle.com/stats/rest/`
- NHL Web: `https://api-web.nhle.com/v1/`
- PrizePicks: (Need API key or scraping)

### **Documentation:**
- SQLite Schema: `schema.sql`
- System Overview: `COMPLETE_SYSTEM_BOOKMARK.md`
- User Guide: `COMPLETE_GUIDE.md`

### **Libraries:**
```python
# Core
import pandas as pd
import numpy as np
import sqlite3

# ML
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss

# Stats
from scipy import stats
from scipy.stats import norm

# Automation
import schedule
import time

# API
import requests
```

---

## ✅ **ACCEPTANCE CRITERIA**

### **ML Model Ready for Production When:**
- [ ] Trained on 15,000+ game logs
- [ ] Accuracy > 65% on test set (beats 62% baseline)
- [ ] Predictions are realistic (no 236 shots!)
- [ ] Backtested on 100+ games
- [ ] A/B tested alongside statistical model
- [ ] Outperforms baseline by 3%+ over 50 predictions
- [ ] Automated retraining works
- [ ] Error handling and logging complete
- [ ] Documentation updated

---

## 🎯 **IMMEDIATE NEXT ACTIONS**

### **Action 1: Create Game Log Fetcher** (START HERE)
```bash
# File: src/data/fetchers/game_logs.py
# Goal: Fetch 2 seasons of game-by-game data
# API: https://api-web.nhle.com/v1/player/{playerId}/game-log/
# Output: player_game_logs table populated
```

### **Action 2: Build Rolling Stats Calculator**
```bash
# File: src/data/processors/rolling_stats.py
# Goal: Calculate L5/L10/L20 from game logs
# Input: player_game_logs table
# Output: player_rolling_stats table populated
```

### **Action 3: Train Initial ML Model**
```bash
# File: src/models/train_ml.py
# Goal: XGBoost classifier achieving 65%+ accuracy
# Input: All features from database
# Output: Saved models in models/ directory
```

---

## 💡 **TIPS FOR SUCCESS**

1. **Start with data:** ML is only as good as the data
2. **Test on historical:** Backtest before live deployment
3. **A/B test everything:** Don't trust, verify
4. **Keep it simple:** XGBoost before deep learning
5. **Automate gradually:** Manual → Semi-auto → Full auto
6. **Monitor closely:** Track accuracy daily
7. **Preserve baseline:** Statistical model is safety net

---

## 🏁 **CONCLUSION**

**Current State:** ✅ Production-ready statistical model  
**Target State:** 🚀 Self-improving ML system  
**Path:** Data → Train → Test → Deploy → Automate

**You have a solid foundation. Now let's build the ML layer on top!**

---

**Last Updated:** 2025-10-27  
**Version:** 2.0 → 3.0 Transition  
**Status:** Ready for ML Development

**Good luck! 🚀🤖**