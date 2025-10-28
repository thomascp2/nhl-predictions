# 🔬 PRIZEPICKS RESEARCH LAB - CLAUDE CODE PROJECT PROMPT

**Project:** Systematic Sports Betting Research Experiment  
**Current Phase:** Week 1 - Data Infrastructure Setup  
**Status:** Pre-launch, needs foundation building  
**Timeline:** 6-month research project with phased rollout

---

## 📋 PROJECT CONTEXT

You are managing a sports betting research project that aims to either:
1. **Prove** systematic statistical analysis can generate +EV on PrizePicks props, OR
2. **Quantify** the exact house edge and publish academic findings

This is NOT gambling for profit—it's a scientific experiment with:
- Small bankroll ($50/day max)
- Rigorous data collection
- Publication-quality methodology
- Academic rigor regardless of win/loss

**Key Documents Available:**
- `PrizePicks_System_v1-0.md` - Baseline methodology & Balanced Chaos Model
- `PrizePicks_v2_Project_Plan.md` - 6-month detailed roadmap
- `PrizePicks_Project_Update_v1.1.md` - Consolidated current status & corrections
- `CORRECTIONS_SUMMARY.md` - Critical data error learnings

---

## 🎯 CURRENT PROJECT STATE

### **Phase:** Week 1, Days 1-2 of 180-day experiment

### **Completed:**
- ✅ System documentation written
- ✅ 6-month project plan created
- ✅ NHL SOG betting framework designed
- ✅ Strategy 4 (anchor parlay system) defined
- ✅ Tier-based confidence system established
- ✅ Advanced stats research (xG, xSLG, Corsi, etc.)

### **Blocked/Incomplete:**
- ❌ No data infrastructure built (databases, APIs)
- ❌ No historical data downloaded (need 2024 MLB/NFL/NHL)
- ❌ No backtesting completed (can't validate v1.0 system)
- ❌ No Python analysis scripts written
- ❌ No player verification system implemented
- ❌ No live data feeds configured

### **Immediate Goal:**
Build the data infrastructure and complete backtesting BEFORE making any live bets.

---

## 🛠️ YOUR MISSION

**Phase 1 Objectives (Complete in Order):**

### **MILESTONE 1: Data Infrastructure (Days 1-2)**
Set up the foundation for data collection and analysis.

**Deliverables:**
1. **Google Sheets Database Structure**
   - Create master tracking sheet with 6 tabs
   - Implement formulas for auto-calculations
   - Set up data validation rules
   
2. **Data Source Integrations**
   - Configure API connections (OpenWeather, Sports Reference)
   - Create web scraping scripts for Baseball Savant, FanGraphs
   - Build automated data refresh workflows
   
3. **Python Environment**
   - Set up virtual environment with all required packages
   - Create project folder structure
   - Write data ingestion scripts

**Success Criteria:**
- [ ] Can pull weather data programmatically
- [ ] Can scrape player stats from public sources
- [ ] Can import/export data between Python and Google Sheets
- [ ] All data sources tested and functional

---

### **MILESTONE 2: Historical Data Collection (Days 3-4)**
Download 2023-2024 season data for backtesting.

**Required Datasets:**

**MLB (2024 season):**
- Top 50 hitters: Game-by-game Total Bases, Hits, H+R+RBI
- Top 50 pitchers: Game-by-game Strikeouts, Innings Pitched
- Include: Date, Opponent, Home/Away, Weather, Park Factor, Result

**NFL (2024-25 through Week 6):**
- Top 30 QBs: Passing yards, completions, attempts
- Top 30 RBs: Rushing yards, attempts, receptions
- Top 50 WRs: Receiving yards, receptions, targets
- Include: Date, Opponent, Home/Away, Rest Days, Game Script (final score)

**NHL (2024-25 first 3 weeks):**
- Top 50 forwards: SOG, Points, TOI per game
- Include: Date, Opponent, Home/Away, xG, Corsi%, Fenwick%

**File Format:**
- Export as CSV with standardized column names
- Store in `/data/historical/` directory
- Create data dictionary documenting all fields

**Success Criteria:**
- [ ] 2,000+ MLB player-games downloaded
- [ ] 800+ NFL player-games downloaded
- [ ] 500+ NHL player-games downloaded
- [ ] All data cleaned and validated (no missing values)
- [ ] Data loaded into Google Sheets successfully

---

### **MILESTONE 3: Backtesting Engine (Days 5-7)**
Simulate v1.0 system on historical data to validate methodology.

**Backtest Requirements:**

1. **Create Synthetic PrizePicks Lines**
   - For each player/game, calculate season average through that date
   - Set "line" at season_avg ± 0.5 (simulate PrizePicks pricing)
   - Lines should be realistic (not too easy or impossible)

2. **Apply v1.0 Tier Assignment Rules**
   ```
   Tier 1 (60%+ confidence):
   - Last 5 games avg > 110% of season avg
   - Opponent ranked bottom 10 vs this stat
   - Player high usage/minutes
   - Favorable weather (if applicable)
   
   Tier 2 (52-59% confidence):
   - Last 5 games avg 95-110% of season avg
   - Opponent ranked middle of pack
   - Normal usage
   
   Tier 3 (45-51% confidence):
   - Regression candidate (recent underperformance)
   - Contrarian play vs recency bias
   ```

3. **Simulate Portfolio Construction**
   - Use Balanced Chaos Model budget allocation
   - Groups A, B, C, D as defined in v1.0
   - Track: Daily P&L, hit rate by tier, ROI by group

4. **Statistical Analysis**
   - Calculate: Overall hit rate, hit rate by tier, hit rate by stat type
   - Test: Did Tier 1 actually hit 60%+ on historical data?
   - Identify: Which stat types performed best? (K props? Receptions?)
   - Measure: Would v1.0 have been profitable on 2024 data?

**Output:**
- `backtest_report_v1.0.md` - Comprehensive analysis document
- `backtest_results.csv` - All picks with outcomes
- `stat_type_performance.csv` - Hit rates by category
- Visualizations: Hit rate by tier chart, cumulative P&L graph

**Success Criteria:**
- [ ] Backtest runs on 100+ days of historical data
- [ ] Results show which stat types work (>55% hit rate)
- [ ] Clear recommendations on what to focus on
- [ ] Statistical significance tested (p-values calculated)

---

### **MILESTONE 4: Bayesian Probability Model (Week 2)**
Build quantitative probability calculator to replace subjective tiers.

**Model Specification:**

```python
def calculate_pick_probability(player_data):
    """
    Calculate probability a player hits OVER the line
    
    Inputs:
    - season_avg: Float (player's season average for stat)
    - last_5_avg: Float (average of last 5 games)
    - last_10_avg: Float (average of last 10 games)
    - std_dev: Float (standard deviation of stat)
    - opponent_rank: Int (1-32, opponent defensive rank vs this stat)
    - line: Float (PrizePicks over/under threshold)
    - home_away: Str ('home' or 'away')
    - rest_days: Int (days since last game)
    - weather: Dict (temp, wind, precipitation if applicable)
    - park_factor: Float (if MLB, park run environment)
    
    Returns:
    - probability: Float (0.0 to 1.0)
    - confidence_tier: Str ('T1', 'T2', 'T3', or 'SKIP')
    - reasoning: Str (explanation of probability)
    """
    
    # Base probability: Historical hit rate on this exact line
    base_prob = calculate_historical_hit_rate(player_data)
    
    # Recent form adjustment (exponentially weighted)
    recent_form = (0.30 * game_1 + 0.25 * game_2 + 0.20 * game_3 + 
                   0.15 * game_4 + 0.10 * game_5) / last_5_avg
    form_weight = 0.5
    
    # Matchup adjustment
    if opponent_rank <= 5:  # Top 5 defense
        matchup_adj = -0.05
    elif opponent_rank >= 28:  # Bottom 5 defense
        matchup_adj = +0.05
    else:
        matchup_adj = 0.0
    matchup_weight = 0.1
    
    # Environmental adjustments (weather, park, rest)
    env_adjustments = calculate_environmental_factors(player_data)
    
    # Final probability (weighted average)
    final_prob = (0.4 * base_prob + 
                  form_weight * recent_form + 
                  matchup_weight * matchup_adj + 
                  env_adjustments)
    
    # Assign tier based on probability
    if final_prob >= 0.60:
        tier = 'T1'
    elif final_prob >= 0.52:
        tier = 'T2'
    elif final_prob >= 0.45:
        tier = 'T3'
    else:
        tier = 'SKIP'
    
    return final_prob, tier
```

**Validation:**
- Backtest Bayesian model on same historical data
- Compare: Did probability-based picks beat subjective tiers?
- Calibration test: Do 60% predictions actually hit ~60% of time?

**Success Criteria:**
- [ ] Model implemented and tested
- [ ] Improves hit rate by 2%+ over v1.0 tiers
- [ ] Well-calibrated (predicted % ≈ actual %)
- [ ] Integrated into daily pick generation workflow

---

### **MILESTONE 5: Player Verification System (Week 2)**
Prevent data errors like the Joe Burrow/Joe Mixon incident.

**Requirements:**

1. **Automated Status Checks**
   ```python
   def verify_player_status(player_name, team, date):
       """
       Check if player is active and correctly assigned
       
       Returns:
       - is_active: Bool
       - current_team: Str
       - injury_status: Str ('active', 'questionable', 'out', 'IR')
       - last_game_played: Date
       - warnings: List[Str] (any red flags)
       """
       pass
   ```

2. **Data Sources**
   - ESPN injury reports
   - Team depth charts
   - Vegas betting lines (if player has props, they're playing)
   - Recent news search (player + injury + 2025)

3. **Red Flag Detection**
   - Player on injury report
   - No games in last 14 days
   - Recent trade/release
   - Not on Vegas boards

**Success Criteria:**
- [ ] Automated checks run before every card generation
- [ ] Flags any questionable player status
- [ ] Prevents picks on inactive players
- [ ] Manual verification still required for high-stakes picks

---

### **MILESTONE 6: Daily Card Generation Workflow (Week 2)**
End-to-end system for generating betting cards.

**Workflow:**

```
INPUT: Date (e.g., "2025-10-16")
  ↓
STEP 1: Scrape today's games and available props
  ↓
STEP 2: For each prop, gather player data
  - Season stats
  - Last 5/10 game averages
  - Opponent defensive rank
  - Weather/rest/park factors
  ↓
STEP 3: Run Bayesian model → Calculate probabilities
  ↓
STEP 4: Verify player statuses (injury reports, etc.)
  ↓
STEP 5: Filter picks (only probability > 54%)
  ↓
STEP 6: Construct portfolio using Balanced Chaos Model
  - Group A: 2-pick Power parlays (Tier 1 only)
  - Group B: 3-4 pick Power parlays (mix T1/T2)
  - Group C: Flex plays (insurance)
  - Group D: High-variance plays (5-6 picks)
  ↓
STEP 7: Generate markdown report with:
  - Pick analysis table (all 15-20 picks)
  - Correlation matrix
  - Portfolio construction (specific bet combinations)
  - Budget breakdown ($50 allocated across groups)
  - Expected value calculations
  - Contingency picks (backups for scratches)
  ↓
OUTPUT: Daily_Card_[DATE].md
```

**Success Criteria:**
- [ ] Can generate complete card in <30 minutes
- [ ] All picks verified and validated
- [ ] Portfolio math adds to exactly $50
- [ ] Output includes tracking template for results
- [ ] System catches data errors automatically

---

## 📊 PROJECT STRUCTURE

**Create this directory structure:**

```
prizepicks-research-lab/
│
├── data/
│   ├── historical/
│   │   ├── mlb_2024_hitters.csv
│   │   ├── mlb_2024_pitchers.csv
│   │   ├── nfl_2024_qbs.csv
│   │   ├── nfl_2024_rbs.csv
│   │   ├── nfl_2024_wrs.csv
│   │   └── nhl_2024_forwards.csv
│   │
│   ├── current/
│   │   ├── todays_props.csv (refreshed daily)
│   │   └── player_status.json (injury reports)
│   │
│   └── results/
│       └── daily_results_[DATE].csv
│
├── models/
│   ├── bayesian_model.py
│   ├── player_verification.py
│   └── portfolio_constructor.py
│
├── scripts/
│   ├── data_collection/
│   │   ├── scrape_baseball_savant.py
│   │   ├── scrape_fangraphs.py
│   │   ├── scrape_pfr.py
│   │   ├── scrape_natural_stat_trick.py
│   │   └── get_weather.py
│   │
│   ├── analysis/
│   │   ├── backtest_engine.py
│   │   ├── calculate_probabilities.py
│   │   └── generate_daily_card.py
│   │
│   └── utils/
│       ├── google_sheets_sync.py
│       ├── kelly_criterion.py
│       └── monte_carlo_sim.py
│
├── reports/
│   ├── daily_cards/
│   │   └── Daily_Card_[DATE].md
│   │
│   ├── weekly/
│   │   └── Week_[N]_Report.md
│   │
│   └── backtests/
│       └── backtest_report_v1.0.md
│
├── docs/
│   ├── PrizePicks_System_v1-0.md
│   ├── PrizePicks_v2_Project_Plan.md
│   ├── PrizePicks_Project_Update_v1.1.md
│   └── CORRECTIONS_SUMMARY.md
│
├── config/
│   ├── api_keys.json (gitignored)
│   └── model_parameters.json
│
├── tests/
│   ├── test_bayesian_model.py
│   └── test_data_collection.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔧 TECHNICAL REQUIREMENTS

### **Python Packages:**
```
pandas>=2.0.0
numpy>=1.24.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
scipy>=1.10.0
gspread>=5.7.0
oauth2client>=4.1.3
python-dotenv>=1.0.0
pytest>=7.2.0
```

### **API Keys Needed:**
- OpenWeather API (free tier: 1,000 calls/day)
- Google Sheets API (for automation)
- Sports Reference API (optional, if free tier exhausted)

### **Data Sources:**
- Baseball Savant (free, no key)
- FanGraphs (free tier)
- Pro Football Reference (free tier)
- Natural Stat Trick (free)
- MoneyPuck (free)
- Hockey Reference (free)

---

## 📝 DELIVERABLES CHECKLIST

**Week 1 (Data Infrastructure):**
- [ ] Google Sheets database created
- [ ] All data source accounts created
- [ ] Python environment configured
- [ ] Historical data (2024) downloaded
- [ ] Data cleaning scripts written
- [ ] Backtest engine implemented
- [ ] `backtest_report_v1.0.md` generated

**Week 2 (Model Development):**
- [ ] Bayesian probability model implemented
- [ ] Player verification system built
- [ ] Daily card generation workflow automated
- [ ] Weather/park factor adjustments added
- [ ] First live test card generated (not bet yet)
- [ ] Week 1 results analyzed

**Week 3-4 (Live Testing):**
- [ ] First $50 live bets placed
- [ ] Daily results tracking operational
- [ ] Kelly Criterion bet sizing implemented
- [ ] Monte Carlo simulator built
- [ ] Phase 1 report completed (30 days of data)

---

## 🎯 SUCCESS METRICS

**Week 1 Goals:**
- Complete backtest showing 2024 performance
- Identify 2-3 stat types with >55% historical hit rate
- Validate that v1.0 methodology has theoretical edge
- Ready to begin live testing in Week 2

**Phase 1 Goals (30 days):**
- Achieve 53%+ hit rate in live testing
- Collect 100+ picks with outcomes
- Positive ROI on at least 1 bet group
- System runs smoothly without breaking

**Long-term Goals (6 months):**
- 56%+ hit rate (statistically profitable)
- +10% ROI
- ML model outperforms Bayesian
- Publication-quality dataset and findings

---

## ⚠️ CRITICAL RULES

1. **Never compromise on data verification** - After Burrow/Mixon errors, always validate
2. **Never lower confidence thresholds to fill a card** - Quality > quantity
3. **Track everything** - Every pick, every outcome, every observation
4. **Treat losses as data** - No emotional reactions, only analysis
5. **Stay on timeline** - Don't skip ahead to live betting without backtesting
6. **Document all decisions** - Why we picked X, why we skipped Y
7. **Be willing to kill strategies** - If something doesn't work, pivot

---

## 💬 COMMUNICATION STYLE

**When providing updates:**
- Lead with current milestone status
- Show % complete on deliverables
- Flag any blockers or issues
- Suggest next immediate action
- Ask clarifying questions if specs unclear

**When generating code:**
- Include comprehensive docstrings
- Add inline comments for complex logic
- Write tests for critical functions
- Handle errors gracefully
- Follow PEP 8 style guidelines

**When analyzing data:**
- Start with summary statistics
- Create visualizations
- Test for statistical significance
- Acknowledge uncertainty appropriately
- Provide actionable insights

---

## 🚀 IMMEDIATE NEXT STEPS

**Start with these tasks (in order):**

1. **Set up project folder structure** (10 min)
2. **Create `requirements.txt` and install packages** (10 min)
3. **Write Baseball Savant scraper for 2024 top 50 hitters** (1 hour)
4. **Write FanGraphs scraper for 2024 top 50 pitchers** (1 hour)
5. **Create Google Sheets database and API connection** (30 min)
6. **Import historical data into Sheets** (30 min)
7. **Build backtest engine skeleton** (1 hour)
8. **Run first backtest on 10 sample players** (30 min)
9. **Generate `backtest_report_v1.0.md` with findings** (30 min)

**Total time estimate:** 5-6 hours of focused work

---

## 📞 WHEN TO ASK FOR HELP

**Ask the user if:**
- Specs are ambiguous or contradictory
- Need API keys or account credentials
- Need to make strategic decision (which model to use, etc.)
- Hit a technical blocker you can't solve
- Need clarification on statistical methodology
- Ready to move to next milestone (get approval)

**Don't ask the user about:**
- Minor implementation details
- Code structure/organization choices
- Which Python library to use (pick best one)
- Variable naming
- File formats (use sensible defaults)

---

## ✅ YOUR FIRST RESPONSE

After reading this prompt, respond with:

1. **Confirmation** you understand the project scope
2. **Current status summary** of what exists vs what needs building
3. **Proposed work plan** for Week 1 deliverables
4. **Any immediate questions** or clarifications needed
5. **Request for API keys** or credentials if required
6. **Estimated timeline** for completing Milestone 1

Then begin work on the first task: setting up the project structure.

---

## 📚 REFERENCE DOCUMENTS

All system documentation is available in the project. Key concepts:

- **Balanced Chaos Model:** Portfolio allocation (Groups A/B/C/D)
- **Tier System:** T1 (60%+), T2 (52-59%), T3 (45-51%)
- **Strategy 4:** Anchor parlay system (1-2 ultra-high-confidence picks)
- **Kelly Criterion:** Fractional Kelly (1/10th) for bet sizing
- **Sharpe Ratio:** Target >0.5 for risk-adjusted returns
- **NHL SOG Framework:** Volume-based props, advanced stats (xG, Corsi)

Refer to these when implementing models and strategies.

---

**Good luck! Build this properly and we'll have either a profitable system or publishable research. Either way, we win. 🔬📊🎯**
