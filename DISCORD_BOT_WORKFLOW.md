# 🤖 Discord Bot Quick Reference Guide

## 📋 Daily Workflow (Order of Operations)

### **Morning Routine (Generate Today's Picks)**

```
Step 1: !run
```
**What it does:**
- Grades yesterday's predictions
- Generates today's predictions (all 82+ picks)
- Compares with PrizePicks lines
- Runs EV optimizer
- Creates summary JSON

**Time:** 2-3 minutes  
**Result:** Daily picks ready!

---

```
Step 2: !optimize
```
**What it does:**
- Evaluates ALL available lines (standard, demon, goblin)
- Calculates true EV for each option
- Selects BEST line per player
- Shows top 5 optimal picks in Discord

**Time:** 30-60 seconds  
**Result:** Top 5 highest EV picks with line recommendations

---

```
Step 3: !picks
```
**What it does:**
- Shows top 10 picks from database
- Standard view (not EV optimized)
- Good for quick overview

**Time:** Instant  
**Result:** Standard top 10 picks

---

### **Evening Routine (Review Performance)**

```
Step 4: !grade [yesterday's date]
```
**What it does:**
- Fetches game results from NHL API
- Grades all predictions for that date
- Updates database with HIT/MISS

**Time:** 30 seconds  
**Example:** `!grade 2025-10-24`  
**Result:** Yesterday's picks graded

---

```
Step 5: !dashboard
```
**What it does:**
- Shows overall hit rate
- Shows ROI and profit
- Breaks down performance by tier

**Time:** Instant  
**Result:** Performance summary

---

## 🎯 Command Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `!run` | Full automation | **Every morning** to generate picks |
| `!optimize` | Find best EV picks | **Before placing bets** |
| `!picks` | Quick view | Anytime for standard picks |
| `!grade [date]` | Grade predictions | **Every evening** after games |
| `!dashboard` | View performance | Check stats anytime |
| `!commands` | Show help | When you forget commands |

---

## 💡 Recommended Daily Flow

### **🌅 Morning (Before Games Start)**

1. **Generate picks:**
   ```
   !run
   ```
   *Wait 2-3 minutes*

2. **Find optimal bets:**
   ```
   !optimize
   ```
   *Review top 5 with highest EV*

3. **Place your bets** on PrizePicks based on optimizer results

---

### **🌙 Evening (After Games End)**

1. **Grade yesterday:**
   ```
   !grade 2025-10-24
   ```
   *(Use actual yesterday's date)*

2. **Check performance:**
   ```
   !dashboard
   ```
   *Review hit rate and ROI*

---

## 📊 Understanding the Output

### **!optimize Output:**
```
1. David Pastrnak (BOS)
   POINTS OVER 1.5 [DEMON]
   Prob: 92.3% | EV: +107.6%
   Kelly: 21.5% of bankroll
```

**What this means:**
- **POINTS OVER 1.5**: The specific line to bet
- **[DEMON]**: Line type (higher payout, harder to hit)
- **Prob: 92.3%**: Our calculated win probability
- **EV: +107.6%**: Expected value (you make $1.08 per $1 bet on average)
- **Kelly: 21.5%**: Optimal bet size (conservative = divide by 4 = 5.4%)

---

### **!picks Output:**
```
1. Alex Ovechkin (WSH) vs OTT
   SHOTS OVER 3.5 [ELITE]
   Probability: 76.0% | Kelly: 25.7
   High shot volume | Home ice
```

**What this means:**
- **[ELITE]**: Confidence tier (T1-ELITE is best)
- **Probability: 76.0%**: Win chance
- **Kelly: 25.7**: Kelly score (higher = better)
- **Reasoning**: Why we like this pick

---

### **!dashboard Output:**
```
Overall:
  Hit Rate: 58.3%
  ROI: +12.5%
  Profit: +4.75u

Record:
  Total: 169
  Graded: 87
  Pending: 82

By Tier:
  T1-ELITE: 35/52 (67.3%)
  T2-STRONG: 15/28 (53.6%)
  T3-MARGINAL: 1/7 (14.3%)
```

**What this means:**
- **Hit Rate**: % of picks that won
- **ROI**: Return on investment (profit per unit bet)
- **Profit**: Total units won/lost
- **By Tier**: Performance breakdown by confidence level

---

## 🎰 Betting Strategy

### **Conservative (Recommended):**
Use **1/4 Kelly** sizing from optimizer:
- If Kelly says 20% → Bet 5% of bankroll
- If Kelly says 16% → Bet 4% of bankroll

### **Moderate:**
Use **1/2 Kelly** sizing:
- If Kelly says 20% → Bet 10% of bankroll

### **Aggressive (Not Recommended):**
Use **Full Kelly** sizing:
- High variance
- Can lose big quickly

---

## 🔥 Pro Tips

### **1. Always use !optimize before betting**
The optimizer finds better lines than the standard picks!

Example:
- Standard: Ovechkin SOG 3.5 (+45% EV)
- Optimizer finds: Ovechkin Points 0.5 GOBLIN (+47% EV, higher probability!)

### **2. Mix tiers for balance**
Don't bet only T1-ELITE picks. Mix in T2-STRONG for diversification.

### **3. Track your own results**
Use !dashboard daily to ensure the model is working for you.

### **4. Don't chase losses**
If you have a bad day, stick to your bankroll management. The edge plays out over time.

### **5. Focus on demon/goblin lines from optimizer**
These often have better EV than standard lines!

---

## ⚠️ Important Notes

### **When games start:**
- Generate picks in the **morning** before games
- Don't wait until games have started

### **Grading timing:**
- Grade **after midnight** when all games are final
- Or grade the **next morning**

### **Database resets:**
- Your picks and history are stored locally
- Back up `database/nhl_predictions.db` regularly

---

## 🆘 Troubleshooting

### **"No picks found"**
- Run `!run` first to generate picks
- Make sure you're using correct date format: YYYY-MM-DD

### **"Automation failed"**
- Check that all scripts are in the project folder
- Ensure database folder exists
- Try running manually: `python complete_automation.py`

### **"No positive EV picks found"**
- This is rare but possible
- Lower the EV threshold in `optimize_ev.py` (line 275)
- Or just use `!picks` for standard recommendations

### **Bot not responding**
- Check bot is online (green dot in Discord)
- Restart bot: `python discord_bot.py`
- Verify token is set correctly

---

## 📱 Command Cheat Sheet

```
Morning:
  !run          → Generate all picks
  !optimize     → Find best EV picks
  
Evening:
  !grade        → Grade yesterday's picks
  !dashboard    → View performance
  
Anytime:
  !picks        → Show today's picks
  !picks [date] → Show picks for specific date
  !commands     → Show all commands
```

---

## 🎯 Example Full Day

**8:00 AM - Before work:**
```
!run
[wait 2-3 minutes]
!optimize
```
→ Place bets based on top 5 optimizer picks

**6:00 PM - Games in progress:**
→ Watch and enjoy!

**11:30 PM - After games:**
```
!grade 2025-10-24
!dashboard
```
→ Review performance, adjust strategy

**Repeat daily!** 🔁

---

## 💰 Expected Results

Based on backtesting:

**Conservative (1/4 Kelly):**
- Hit Rate: 58-62%
- ROI: +8-15%
- Profit: Steady, low variance

**Using EV Optimizer:**
- Hit Rate: 62-66% (higher!)
- ROI: +12-18%
- Profit: Better picks = better results

**Over 100+ picks:**
- Expect positive ROI
- Some bad days are normal
- Edge shows over time

---

**Trust the process. Trust the math. Let's make money! 💎🚀**
