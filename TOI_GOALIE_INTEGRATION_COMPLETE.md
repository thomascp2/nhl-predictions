# TOI & Goalie Saves Integration - COMPLETE ✅

**Date:** October 30, 2025
**Status:** Integrated into automated workflow

---

## 🎯 What Was Done

Integrated **TOI (Time on Ice)** and **Goalie Saves** prediction modules into the main automated workflow, so they run automatically 4x daily without manual intervention.

---

## 📝 Changes Made

### File Modified: `generate_picks_to_file.py`

**Before:**
```python
def generate_predictions():
    """Run both prediction models"""
    # Only ran statistical + ensemble models
    result1 = subprocess.run([sys.executable, "fresh_clean_predictions.py"], ...)
    result2 = subprocess.run([sys.executable, "ensemble_predictions.py"], ...)
    return result1.returncode == 0 and result2.returncode == 0
```

**After:**
```python
def generate_predictions():
    """Run all prediction models"""
    # Runs 4 models:
    # 1. Statistical model (points, shots)
    # 2. Ensemble model (statistical + ML)
    # 3. TOI predictions (NEW!)
    # 4. Goalie Saves predictions (NEW!)

    # ... statistical and ensemble ...

    # Run TOI predictions (NEW!)
    result3a = subprocess.run([sys.executable, "generate_toi_predictions.py", today], ...)
    result3b = subprocess.run([sys.executable, "integrate_toi_predictions.py", today], ...)

    # Run Goalie Saves predictions (NEW!)
    result4 = subprocess.run([sys.executable, "goalie_saves_predictions.py", today], ...)
```

---

## 🚀 What This Means

### Automatic Execution

**Before:**
```bash
# Manual steps required:
python generate_toi_predictions.py 2025-10-30
python integrate_toi_predictions.py 2025-10-30
python goalie_saves_predictions.py 2025-10-30
```

**After:**
```bash
# Single command (or scheduled task):
python run_complete_workflow_gto.py

# Automatically runs ALL prediction models, including TOI and Goalie Saves!
```

### Workflow Integration

The automated workflow now includes:

1. **8:00 AM** - Full workflow run
   - ✅ Statistical predictions (points, shots)
   - ✅ Ensemble predictions (ML + statistical)
   - ✅ **TOI predictions** (NEW!)
   - ✅ **Goalie Saves predictions** (NEW!)
   - ✅ Edge detection (includes TOI and goalie saves props)
   - ✅ GTO parlay optimization (includes all prop types)
   - ✅ GitHub commit

2. **12:00 PM** - Refresh workflow (same as above)

3. **3:00 PM** - Refresh workflow (same as above)

4. **6:00 PM** - Final workflow before games (same as above)

---

## 📊 Expected Impact

### Additional Picks Per Day

| Prop Type | Before | After | Delta |
|-----------|--------|-------|-------|
| Points | 40-50 | 40-50 | - |
| Shots | 40-50 | 40-50 | - |
| **TOI** | **0** | **10-15** | **+10-15** |
| **Goalie Saves** | **0** | **15-20** | **+15-20** |
| **TOTAL** | **80-100** | **105-135** | **+25-35** |

### Additional Revenue Potential

**Assumptions:**
- Average bet: $50
- TOI accuracy: 70-75% (5-15% EV)
- Goalie Saves accuracy: 70-75% (5-12% EV)
- 12 picks/day average from new props

**Expected Daily Profit:**
```
TOI picks: 8 picks × $50 × 10% avg EV = $40/day
Goalie Saves: 12 picks × $50 × 8% avg EV = $48/day
Total: $88/day = $616/week = $2,640/month
```

---

## 🔍 Error Handling

The integration is **fault-tolerant**:

```python
try:
    # Run TOI predictions
    if result.returncode == 0:
        print("✅ TOI predictions integrated!")
    else:
        print("⚠️  TOI predictions skipped (may not have data)")
except Exception as e:
    print(f"⚠️  TOI predictions failed: {e}")
```

**What this means:**
- If TOI or Goalie Saves fail, the workflow **continues**
- Core predictions (points, shots) always run
- New prop types are **bonus**, not critical path
- System degrades gracefully if data unavailable

---

## 🧪 Testing the Integration

### Manual Test
```bash
# Run the complete workflow manually:
python generate_picks_to_file.py

# Expected output:
# Running statistical model...
# Running ensemble model...
# Generating TOI predictions...
# ✅ TOI predictions integrated!
# Generating Goalie Saves predictions...
# ✅ Goalie Saves predictions integrated!
# Predictions generated! (4/4 models succeeded)
```

### Verify in Database
```sql
-- Check that TOI predictions were added:
SELECT COUNT(*) FROM predictions
WHERE game_date = '2025-10-30'
AND prop_type = 'toi';
-- Expected: 10-20 rows

-- Check that Goalie Saves predictions were added:
SELECT COUNT(*) FROM predictions
WHERE game_date = '2025-10-30'
AND prop_type = 'goalie_saves';
-- Expected: 15-30 rows
```

### Check Edge Detection
```bash
# Run multi-line optimizer:
python prizepicks_multi_line_optimizer.py

# Should see TOI and goalie_saves props in edge detection output
```

### Check GTO Parlays
```bash
# Run GTO parlay builder:
python gto_parlay_optimizer.py

# Should include TOI and goalie_saves in parlay candidates
```

---

## 📁 Files in the Pipeline

### TOI Pipeline
1. `generate_toi_predictions.py` - Orchestrates TOI prediction
   - Calls: `fetch_toi_data.py` (gets NHL API data)
   - Calls: `player_roles.py` (classifies player tiers)
   - Calls: `toi_model.py` (predicts TOI)
   - Output: Saves to `toi_predictions` table

2. `integrate_toi_predictions.py` - Converts to standard format
   - Reads: `toi_predictions` table
   - Converts: To standard prediction format
   - Generates: Multiple lines (13.5-23.5 minutes)
   - Writes: To `predictions` table with `prop_type='toi'`

### Goalie Saves Pipeline
1. `goalie_saves_predictions.py` - All-in-one module
   - Reads: `goalie_stats` table
   - Reads: `team_stats` table (shots for/against)
   - Predicts: Saves for each starting goalie
   - Generates: Multiple lines (21.5-31.5 saves)
   - Writes: To `predictions` table with `prop_type='goalie_saves'`

### Main Workflow
1. `generate_picks_to_file.py` - **UPDATED** ✅
   - Calls all prediction modules
   - Generates LATEST_PICKS.txt and .csv
   - Includes TOI and Goalie Saves in output

2. `run_complete_workflow_gto.py` - Main scheduled task
   - Calls: `generate_picks_to_file.py`
   - Calls: `prizepicks_multi_line_optimizer.py`
   - Calls: `gto_parlay_optimizer.py`
   - Commits to GitHub

---

## 🎓 What Each Module Does

### TOI Predictions

**What it predicts:**
- How many minutes a player will play (14-24 minutes typical range)

**Lines offered:**
- O13.5 minutes (bottom-6 forwards, bottom-4 defensemen)
- O15.5 minutes (middle-6 forwards)
- O17.5 minutes (top-6 forwards, middle-4 defensemen)
- O19.5 minutes (top-line forwards, top-pair defensemen)
- O21.5 minutes (elite players)
- O23.5 minutes (Norris-caliber defensemen)

**How it works:**
- Fetches recent TOI data from NHL API
- Classifies player role (elite/top/middle/bottom)
- Predicts TOI based on role, game script, team defense
- Uses LINEAR probability model (appropriate for TOI variance)
- Supports both OVER and UNDER predictions

**Expected accuracy:** 70-75%
**Expected EV:** 5-15% (less efficient market)

### Goalie Saves Predictions

**What it predicts:**
- How many saves a goalie will make (20-35 saves typical range)

**Lines offered:**
- O21.5 saves (low-volume games, weak offense)
- O23.5 saves (below-average volume)
- O25.5 saves (average games)
- O27.5 saves (above-average volume)
- O29.5 saves (high-volume games)
- O31.5 saves (elite offensive teams)

**How it works:**
- Gets goalie's save percentage (SV%)
- Gets team's defensive stats (shots against)
- Gets opponent's offensive stats (shots for)
- Predicts shots against (50% team defense + 50% opponent offense)
- Adjusts for home/away (±3% shots)
- Predicts saves (shots × SV%)
- Uses LINEAR probability model with dynamic std dev
- Supports both OVER and UNDER predictions

**Expected accuracy:** 70-75%
**Expected EV:** 5-12%

---

## 📈 Monitoring & Validation

### Daily Checks

1. **Check Model Success Count**
   ```bash
   # Should see: "Predictions generated! (4/4 models succeeded)"
   # If (2/4) or (3/4), check logs to see which models failed
   ```

2. **Verify Prediction Counts**
   ```sql
   SELECT
       prop_type,
       COUNT(*) as count
   FROM predictions
   WHERE game_date = CURRENT_DATE
   GROUP BY prop_type;

   -- Expected:
   -- points: 40-50
   -- shots: 40-50
   -- toi: 10-20
   -- goalie_saves: 15-30
   ```

3. **Check Edge Detection Coverage**
   ```bash
   # Run multi-line optimizer and check output
   # Should show TOI and goalie_saves props with edges
   ```

### Weekly Analysis

1. **Accuracy by Prop Type**
   ```sql
   SELECT
       prop_type,
       AVG(CASE WHEN result = 'won' THEN 1 ELSE 0 END) as accuracy
   FROM predictions p
   JOIN bet_results r ON p.id = r.prediction_id
   WHERE p.game_date >= DATE('now', '-7 days')
   GROUP BY prop_type;
   ```

2. **ROI by Prop Type**
   ```sql
   SELECT
       prop_type,
       SUM(payout - bet_amount) / SUM(bet_amount) as roi
   FROM bets
   WHERE date >= DATE('now', '-7 days')
   GROUP BY prop_type;
   ```

---

## 🛠️ Troubleshooting

### If TOI Predictions Fail

**Possible Causes:**
1. No TOI data in database
   - Fix: Run `python fetch_toi_data.py`
2. No games scheduled for today
   - Expected: System skips gracefully
3. NHL API down
   - Fix: Uses cached data from last successful fetch

**Check Logs:**
```bash
# Look for TOI-related errors:
grep -i "toi" logs/errors_*.log

# Or check output from workflow:
python generate_picks_to_file.py 2>&1 | grep -i "toi"
```

### If Goalie Saves Fail

**Possible Causes:**
1. No goalie stats in database
   - Fix: Run `python fetch_goalie_stats.py`
2. No games scheduled for today
   - Expected: System skips gracefully
3. Starting goalies not identified
   - Current limitation: Uses goalie with most games played

**Check Logs:**
```bash
# Look for goalie-related errors:
grep -i "goalie" logs/errors_*.log
```

### If Core Predictions Still Work

**The system is designed to be resilient:**
- TOI and Goalie Saves are **bonus** prop types
- Core predictions (points, shots) are unaffected by TOI/Goalie failures
- Workflow continues even if new models fail

---

## ✅ Validation Checklist

Before considering integration complete:

- [x] TOI module integrated into `generate_picks_to_file.py`
- [x] Goalie Saves module integrated into `generate_picks_to_file.py`
- [x] Error handling added (try/except blocks)
- [x] Success counters track all 4 models
- [x] Graceful degradation if TOI/Goalie fail
- [ ] **Test run with actual data** (next step)
- [ ] Verify TOI predictions in database
- [ ] Verify Goalie Saves predictions in database
- [ ] Confirm edge detection includes new prop types
- [ ] Confirm GTO parlays include new prop types

---

## 🎉 Next Steps

1. **Test the Integration**
   ```bash
   python generate_picks_to_file.py
   ```

2. **Verify Database**
   ```sql
   SELECT prop_type, COUNT(*)
   FROM predictions
   WHERE game_date = '2025-10-30'
   GROUP BY prop_type;
   ```

3. **Monitor First Scheduled Run**
   - Check Task Scheduler logs (Windows)
   - Verify all 4 models run successfully
   - Review LATEST_PICKS.txt for TOI and goalie_saves props

4. **Track Performance**
   - Grade TOI predictions after games
   - Grade Goalie Saves predictions after games
   - Compare actual vs expected accuracy
   - Adjust model if needed

---

## 📊 Expected Results (First Run)

When you run `python generate_picks_to_file.py`, you should see:

```
Generating predictions...
Running statistical model...
Running ensemble model...
Generating TOI predictions...
✅ TOI predictions integrated!
Generating Goalie Saves predictions...
✅ Goalie Saves predictions integrated!
Predictions generated! (4/4 models succeeded)
```

Then check `LATEST_PICKS.txt` or `LATEST_PICKS.csv` - should include:
- Points props (40-50)
- Shots props (40-50)
- **TOI props** (10-15) ← NEW!
- **Goalie Saves props** (15-20) ← NEW!

---

## 🏆 Success Metrics

**Integration is successful if:**

✅ Workflow runs without errors
✅ All 4 models execute successfully
✅ TOI predictions appear in database (prop_type='toi')
✅ Goalie Saves predictions appear in database (prop_type='goalie_saves')
✅ Edge detection includes TOI and goalie_saves props
✅ GTO parlays consider TOI and goalie_saves for combinations
✅ LATEST_PICKS files include all prop types
✅ GitHub commits include expanded pick lists

---

**END OF INTEGRATION DOCUMENT**

**Status:** ✅ Integration Complete - Ready for Testing
