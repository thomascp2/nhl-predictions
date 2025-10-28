# Smart NHL Picks System - Complete Guide

## What We Just Built

You now have a **bulletproof** picks generation system that:
- ✅ Auto-checks data freshness (only fetches if >2 hours old)
- ✅ Handles API failures gracefully (uses cached data)
- ✅ Never crashes completely (always generates some predictions)
- ✅ Auto-pushes to GitHub (view from anywhere)
- ✅ Shows data freshness in picks file
- ✅ Retry logic for failed API calls
- ✅ No timeout limits (won't fail if slow)
- ✅ Windows compatible (no emoji errors)

---

## How It Works

### Data Freshness Logic

```
Data Age < 2 hours  → Skip fetch, use cached data (90 seconds)
Data Age > 2 hours  → Fetch fresh data (3-5 minutes)
API fails?          → Use cached data, warn you, continue
```

### Failsafe Guarantees

1. **If NHL API is down** → Uses cached data, warns you
2. **If fetch times out** → Retries 2x, then uses cached data
3. **If some fetches fail** → Uses mix of fresh + cached
4. **If all fetches fail** → Uses all cached data, still generates picks
5. **If git push fails** → Picks saved locally, you can push manually

**Bottom line: It NEVER fails completely!**

---

## How to Use

### Option 1: Run Once Manually

```bash
python generate_picks_to_file.py
```

**What happens:**
1. Checks data age
2. Fetches fresh data only if >2 hours old
3. Generates predictions (both models)
4. Saves to `LATEST_PICKS.txt` + timestamped file
5. Auto-pushes to GitHub
6. Prints URLs to view online

**Time:** 90 seconds (fresh data) or 3-5 minutes (stale data)

---

### Option 2: Auto-Schedule All Day

```bash
python run_picks_throughout_day.py
```

**What happens:**
- Runs immediately
- Then auto-runs at: **9 AM, 12 PM, 3 PM, 6 PM**
- Each run checks data freshness
- Updates GitHub each time
- Stops after 6 PM
- No timeout limits (won't crash)

**How it optimizes:**
- **First run (9 AM)**: Fetches fresh data (3-5 min)
- **Later runs**: Uses fresh data from 9 AM (90 sec)
- **Before games**: Checks if data >2 hours old, refetches if needed

---

## What You'll See

### Example Output (Fresh Data)

```
================================================================================
SMART NHL PICKS GENERATOR
================================================================================

================================================================================
SMART DATA REFRESH
================================================================================
Last data update: 2025-10-27 10:37 PM
Data age: 0.5 hours

[FRESH] Data is fresh (less than 2 hours old)
Skipping data refresh - using cached data
================================================================================

================================================================================
GENERATING PREDICTIONS
================================================================================
Generating predictions...
Running statistical model...
Running ensemble model...
Predictions generated!

Fetching T1-ELITE picks from database...
Writing picks to PICKS_2025-10-27_10-38PM.txt...
Writing picks to LATEST_PICKS.txt...

Pushing to GitHub...
Successfully pushed to GitHub!

================================================================================
DONE!
================================================================================

Found 11 T1-ELITE picks for today

View picks online at:
https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
https://github.com/thomascp2/nhl-predictions/blob/main/PICKS_2025-10-27_10-38PM.txt
```

---

### Example Output (Stale Data - Fetching)

```
================================================================================
SMART DATA REFRESH
================================================================================
Last data update: 2025-10-27 06:00 PM
Data age: 4.5 hours

[STALE] Data is stale (more than 2 hours old)
Fetching fresh data from NHL API...

  Fetching Player Stats (2025-26)... (attempt 1/2)
  [SUCCESS] Player Stats (2025-26) updated

  Fetching Goalie Stats... (attempt 1/2)
  [SUCCESS] Goalie Stats updated

================================================================================
DATA REFRESH COMPLETE: 2/2 successful
================================================================================

[SUCCESS] All data updated - predictions will use fresh data
```

---

### Example Output (API Failure - Graceful)

```
================================================================================
SMART DATA REFRESH
================================================================================
Last data update: 2025-10-27 06:00 PM
Data age: 4.5 hours

[STALE] Data is stale (more than 2 hours old)
Fetching fresh data from NHL API...

  Fetching Player Stats (2025-26)... (attempt 1/2)
  [WARNING] Player Stats (2025-26) timed out
  Retrying...
  Fetching Player Stats (2025-26)... (attempt 2/2)
  [FAILED] Player Stats (2025-26) failed after 2 attempts - using cached data

  Fetching Goalie Stats... (attempt 1/2)
  [SUCCESS] Goalie Stats updated

================================================================================
DATA REFRESH COMPLETE: 1/2 successful
================================================================================

[WARNING] Some data fetches failed - predictions will use mixed data
(Some fresh, some cached)

================================================================================
GENERATING PREDICTIONS
================================================================================
...continues normally...
```

---

## Picks File Format

```
================================================================================
NHL PREDICTIONS - T1-ELITE PICKS ONLY
Generated: 2025-10-27 10:38 PM
Data Age: 0.5 hours old (Updated: 10:37 PM) - [VERY FRESH]
================================================================================

TOTAL T1-ELITE PICKS: 11
Accuracy Target: 73-75%

--------------------------------------------------------------------------------

PICK #1
Player: Connor McDavid (EDM vs VAN)
Prop: Points - Line: 1.5
Probability: 72.3% | EV: 1.45
Model: ensemble_v1
Reasoning: High historical performance vs opponent, averaging 1.8 PPG in last 10
--------------------------------------------------------------------------------
...
```

### Data Freshness Indicators

- `[VERY FRESH]` - Less than 1 hour old
- `[FRESH]` - 1-3 hours old
- `[STALE]` - More than 3 hours old
- `[UNKNOWN]` - Can't determine age

---

## Access From Anywhere

**Bookmark this on your phone:**
https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt

**View all timestamped picks:**
https://github.com/thomascp2/nhl-predictions

---

## Daily Workflow

### Morning (8:45 AM)

```bash
python run_picks_throughout_day.py
```

- Minimize the window
- Go to work/breakfast
- Script runs in background

### Throughout Day

- **At work:** Open GitHub bookmark on phone
- **Before betting:** Refresh page for latest picks
- **Focus on:** T1-ELITE picks with highest probability
- **Check:** Data freshness indicator

### Evening (After 6 PM)

- Script stops automatically
- Close the window
- Check final picks before late games

---

## Troubleshooting

### Q: Data keeps showing as STALE?
**A:** Your fetch scripts might be failing. Check internet connection or run fetch scripts manually:
```bash
python fetch_2025_26_stats.py
python fetch_goalie_stats.py
```

### Q: GitHub push failed?
**A:** Two reasons:
1. **No changes** (picks identical to last run) - This is fine, picks are saved locally
2. **Git error** - Push manually: `git add LATEST_PICKS.txt PICKS_*.txt && git commit -m "Update picks" && git push`

### Q: Script taking forever?
**A:** Probably fetching fresh data (3-5 min). Check output - should show "Fetching Player Stats..."

### Q: All picks showing STALE data warning?
**A:** API might be down. Picks are still generated from cached data (might be outdated but still useful).

### Q: No T1-ELITE picks found?
**A:** Light day or models aren't confident. Check T2-STRONG picks or run again closer to game time.

---

## Advanced: Manual Data Refresh

If you want to force fresh data without waiting:

```bash
python smart_data_refresh.py
```

This will:
- Always fetch fresh data (ignores 2-hour threshold)
- Show detailed fetch progress
- Update database
- Don't generate predictions (just refreshes data)

Then run:
```bash
python generate_picks_to_file.py
```

---

## System Architecture

```
┌─────────────────────────────────────┐
│  generate_picks_to_file.py          │
│  (Main entry point)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  smart_data_refresh.py              │
│  - Check data age                   │
│  - Fetch if >2 hours old            │
│  - Retry failed fetches 2x          │
│  - Graceful failure handling        │
└──────────────┬──────────────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
┌──────────┐      ┌──────────┐
│ fetch_   │      │ fetch_   │
│ 2025_26_ │      │ goalie_  │
│ stats.py │      │ stats.py │
└──────────┘      └──────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Prediction Models                  │
│  - fresh_clean_predictions.py       │
│  - ensemble_predictions.py          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Output                             │
│  - LATEST_PICKS.txt                 │
│  - PICKS_2025-10-27_10-38PM.txt     │
│  - Auto-push to GitHub              │
└─────────────────────────────────────┘
```

---

## Performance

| Scenario | Time | Data Freshness |
|----------|------|----------------|
| Fresh data (<2 hrs) | 90 seconds | Cached |
| Stale data (>2 hrs) | 3-5 minutes | Fresh from API |
| API timeout (1 fetch) | 3-4 minutes | Mixed (1 fresh, 1 cached) |
| API totally down | 90 seconds | All cached |

---

## File Summary

| File | Purpose | When to Use |
|------|---------|-------------|
| `generate_picks_to_file.py` | Smart picks generator | Anytime you want picks |
| `run_picks_throughout_day.py` | Auto-scheduler | Morning (runs all day) |
| `smart_data_refresh.py` | Data freshness manager | Automatic (called by generator) |
| `LATEST_PICKS.txt` | Current picks | Bookmark this URL |
| `PICKS_2025-10-27_10-38PM.txt` | Timestamped history | Track picks over time |

---

## Key Benefits Over Old System

**Old System:**
- ❌ Run 24/7 or manually fetch data each time
- ❌ No freshness checking (always fetched, slow)
- ❌ Crashes if API down
- ❌ No retry logic
- ❌ Hard to access remotely

**New Smart System:**
- ✅ Only fetches when needed (smart!)
- ✅ Checks freshness automatically
- ✅ Never crashes (graceful failures)
- ✅ Retries failed fetches
- ✅ Auto-pushes to GitHub (access anywhere)
- ✅ Shows data age in picks file
- ✅ Optimized for speed (90 sec when fresh)

---

## Production Status

```
✅ Smart data refresh       READY
✅ Graceful failure handling READY
✅ GitHub auto-push          READY
✅ Windows compatibility     READY
✅ Retry logic               READY
✅ Data freshness tracking   READY
✅ Mobile access (GitHub)    READY
✅ Auto-scheduling           READY
✅ No emoji errors           READY

STATUS: PRODUCTION READY 🚀
```

---

**You now have a professional-grade, bulletproof NHL picks system!**

**Tomorrow morning:**
1. Run `python run_picks_throughout_day.py`
2. Bookmark: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
3. Check picks from anywhere
4. Win!
