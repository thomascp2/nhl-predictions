# DAILY WORKFLOW - Order of Operations

**Last Updated:** November 2, 2025

---

## 🚀 **SIMPLEST OPTION (Recommended for Most Users)**

### **ONE COMMAND - Does Everything:**

```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**What it does:**
1. ✅ Generates predictions (all 3 models)
2. ✅ Fetches PrizePicks lines
3. ✅ Runs Stars filter (Strategy 1)
4. ✅ Runs Market vs Model (Strategy 2)
5. ✅ Shows you both sets of results

**Time:** ~2-3 minutes

**Output:**
- Stars picks: 3-8 picks
- Edge picks: 0-10 picks
- Picks in BOTH = highest confidence ⭐

---

## 📊 **UNDERSTANDING THE TWO STRATEGIES**

### **Strategy 1: STARS FILTER**
**What:** 50 elite players in favorable matchups
**Goal:** Simplify betting to high-quality picks

**Criteria:**
- ✅ Player is a star (50-player list)
- ✅ T2-STRONG or better (≥65% confidence)
- ✅ High O/U (≥5.5 goals)
- ✅ Reasonable odds (ML -175 to +150)

**Result:** ~3-8 picks/day

**Example:**
```
Connor McDavid - Points OVER 0.5
├── Star: ✅ (Tier 1 superstar)
├── Confidence: ✅ (91.4% - T1-ELITE)
├── O/U: ✅ (6.5 - high-scoring game)
└── ML: ✅ (EDM -152 - reasonable favorite)
→ INCLUDED in stars picks
```

---

### **Strategy 2: MARKET VS MODEL**
**What:** Find bets where YOUR model beats the MARKET
**Goal:** Maximize expected value (+EV)

**Criteria:**
- ✅ Your model probability > Market probability
- ✅ Edge ≥5% (model - market)
- ✅ T2-STRONG or better (≥65% confidence)

**Result:** ~0-10 picks/day (some days = 0 picks)

**Example:**
```
Connor McDavid - Shots OVER 3.5
├── Your Model: 85% probability
├── Market (PrizePicks): 47% probability
├── Edge: +38% (huge!)
└── Rating: HUGE EDGE - MAX BET
→ INCLUDED in edge picks
```

---

## 🎯 **DECISION TREE: Which Picks to Bet?**

```
┌─────────────────────────────────────┐
│ Pick appears in BOTH strategies?   │
└─────────────┬───────────────────────┘
              │
      ┌───────┴───────┐
      │ YES           │ NO
      ▼               ▼
┌─────────────┐  ┌──────────────────┐
│ BET THIS!   │  │ Check edge %     │
│             │  └────────┬─────────┘
│ Highest     │           │
│ confidence  │    ┌──────┴──────┐
│             │    │ ≥20%   │<20% │
│ Standard    │    ▼        ▼     ▼
│ stake       │  ┌────┐  ┌────┐ ┌──────┐
└─────────────┘  │BET │  │BET │ │MAYBE │
                 │MAX │  │STD │ │      │
                 └────┘  └────┘ └──────┘
```

### **Betting Priority:**

**TIER 1: In BOTH lists** (Highest Confidence) ⭐
- Star player ✅
- Favorable matchup ✅
- +EV edge ✅
- **Action:** BET with standard stake

**TIER 2: Edge ≥20%** (Huge Edge)
- Massive market inefficiency
- May or may not be a star
- **Action:** BET with max stake (rare!)

**TIER 3: Edge 10-19%** (Strong Edge)
- Good market inefficiency
- **Action:** BET with standard stake

**TIER 4: Stars only, no edge data** (Favorable Situation)
- Star in good matchup
- But no market comparison
- **Action:** BET with reduced stake (or skip)

**SKIP: Edge <5%** (Too Close to Market)
- Market is efficient
- **Action:** SKIP

---

## 🗓️ **DAILY SCHEDULE OPTIONS**

### **Option A: Morning Run (Recommended)**

**Time:** 10:00 AM

```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**Why:**
- ✅ Lines are posted for the day
- ✅ Plenty of time before games start
- ✅ Can check PrizePicks throughout day

---

### **Option B: Multiple Runs (Advanced)**

**Morning (10 AM):**
```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

**Afternoon (3 PM):**
```bash
# Re-fetch lines (they may have moved)
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

**Evening (6 PM):**
```bash
# Final check
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

**Why:** Lines move throughout the day, edges may appear/disappear

---

### **Option C: Manual Control**

**If you want to run each step separately:**

```bash
# Step 1: Generate predictions
python RUN_DAILY_PICKS.py

# Step 2: Fetch market lines
python fetch_prizepicks_current_lines.py

# Step 3A: Stars filter
python stars_only_filter.py

# Step 3B: Market vs model
python market_vs_model.py
```

**Why:** Maximum control, can skip steps if needed

---

## 📋 **QUICK REFERENCE CHART**

| Command | What It Does | When to Use | Output |
|---------|-------------|-------------|--------|
| `RUN_COMPLETE_DAILY_WORKFLOW.py` | Everything | **Daily (recommended)** | Both strategies |
| `RUN_STARS_ONLY.py` | Generate + Stars filter | Want simple picks only | 3-8 stars picks |
| `RUN_DAILY_PICKS.py` | Generate predictions only | Manual workflow | Database updated |
| `fetch_prizepicks_current_lines.py` | Get PrizePicks lines | Before market vs model | Database updated |
| `stars_only_filter.py` | Stars filter only | After predictions exist | 3-8 stars picks |
| `market_vs_model.py` | Find edges only | After lines fetched | 0-10 edge picks |

---

## 🎯 **RECOMMENDED WORKFLOW FOR YOU**

Based on your needs, I recommend:

### **DAILY (Morning):**

```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

This gives you:
1. ✅ Stars picks (3-8 simple, high-quality picks)
2. ✅ Edge picks (0-10 +EV market inefficiencies)
3. ✅ Both shown in one output

### **OPTIONAL (Afternoon/Evening):**

```bash
# Re-fetch lines to see if edges still exist
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

### **BET ON:**

1. **Picks in BOTH lists** (stars + edge) = Highest confidence
2. **Edge ≥10%** even if not in stars list = Strong +EV
3. **Stars only** if no edge data = Backup picks

---

## ❓ **FAQ**

### **Q: Do I still run the stars script?**
**A:** YES, but it's included in `RUN_COMPLETE_DAILY_WORKFLOW.py`

You can also run it separately:
```bash
python stars_only_filter.py
```

---

### **Q: What's the order of operations?**
**A:**
1. Generate predictions (ONE TIME)
2. Fetch PrizePicks lines (ONE TIME)
3. Run BOTH filters (Stars + Market vs Model)
4. Compare results, bet on picks in both lists

Or just: `python RUN_COMPLETE_DAILY_WORKFLOW.py` (does all of this)

---

### **Q: Which strategy is better?**
**A:** Use BOTH!
- **Stars filter:** Simple, focuses on best players
- **Market vs Model:** Finds market inefficiencies

**Best bets:** Picks that appear in BOTH lists

---

### **Q: Can I use only one strategy?**
**A:** Yes!

**Stars only:**
```bash
python RUN_STARS_ONLY.py
```

**Market vs Model only:**
```bash
python fetch_prizepicks_current_lines.py
python market_vs_model.py
```

But using BOTH gives you more confidence when they agree.

---

### **Q: How often do I need to run this?**
**A:**
- **Minimum:** Once per day (morning)
- **Better:** 2-3 times per day (lines move)
- **Overkill:** Every hour (not necessary)

---

### **Q: What if I get 0 edge picks?**
**A:** Normal!
- Some days market is efficient
- No edges = no bets (that's OK!)
- Fall back to stars picks if needed

---

### **Q: What if stars picks and edge picks disagree?**
**A:** Prioritize by edge:
- Edge ≥20%: Bet it (even if not a star)
- Edge 10-19%: Bet it (even if not a star)
- Edge 5-9%: Small bet or skip
- Stars only (no edge data): Reduced stake

---

## 📁 **FILES REFERENCE**

**Main Workflows:**
- `RUN_COMPLETE_DAILY_WORKFLOW.py` ⭐ **USE THIS**
- `RUN_STARS_ONLY.py` (stars filter only)
- `RUN_DAILY_PICKS.py` (predictions only)

**Individual Components:**
- `fetch_prizepicks_current_lines.py` (get market lines)
- `stars_only_filter.py` (stars filter)
- `market_vs_model.py` (find edges)

**Guides:**
- `DAILY_WORKFLOW_GUIDE.md` ⭐ **THIS FILE**
- `MARKET_VS_MODEL_GUIDE.md` (market vs model explained)
- `STARS_CRITERIA_EXPLAINED.md` (stars filter criteria)
- `STARS_ONLY_STRATEGY.md` (simplified betting strategy)

---

## ✅ **TL;DR - Just Tell Me What to Run**

### **Every Morning:**

```bash
python RUN_COMPLETE_DAILY_WORKFLOW.py
```

That's it. One command. Everything you need.

### **Then:**

1. Look at the output (two sets of picks)
2. Bet on picks that appear in BOTH lists
3. Bet on edge picks ≥10% (even if not in stars list)
4. Done!

---

**Last Updated:** November 2, 2025
**Status:** ✅ Complete - Ready to Use
