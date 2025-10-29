# NHL Predictions System - Complete User Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Daily Workflow](#daily-workflow)
4. [Key Features](#key-features)
5. [File Reference](#file-reference)
6. [Command Reference](#command-reference)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## System Overview

**NHL Predictions System** - AI-powered NHL player prop predictions with 73-75% accuracy.

### What It Does
- Fetches fresh player/team/goalie stats from NHL API
- Calculates game total O/U based on team matchups
- Generates predictions for Points and Shots props
- Weights predictions by game scoring environment (O/U)
- Filters out low-quality bets (points props in defensive games)
- Creates weighted parlays (65% shots / 35% points)
- Auto-commits picks to GitHub (TXT + CSV)

### Accuracy Target
- **T1-ELITE picks**: 73-75% accuracy
- **T2-STRONG picks**: 65-70% accuracy
- **T3-MARGINAL picks**: 55-60% accuracy

---

## Quick Start

### First Time Setup

1. **Install Windows Task Scheduler** (one-time)
   ```powershell
   # Run PowerShell as Administrator
   cd "C:\Users\thoma\PrizePicks-Research-Lab"
   .\setup_windows_scheduler.ps1
   ```

2. **Verify Automation**
   ```powershell
   # Check scheduled task
   Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
   ```

### Manual Pick Generation

```bash
# Generate today's picks
python generate_picks_to_file.py

# Output:
# - LATEST_PICKS.txt (human readable)
# - LATEST_PICKS.csv (spreadsheet format)
# - Auto-committed to GitHub
```

### Generate Parlays

```bash
# Create weighted parlays (65% shots, 35% points)
python generate_weighted_parlays.py

# Output:
# - LATEST_PARLAYS.txt
# - 2-leg through 5-leg parlays
```

---

## Daily Workflow

### Automated (Hands-Free) 🤖

**Windows Task Scheduler runs automatically:**

- **8:55 AM**: Task starts
- **9:00 AM**: First picks generated → GitHub
- **12:00 PM**: Picks refreshed → GitHub
- **3:00 PM**: Picks refreshed → GitHub
- **6:00 PM**: Final picks → GitHub, window closes

**What happens each run:**
1. Checks if data is stale (>2 hours old)
2. If stale: Fetches fresh stats from NHL API
3. Calculates game O/U totals
4. Generates predictions with O/U weighting
5. Filters low-quality picks
6. Exports to TXT and CSV
7. Commits and pushes to GitHub

### Manual (On-Demand) 🖱️

```bash
# Quick pick generation
python generate_picks_to_file.py

# Full data refresh + predictions
python complete_automation.py

# Generate parlays only
python generate_weighted_parlays.py
```

---

## Key Features

### 1. Game Total O/U Integration ⭐ NEW

**What it does:**
- Calculates expected game totals based on team offense/defense
- Adjusts player expectations based on scoring environment

**O/U Multipliers:**
- **7.0+ O/U**: +15% boost (high-scoring game)
- **6.5 O/U**: +8% boost (above average)
- **6.0 O/U**: No adjustment (neutral)
- **5.5 O/U**: -8% penalty (below average)
- **<5.5 O/U**: -15% penalty (defensive battle)

**Example:**
- Celebrini in SJS vs LAK (O/U 7.0): 2.01 expected points (+15%)
- Same player in low O/U game: Would be downgraded

### 2. Quality Filter - Low O/U Games ⭐ NEW

**Rule:** Blocks all POINTS props when O/U ≤ 5.5

**Why:**
- Defensive battles = limited scoring
- Even elite players struggle to score
- Shots props still viable (players shoot regardless)

**Example Today:**
- NYR @ VAN (O/U 5.5): 5 shots picks, 0 points picks ✅

### 3. Weighted Parlay Generator ⭐ NEW

**Strategy:** 65% shots / 35% points

**Why:**
- Shots are more consistent than points
- Higher hit rate on parlays
- Better bankroll protection

**Output:**
- 2-leg: ~83% probability, 3x payout
- 3-leg: ~79% probability, 6x payout
- 4-leg: ~69% probability, 10x payout
- 5-leg: Lower probability, 20x payout

**Features:**
- No duplicate teams (reduces correlation)
- Sorted by Expected Value
- Shows probability + payout for each parlay

### 4. CSV Export ⭐ NEW

**Files Generated:**
- `LATEST_PICKS.txt` - Human readable format
- `LATEST_PICKS.csv` - Spreadsheet format

**CSV Columns:**
```
Player, Team, Opponent, Prop Type, Line, Probability (%),
Expected Value, Confidence Tier, Model, Reasoning
```

**Use Cases:**
- Import to Excel/Google Sheets
- Filter/sort by probability
- Build custom parlay combinations
- Track historical performance

### 5. Smart Data Refresh

**Checks data age before fetching:**
- Fresh (<2 hours): Uses cached data
- Stale (>2 hours): Fetches from NHL API

**What gets updated:**
- Player season stats (PPG, SOG, TOI, etc.)
- Team defensive stats (GA/G, SA/G)
- Goalie stats (SV%, GAA)
- Game O/U totals

### 6. Confidence Tiers

**T1-ELITE** (73-75% accuracy)
- Highest confidence picks
- 70%+ probability
- Focus your bets here

**T2-STRONG** (65-70% accuracy)
- Good picks
- 60-70% probability
- Use for parlays

**T3-MARGINAL** (55-60% accuracy)
- Lower confidence
- 50-60% probability
- Use sparingly or avoid

---

## File Reference

### Critical Files (DO NOT DELETE)

**Database:**
- `database/nhl_predictions.db` - All predictions, stats, results

**Prediction Models:**
- `enhanced_predictions_FIXED_FINAL_FINAL.py` - Main model (with O/U)
- `ensemble_predictions.py` - Ensemble model
- `fresh_clean_predictions.py` - Prediction wrapper

**Data Fetching:**
- `fetch_player_stats.py` - Player stats
- `fetch_team_stats.py` - Team stats
- `fetch_goalie_stats.py` - Goalie stats
- `fetch_game_totals.py` - Game O/U calculator
- `smart_data_refresh.py` - Refresh coordinator

**Automation:**
- `generate_picks_to_file.py` - Main picks generator (TXT + CSV)
- `run_picks_throughout_day.py` - Scheduler (9 AM - 6 PM)
- `run_daily_picks.bat` - Windows Task Scheduler entry point

**Utilities:**
- `generate_weighted_parlays.py` - Parlay generator

### Output Files (Auto-Generated)

**Daily Picks:**
- `LATEST_PICKS.txt` - Latest picks (human readable)
- `LATEST_PICKS.csv` - Latest picks (CSV format)
- `PICKS_YYYY-MM-DD_HH-MMPM.txt` - Timestamped archive
- `PICKS_YYYY-MM-DD_HH-MMPM.csv` - Timestamped archive

**Parlays:**
- `LATEST_PARLAYS.txt` - Latest parlay recommendations
- `PARLAYS_YYYY-MM-DD.txt` - Timestamped parlays

### Safe to Delete

- Old `PICKS_2025-*` files (timestamped archives)
- `logs/` folder contents
- `*_OLD.py` files (backups)
- `__pycache__/` folders

---

## Command Reference

### Generate Picks

```bash
# Full generation (recommended)
python generate_picks_to_file.py

# Quick prediction only (no GitHub push)
python fresh_clean_predictions.py

# Full workflow (data refresh + predictions + dashboard)
python complete_automation.py
```

### Generate Parlays

```bash
# Weighted parlays (65% shots, 35% points)
python generate_weighted_parlays.py
```

### Data Management

```bash
# Fetch fresh player stats
python fetch_player_stats.py

# Fetch team stats
python fetch_team_stats.py

# Update game O/U totals
python fetch_game_totals.py

# Smart refresh (only if stale)
python smart_data_refresh.py
```

### Database Queries

```bash
# Count today's picks by tier
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db');
cursor = conn.cursor();
cursor.execute('SELECT confidence_tier, COUNT(*) FROM predictions WHERE game_date = date(\"now\") GROUP BY confidence_tier');
print(cursor.fetchall())"

# View today's T1-ELITE picks
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db');
cursor = conn.cursor();
cursor.execute('SELECT player_name, prop_type, probability FROM predictions WHERE game_date = date(\"now\") AND confidence_tier = \"T1-ELITE\" ORDER BY probability DESC LIMIT 10');
[print(f'{p[0]}: {p[1]} - {p[2]:.1%}') for p in cursor.fetchall()]"
```

### Task Scheduler Management

```powershell
# Check task status
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"

# Get last run info
Get-ScheduledTaskInfo -TaskName "NHL Picks Daily Auto-Scheduler"

# Manually trigger task (for testing)
Start-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"

# Check next run time
(Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler").Triggers
```

### Git/GitHub

```bash
# Check status
git status

# View recent commits
git log --oneline -10

# Pull latest changes
git pull

# Push local changes
git add . && git commit -m "Manual update" && git push
```

---

## Troubleshooting

### Automation Not Running

**Check Task Scheduler:**
```powershell
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" | Select-Object State, LastRunTime, NextRunTime
```

**Common Issues:**
1. **Task shows "Ready" but never ran**
   - Trigger time not reached yet
   - Check NextRunTime

2. **Task failed (LastTaskResult = 1)**
   - Python not found
   - Re-run `setup_windows_scheduler.ps1`

3. **No picks generated**
   - Check logs: `logs/pipeline.log`
   - Run manually: `python generate_picks_to_file.py`

### No Picks Generated

**Check data freshness:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db');
cursor = conn.cursor();
cursor.execute('SELECT MAX(last_updated) FROM player_stats');
print(cursor.fetchone())"
```

**Solutions:**
1. Refresh data: `python smart_data_refresh.py`
2. Check if games exist today: Look at schedule
3. Re-run predictions: `python generate_picks_to_file.py`

### API Fetch Failures

**Symptoms:**
- "Data fetch failed" errors
- Stale data warnings

**Solutions:**
1. Wait and retry (NHL API rate limits)
2. Check internet connection
3. Run: `python fetch_player_stats.py` manually

### GitHub Push Failed

**Common causes:**
- No internet connection
- Git credentials expired
- Merge conflict

**Solutions:**
```bash
# Check status
git status

# Pull latest first
git pull

# Then retry
python generate_picks_to_file.py
```

### CSV Not Showing in GitHub

**Check if committed:**
```bash
git log --oneline -5
```

**Manually commit:**
```bash
git add LATEST_PICKS.csv
git commit -m "Add CSV picks"
git push
```

---

## Advanced Usage

### Custom Parlay Configurations

Edit `generate_weighted_parlays.py`:

```python
# Change shot/point weighting
parlays = generate_weighted_parlays(
    shots_picks,
    points_picks,
    parlay_size=4,
    num_parlays=10,
    shots_weight=0.75  # 75% shots instead of 65%
)
```

### Adjust O/U Thresholds

Edit `enhanced_predictions_FIXED_FINAL_FINAL.py`:

```python
# Line 45-55: Modify O/U multipliers
if game_ou_total >= 7.0:
    game_total_factor = 1.20  # Increase from 1.15
elif game_ou_total >= 6.5:
    game_total_factor = 1.10  # Increase from 1.08
# ... etc
```

### Change Confidence Tiers

Edit `fresh_clean_predictions.py`:

```python
# Line 48-54: Adjust probability thresholds
if prob >= 0.75:  # Stricter (was 0.70)
    tier = 'T1-ELITE'
elif prob >= 0.65:  # Stricter (was 0.60)
    tier = 'T2-STRONG'
```

### Export to Different Formats

**JSON Export:**
```python
import json

picks = get_todays_picks()
with open('picks.json', 'w') as f:
    json.dump(picks, f, indent=2)
```

**Excel Export (requires openpyxl):**
```python
import pandas as pd

df = pd.read_csv('LATEST_PICKS.csv')
df.to_excel('picks.xlsx', index=False)
```

---

## GitHub Links

**View picks online:**
- TXT: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
- CSV: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.csv
- Parlays: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PARLAYS.txt

**Repository:**
- https://github.com/thomascp2/nhl-predictions

---

## Tips & Best Practices

### Betting Strategy

1. **Focus on T1-ELITE picks** (73-75% accuracy)
2. **Use parlays wisely**:
   - 2-3 leg parlays: Safest
   - 4-5 leg parlays: Higher risk/reward
3. **Avoid points props in low O/U games** (system filters these)
4. **Shots props are more consistent** than points
5. **Bankroll management**: Bet 1-2% per pick

### Data Quality

1. **Let automation run** - handles data freshness
2. **Manual refresh if needed**: `python smart_data_refresh.py`
3. **Check data age** in LATEST_PICKS.txt header
4. **Fresh data (<2 hours) = best predictions**

### Parlay Building

1. **Use 65/35 shot weighting** (default)
2. **Avoid same-team parlays** (system prevents this)
3. **Check combined probability** before betting
4. **2-3 leg parlays hit more often**
5. **Sort by EV** (Expected Value) - system does this

### File Management

1. **Keep LATEST_* files** - always current
2. **Archive old PICKS_* files** monthly
3. **Backup database** weekly: `database/nhl_predictions.db`
4. **Check GitHub** for remote backup

---

## Version History

**v3.0** (Current)
- Game total O/U integration
- Low O/U quality filter (blocks points in defensive games)
- Weighted parlay generator (65% shots / 35% points)
- CSV export
- Smart data refresh

**v2.0**
- Windows Task Scheduler automation
- Auto-commit to GitHub
- Ensemble prediction model

**v1.0**
- Basic NHL predictions
- Statistical model
- Manual execution

---

## Support & Contact

**Issues:**
- Check troubleshooting section first
- Review logs: `logs/pipeline.log`
- Check GitHub commit history for recent changes

**Updates:**
- System auto-updates from GitHub
- Check commit messages for feature changes

---

**Last Updated:** October 28, 2025
**Version:** 3.0
