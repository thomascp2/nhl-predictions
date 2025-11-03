# MARKET VS MODEL BETTING SYSTEM
**Find +EV Edges Like Professional Bettors**

Last Updated: November 2, 2025

---

## 🎯 **WHAT THIS DOES**

Compares **your model's predictions** to **PrizePicks market lines** to find bets where you have an edge.

**Example:**
```
YOUR MODEL:
  Player: Connor McDavid
  Prop: Shots OVER 3.5
  Probability: 85%

MARKET (PrizePicks):
  Available Lines: 2.5, 3.5, 4.5
  Best Match: 3.5 (EXACT)
  Implied Probability: ~47% (2x multiplier)

EDGE: 85% - 47% = +38% EDGE ✅ BET THIS!
```

---

## 💡 **WHY THIS MATTERS**

### **Professional Betting = Finding Market Inefficiencies**

**Market is RIGHT most of the time:**
- Sportsbooks employ PhDs in statistics
- They have more data than you
- Line movement reflects sharp money

**BUT sometimes YOUR MODEL sees something the market doesn't:**
- Recent player trends
- Specific matchup advantages
- Situational factors market hasn't priced in

**When you have an edge (Model > Market) = +EV Bet**

---

## 🔍 **UNDERSTANDING MULTIPLE LINES**

### **PrizePicks Offers Multiple Lines Per Prop:**

```
Connor McDavid Shots:
├── OVER 2.5 - 2.0x payout (easier to hit)
├── OVER 3.5 - 2.5x payout (medium)
└── OVER 4.5 - 3.5x payout (harder to hit)
```

**Why This Matters:**
- **Easier line** (2.5) = Higher probability, lower payout
- **Harder line** (4.5) = Lower probability, higher payout
- **Medium line** (3.5) = Balanced risk/reward

**Our System:**
1. Looks at ALL available lines
2. Finds the line CLOSEST to what your model predicts
3. Calculates edge for that SPECIFIC line
4. Shows you which exact line to bet on PrizePicks

---

## 🚀 **HOW TO USE IT**

### **ONE-COMMAND WORKFLOW:**

```bash
python market_vs_model.py
```

**What it does:**
1. ✅ Gets your model predictions from database
2. ✅ Fetches current PrizePicks lines
3. ✅ Compares model vs market for each player
4. ✅ Calculates edges (Model Prob - Market Prob)
5. ✅ Shows only significant edges (≥5% by default)

---

### **STEP-BY-STEP MANUAL WORKFLOW:**

#### **Step 1: Generate Predictions** (if needed)
```bash
python RUN_DAILY_PICKS.py
```

#### **Step 2: Fetch Current PrizePicks Lines**
```bash
python fetch_prizepicks_current_lines.py
```

This fetches:
- All NHL player props from PrizePicks API
- ALL lines for each prop (not just one)
- Saves to database for comparison

#### **Step 3: Find Edges**
```bash
python market_vs_model.py 2025-11-03
```

Shows you:
- Players where your model has an edge
- Exact line to bet on PrizePicks
- Edge percentage
- Expected Value

---

## 📊 **INTERPRETING RESULTS**

### **Example Output:**

```
BET #1 - T1-ELITE (Edge: +38.0%)
Player:  Connor McDavid (EDM vs STL)
Prop:    SHOTS OVER 3.5

YOUR MODEL:
  Line:        3.5
  Probability: 85.0%
  Reasoning:   4.2 SOG/G average, favorable matchup

MARKET (PrizePicks) - AVAILABLE LINES:
  All Lines:   2.5, 3.5, 4.5
  Best Match:  3.5 (EXACT)
  Probability: 47.0%
  Multiplier:  2.0x

EDGE ANALYSIS:
  Your Edge:   +38.0%
  Expected EV: $38.00 per $100 bet
  Rating:      HUGE EDGE - MAX BET
```

### **What This Means:**

1. **Your Model:** 85% confident McDavid gets OVER 3.5 shots
2. **Market (PrizePicks):** Implies 47% (from 2x multiplier)
3. **Edge:** You're 38% MORE confident than the market
4. **EV:** You expect to profit $38 per $100 bet long-term
5. **Action:** ✅ **BET THIS** - You have a huge edge

---

## 🎲 **EDGE RATING GUIDE**

| Edge % | Rating | Action | Bet Size |
|--------|--------|--------|----------|
| ≥20% | **HUGE EDGE** | MAX BET | 2-3% of bankroll |
| 10-19% | **STRONG EDGE** | BET THIS | 1-2% of bankroll |
| 5-9% | **SMALL EDGE** | Consider | 0.5-1% of bankroll |
| 0-4% | **MARGINAL** | Skip | Too close to market |
| <0% | **NEGATIVE** | NEVER BET | Market is sharper |

---

## ⚠️ **LINE MATCHING EXPLAINED**

### **Scenario 1: EXACT MATCH (Best)**

```
Your Model: McDavid OVER 3.5 shots - 85% prob
Market Lines: 2.5, 3.5, 4.5
Best Match: 3.5 (EXACT)
```

✅ **Perfect comparison** - model and market agree on the line

---

### **Scenario 2: CLOSEST MATCH (Good)**

```
Your Model: Matthews OVER 3.5 shots - 80% prob
Market Lines: 2.5, 4.5 (no 3.5 available)
Best Match: 4.5 (CLOSEST)
```

⚠️ **Acceptable** - comparing to closest available line (4.5)

**Warning shown:** Model line (3.5) differs from market line (4.5)

---

### **Scenario 3: LARGE MISMATCH (Be Careful)**

```
Your Model: Bedard OVER 2.5 shots - 75% prob
Market Lines: 4.5, 5.5 (no 2.5 available)
Best Match: 4.5 (CLOSEST)
```

❌ **Risky** - large difference between model (2.5) and market (4.5)

**Action:** Edge calculation may be inaccurate, proceed with caution

---

## 💰 **BANKROLL MANAGEMENT**

### **Kelly Criterion (Recommended):**

```
Bet Size = (Edge × Bankroll) / Odds

Example:
- Edge: 38%
- Bankroll: $1,000
- Odds: 2x (even money)
- Bet Size: (0.38 × $1000) / 2 = $190
- Conservative: Use 25% Kelly = $47.50
```

### **Fixed Percentage (Simpler):**

| Edge | Bet % of Bankroll |
|------|-------------------|
| ≥20% | 2-3% |
| 10-19% | 1-2% |
| 5-9% | 0.5-1% |

**Example with $1,000 bankroll:**
- 38% edge = 2% bet = $20
- 15% edge = 1.5% bet = $15
- 7% edge = 0.75% bet = $7.50

---

## 📈 **EXPECTED RESULTS**

### **Volume:**
- **Most days:** 0-3 significant edges (≥10%)
- **Good days:** 3-8 significant edges
- **Rare days:** 10+ significant edges (market is way off)

### **Quality:**
- **≥20% edges:** 1-2 per week (rare, bet heavy)
- **10-19% edges:** 3-5 per week (bet standard)
- **5-9% edges:** 10-15 per week (bet small or skip)

### **Accuracy:**
- **If your model is calibrated correctly:** Edges should hold over time
- **Track results:** Compare actual hit rate to predicted probability
- **Adjust if needed:** If model is overconfident, reduce edge estimates

---

## 🛠️ **ADVANCED USAGE**

### **Adjust Minimum Edge:**

```bash
# Only show edges ≥10% (fewer, higher quality)
python market_vs_model.py --min-edge 10.0

# Show all edges ≥1% (more picks, some marginal)
python market_vs_model.py --min-edge 1.0
```

### **Filter to Stars Only:**

```bash
# Only analyze star players (default)
python market_vs_model.py --stars-only

# Analyze all players
python market_vs_model.py --all-players
```

### **Specific Date:**

```bash
python market_vs_model.py 2025-11-03
```

---

## 📝 **EXAMPLE WORKFLOW (Daily)**

### **Morning (10 AM):**

```bash
# 1. Generate predictions
python RUN_DAILY_PICKS.py

# 2. Fetch PrizePicks lines
python fetch_prizepicks_current_lines.py

# 3. Find edges
python market_vs_model.py
```

**Result:** List of 0-10 bets with positive edges

### **Afternoon (3 PM):**

```bash
# Re-fetch lines (they may have moved)
python fetch_prizepicks_current_lines.py

# Re-run edge finder
python market_vs_model.py
```

**Result:** Updated edges (some may have disappeared if lines moved)

### **Evening (6 PM):**

```bash
# Final check before games start
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

**Action:** Place bets on any remaining edges ≥10%

---

## ⚠️ **IMPORTANT CAVEATS**

### **1. Market is Usually Right**
- Don't bet just because you have a small edge
- Market has more information than you
- Respect the market, only bet when edge is significant

### **2. Your Model Must Be Calibrated**
- If model says 80%, player should hit 80% of the time
- Track your results to validate calibration
- Adjust probabilities if model is over/under confident

### **3. PrizePicks Juice**
- 2x multiplier ≠ 50% probability
- PrizePicks takes ~5-10% juice
- Actual break-even is ~47% for 2x multiplier
- Our system accounts for this in calculations

### **4. Lines Move**
- PrizePicks lines change throughout the day
- Edge at 10 AM may be gone by 6 PM
- Re-fetch lines before placing bets

### **5. Sample Size Matters**
- Don't chase short-term results
- Need 100+ bets to validate edge
- Variance is real - expect losing streaks

---

## 🎓 **LEARNING FROM RESULTS**

### **Track Your Bets:**

Create a spreadsheet with:
- Date
- Player
- Prop
- Line
- Your Model Prob
- Market Prob
- Edge %
- Result (W/L)

### **After 50+ Bets, Analyze:**

**Question 1:** Are your edges real?
- If 80% predictions hit 80% = good calibration ✅
- If 80% predictions hit 60% = model overconfident ❌

**Question 2:** Which edge ranges are profitable?
- Maybe ≥15% edges are profitable
- But 5-10% edges lose money (market is sharper)
- Adjust strategy accordingly

**Question 3:** Which props are best?
- Maybe you have edge on Shots but not Points
- Focus on your strengths

---

## 📞 **QUICK REFERENCE**

### **Daily Commands:**

```bash
# Complete workflow (one command)
python fetch_prizepicks_current_lines.py && python market_vs_model.py

# With fresh predictions
python RUN_DAILY_PICKS.py && python fetch_prizepicks_current_lines.py && python market_vs_model.py
```

### **Files Created:**

- `fetch_prizepicks_current_lines.py` - Fetches current PrizePicks lines
- `market_vs_model.py` - Compares model to market, finds edges
- `MARKET_VS_MODEL_GUIDE.md` - This guide

### **Database Tables:**

- `prizepicks_lines` - Current market lines (all lines per prop)
- `predictions` - Your model predictions
- `prizepicks_edges` - Historical edge tracking (optional)

---

## ✅ **SUMMARY**

**What You Built:**
1. ✅ Fetch current PrizePicks lines (all lines per prop)
2. ✅ Compare to your model predictions
3. ✅ Calculate edges (Model - Market)
4. ✅ Show only significant +EV bets
5. ✅ Handle multiple lines per prop intelligently

**How to Use It:**
```bash
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

**What to Bet:**
- ≥20% edges: Max bet (rare, huge value)
- 10-19% edges: Standard bet (good value)
- 5-9% edges: Small bet or skip (marginal)
- <5% edges: NEVER bet (too close to market)

**Expected Results:**
- 0-8 significant edges per day
- Long-term profit if model is calibrated
- Track results to validate edges

---

**Last Updated:** November 2, 2025
**Status:** ✅ Fully Functional - Ready to Use

**Next Steps:** Run `python fetch_prizepicks_current_lines.py` to get started!
