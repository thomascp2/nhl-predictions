# 🎰 GTO Parlay Optimizer - Complete Guide

## 🎯 What Is This?

The **GTO (Game Theory Optimal) Parlay Optimizer** builds +EV parlays using frequency allocation similar to poker solvers. Instead of randomly combining picks, it strategically distributes your best picks across multiple parlays to maximize long-term expected value while managing risk.

---

## 🧠 How It Works

### Traditional Approach (What Most Bettors Do)
```
❌ Pick highest EV plays
❌ Combine them all in one big parlay
❌ Either win big or lose everything
❌ Overuse best picks, underuse good picks
```

### GTO Approach (What We Do)
```
✅ Assign frequency targets based on EV (like poker hand ranges)
✅ Build multiple parlays with balanced exposure
✅ Ensure picks aren't correlated (same game/team)
✅ Use Kelly criterion for optimal bet sizing
✅ Maximize portfolio EV, not individual parlay EV
```

---

## 🔑 Key Concepts

### 1. Frequency Allocation
Just like GTO poker solvers assign frequencies to hands:
- **15%+ EV picks** → Max frequency (20 appearances)
- **10-15% EV picks** → High frequency (16 appearances)
- **7-10% EV picks** → Medium frequency (12 appearances)
- **5-7% EV picks** → Low frequency (8 appearances)
- **3-5% EV picks** → Minimum frequency (5 appearances)

This ensures:
- ✅ Best picks get maximum exposure
- ✅ Good picks don't get ignored
- ✅ Balanced portfolio distribution

### 2. Correlation Avoidance
The optimizer automatically rejects parlays with:
- Same game (e.g., Matthews POINTS + Nylander POINTS in TOR vs CBJ)
- Same team (e.g., two Maple Leafs players)

Why? Correlated picks reduce true probability:
```python
# Independent picks (different games):
Matthews 75% × Kucherov 70% = 52.5% ✅

# Correlated picks (same game):
Matthews 75% × Nylander 75% ≠ 56.25% ❌
# True probability is lower because if Matthews struggles,
# Nylander probably struggles too (same game conditions)
```

### 3. Kelly Criterion Sizing
Each parlay gets optimal bet size using fractional Kelly:
```python
# Kelly formula:
f = (bp - q) / b
where:
    b = payout - 1
    p = win probability
    q = 1 - p

# We use Quarter Kelly (25%) for safety
bet_size = bankroll × kelly × 0.25
```

Example:
```
Parlay: 55% probability, 3x payout
Kelly = (2 × 0.55 - 0.45) / 2 = 0.325 (32.5%)
Quarter Kelly = 32.5% × 0.25 = 8.1%

With $1000 bankroll:
Bet size = $1000 × 0.081 = $81
```

---

## 📊 PrizePicks Payout Structure

The optimizer uses real PrizePicks payouts:

| Legs | Payout | Breakeven | Notes |
|------|--------|-----------|-------|
| 2-leg | 3.0x | 57.7% | Standard Power Play |
| 3-leg | 5.0x | 58.5% | Good for balanced parlays |
| 4-leg | 10.0x | 56.2% | High risk, high reward |
| 5-leg | 20.0x | 52.5% | Lottery ticket territory |

**Why this matters:**
- Your model says each pick is 70% → Parlay should be 70%^2 = 49% (2-leg)
- PrizePicks pays 3x → Breakeven is 33.3%
- **Your edge:** 49% - 33.3% = **+15.7% EV** ✅

---

## 🚀 How To Use

### Step 1: Run Complete Workflow
```bash
cd C:\Users\thoma\PrizePicks-Research-Lab
python run_complete_workflow_gto.py
```

This runs:
1. Generates predictions (with smart data refresh)
2. Finds PrizePicks edge (7%+ edge plays)
3. **Builds GTO-optimized parlays**

### Step 2: Review Output

The optimizer shows:

#### Frequency Allocation
```
PICK FREQUENCY ALLOCATION (GTO-Style)
================================================================================
player_name              prop_type  ev_score  target_frequency
William Nylander         points     12.3%     20
Auston Matthews          shots      11.8%     16
Kirill Marchenko         shots      9.5%      12
John Tavares             points     7.2%      8
```

#### Candidate Generation
```
[*] Generating 2-leg parlay candidates...
  Total 2-leg combinations: 45
  Profitable (EV > 10.0%): 23

[*] Generating 3-leg parlay candidates...
  Total 3-leg combinations: 120
  Profitable (EV > 10.0%): 38
```

#### Optimized Parlays
```
PARLAY #1 (2-leg)
--------------------------------------------------------------------------------
  Leg 1: William Nylander      POINTS  O0.5
  Leg 2: Kirill Marchenko      SHOTS   O2.5

  Probability: 72.0%
  Payout:      3.0x
  EV:          +116.0%
  Kelly Bet:   $47.23 (4.7% of bankroll)
  Expected:    +$54.79
```

### Step 3: Check CSV Export
```bash
# Generated file: GTO_PARLAYS_2025-10-29_05-30PM.csv
# Open in Excel/Google Sheets for easy reference
```

---

## 💰 Betting Strategy

### Bankroll Allocation
```
$1000 Bankroll Example:

Singles (Individual Picks):
- Nylander POINTS O0.5 (15% edge): $30 (3%)
- Matthews SHOTS O2.5 (12% edge):  $25 (2.5%)
- Marchenko SHOTS O2.5 (10% edge): $20 (2%)
Total Singles Risk: $75 (7.5%)

Parlays (GTO Optimized):
- 2-leg Parlay #1: $47 (4.7%)
- 2-leg Parlay #2: $35 (3.5%)
- 3-leg Parlay #1: $28 (2.8%)
Total Parlay Risk: $110 (11%)

TOTAL RISK: $185 (18.5% of bankroll)
```

### Risk Management Rules
1. **Never risk more than 20% of bankroll per day**
2. **Use Quarter Kelly (25%) for parlays**
3. **Singles should be 50% of total risk**
4. **Parlays should be 50% of total risk**
5. **Track results daily, adjust if hit rate drops**

---

## 📈 Expected Performance

### Theoretical Performance
If your model is accurately calibrated:

```
Singles Portfolio (10 picks):
- Average edge: 10%
- Hit rate: 73%
- Average bet: $25
- Expected daily: +$25 (10% of $250)

Parlays Portfolio (5 parlays):
- Average edge: 15%
- Hit rate: 45%
- Average bet: $35
- Expected daily: +$26 (15% of $175)

TOTAL EXPECTED: +$51/day (+5.1% ROI)
```

### Reality Check
- Variance is HIGH (especially on parlays)
- Some days you'll lose everything
- Some days you'll 10x
- **Long-term is what matters**

Week-by-week expectations:
```
Week 1: -$150 (bad variance)
Week 2: +$420 (2 big parlays hit)
Week 3: -$80 (close calls)
Week 4: +$290 (solid week)
Month Total: +$480 (+12% ROI)
```

---

## 🎓 Advanced Features

### Custom Bankroll
```bash
# Optimize for $2500 bankroll
python gto_parlay_optimizer.py 2025-10-29 2500
```

### Adjust Parlay Targets
Edit `gto_parlay_optimizer.py`:
```python
# Line 500+
optimizer.optimize_parlay_selection(
    target_2leg=12,  # More 2-leg parlays
    target_3leg=6,   # More 3-leg parlays
    target_4leg=2    # Fewer 4-leg parlays
)
```

### Adjust Minimum EV Threshold
```python
# Line 489+
optimizer.generate_candidate_parlays(
    min_parlay_ev=0.15  # Only parlays with 15%+ EV
)
```

---

## 🔧 Integration with Existing System

### Daily Workflow

**Morning (9 AM):**
```bash
python run_complete_workflow_gto.py
```
→ Generates picks, finds edge, builds GTO parlays

**Check Output:**
1. `LATEST_PICKS.txt` - Individual T1-ELITE picks
2. `GTO_PARLAYS_*.csv` - Optimized parlays
3. Console output - Betting recommendations

**Place Bets:**
- Log into PrizePicks
- Place singles based on LATEST_PICKS.txt
- Place parlays based on GTO recommendations
- Use Kelly sizing from output

**Evening (Grade Results):**
```bash
python grade_predictions.py 2025-10-29
```
→ Track performance, adjust if needed

---

## 📊 Viewing Results in Database

### Check Edge Plays
```sql
SELECT
    player_name,
    prop_type,
    line,
    edge,
    our_probability,
    pp_implied_probability
FROM prizepicks_edges
WHERE date = '2025-10-29'
AND edge >= 10.0
ORDER BY edge DESC;
```

### Check Parlay Performance (Future)
```sql
-- After grading system is enhanced
SELECT
    parlay_id,
    legs,
    probability,
    payout,
    ev,
    result,
    profit
FROM gto_parlays_graded
WHERE date >= '2025-10-01'
ORDER BY date DESC;
```

---

## ❓ FAQ

### Q: Why don't we just parlay all the best picks together?
**A:** That creates massive correlation risk and over-exposes you to variance. GTO balancing spreads risk across multiple uncorrelated parlays.

### Q: What if I don't have a $1000 bankroll?
**A:** Scale down proportionally. With $100 bankroll:
- Singles: $2-5 each
- Parlays: $3-8 each
- Total risk: $15-20/day

### Q: How often should parlays hit?
**A:** Depends on legs:
- 2-leg at 70% each: ~49% hit rate
- 3-leg at 70% each: ~34% hit rate
- 4-leg at 70% each: ~24% hit rate

If your hit rate is significantly lower, your probability estimates are too optimistic.

### Q: Can I use this for other sports?
**A:** Yes! Just adjust:
1. Load picks from different API (NFL/NBA)
2. Update payout structure if different
3. Run optimizer as normal

### Q: What if PrizePicks changes payouts?
**A:** Update `calculate_parlay_payout()` in `gto_parlay_optimizer.py`:
```python
# Line 114
prizepicks_payouts = {
    2: 3.0,  # Update if changed
    3: 5.0,
    4: 10.0,
    5: 20.0,
    6: 25.0
}
```

---

## 🎯 Next Steps

### Short Term (This Week)
1. Run workflow daily
2. Track all bets in spreadsheet
3. Grade results each morning
4. Adjust if hit rate < 60%

### Medium Term (This Month)
1. Build grading system for parlays
2. Track GTO frequency effectiveness
3. Retrain ML model on graded data
4. Optimize frequency thresholds

### Long Term (This Season)
1. Build bankroll tracking dashboard
2. Implement dynamic Kelly adjustment
3. Add live line monitoring
4. Build Discord bot for mobile access

---

## 🚨 Important Disclaimers

1. **Past performance ≠ future results**
2. **Sports betting has variance** - even +EV bets lose
3. **Only bet what you can afford to lose**
4. **Track results religiously** - if hit rate drops, stop betting
5. **Legal compliance** - ensure sports betting is legal in your jurisdiction
6. **Responsible gambling** - set limits, take breaks, seek help if needed

---

## 💡 Pro Tips

1. **Run workflow 2-3x per day** - lines update, new games added
2. **Focus on 2-leg parlays** - best risk/reward ratio
3. **Avoid 5+ leg parlays** - lottery tickets, not +EV
4. **Diversify across games** - reduces correlation risk
5. **Never chase losses** - stick to Kelly sizing
6. **Grade results daily** - adjust if model drifts
7. **Keep detailed records** - IRS wants records, you want data

---

## 📞 Support

Issues? Questions? Improvements?

1. Check output logs for error messages
2. Verify database has edge plays: `python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db'); print(pd.read_sql('SELECT COUNT(*) FROM prizepicks_edges WHERE date = \"2025-10-29\"', conn))"`
3. Re-run workflow if edge plays exist but optimizer fails

---

**Good luck and bet responsibly!** 🏒💎🚀
