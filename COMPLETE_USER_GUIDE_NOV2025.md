# NHL BETTING SYSTEM - COMPLETE USER GUIDE
**Last Updated:** November 2, 2025 8:35 PM
**Status:** Production Ready

---

## 📋 TABLE OF CONTENTS

1. [Daily Workflow](#daily-workflow)
2. [Key Scripts Reference](#key-scripts-reference)
3. [Data Freshness & API Management](#data-freshness--api-management)
4. [Database Maintenance](#database-maintenance)
5. [Grading & Performance Tracking](#grading--performance-tracking)
6. [Automated Game Logs (50 Stars)](#automated-game-logs-50-stars)
7. [Troubleshooting](#troubleshooting)
8. [File Organization](#file-organization)

---

## 🚀 DAILY WORKFLOW

### **Quick Start - ONE COMMAND:**

```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**What it does:**
1. ✅ Generates predictions (Statistical, Ensemble, Goalie models)
2. ✅ Fetches PrizePicks lines (current market data)
3. ✅ Runs Stars Filter (50 elite players, favorable matchups)
4. ✅ Runs Market vs Model (find +EV edges)
5. ✅ Exports comprehensive CSV (ALL data - stars, edges, matchups)

**Output Files:**
- `LATEST_PICKS.txt` - T1-ELITE picks only
- `LATEST_PICKS.csv` - T1-ELITE picks only
- `COMPLETE_ANALYSIS_YYYYMMDD_HHMMPM.csv` - ⭐ **MASTER FILE** (all picks, edges, matchups)

**Time:** ~3-5 minutes

---

## 📅 RECOMMENDED SCHEDULE

### **Daily Runs:**

**Option A: Single Run (Recommended for Most Users)**
```bash
# Run once per day at 10 AM
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**Option B: Multiple Runs (Advanced - Track Line Movement)**
```bash
# Morning (10 AM) - Initial picks
python RUN_COMPLETE_DAILY_WORKFLOW.py

# Afternoon (3 PM) - Check if edges still exist
python fetch_prizepicks_current_lines.py 2025-11-03
python market_vs_model.py 2025-11-03

# Evening (6 PM) - Final check before games
python fetch_prizepicks_current_lines.py 2025-11-03
python market_vs_model.py 2025-11-03
```

**Why multiple runs?**
- PrizePicks lines move throughout the day
- Edges at 10 AM may disappear by 6 PM
- Re-running market_vs_model.py shows updated edges

---

### **Weekly Maintenance:**

**Sunday (Weekly Review):**
```bash
# Grade last week's predictions
python grade_predictions.py --date-range last-7-days

# Update star player game logs
python update_star_player_logs.py

# Review performance
python view_performance_summary.py
```

---

## 📚 KEY SCRIPTS REFERENCE

### **Main Workflows:**

| Script | Purpose | When to Run | Output |
|--------|---------|-------------|--------|
| `RUN_COMPLETE_DAILY_WORKFLOW.py` | Complete betting workflow | Daily (10 AM) | COMPLETE_ANALYSIS CSV |
| `RUN_DAILY_PICKS.py` | Generate predictions only | Manual (if needed) | LATEST_PICKS files |
| `RUN_STARS_ONLY.py` | Stars filter only | Manual | Stars picks |

### **Data Collection:**

| Script | Purpose | Frequency | Auto-Refresh? |
|--------|---------|-----------|---------------|
| `fetch_prizepicks_current_lines.py` | Get PrizePicks market lines | Multiple times/day | ✅ Yes (in workflow) |
| `fetch_2025_26_stats.py` | Player season stats | Daily | ✅ Yes (auto if >2hrs old) |
| `fetch_goalie_stats.py` | Goalie stats | Daily | ✅ Yes (auto if >2hrs old) |
| `fetch_betting_lines.py` | Game O/U and ML | Daily | ✅ Yes (auto if >2hrs old) |
| `fetch_game_logs.py` | Player game logs (all) | Weekly | ❌ No (manual) |
| `update_star_player_logs.py` | Game logs (50 stars only) | Weekly | ⭐ **NEW** (auto) |

### **Analysis & Export:**

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `stars_only_filter.py` | Filter to 50 stars + favorable matchups | Daily (in workflow) |
| `market_vs_model.py` | Find market edges | Daily (in workflow) |
| `export_complete_analysis.py` | Export comprehensive CSV | Daily (in workflow) |

### **Performance & Grading:**

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `grade_predictions.py` | Grade predictions vs actual results | Weekly |
| `view_performance_summary.py` | View model accuracy | Weekly |
| `analyze_edge_performance.py` | Validate market edges | Monthly |

---

## 🔄 DATA FRESHNESS & API MANAGEMENT

### **Smart Data Refresh (Automatic):**

The system includes **smart_data_refresh.py** that automatically checks data age:

```python
# Runs automatically in RUN_DAILY_PICKS.py
# If data is older than 2 hours, fetches fresh data:
- Player stats (fetch_2025_26_stats.py)
- Goalie stats (fetch_goalie_stats.py)
- Betting lines (fetch_betting_lines.py)
```

**Manual Data Refresh:**
```bash
# Force refresh all data (ignoring age check)
python smart_data_refresh.py --force
```

---

### **API Rate Limits:**

**NHL API (Free):**
- No rate limit
- Used for: Schedule, player stats, goalie stats
- Reliability: High

**PrizePicks API (Free):**
- Rate limit: ~60 requests/hour
- Used for: Player prop lines
- Reliability: Medium (occasionally returns empty)

**Best Practices:**
- Run workflow 1-3 times per day (not every hour)
- If PrizePicks returns 0 lines, wait 10 minutes and retry
- Don't hammer APIs - respect rate limits

---

## 💾 DATABASE MAINTENANCE

### **Database Location:**
```
database/nhl_predictions.db
```

### **Key Tables:**

**Predictions:**
- `predictions` - All model predictions
- `prediction_batches` - Batch tracking

**Player Data:**
- `player_stats` - Season stats (2025-26)
- `player_game_logs` - Game-by-game logs
- `goalie_stats` - Goalie statistics

**Market Data:**
- `prizepicks_lines` - PrizePicks market lines
- `game_betting_lines` - Game O/U and ML

**Performance:**
- `prediction_outcomes` - Graded predictions
- `model_performance` - Model accuracy tracking

---

### **Database Cleanup (Monthly):**

```bash
# Remove old predictions (older than 30 days)
python cleanup_old_predictions.py --days 30

# Vacuum database (optimize size)
python vacuum_database.py

# Backup database
python backup_database.py
```

---

## 📊 GRADING & PERFORMANCE TRACKING

### **Why Grade Predictions?**
- Validate model accuracy
- Identify which props/tiers perform best
- Calibrate confidence levels
- Track edge performance vs market

---

### **Automated Grading Workflow:**

**1. Daily Auto-Grade (Next Morning):**
```bash
# Grades yesterday's predictions automatically
# Run this at 8 AM (after all games finish)
python auto_grade_yesterday.py
```

**What it does:**
- Fetches actual game results from NHL API
- Compares predictions to actual outcomes
- Updates `prediction_outcomes` table
- Calculates accuracy by tier, prop type, player

---

**2. Weekly Performance Review (Sunday):**
```bash
# Grade all predictions from last 7 days
python grade_predictions.py --date-range last-7-days

# View performance summary
python view_performance_summary.py
```

**Example Output:**
```
OVERALL PERFORMANCE (Last 7 Days)
=====================================
Total Predictions: 156
Correct: 112
Accuracy: 71.8%

BY CONFIDENCE TIER:
T1-ELITE (85%+): 75.0% accuracy (48/64)
T2-STRONG (65-84%): 70.5% accuracy (43/61)
T3-SOLID (50-64%): 67.7% accuracy (21/31)

BY PROP TYPE:
Points: 75.2% accuracy
Shots: 68.9% accuracy
Goals: 80.0% accuracy

BY PLAYER (Top 5):
Connor McDavid: 85.7% (6/7)
Leon Draisaitl: 83.3% (5/6)
Auston Matthews: 80.0% (4/5)
```

---

**3. Monthly Edge Validation:**
```bash
# Analyze market edge performance
python analyze_edge_performance.py --date-range last-30-days
```

**Example Output:**
```
EDGE PERFORMANCE (Last 30 Days)
=====================================

HUGE EDGES (>=20%):
- Predicted Win Rate: 68%
- Actual Win Rate: 65%
- Total Bets: 23
- Result: Profitable (close to prediction)

STRONG EDGES (10-19%):
- Predicted Win Rate: 58%
- Actual Win Rate: 55%
- Total Bets: 47
- Result: Profitable (slight overconfidence)

SMALL EDGES (5-9%):
- Predicted Win Rate: 52%
- Actual Win Rate: 48%
- Total Bets: 68
- Result: Unprofitable (market is sharper)

RECOMMENDATION: Only bet edges >=10%
```

---

### **Manual Grading (If Needed):**

```bash
# Grade specific date
python grade_predictions.py --date 2025-11-03

# Grade specific player
python grade_predictions.py --player "Connor McDavid"

# Grade specific prop type
python grade_predictions.py --prop-type points
```

---

## 🎯 AUTOMATED GAME LOGS (50 STARS)

### **Problem:**
- Full game logs for all players = slow and unnecessary
- We only care about 50 stars now
- Need fresh game logs for accurate predictions

### **Solution: Targeted Game Log Updates**

**New Script: `update_star_player_logs.py`**

```python
"""
Update game logs for 50 stars only (fast and efficient)

Features:
- Only fetches logs for stars in STARS list
- Incremental updates (only new games)
- Runs in ~30 seconds (vs 10+ minutes for all players)
- Integrated into weekly workflow

Usage:
    python update_star_player_logs.py
"""
```

**How it works:**
1. Gets list of 50 stars from `stars_only_filter.py`
2. Checks last game log date for each star
3. Only fetches NEW games since last update
4. Updates `player_game_logs` table
5. Takes ~30 seconds (vs 10 minutes for all players)

---

### **Schedule for Game Log Updates:**

**Recommended:**
```bash
# Sunday morning (after week of games)
python update_star_player_logs.py
```

**Advanced (Daily Updates):**
```bash
# Add to daily workflow (optional)
python update_star_player_logs.py
```

---

### **Integration:**

**Option 1: Manual Weekly Update**
```bash
# Every Sunday at 10 AM
python update_star_player_logs.py
```

**Option 2: Add to Task Scheduler**
```batch
REM Add to fix_task_scheduler.bat
schtasks /create /tn "NHL Update Star Logs Sunday" ^
  /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && python update_star_player_logs.py" ^
  /sc weekly /d SUN /st 10:00 /rl highest /f
```

---

## 🛠️ TROUBLESHOOTING

### **Issue: 0 Predictions Generated**

**Possible Causes:**
1. Light game day (few games scheduled)
2. Data refresh failed
3. Date mismatch

**Solution:**
```bash
# Force data refresh
python smart_data_refresh.py --force

# Re-run workflow
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

---

### **Issue: Market vs Model Shows 0 Edges**

**Possible Causes:**
1. PrizePicks lines not fetched
2. Date mismatch between predictions and lines
3. Market is efficient (no edges available)

**Solution:**
```bash
# Check if lines were fetched
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM prizepicks_lines WHERE date=\"2025-11-03\"'); print(f'Lines: {cursor.fetchone()[0]}')"

# Re-fetch lines
python fetch_prizepicks_current_lines.py 2025-11-03

# Re-run market analysis
python market_vs_model.py 2025-11-03
```

---

### **Issue: PrizePicks API Returns 0 Lines**

**Possible Causes:**
1. Rate limited
2. API temporarily down
3. No NHL games today

**Solution:**
```bash
# Wait 10 minutes, then retry
sleep 600
python fetch_prizepicks_current_lines.py

# Check NHL schedule
python -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d'))"
```

---

### **Issue: Task Scheduler Not Running**

**Check tasks:**
```bash
schtasks /query /tn "NHL Morning Run 0700"
```

**Recreate tasks:**
```bash
fix_task_scheduler.bat
```

---

## 📁 FILE ORGANIZATION

### **Main Scripts (Root Directory):**
```
RUN_COMPLETE_DAILY_WORKFLOW.py  ⭐ Main workflow
RUN_DAILY_PICKS.py              - Generate predictions
RUN_STARS_ONLY.py               - Stars filter only

fetch_prizepicks_current_lines.py  - Get PrizePicks lines
fetch_2025_26_stats.py             - Player stats
fetch_goalie_stats.py              - Goalie stats
fetch_betting_lines.py             - Game O/U and ML

stars_only_filter.py            - Stars filter logic
market_vs_model.py              - Edge finder
export_complete_analysis.py     - CSV export

grade_predictions.py            - Grade predictions
auto_grade_yesterday.py         - Auto-grade daily
update_star_player_logs.py      ⭐ Update 50 stars logs
```

### **Data Files:**
```
database/
  nhl_predictions.db            - Main database

LATEST_PICKS.txt                - Current T1-ELITE picks
LATEST_PICKS.csv                - Current T1-ELITE picks (CSV)

COMPLETE_ANALYSIS_YYYYMMDD_HHMMPM.csv  ⭐ Master analysis file
PICKS_YYYY-MM-DD_HH-MMPM.txt          - Timestamped picks
```

### **Documentation:**
```
COMPLETE_USER_GUIDE_NOV2025.md      ⭐ This file
DAILY_WORKFLOW_GUIDE.md             - Daily workflow
MARKET_VS_MODEL_GUIDE.md            - Market vs model explained
STARS_CRITERIA_EXPLAINED.md        - 50 stars list + criteria
STARS_ONLY_STRATEGY.md              - Simplified betting
RECOMMENDED_STARS_LIST.py           - Stars list (Python module)
```

---

## 🎓 BEST PRACTICES

### **DO:**
✅ Run workflow 1-3 times per day (morning, afternoon, evening)
✅ Grade predictions weekly to validate accuracy
✅ Update star player logs weekly (Sunday)
✅ Track results in spreadsheet for analysis
✅ Respect API rate limits
✅ Backup database monthly
✅ Review performance metrics monthly

### **DON'T:**
❌ Run workflow every hour (unnecessary API calls)
❌ Bet on edges <5% (too close to market)
❌ Ignore unfavorable matchups (heavy favorite/underdog)
❌ Skip grading (you won't know if edges are real)
❌ Bet on negative edges (market is sharper)
❌ Chase short-term results (need 100+ bets for validation)

---

## 📈 SUCCESS METRICS

### **Track These KPIs:**

**Model Accuracy:**
- T1-ELITE: Target 73-75%
- T2-STRONG: Target 68-72%
- T3-SOLID: Target 55-65%

**Edge Performance:**
- Huge edges (>=20%): Should be profitable
- Strong edges (>=10%): Should be profitable
- Small edges (5-9%): May not be profitable (skip if negative EV)

**ROI:**
- Track total bets, wins, losses
- Calculate ROI = (Profit / Total Wagered) × 100
- Target: 5-10% ROI over 100+ bets

---

## 🚨 WHEN TO ADJUST SYSTEM

### **Red Flags:**

**1. Model Overconfident:**
- T1-ELITE hitting <70% → Recalibrate thresholds
- All edges losing money → Model is off

**2. Market is Sharper:**
- Consistent losses on edges >=10% → Raise minimum edge to 15%
- Negative EV on small edges → Stop betting <10% edges

**3. Specific Props Underperforming:**
- Shots hitting <60% → Remove shots from predictions
- Points hitting >75% → Increase confidence

**Solution:**
```bash
# Recalibrate model thresholds
python recalibrate_confidence_tiers.py --based-on-actual-performance

# Adjust edge thresholds in market_vs_model.py
# Change min_edge_pct from 5.0 to 10.0
```

---

## ⏰ COMPLETE WEEKLY SCHEDULE

**Sunday (10 AM):**
```bash
# Update star player logs (weekly)
python update_star_player_logs.py

# Grade last week's predictions
python grade_predictions.py --date-range last-7-days

# View performance
python view_performance_summary.py
```

**Monday-Saturday (10 AM):**
```bash
# Daily workflow
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**Monday-Saturday (6 PM - Optional):**
```bash
# Final edge check before games
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

---

## 📞 QUICK REFERENCE COMMANDS

**Daily:**
```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**Weekly:**
```bash
python update_star_player_logs.py
python grade_predictions.py --date-range last-7-days
```

**Monthly:**
```bash
python analyze_edge_performance.py --date-range last-30-days
python backup_database.py
```

**Troubleshooting:**
```bash
# Force data refresh
python smart_data_refresh.py --force

# Check database
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM predictions WHERE game_date=\"2025-11-03\"'); print(f'Predictions: {cursor.fetchone()[0]}')"

# Manual prediction generation
python RUN_DAILY_PICKS.py 2025-11-03
```

---

**Last Updated:** November 2, 2025 8:35 PM
**Version:** 1.0
**Status:** ✅ Production Ready

**System Components:**
- ✅ Prediction Models (3): Statistical, Ensemble, Goalie
- ✅ Stars Filter (50 players)
- ✅ Market vs Model (Edge finder)
- ✅ Comprehensive CSV Export
- ✅ Smart Data Refresh
- ✅ Automated Grading
- ⭐ **NEW:** Targeted Star Player Log Updates

**Next Maintenance:** Sunday, November 3, 2025 (Weekly review)
