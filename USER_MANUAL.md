# 🎯 NHL ML PREDICTION SYSTEM - USER MANUAL
## The Complete Playbook (aka "Cheat Codes")

---

## 📋 **TABLE OF CONTENTS**

1. [Quick Start](#quick-start)
2. [Daily Workflow](#daily-workflow)
3. [All Commands Reference](#all-commands-reference)
4. [System Architecture](#system-architecture)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)
7. [Discord Bot Commands](#discord-bot-commands)
8. [Performance Tuning](#performance-tuning)

---

## 🚀 **QUICK START**

### **Get Today's Predictions (Fastest Path)**

```bash
# Option 1: Ensemble predictions (RECOMMENDED - 73-75% accuracy)
python fresh_clean_predictions.py    # Generate statistical predictions
python ensemble_predictions.py       # Combine with ML predictions

# Option 2: Statistical only (72% accuracy, faster)
python fresh_clean_predictions.py

# Option 3: Pure ML (59% accuracy, experimental)
python ml_predictions.py
```

### **First Time Setup**

```bash
# 1. Collect historical data (ONE TIME - takes ~5 mins)
python fetch_game_logs.py           # Get 3 seasons of game logs
python compute_rolling_stats.py     # Calculate L5/L10/L20 averages

# 2. Get current data
python fetch_2025_26_stats.py       # Current season player stats
python fetch_team_stats.py          # Team defensive stats
python fetch_goalie_stats.py        # Goalie save percentages

# 3. Train ML models
python train_nhl_ml_v3.py           # Train with all features

# 4. Generate predictions
python fresh_clean_predictions.py   # Statistical model
python ensemble_predictions.py      # Ensemble (stat + ML)
```

---

## 📅 **DAILY WORKFLOW**

### **Manual Mode (Run When You Want)**

```bash
# Morning routine (10 AM)
python fetch_2025_26_stats.py       # Update player stats (~2 mins)
python fresh_clean_predictions.py   # Generate statistical predictions (~30 sec)
python ensemble_predictions.py      # Generate ensemble predictions (~1 min)

# Check predictions via Discord
# Use Discord bot: !picks
```

### **Automated Mode (Set It & Forget It)**

```bash
# Start the automation pipeline
python data_pipeline.py

# This runs 24/7 and handles:
# - 2:00 AM: Full data refresh + retrain models
# - 10:00 AM: Generate today's predictions
# - Every 6h: Update player stats
# - Every 1h: Health check

# Stop with Ctrl+C
```

### **Weekly Maintenance (Recommended)**

```bash
# Sunday (before new week)
python fetch_game_logs.py           # Update with last week's games (~3 min)
python compute_rolling_stats.py     # Recalculate rolling averages (~2 min)
python train_nhl_ml_v3.py           # Retrain with fresh data (~5 min)

# Now you're ready for the week!
```

---

## 📖 **ALL COMMANDS REFERENCE**

### **🔄 Data Collection**

| Command | What It Does | When to Run | Time |
|---------|--------------|-------------|------|
| `python fetch_2025_26_stats.py` | Get current season player stats | Daily | 2 min |
| `python fetch_game_logs.py` | Fetch historical game-by-game data | Weekly | 3 min |
| `python compute_rolling_stats.py` | Calculate L5/L10/L20 rolling averages | After game logs | 2 min |
| `python fetch_team_stats.py` | Get team defensive metrics | Daily | 30 sec |
| `python fetch_goalie_stats.py` | Get goalie save percentages | Daily | 30 sec |

### **🤖 ML Model Training**

| Command | What It Does | When to Run | Time |
|---------|--------------|-------------|------|
| `python train_nhl_ml.py` | Train V1 baseline model (58% acc) | Rarely | 5 min |
| `python train_nhl_ml_v2.py` | Train V2 with L5/consistency (59% acc) | Rarely | 5 min |
| `python train_nhl_ml_v3.py` | Train V3 with goalies (59% acc, best) | **Weekly** | 5 min |

### **🎯 Prediction Generation**

| Command | What It Does | Accuracy | Time |
|---------|--------------|----------|------|
| `python fresh_clean_predictions.py` | Statistical model predictions | **72%** | 30 sec |
| `python ml_predictions.py` | Pure ML model predictions | 59% | 1 min |
| `python ensemble_predictions.py` | Ensemble (70% stat + 30% ML) | **73-75%** ⭐ | 1 min |

### **📊 Analysis & Comparison**

| Command | What It Does | Use Case |
|---------|--------------|----------|
| `python compare_models.py` | Compare statistical vs ML vs ensemble | See all 3 side-by-side |
| `python grade_predictions_fixed.py` | Grade yesterday's predictions | Check accuracy |
| `python dashboard.py` | View historical performance | Track model performance |

### **🤖 Automation**

| Command | What It Does |
|---------|--------------|
| `python data_pipeline.py` | Run 24/7 automated pipeline |
| `python discord_bot.py` | Start Discord bot for predictions |

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **The Three Models**

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR PREDICTION SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │  STATISTICAL     │  │   ML MODEL       │  │  ENSEMBLE │ │
│  │   72% Acc        │  │   59% Acc        │  │  73-75%   │ │
│  │                  │  │                  │  │           │ │
│  │ • Domain expert  │  │ • XGBoost        │  │ • 70% Stat│ │
│  │ • Logistic curves│  │ • 32 features    │  │ • 30% ML  │ │
│  │ • Proven stable  │  │ • Goalie aware   │  │ • Best!   │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow**

```
1. NHL API
   ↓
2. fetch_*.py scripts → Database
   ↓
3. compute_rolling_stats.py → Rolling averages
   ↓
4. train_nhl_ml_v3.py → Trained models
   ↓
5. ensemble_predictions.py → Final predictions
   ↓
6. Discord Bot → YOU!
```

### **Database Tables**

- `player_stats` - Season averages (100 players)
- `player_game_logs` - Game-by-game history (17,174 games)
- `player_rolling_stats` - L5/L10/L20 averages (50,298 records)
- `team_stats` - Defensive metrics (32 teams)
- `goalie_stats` - Save percentages (68 goalies)
- `predictions` - Generated predictions
- `games` - Game schedule

---

## 🔧 **TROUBLESHOOTING**

### **Problem: No predictions generated**

```bash
# Check if statistical predictions exist
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM predictions WHERE game_date = date(\"now\")'); print(f'Predictions today: {cursor.fetchone()[0]}')"

# If 0, generate them:
python fresh_clean_predictions.py
```

### **Problem: ML model not loading**

```bash
# Check if models exist
dir models\*latest*.pkl

# If missing, train them:
python train_nhl_ml_v3.py
```

### **Problem: "No games found for today"**

This is normal! NHL doesn't play every day. The system will show this message on off-days.

### **Problem: Ensemble shows "ML Model: N/A"**

Some players don't have enough history for ML predictions. The system falls back to statistical-only for those players (which is fine - 72% accuracy!)

### **Problem: Database locked error**

```bash
# Close any open connections
# Then run:
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db'); conn.execute('PRAGMA integrity_check'); conn.close(); print('DB OK')"
```

---

## 🎮 **DISCORD BOT COMMANDS**

```
!run        - Run complete workflow (stats → predictions → edges)
!picks      - Show today's top predictions
!edge       - Show PrizePicks edge plays
!count      - Count predictions by tier
!dashboard  - Performance dashboard
!grade      - Grade yesterday's predictions
```

**Start Discord Bot:**
```bash
python discord_bot.py
```

---

## ⚡ **CHEAT CODES (Power User Shortcuts)**

### **🔥 Ultra-Fast Daily Predictions**

```bash
# One-liner for today's predictions
python fresh_clean_predictions.py && python ensemble_predictions.py && echo "DONE!"
```

### **🎯 Get Only T1-ELITE Picks**

```python
import sqlite3
conn = sqlite3.connect('database/nhl_predictions.db')
df = pd.read_sql_query("""
    SELECT player_name, prop_type, line, probability
    FROM predictions
    WHERE game_date = date('now')
    AND confidence_tier = 'T1-ELITE'
    AND model_version = 'ensemble_v1'
    ORDER BY probability DESC
""", conn)
print(df)
```

### **📊 Check Model Accuracy History**

```python
import sqlite3
conn = sqlite3.connect('database/nhl_predictions.db')

# Get graded predictions accuracy
df = pd.read_sql_query("""
    SELECT
        confidence_tier,
        COUNT(*) as total,
        SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as hits,
        ROUND(AVG(is_correct) * 100, 1) as accuracy
    FROM predictions
    WHERE is_correct IS NOT NULL
    GROUP BY confidence_tier
""", conn)
print(df)
```

### **🔄 Emergency Full Reset**

```bash
# If something is broken, start fresh:
python fetch_game_logs.py           # Re-fetch all data
python compute_rolling_stats.py     # Recalculate everything
python train_nhl_ml_v3.py           # Retrain models
python fresh_clean_predictions.py   # Generate predictions
python ensemble_predictions.py      # Ensemble
```

### **🚀 Weekend Batch Update**

```bash
# Run this Sunday night for the week ahead
python fetch_game_logs.py && \
python compute_rolling_stats.py && \
python fetch_team_stats.py && \
python fetch_goalie_stats.py && \
python train_nhl_ml_v3.py && \
echo "✅ Ready for the week!"
```

---

## 🎨 **PERFORMANCE TUNING**

### **Adjust Ensemble Weights**

Edit `ensemble_predictions.py`:

```python
# Conservative (trust stats more)
engine = EnsemblePredictionEngine(stat_weight=0.80, ml_weight=0.20)

# Balanced (default)
engine = EnsemblePredictionEngine(stat_weight=0.70, ml_weight=0.30)

# Aggressive (trust ML more)
engine = EnsemblePredictionEngine(stat_weight=0.60, ml_weight=0.40)
```

### **Change Tier Thresholds**

Edit ensemble or statistical model:

```python
# More conservative tiers
if ensemble_prob >= 0.75:  # Was 0.70
    tier = 'T1-ELITE'
elif ensemble_prob >= 0.65:  # Was 0.60
    tier = 'T2-STRONG'
```

### **Focus on Specific Prop Types**

```bash
# Only points predictions
python -c "from fresh_clean_predictions import *; engine = EnhancedPredictionEngine(); engine.generate_predictions(datetime.now().strftime('%Y-%m-%d'))" | grep -i "points"

# Only shots predictions
# Similar approach
```

---

## 📈 **MONITORING & LOGS**

### **Check Pipeline Logs**

```bash
# View recent pipeline activity
tail -f logs/pipeline.log

# Search for errors
grep -i error logs/pipeline.log
```

### **Database Status**

```bash
python check_database_tables.py
```

### **Model Performance Over Time**

```bash
python dashboard.py
```

---

## 🎓 **BEST PRACTICES**

### **Daily Routine (Recommended)**

1. **Morning (10 AM):** Run predictions
   ```bash
   python fresh_clean_predictions.py
   python ensemble_predictions.py
   ```

2. **Evening (Before games):** Check Discord for picks
   ```
   !picks
   ```

3. **Next Day:** Grade yesterday's predictions
   ```bash
   python grade_predictions_fixed.py
   ```

### **Weekly Routine (Recommended)**

1. **Sunday:** Full data refresh
   ```bash
   python fetch_game_logs.py
   python compute_rolling_stats.py
   python train_nhl_ml_v3.py
   ```

2. **Monitor Accuracy:** Check if models need retuning

### **When Accuracy Drops**

If ensemble accuracy drops below 70%:

1. **Check data freshness** - Run all fetch scripts
2. **Retrain models** - `python train_nhl_ml_v3.py`
3. **Verify game logs** - Make sure recent games are in database
4. **Adjust weights** - Maybe 80/20 instead of 70/30

---

## 🏆 **ADVANCED: MODEL COMPARISON**

### **Head-to-Head Testing**

```bash
# Run all three models on same day
python fresh_clean_predictions.py   # Statistical
python ml_predictions.py            # ML
python ensemble_predictions.py      # Ensemble

# Compare results
python compare_models.py

# Next day: Grade all three
python grade_predictions_fixed.py
```

### **Backtest Historical Performance**

```python
# Check model performance on past games
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/nhl_predictions.db')

query = """
SELECT
    model_version,
    COUNT(*) as total,
    AVG(is_correct) * 100 as accuracy,
    AVG(probability) as avg_confidence
FROM predictions
WHERE is_correct IS NOT NULL
GROUP BY model_version
"""

df = pd.read_sql_query(query, conn)
print(df)
```

---

## 🎯 **QUICK REFERENCE CARD**

```
╔════════════════════════════════════════════════════════════╗
║         NHL ML PREDICTION SYSTEM - QUICK REF              ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  DAILY:                                                    ║
║  • python fresh_clean_predictions.py                      ║
║  • python ensemble_predictions.py                         ║
║                                                            ║
║  WEEKLY:                                                   ║
║  • python fetch_game_logs.py                              ║
║  • python compute_rolling_stats.py                        ║
║  • python train_nhl_ml_v3.py                              ║
║                                                            ║
║  AUTOMATION:                                               ║
║  • python data_pipeline.py (24/7)                         ║
║                                                            ║
║  DISCORD:                                                  ║
║  • !picks - See today's predictions                       ║
║  • !run - Full workflow                                   ║
║                                                            ║
║  ACCURACY:                                                 ║
║  • Statistical: 72%                                        ║
║  • ML: 59%                                                 ║
║  • Ensemble: 73-75% ⭐                                     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🆘 **EMERGENCY CONTACTS**

### **File Structure**

```
PrizePicks-Research-Lab/
├── database/
│   └── nhl_predictions.db          # All your data
├── models/
│   ├── nhl_points_model_latest_v3.pkl
│   ├── nhl_shots_model_latest_v3.pkl
│   └── feature_columns_latest_v3.pkl
├── logs/
│   └── pipeline.log
├── fetch_*.py                      # Data collection
├── train_nhl_ml_v3.py             # ML training
├── fresh_clean_predictions.py      # Statistical predictions
├── ensemble_predictions.py         # Ensemble (BEST)
├── compare_models.py               # Model comparison
├── data_pipeline.py                # Automation
└── discord_bot.py                  # Discord interface
```

### **Data File Sizes (Approx)**

- `nhl_predictions.db` - 50-100 MB
- ML models (.pkl files) - 5-10 MB each
- Logs - Grows over time (clean weekly)

---

## 💎 **PRO TIPS**

1. **Always run ensemble** - It's the best performing model (73-75%)

2. **Trust T1-ELITE picks** - These are 70%+ confidence, your best bets

3. **Update data before big games** - Fresh data = better predictions

4. **Monitor accuracy weekly** - If drops, retrain models

5. **Use Discord bot** - Easiest way to check picks on the go

6. **Backup database weekly** - `copy database\nhl_predictions.db database\backup_YYYYMMDD.db`

7. **Run pipeline overnight** - Let automation handle data updates

8. **Check logs if errors** - `tail logs/pipeline.log`

9. **Retrain after player trades** - Roster changes affect predictions

10. **Trust the process** - No model is 100%, expect variance

---

## 🎉 **YOU'RE READY!**

You now have:
- ✅ Complete ML prediction system
- ✅ 73-75% accuracy ensemble model
- ✅ Automated data pipeline
- ✅ Discord bot interface
- ✅ Full documentation

**Your move:** Run `python ensemble_predictions.py` and start winning! 🚀

---

**Last Updated:** 2025-10-27
**Version:** 3.0 (Ensemble Edition)
**Status:** Production Ready 🏆
