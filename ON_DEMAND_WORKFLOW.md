# On-Demand Workflow Guide
## No 24/7 Pipeline Required!

---

## Why On-Demand is Better

**24/7 Pipeline Downsides:**
- Your computer must run continuously
- Wastes energy overnight
- Unnecessary predictions at 2 AM when no games
- Complex scheduling overhead

**On-Demand Benefits:**
- ✓ Run predictions only when you need them
- ✓ Computer can sleep/shutdown when not in use
- ✓ Discord bot controls everything
- ✓ Still fully automated (just triggered manually)
- ✓ Faster iteration when testing

---

## Daily Workflow (On-Demand Style)

### Morning Routine (10 AM)

**Option 1: Discord Bot (Recommended)**

```
# In Discord:
!generate
```

This will:
1. Generate statistical predictions (~30 sec)
2. Generate ensemble predictions (~60 sec)
3. Save to database
4. Ready for viewing!

Then:
```
!picks T1-ELITE    # See top picks
!picks T2-STRONG   # See second tier
!count             # Quick summary
```

**Option 2: Command Line**

```bash
# In PowerShell:
python fresh_clean_predictions.py
python ensemble_predictions.py
```

### Check Results

```
# Discord:
!picks T1-ELITE

# Shows:
**T1-ELITE Picks - 2025-10-27**
1. Evgeni Malkin (PIT) vs OTT
   points O0.5
   Prob: 84.2% | Expected: 1.15

2. David Pastrnak (BOS) vs CBJ
   points O0.5
   Prob: 79.1% | Expected: 1.08
```

### Evening (Before Games)

If you want to refresh with latest stats:

```
# Discord:
!generate
```

That's it! Fresh predictions in 90 seconds.

---

## Weekly Maintenance

### Sunday Night (New Week Setup)

**Update Training Data:**

```bash
# 1. Fetch last week's game logs
python fetch_game_logs.py

# 2. Recompute rolling stats
python compute_rolling_stats.py

# 3. Retrain ML models with fresh data
python train_nhl_ml_v3.py
```

**Time:** ~10 minutes total

Then you're good for the whole week!

---

## Discord Bot Commands (Complete List)

### Generate Predictions

| Command | Description | Time |
|---------|-------------|------|
| `!generate` | Fresh predictions (stat + ensemble) | 90 sec |
| `!predict` | Statistical predictions only | 30 sec |
| `!run` | Full workflow (stats + prizepicks + edges) | 3 min |

### View Predictions

| Command | Description |
|---------|-------------|
| `!picks [tier]` | Show predictions by tier (T1-ELITE, T2-STRONG, T3-MARGINAL) |
| `!edge [min]` | Show PrizePicks edge plays (e.g., `!edge 15` = 15%+ edge) |
| `!raw [limit]` | Raw predictions from database |
| `!count` | Count predictions by tier |

### Export Data

| Command | Description |
|---------|-------------|
| `!sheet [table]` | Export table to CSV (predictions, player_stats, etc.) |
| `!sheetall` | Export all tables to CSV |

### Performance Tracking

| Command | Description |
|---------|-------------|
| `!grade` | Grade yesterday's predictions (accuracy check) |
| `!stats` | Show historical statistics |
| `!backup [date]` | Backup database |

### Help

| Command | Description |
|---------|-------------|
| `!commands` | Show all available commands |

---

## Typical Day Example

### Morning (10:00 AM)

```
You: !generate
Bot: Generating Fresh NHL Predictions...
Bot: This takes about 60-90 seconds...
Bot: [1/2] Running statistical model...
Bot: [OK] Statistical predictions generated
Bot: [2/2] Running ensemble model (stat + ML)...
Bot: [OK] Ensemble predictions generated
Bot: [OK] Fresh Predictions Ready!
Bot: Next Steps:
     !picks T1-ELITE - See top tier picks
     !picks T2-STRONG - See second tier
```

### View Picks

```
You: !picks T1-ELITE
Bot: **T1-ELITE Picks - 2025-10-27**
     1. Evgeni Malkin (PIT) vs OTT
        points O0.5
        Prob: 84.2% | Expected: 1.15
     ...
     Found 8 T1-ELITE picks
```

### Check Edge Plays (PrizePicks)

```
You: !edge 10
Bot: **Top Edge Plays - 2025-10-27**
     Minimum edge: 10%
     1. David Pastrnak
        points O0.5 [GOBLIN]
        Edge: +24.5% | Our: 79.1% | Market: 54.6%
        EV: +44.8% | Kelly: 12.3
     ...
```

### Evening (Before Games)

```
You: !generate     # Refresh one more time with latest stats
Bot: ...
You: !picks T1-ELITE
```

### Next Day (Check Accuracy)

```
You: !grade
Bot: **Grading Yesterday (2025-10-27)**
     T1-ELITE: 7/8 = 87.5% accuracy
     T2-STRONG: 12/15 = 80.0% accuracy
     Overall: 19/23 = 82.6% accuracy
     [OK] Above target (73-75%)!
```

---

## Manual Mode vs Pipeline Mode

### Manual On-Demand (Recommended)

**When to use:**
- Normal daily operation
- Testing/development
- Want control over timing
- Computer doesn't run 24/7

**How:**
1. Run `!generate` in Discord when you want predictions
2. Takes 90 seconds
3. View with `!picks`

### Pipeline Mode (Optional)

**When to use:**
- Want predictions auto-generated every day
- Computer runs 24/7 anyway
- Don't want to remember to run commands

**How:**
```bash
python data_pipeline_simple.py
```

This runs:
- 2:00 AM - Full data refresh + retrain
- 10:00 AM - Generate predictions
- Every 6h - Update stats
- Every 1h - Health check

**Note:** You still need to check Discord for picks!

---

## Comparison: On-Demand vs Pipeline

| Feature | On-Demand | Pipeline |
|---------|-----------|----------|
| **Computer uptime** | As needed | 24/7 required |
| **Power usage** | Minimal | Continuous |
| **Control** | Full control | Automated |
| **Flexibility** | Run anytime | Fixed schedule |
| **Setup complexity** | Simple | More complex |
| **Maintenance** | Manual triggers | Self-maintaining |
| **Speed to predictions** | 90 seconds | Waits for scheduled time |
| **Good for testing** | Excellent | Slower iteration |

**Recommendation:** Start with on-demand, switch to pipeline only if you want full automation.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  ON-DEMAND NHL PREDICTION WORKFLOW                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  DAILY (Morning):                                    │
│  → Discord: !generate                                │
│  → Discord: !picks T1-ELITE                          │
│  → Place bets on top picks                           │
│                                                      │
│  WEEKLY (Sunday):                                    │
│  → python fetch_game_logs.py                         │
│  → python compute_rolling_stats.py                   │
│  → python train_nhl_ml_v3.py                         │
│                                                      │
│  NEXT DAY:                                           │
│  → Discord: !grade                                   │
│  → Check accuracy                                    │
│                                                      │
│  TIME INVESTMENT:                                    │
│  → Daily: 2 minutes                                  │
│  → Weekly: 10 minutes                                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Advanced: Scheduled On-Demand

You can combine on-demand with light automation:

### Windows Task Scheduler

**Schedule `!generate` to run at 10 AM daily:**

1. Create `run_predictions.bat`:
```batch
@echo off
cd C:\Users\thoma\PrizePicks-Research-Lab
python fresh_clean_predictions.py
python ensemble_predictions.py
```

2. Open Task Scheduler
3. Create Basic Task
   - Name: "NHL Predictions"
   - Trigger: Daily at 10:00 AM
   - Action: Start a program
   - Program: `run_predictions.bat`

Now predictions auto-generate every morning, but your computer can still sleep at night!

### Python Scheduler (Lightweight)

Create `light_scheduler.py`:

```python
import schedule
import time
import subprocess
import sys

def generate_predictions():
    print("Generating predictions...")
    subprocess.run([sys.executable, "fresh_clean_predictions.py"])
    subprocess.run([sys.executable, "ensemble_predictions.py"])
    print("Done!")

# Only run during waking hours
schedule.every().day.at("10:00").do(generate_predictions)
schedule.every().day.at("18:00").do(generate_predictions)

print("Light scheduler running (10 AM & 6 PM only)")
print("Your computer can sleep between predictions!")

while True:
    schedule.run_pending()
    time.sleep(60)
```

Run when your computer is on:
```bash
python light_scheduler.py
```

---

## Troubleshooting

### No predictions generated

```
# Discord:
!generate

# If it fails, run manually:
python fresh_clean_predictions.py
python ensemble_predictions.py
```

### Want to see what's in database

```
# Discord:
!count    # See how many predictions by tier
!raw 20   # See raw predictions
```

### Check if models are trained

```
# Command line:
dir models\*latest*.pkl

# Should see:
# nhl_points_model_latest_v3.pkl
# nhl_shots_model_latest_v3.pkl
# feature_columns_latest_v3.pkl
```

### Retrain models if needed

```bash
python train_nhl_ml_v3.py
```

---

## Summary

**You don't need 24/7 operation!**

The on-demand workflow is:
1. **Simpler** - Discord command or quick script
2. **Faster** - Predictions in 90 seconds
3. **Flexible** - Run whenever you want
4. **Efficient** - Computer doesn't need to run all night

**The Discord bot is your control center:**
- `!generate` - Make predictions
- `!picks` - View picks
- `!grade` - Check accuracy

That's all you need for daily operation!

---

**Next:** See `EXPANSION_PLAN_NBA_NFL.md` for multi-sport roadmap

---

*Last Updated: 2025-10-27*
*Version: 1.0*
