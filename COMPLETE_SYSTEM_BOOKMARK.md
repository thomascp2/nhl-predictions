# Points Prediction (Logistic Model)
if ppg >= 1.5:
    prob = 0.95
elif ppg >= 1.0:
    prob = 0.70 + (ppg - 1.0) * 0.5
elif ppg >= 0.5:
    prob = 0.50 + (ppg - 0.5) * 0.4
else:
    prob = ppg * 1.0

# Shots Prediction (Normal Distribution)
expected = sog_per_game * 1.05  # home boost
std_dev = expected * 0.40
prob = 1 - norm.cdf(2.5, expected, std_dev)
```

**Features Used:**
- ✅ Season averages (PPG, SOG/G)
- ✅ Home/away adjustment (±5%)
- ❌ NO rolling stats (cleared)
- ❌ NO opponent adjustments (defaulted to 1.0x)
- ❌ NO goalie adjustments (defaulted to 1.0x)

---

## 🎯 **WHAT'S WORKING**

### ✅ **Data Pipeline:**
- Fetches 2025-26 season stats from NHL API
- 100 players loaded
- Updates player_stats table
- Season-based predictions (not using old data)

### ✅ **Prediction Engine:**
- Generates realistic predictions
  - Malkin: 1.63 expected points ✅
  - Pastrnak: 3.52 expected shots ✅
  - NOT 236 expected shots ❌
- Outputs 26 predictions for 2 games
- Tiers: T1-ELITE (70%+), T2-STRONG (60-70%), T3-MARGINAL (<60%)

### ✅ **Discord Integration:**
- `!run` command works
- Shows formatted picks
- Real-time updates

### ✅ **Database:**
- SQLite working
- Clean predictions table
- No corrupt data

---

## 🚨 **WHAT'S NOT WORKING / TODO**

### ❌ **Opponent Adjustments:**
- Always shows `[Opp: 1.00x]`
- team_stats table empty or not being queried
- **Need:** Populate team defensive stats

### ❌ **Goalie Adjustments:**
- Always shows `[Goalie: 1.00x]`
- goalie_stats table empty or not being queried
- **Need:** Fetch goalie stats, confirm starters

### ❌ **Rolling Stats:**
- Cleared (old stale data)
- Not being calculated
- **Need:** Rebuild with game logs

### ❌ **Game Logs:**
- player_game_logs table empty
- **Critical for ML:** Need game-by-game data for training

### ❌ **Automated Data Pipeline:**
- Manual refresh only
- No hourly/daily automation
- **Need:** Schedule jobs

### ❌ **ML Models:**
- Not built yet
- Using statistical models only
- **Next phase:** XGBoost implementation

### ❌ **PrizePicks Integration:**
- No edge plays showing
- Needs API key or scraping
- **Low priority:** Manual comparison works

---

## 🏆 **RECENT FIXES (What We Solved Today)**

### **Problem 1: Wrong Season Data**
**Issue:** Using 2024-25 season (80 games old data)
**Fix:** Created `fetch_2025_26_stats.py` to fetch current season
**Result:** ✅ Now using 2025-26 with 10 games played

### **Problem 2: Insane Expected Values**
**Issue:** Predicted 236 shots (using total instead of per-game)
**Fix:** Fixed calculation in `enhanced_predictions_FIXED_FINAL_FINAL.py`
**Result:** ✅ Now predicts 3.5 shots (realistic)

### **Problem 3: Stale Rolling Stats**
**Issue:** Rolling stats from 2024-25 overriding season averages
**Fix:** `clear_rolling_stats.py` deleted all rolling stats
**Result:** ✅ Now uses season averages directly

### **Problem 4: Database Had Duplicate Bad Predictions**
**Issue:** Discord showing old crazy predictions
**Fix:** `fresh_clean_predictions.py` clears and regenerates
**Result:** ✅ Clean predictions, realistic values

---

## 📈 **PERFORMANCE METRICS**

### **Current Results:**
- **Games:** 2
- **Predictions:** 26
- **Top Pick:** Malkin Points O0.5 (95% prob)
- **Accuracy:** TBD (need to grade after games)

### **Expected Performance (Statistical Model):**
- T1-ELITE: 65-70% hit rate
- T2-STRONG: 60-65% hit rate
- T3-MARGINAL: 55-60% hit rate
- Overall: ~62% hit rate

### **Target Performance (With ML):**
- T1-ELITE: 70-75% hit rate
- T2-STRONG: 65-70% hit rate
- Overall: ~68% hit rate
- ROI: 15-25%

---

## 🚀 **NEXT PHASE: ML INTEGRATION**

### **Phase 1: Data Collection (Week 1)**
1. Build `fetch_game_logs.py` - Get game-by-game data
2. Populate `player_game_logs` table - 2 seasons of data
3. Build `compute_rolling_stats.py` - Calculate L5/L10/L20
4. Fetch team defensive stats
5. Fetch goalie stats

### **Phase 2: ML Model Training (Week 2-3)**
1. Create `train_nhl_ml.py` - XGBoost classifier
2. Train on 2 seasons of data (~15,000 games)
3. Features: season avg, rolling avg, opponent, goalie, home/away
4. Target: P(points > 0.5), P(shots > 2.5)
5. Achieve 65%+ accuracy on test set

### **Phase 3: Integration (Week 4)**
1. Replace statistical model with ML predictions
2. A/B test: Run both models, compare
3. Automated nightly retraining
4. Gradual rollout

### **Phase 4: Automation (Week 5-6)**
1. Scheduled data fetching (hourly)
2. Nightly grading + retraining
3. Auto-generate predictions
4. Auto-post to Discord

---

## 🔧 **KEY SCRIPTS TO PRESERVE**

### **✅ KEEP (Production):**
```
enhanced_predictions_FIXED_FINAL_FINAL.py  ← Core engine
fresh_clean_predictions.py                  ← Generate + save
daily_run.py                                ← Daily workflow
fetch_2025_26_stats.py                      ← Data fetching
discord_bot.py                              ← Discord interface
grade_predictions.py                        ← Grading
dashboard.py                                ← Performance
clear_rolling_stats.py                      ← Utility
```

### **🔍 KEEP (Debugging):**
```
debug_pastrnak.py
check_seasons.py
check_rolling_override.py
investigate_sanderson_FIXED.py
multi_line_ev_calculator.py
```

### **📖 KEEP (Docs):**
```
COMPLETE_SYSTEM_BOOKMARK.md  ← This file
CLAUDE_CODE_HANDOFF.md        ← For Claude Code
schema.sql
2025_NHL_Schedule.csv
```

### **❌ ARCHIVE (Old/Broken):**
```
enhanced_predictions.py                    ← Has bugs
enhanced_predictions_CURRENT_SEASON.py     ← Uses rolling stats wrong
update_to_current_season.py                ← Manual only
diagnose_opponent_goalie.py                ← One-time debug
fix_opponent_goalie.py                     ← One-time fix