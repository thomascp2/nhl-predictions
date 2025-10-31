# NHL Betting System - Game Day Schedule

**Your Daily Routine for Maximum Profitability** 🏒💰

---

## ⏰ Complete Daily Schedule

### 🌅 Morning (7:00 AM - 9:00 AM)

#### 7:00 AM - Wake Up & Coffee ☕
- Check Discord/Slack for system notifications
- Quick glance at GitHub for last night's results

#### **7:30 AM - Review Yesterday's Results** 📊
```bash
# Check dashboard
streamlit run app.py
# Navigate to: Performance → View yesterday's results
```

**What to Check:**
- Hit rate (target: 70%+)
- Parlay success rate (target: 50%+)
- Profit/Loss (track ROI)
- Any system errors in logs

**Action Items:**
- If accuracy < 65% → Check adaptive weights
- If parlays hitting < 40% → Review correlation detection
- If errors → Check `logs/errors_YYYY-MM-DD.log`

---

#### **8:00 AM - Automated Workflow Runs** 🤖 **(AUTOMATIC)**

**System automatically executes:**
```
1. Grade Yesterday's Picks (if morning 6-11 AM)
   └─> Updates database with W/L results
   └─> Calculates accuracy stats

2. Fetch Fresh Data (if > 2 hours old)
   ├─> Player stats from NHL API
   ├─> Team stats
   ├─> Goalie stats
   └─> Daily odds from The Odds API (1 call)

3. Generate Predictions for Today
   ├─> Statistical predictions (fresh_clean_predictions.py)
   ├─> ML predictions (ensemble_predictions.py)
   ├─> TOI predictions (if enabled)
   └─> Goalie saves predictions (if enabled)

4. Find Edges (after 10 PM, uses tomorrow's date)
   ├─> Fetches PrizePicks lines (150-200 props)
   ├─> Matches against predictions
   ├─> Calculates EV with exponential decay
   └─> Saves edges to database

5. Build GTO Parlays
   ├─> Filters edges (7%+ EV)
   ├─> Prioritizes GOBLIN/STANDARD over DEMON
   ├─> Applies correlation detection
   ├─> Generates 10-15 optimal parlays
   └─> Ranks by combined EV

6. Commit to GitHub
   ├─> LATEST_PICKS.txt/csv
   ├─> MULTI_LINE_EDGES_*.csv
   └─> GTO_PARLAYS_*.csv
```

**Estimated Runtime:** 3-5 minutes

---

#### **8:05 AM - Review Generated Picks** 👀

**Dashboard Review:**
```bash
streamlit run app.py
# Navigate to: Today's Picks
```

**What to Look For:**
- **T1-ELITE picks** (75%+ probability) - Core plays
- **T2-STRONG picks** (65-75%) - Secondary plays
- **Edge plays** with 10%+ EV - High value

**Check Bankroll Manager:**
```
Navigate to: System Utilities → Bankroll Manager
- Review bankroll status
- Calculate bet sizes for top picks
- Check daily risk remaining
```

**Action:**
1. Identify 5-10 core picks (T1-ELITE with 10%+ edge)
2. Calculate Kelly bet sizes
3. Note any warnings about daily risk limits

---

### 🌞 Mid-Morning (9:00 AM - 12:00 PM)

#### **9:00-10:00 AM - Place Morning Bets** 💸

**Betting Workflow:**

1. **Review Top Picks**
   - T1-ELITE picks with 10-20% edge
   - Focus on GOBLIN/STANDARD lines (more reliable)

2. **Calculate Bet Sizes**
   ```python
   # Use dashboard: System Utilities → Bankroll Manager
   - Enter probability, payout, edge
   - Get recommended bet size
   - Respect daily risk limits (20% max)
   ```

3. **Place Bets on PrizePicks**
   - Start with singles (2-3 top picks)
   - Consider 2-3 leg parlays if high confidence
   - Avoid DEMON lines early (save for later confirmation)

4. **Record Bets in System**
   ```python
   from bankroll_manager import BankrollManager
   manager = BankrollManager()

   manager.record_bet(
       bet_amount=50,
       bet_type='single',
       bet_description='Dylan Larkin POINTS O0.5 [GOBLIN]',
       probability=0.95,
       payout_multiplier=1.44,
       expected_value=0.37,
       result='pending',
       payout=0
   )
   ```

**Typical Morning Bets:**
- 3-5 singles (GOBLIN/STANDARD lines)
- 1-2 small parlays (2-leg, high confidence)
- Total risk: 5-10% of bankroll

---

#### **10:00-12:00 PM - Monitor Line Movement** 📈

**What to Watch:**
- PrizePicks line changes (rare but possible)
- Breaking news (injuries, scratches, line changes)
- Weather for outdoor games

**Action:**
- Check Twitter/NHL news for updates
- If star player scratch → Avoid their props
- If line changes significantly → Recalculate EV

---

### ☀️ Afternoon (12:00 PM - 5:00 PM)

#### **12:00 PM - Second Workflow Run** 🤖 **(AUTOMATIC)**

**System runs again:**
- Refreshes edges (PrizePicks may have new lines)
- Rebuilds parlays with latest data
- Commits updated files to GitHub

**Your Action:**
```bash
# Check GitHub for updates
# Or refresh dashboard
streamlit run app.py  # Press R to refresh
```

**Look for:**
- New edges that emerged
- Updated parlay recommendations
- Any alerts or warnings

---

#### **12:30-2:00 PM - Midday Strategy Session** 🧠

**Deep Dive on Today's Slate:**

1. **Game Analysis**
   - Check matchups (teams playing, goalie matchups)
   - Review The Odds API game odds
   - Identify game scripts (blowouts vs close games)

2. **Player Context**
   - TOI expectations (top-line minutes?)
   - Recent performance (hot/cold streaks)
   - Rest days, travel, back-to-backs

3. **Correlation Review**
   ```bash
   # Dashboard: System Utilities → Correlation Detector
   # Test any parlay legs you're considering
   ```

4. **Edge Confirmation**
   - Why does our model like this pick?
   - What could go wrong?
   - Is the edge real or data issue?

---

#### **3:00 PM - Third Workflow Run** 🤖 **(AUTOMATIC)**

**System runs again:**
- Final data refresh before games start
- Updates predictions with latest news
- Rebuilds edges and parlays

**Your Action:**
- Final review of picks
- Consider adding 1-2 more bets if strong edges
- Finalize parlay selections

---

### 🌆 Evening (5:00 PM - 8:00 PM)

#### **5:00-6:00 PM - Final Betting Window** 💸

**Lock in Evening Plays:**

1. **Review 6 PM workflow results**
   - Last update before most games start
   - Any last-minute edges?

2. **Consider Parlays**
   ```bash
   # Dashboard: GTO Parlays
   # Review top 3-5 parlay recommendations
   # Check correlation scores
   # Calculate expected payouts
   ```

3. **Finalize Bets**
   - Add any remaining singles
   - Place 1-2 larger parlays (3-4 legs) if confident
   - Total daily risk should be < 20% of bankroll

**Typical Evening Bets:**
- 2-3 additional singles
- 1-2 medium parlays (3-leg)
- Total risk: 5-10% more (15-20% total for day)

---

#### **6:00 PM - Fourth Workflow Run** 🤖 **(AUTOMATIC - FINAL)**

**Last update before games:**
- Final edge calculations
- Last parlay recommendations
- Commit to GitHub

---

#### **6:30-7:00 PM - Pre-Game Review** 🏒

**Final Checklist:**
- ✅ All bets placed?
- ✅ Bets recorded in bankroll manager?
- ✅ Daily risk within limits?
- ✅ Comfortable with selections?

**Set Up Live Tracking:**
```bash
# Option 1: NHL.com live scores
# Option 2: TheScore app
# Option 3: ESPN app
```

---

### 🌙 Night (7:00 PM - 11:00 PM)

#### **7:00 PM - Games Start** 🎮

**Live Monitoring:**
- Watch key games (if possible)
- Track live scores on phone/app
- Monitor Twitter for updates

**Stress-Free Approach:**
- Trust your process
- Don't sweat individual losses
- Focus on long-term edge

---

#### **9:00-11:00 PM - Most Games End** 🏁

**Results Tracking:**
- Check final scores
- Count wins/losses
- Update bet results

**Record Results:**
```python
from bankroll_manager import BankrollManager
manager = BankrollManager()

# Record each settled bet
manager.record_bet(
    bet_amount=50,
    bet_type='single',
    bet_description='Dylan Larkin POINTS O0.5 [GOBLIN]',
    probability=0.95,
    payout_multiplier=1.44,
    expected_value=0.37,
    result='won',  # or 'lost'
    payout=72  # if won
)
```

---

#### **11:00 PM - Day Wrap-Up** 🌙

**End of Day Review:**
```bash
# Dashboard: System Utilities → Bankroll Manager
# View daily P/L, win rate, updated bankroll
```

**Quick Analysis:**
- Today's hit rate?
- Parlay success?
- Bankroll change?
- Any surprises?

**Sleep Well:**
- System will auto-grade at 8 AM tomorrow
- Automated workflow handles everything
- Your job is done until tomorrow morning ✅

---

## 📅 Tomorrow Morning (Oct 31 - Example)

### What Happens Overnight:

**After 10 PM (Smart Timing):**
- PrizePicks switches to tomorrow's (Oct 31) lines
- System detects this automatically
- Edge detection uses Oct 31 date
- Shows helpful message if predictions don't exist yet

**8 AM Tomorrow:**
- System generates Oct 31 predictions
- Finds edges against Oct 31 PrizePicks lines
- Builds new parlays for Oct 31 games
- You wake up to fresh picks ready! 🎉

---

## 🎯 Weekly Routine

### Monday-Saturday (Game Days)
- Follow schedule above
- 4 automated workflows per day (8 AM, 12 PM, 3 PM, 6 PM)
- Active betting and monitoring

### Sunday
- **Lighter Schedule** (fewer NHL games)
- Review weekly performance
- Adjust bankroll if needed
- Plan for upcoming week

### Monthly Tasks
- Review adaptive weight adjustments
- Analyze parlay correlation impact
- Retrain learned multipliers (after 50+ observations)
- Update system if needed

---

## 📊 Key Metrics to Track

### Daily
- ✅ Hit rate (target: 70-75%)
- ✅ Parlay hit rate (target: 50-55%)
- ✅ Daily P/L
- ✅ Bets placed vs planned

### Weekly
- ✅ Weekly ROI (target: +5-10%)
- ✅ Total bets placed
- ✅ Average bet size
- ✅ Risk management (stayed within limits?)

### Monthly
- ✅ Monthly ROI
- ✅ Bankroll growth
- ✅ Model performance trends
- ✅ Parlay vs singles performance

---

## 🚀 Pro Tips

### Time Management
- **Mornings (8-9 AM):** Most important hour - review and plan
- **Midday (12-3 PM):** Monitor and adjust
- **Evening (5-7 PM):** Final bets and prepare
- **Night (7-11 PM):** Relax and track (optional)

### Betting Strategy
- **Singles First:** Build bankroll with high-probability singles
- **Parlays Second:** Use parlays for upside, not as core strategy
- **Risk Management:** Never exceed 20% daily risk
- **Long-Term Focus:** Trust the process, variance is normal

### Emotional Control
- **Don't Chase:** Losing day? Stop betting, trust tomorrow
- **Don't Overbet:** Winning streak? Stick to Kelly sizing
- **Stay Disciplined:** Follow the system, ignore gut feelings
- **Review Objectively:** Focus on process, not results

---

## 🛠️ Maintenance Schedule

### Daily (Automatic)
- ✅ System workflows (8 AM, 12 PM, 3 PM, 6 PM)
- ✅ GitHub commits (auto)
- ✅ Log generation (auto)

### Weekly (Manual - 15 min)
- Check system logs for errors
- Review bankroll manager status
- Verify data freshness

### Monthly (Manual - 1 hour)
- Run `SYSTEM_IMPROVEMENTS_2025-10-30.md` checklist
- Review adaptive weights performance
- Check for system updates
- Backup database

---

## 🎉 Success Checklist

**You're doing it right if:**
- ✅ Hit rate consistently 70%+
- ✅ Staying within daily risk limits
- ✅ Bankroll growing month-over-month
- ✅ Following system picks (not overriding)
- ✅ Recording all bets in bankroll manager
- ✅ Reviewing performance regularly
- ✅ Sleeping well (system is automated!)

---

**Remember:** The system does 95% of the work. Your job is to:
1. Review picks
2. Calculate bet sizes
3. Place bets
4. Record results
5. Trust the process

**The automated workflow handles everything else!** 🚀

---

**END OF SCHEDULE**
