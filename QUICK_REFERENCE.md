# NHL Predictions - Quick Reference Card

## 🎯 Most Common Commands

```bash
# Generate picks (TXT + CSV → GitHub)
python generate_picks_to_file.py

# Generate parlays
python generate_weighted_parlays.py

# Refresh data only
python smart_data_refresh.py
```

## 📊 View Latest Picks

**Local Files:**
- `LATEST_PICKS.txt` - Human readable
- `LATEST_PICKS.csv` - Spreadsheet format
- `LATEST_PARLAYS.txt` - Parlay recommendations

**GitHub:**
- TXT: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
- CSV: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.csv

## 🤖 Automation Schedule

**Daily (Hands-Free):**
- 9:00 AM - First picks
- 12:00 PM - Refresh
- 3:00 PM - Refresh
- 6:00 PM - Final picks

All auto-committed to GitHub

## 🎲 Parlay Strategy

**Weighting:** 65% Shots / 35% Points

**Why:** Shots are more consistent

**Best Picks:**
- 2-leg: ~83% hit rate, 3x payout
- 3-leg: ~79% hit rate, 6x payout
- 4-leg: ~69% hit rate, 10x payout

## 📈 Confidence Tiers

- **T1-ELITE**: 73-75% accuracy (BET THESE)
- **T2-STRONG**: 65-70% accuracy (Good for parlays)
- **T3-MARGINAL**: 55-60% accuracy (Avoid)

## 🧮 O/U Impact (NEW Feature)

**High Scoring (O/U 7.0+):** +15% boost
**Above Avg (O/U 6.5):** +8% boost
**Neutral (O/U 6.0):** No change
**Below Avg (O/U 5.5):** -8% penalty

**Quality Filter:** Points props blocked when O/U ≤ 5.5

## 🔧 Task Scheduler

```powershell
# Check status
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"

# Get run info
Get-ScheduledTaskInfo -TaskName "NHL Picks Daily Auto-Scheduler"

# Manual trigger (test)
Start-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
```

## 🚨 Quick Troubleshooting

**No picks generated:**
```bash
python smart_data_refresh.py
python generate_picks_to_file.py
```

**Automation not running:**
```powershell
# Re-run setup (PowerShell Admin)
.\setup_windows_scheduler.ps1
```

**Check data age:**
- Look at top of LATEST_PICKS.txt
- Should be <2 hours old

## 💾 Critical Files (Don't Delete)

1. `database/nhl_predictions.db` - ALL DATA
2. `enhanced_predictions_FIXED_FINAL_FINAL.py` - Main model
3. `generate_picks_to_file.py` - Picks generator
4. `run_daily_picks.bat` - Automation entry point
5. `generate_weighted_parlays.py` - Parlay generator

## 📁 Output Files

**Auto-Generated (Updated Each Run):**
- LATEST_PICKS.txt
- LATEST_PICKS.csv
- LATEST_PARLAYS.txt

**Archives (Timestamped):**
- PICKS_YYYY-MM-DD_HH-MMPM.txt
- PICKS_YYYY-MM-DD_HH-MMPM.csv

## 🎯 Betting Tips

1. **Focus on T1-ELITE** picks
2. **Shots > Points** for consistency
3. **2-3 leg parlays** are safest
4. **Avoid low O/U** points props (system filters these)
5. **Bet 1-2%** of bankroll per pick

## 📞 Emergency Commands

**Force data refresh:**
```bash
python fetch_player_stats.py
python fetch_team_stats.py
python fetch_game_totals.py
```

**Database check:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db');
cursor = conn.cursor();
cursor.execute('SELECT COUNT(*) FROM predictions WHERE game_date = date(\"now\")');
print(f'Picks today: {cursor.fetchone()[0]}')"
```

**Git sync:**
```bash
git status
git pull
git push
```

## 📖 Full Documentation

See `USER_GUIDE.md` for complete documentation

---

**Quick Access:** Pin this file to your desktop for fast reference!
