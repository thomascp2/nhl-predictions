# Multi-Sport Expansion Plan: NBA & NFL
## From NHL-Only to Multi-Sport Prediction Platform

---

## Executive Summary

**Current State:** Production-ready NHL prediction system (73-75% accuracy)

**Goal:** Expand to NBA and NFL using the same proven architecture

**Timeline:**
- NBA: 4-6 weeks (similar complexity to NHL)
- NFL: 6-8 weeks (more complex features, weekly games)
- Full Multi-Sport Platform: 3-4 months

**Expected Accuracy Targets:**
- NBA: 70-75% (higher scoring = more predictable)
- NFL: 68-72% (weekly variance, fewer games)

---

## Phase 1: NBA Expansion (Weeks 1-6)

### Week 1-2: Data Collection Infrastructure

#### NBA API Options
1. **NBA.com Stats API** (Primary)
   - Endpoint: `https://stats.nba.com/stats/`
   - Free, comprehensive
   - Player game logs, advanced stats, shot charts
   - Similar structure to NHL API

2. **Balldontlie.io** (Backup)
   - Free tier: 1000 requests/day
   - Simpler but less detailed

3. **Rapid API - NBA API** (Paid fallback)
   - $10/month for 10K requests

#### New Database Tables

```sql
-- NBA Player Stats
CREATE TABLE nba_player_stats (
    player_id INTEGER,
    player_name TEXT,
    team TEXT,
    season TEXT,
    games_played INTEGER,
    minutes_per_game REAL,
    points_per_game REAL,
    rebounds_per_game REAL,
    assists_per_game REAL,
    steals_per_game REAL,
    blocks_per_game REAL,
    turnovers_per_game REAL,
    field_goal_pct REAL,
    three_point_pct REAL,
    free_throw_pct REAL,
    usage_rate REAL,
    true_shooting_pct REAL,
    last_updated TEXT
);

-- NBA Game Logs
CREATE TABLE nba_player_game_logs (
    game_id INTEGER,
    game_date TEXT,
    player_name TEXT,
    team TEXT,
    opponent TEXT,
    is_home INTEGER,
    minutes_played REAL,
    points INTEGER,
    rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    three_pointers_made INTEGER,
    three_pointers_attempted INTEGER,
    free_throws_made INTEGER,
    free_throws_attempted INTEGER,
    plus_minus INTEGER
);

-- NBA Team Stats
CREATE TABLE nba_team_stats (
    team_code TEXT PRIMARY KEY,
    team_name TEXT,
    season TEXT,
    pace REAL,                    -- Possessions per game
    offensive_rating REAL,        -- Points per 100 possessions
    defensive_rating REAL,        -- Opp points per 100 possessions
    net_rating REAL,
    points_allowed_per_game REAL,
    rebounds_allowed_per_game REAL,
    three_point_pct_allowed REAL,
    last_updated TEXT
);

-- NBA Rolling Stats
CREATE TABLE nba_player_rolling_stats (
    player_name TEXT,
    team TEXT,
    as_of_date TEXT,
    games_in_window INTEGER,
    window_size INTEGER,          -- L5, L10, L20
    ppg_rolling REAL,
    rpg_rolling REAL,
    apg_rolling REAL,
    minutes_rolling REAL,
    usage_rolling REAL,
    ts_pct_rolling REAL,
    -- Z-scores
    z_score_points REAL,
    z_score_rebounds REAL,
    z_score_assists REAL,
    -- Variance
    std_points REAL,
    std_rebounds REAL,
    std_assists REAL
);

-- NBA Predictions
CREATE TABLE nba_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_date TEXT,
    player_name TEXT,
    team TEXT,
    opponent TEXT,
    prop_type TEXT,               -- points, rebounds, assists, pts+reb+ast
    line REAL,
    probability REAL,
    expected_value REAL,
    kelly_score REAL,
    confidence_tier TEXT,
    model_version TEXT,
    reasoning TEXT,
    created_at TEXT
);
```

#### Data Collection Scripts (New Files)

1. **`fetch_nba_player_stats.py`**
   - Fetch current season stats for top 200 players
   - Similar to `fetch_2025_26_stats.py`

2. **`fetch_nba_game_logs.py`**
   - Historical game-by-game data (2022-2025 seasons)
   - ~80K games per season

3. **`fetch_nba_team_stats.py`**
   - Team pace, offensive/defensive ratings
   - Opponent adjustments

4. **`compute_nba_rolling_stats.py`**
   - L5/L10/L20 averages
   - Hot/cold streaks
   - Back-to-back game adjustments

### Week 3-4: NBA Prediction Models

#### Prop Types to Predict

**Primary Props (Start Here):**
1. Points O/U (most common)
2. Rebounds O/U
3. Assists O/U
4. Points + Rebounds + Assists (PRA) combo

**Advanced Props (Phase 2):**
5. Threes Made O/U
6. Steals + Blocks combo
7. Double-double probability
8. Fantasy points

#### NBA-Specific Features (35 features)

**Player Stats (15):**
- Season PPG/RPG/APG
- Minutes per game
- Usage rate
- True shooting %
- Field goal % / 3PT%
- Free throw attempts per game
- Position (Guard, Forward, Center)

**Rolling Averages (10):**
- L5/L10 PPG/RPG/APG
- L5/L10 minutes
- L5 true shooting %

**Opponent Adjustments (5):**
- Opponent defensive rating
- Opponent pace (possessions per game)
- Opponent points allowed per game
- Opponent rebounds allowed
- Opponent 3PT% allowed

**Situational (5):**
- Home/Away
- Back-to-back game (fatigue factor)
- Days of rest
- Team win streak/lose streak
- Time of season (players rest late season)

#### Model Files (New)

1. **`train_nba_ml_v1.py`**
   - XGBoost classifier
   - Binary classification (over/under)
   - Separate models for points, rebounds, assists

2. **`nba_statistical_predictions.py`**
   - Logistic regression approach
   - Domain expertise built-in
   - 68-72% expected accuracy

3. **`nba_ensemble_predictions.py`**
   - Combine statistical + ML
   - 70-75% target accuracy

### Week 5-6: Integration & Testing

#### Discord Bot Commands (Add to existing bot)

```python
@bot.command(name='nba')
async def nba_predictions(ctx, tier: str = 'T1-ELITE'):
    """Show NBA predictions by tier"""
    # Query nba_predictions table
    # Format and display

@bot.command(name='nbarun')
async def run_nba_workflow(ctx):
    """Generate fresh NBA predictions"""
    # Call nba prediction pipeline

@bot.command(name='sport')
async def show_sport_predictions(ctx, sport: str = 'nhl', tier: str = 'T1-ELITE'):
    """Universal command: !sport nhl/nba/nfl [tier]"""
    # Route to appropriate predictions table
```

#### PrizePicks Integration

- Add NBA markets to edge calculation
- Cross-sport bankroll management
- Multi-sport parlays (advanced)

---

## Phase 2: NFL Expansion (Weeks 7-14)

### Week 7-8: NFL Data Collection

#### NFL API Options

1. **ESPN API** (Free, hidden)
   - `https://site.api.espn.com/apis/site/v2/sports/football/nfl/`
   - Player stats, game logs, injuries

2. **NFL.com Stats API**
   - Official but rate-limited

3. **Sleeper API** (Fantasy-focused)
   - Good for player props
   - Free, well-documented

4. **Pro Football Reference** (Web scraping backup)
   - Most comprehensive
   - Requires scraping (legal gray area)

#### NFL Database Tables

```sql
-- NFL Player Stats
CREATE TABLE nfl_player_stats (
    player_id INTEGER,
    player_name TEXT,
    team TEXT,
    position TEXT,             -- QB, RB, WR, TE, K
    season TEXT,
    games_played INTEGER,

    -- QB Stats
    passing_yards_per_game REAL,
    passing_tds_per_game REAL,
    interceptions_per_game REAL,
    completion_pct REAL,

    -- RB/WR Stats
    rushing_yards_per_game REAL,
    rushing_tds_per_game REAL,
    receptions_per_game REAL,
    receiving_yards_per_game REAL,
    receiving_tds_per_game REAL,
    targets_per_game REAL,

    -- Usage
    snap_count_pct REAL,
    red_zone_targets REAL,

    last_updated TEXT
);

-- NFL Game Logs (Weekly)
CREATE TABLE nfl_player_game_logs (
    game_id INTEGER,
    game_date TEXT,
    week INTEGER,
    player_name TEXT,
    team TEXT,
    opponent TEXT,
    is_home INTEGER,

    -- QB
    passing_yards INTEGER,
    passing_tds INTEGER,
    interceptions INTEGER,
    completions INTEGER,
    attempts INTEGER,

    -- RB/WR
    rushing_yards INTEGER,
    rushing_tds INTEGER,
    receptions INTEGER,
    receiving_yards INTEGER,
    receiving_tds INTEGER,
    targets INTEGER
);

-- NFL Team Defense Stats
CREATE TABLE nfl_team_stats (
    team_code TEXT PRIMARY KEY,
    season TEXT,

    -- Defensive rankings
    passing_yards_allowed_per_game REAL,
    rushing_yards_allowed_per_game REAL,
    points_allowed_per_game REAL,
    sacks_per_game REAL,

    -- Pass defense by position
    yards_allowed_to_qb REAL,
    yards_allowed_to_wr REAL,
    yards_allowed_to_rb REAL,
    yards_allowed_to_te REAL,

    last_updated TEXT
);

-- NFL Injury Reports
CREATE TABLE nfl_injury_reports (
    player_name TEXT,
    team TEXT,
    injury_status TEXT,        -- OUT, DOUBTFUL, QUESTIONABLE, PROBABLE
    injury_type TEXT,
    week INTEGER,
    updated_at TEXT
);
```

#### NFL-Specific Challenges

**1. Weekly Games = Less Data**
- Only 17 games per season (vs 82 NHL/NBA)
- Harder to establish trends
- Solution: Use multi-year data, increase window sizes

**2. Injuries Are Critical**
- Must integrate injury reports
- Backup player usage changes dramatically
- Solution: Real-time injury scraping before predictions

**3. Weather Matters**
- Wind, rain, snow affect passing games
- Solution: Integrate weather API for game-day forecasts

**4. Positional Complexity**
- QB vs RB vs WR vs TE all have different prop markets
- Solution: Separate models per position

### Week 9-11: NFL Prediction Models

#### Prop Types

**QB Props:**
- Passing yards O/U
- Passing TDs O/U
- Interceptions O/U
- Completions O/U
- Longest completion O/U

**RB Props:**
- Rushing yards O/U
- Rushing attempts O/U
- Receptions O/U
- Rushing + Receiving yards combo

**WR/TE Props:**
- Receiving yards O/U
- Receptions O/U
- Longest reception O/U
- Anytime TD scorer (binary)

#### NFL-Specific Features (40+ features)

**Player Stats (12):**
- Position
- Yards per game (by type)
- TDs per game
- Targets/Carries per game
- Snap count %
- Red zone usage
- Target share (WRs)

**Rolling Averages (8):**
- L3/L5 yards (limited sample size)
- L3/L5 TDs
- L3 target share

**Opponent Adjustments (10):**
- Opponent pass defense rank
- Opponent rush defense rank
- Yards allowed to position
- TDs allowed to position
- Sacks per game (for QBs)

**Situational (10):**
- Home/Away
- Indoor/Outdoor stadium
- Weather (wind speed, precipitation)
- Primetime game (SNF, MNF, TNF)
- Division rival game
- Days of rest
- Playoff implications
- Injury report status
- Backup QB playing

#### Model Files

1. **`train_nfl_ml_qb.py`** - QB-specific model
2. **`train_nfl_ml_rb.py`** - RB-specific model
3. **`train_nfl_ml_wr_te.py`** - WR/TE model
4. **`nfl_ensemble_predictions.py`** - Combine all

### Week 12-14: Weather & Injury Integration

#### Weather API Integration

```python
# fetch_game_weather.py
import requests

def get_game_weather(stadium_location, game_time):
    """
    Fetch weather for outdoor stadiums
    API: OpenWeatherMap (free tier)
    """
    # Wind speed > 15mph = reduce passing yards predictions
    # Rain = reduce passing, increase rushing
    # Snow/Cold (<20F) = reduce overall scoring
```

#### Injury Scraping

```python
# fetch_nfl_injuries.py
def scrape_injury_reports():
    """
    Source: ESPN injury reports (updated daily)
    Critical for lineup changes affecting usage
    """
    # OUT = reduce to 0
    # DOUBTFUL = reduce by 70%
    # QUESTIONABLE = reduce by 30%
    # PROBABLE = no reduction
```

---

## Phase 3: Multi-Sport Platform (Weeks 15+)

### Unified Architecture

#### Sport-Agnostic Database Design

```sql
-- Universal predictions table
CREATE TABLE predictions_all_sports (
    id INTEGER PRIMARY KEY,
    sport TEXT,                   -- 'nhl', 'nba', 'nfl'
    game_date TEXT,
    player_name TEXT,
    team TEXT,
    opponent TEXT,
    prop_type TEXT,
    line REAL,
    probability REAL,
    expected_value REAL,
    confidence_tier TEXT,
    model_version TEXT
);
```

#### Unified Discord Bot

```python
@bot.command(name='picks')
async def show_all_picks(ctx, sport: str = 'all', tier: str = 'T1-ELITE'):
    """
    !picks all T1-ELITE - Show all sports
    !picks nhl T1-ELITE - NHL only
    !picks nba T2-STRONG - NBA only
    !picks nfl T1-ELITE - NFL only
    """

    if sport == 'all':
        # Show top picks from each sport
        nhl_picks = get_predictions('nhl', tier)
        nba_picks = get_predictions('nba', tier)
        nfl_picks = get_predictions('nfl', tier)

        # Format as unified list sorted by confidence
    else:
        # Show single sport
        picks = get_predictions(sport, tier)
```

#### Daily Workflow Script

```python
# daily_multi_sport_workflow.py
"""
Runs predictions for all active sports on a given day
"""

def run_daily_workflow(date):
    # Check which sports have games today
    sports_active = []

    if has_nhl_games(date):
        sports_active.append('nhl')
    if has_nba_games(date):
        sports_active.append('nba')
    if has_nfl_games(date):
        sports_active.append('nfl')

    # Run predictions for each sport
    for sport in sports_active:
        run_sport_predictions(sport, date)

    # Combine and rank all predictions
    combine_all_sports(date)
```

### Cross-Sport Features

#### Bankroll Management

```python
# multi_sport_bankroll.py
"""
Kelly criterion across multiple sports
Diversification benefits
"""

def allocate_bankroll(total_bankroll, sport_predictions):
    """
    Allocate based on:
    - Number of plays per sport
    - Confidence tiers
    - Sport-specific historical accuracy
    - Correlation (avoid parlays on same game)
    """
```

#### Performance Dashboard

```python
# multi_sport_dashboard.py
"""
Track accuracy by sport, prop type, tier
"""

@bot.command(name='dashboard')
async def show_dashboard(ctx):
    """
    Overall: 72.5% accuracy
    NHL: 73.2% (1,247 plays)
    NBA: 71.8% (892 plays)
    NFL: 72.0% (234 plays)

    Best Prop Types:
    - NHL Points O0.5: 74.1%
    - NBA Points O/U: 73.5%
    - NFL QB Passing Yards: 70.2%
    """
```

---

## Development Timeline

### Detailed Schedule

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | NBA Data | `fetch_nba_*.py`, NBA database tables |
| 3-4 | NBA Models | `train_nba_ml_v1.py`, NBA predictions |
| 5-6 | NBA Integration | Discord commands, testing |
| 7-8 | NFL Data | `fetch_nfl_*.py`, NFL database tables |
| 9-10 | NFL Models (QB/RB) | Position-specific models |
| 11-12 | NFL Models (WR/TE) | Remaining positions |
| 13-14 | Weather/Injuries | Real-time data integration |
| 15-16 | Multi-Sport Platform | Unified bot, cross-sport features |
| 17-18 | Testing & Refinement | Backtest all sports, accuracy tuning |

### Parallel Development Approach

**Can be done simultaneously:**
- NBA data collection + NHL production operation
- NFL planning + NBA model training
- Multi-sport bot design + individual sport testing

**Estimated Time Investment:**
- **Part-time (10 hrs/week):** 4-5 months total
- **Full-time (40 hrs/week):** 6-8 weeks total
- **Aggressive (60 hrs/week):** 4 weeks total

---

## Technical Challenges & Solutions

### Challenge 1: Data Source Reliability

**Problem:** Free APIs can change, break, or rate-limit

**Solutions:**
1. Build multiple backup APIs for each sport
2. Implement exponential backoff retry logic
3. Cache data aggressively
4. Monitor API health daily
5. Consider paid APIs for production ($50-100/month)

### Challenge 2: Different Seasons

**Problem:** NHL (Oct-Apr), NBA (Oct-Jun), NFL (Sep-Feb) have overlaps

**Solution:**
- September: NFL only
- October-February: All 3 sports (busiest!)
- March-April: NHL + NBA
- May-June: NBA playoffs
- July-August: Off-season (model retraining)

### Challenge 3: Storage & Performance

**Problem:** 3 sports = 3x database size

**Current NHL Database:** ~100 MB
**With NBA + NFL:** ~400-500 MB

**Solutions:**
1. Archive old seasons (keep last 3 years only)
2. Index critical columns (player_name, game_date)
3. Consider PostgreSQL for production (vs SQLite)
4. Implement data retention policies

### Challenge 4: Accuracy Variance by Sport

**Expected Accuracy:**
- NHL: 73-75% (proven)
- NBA: 70-75% (higher scoring, more predictable)
- NFL: 68-72% (weekly variance, injuries)

**Solution:**
- Adjust confidence tiers per sport
- Don't force same accuracy targets
- Weight bankroll allocation by sport accuracy

---

## Cost Analysis

### Free Tier (Current + Expansion)

**APIs:**
- NHL API: Free ✓
- NBA API: Free ✓
- NFL ESPN API: Free ✓
- Weather API (OpenWeather): Free tier (1K calls/day) ✓

**Hosting:**
- Local machine: $0
- Discord bot: $0

**Total: $0/month**

### Paid Tier (Production-Grade)

**APIs:**
- Rapid API NBA Premium: $20/month
- NFL Stats Premium: $30/month
- Weather API Pro: $10/month
- Server hosting (VPS): $20/month

**Total: ~$80/month**

### ROI Calculation

If accuracy targets are met:
- 72% accuracy on 10 bets/day at $50 each
- Expected win rate: 7.2 wins, 2.8 losses
- At -110 odds: $50 x 7.2 x 0.91 = $327.60 wins
- Losses: $50 x 2.8 = $140
- Daily profit: ~$187
- **Monthly profit: ~$5,610**

**ROI on $80/month investment: 70x**

---

## Success Metrics

### KPIs by Sport

**NHL (Baseline):**
- Accuracy: 73-75%
- Plays per day: 10-15
- T1-ELITE hit rate: 78%+

**NBA (Target):**
- Accuracy: 70-75%
- Plays per day: 15-20 (more games)
- T1-ELITE hit rate: 75%+

**NFL (Target):**
- Accuracy: 68-72%
- Plays per week: 30-50
- T1-ELITE hit rate: 72%+

### Platform Metrics

- **Total plays per week:** 150-200 (across all sports)
- **Overall accuracy:** 71-74%
- **Expected weekly ROI:** 25-35%
- **User engagement:** Discord commands usage
- **System uptime:** 99%+ (on-demand vs 24/7)

---

## Risk Mitigation

### Technical Risks

1. **API Changes**
   - Mitigation: Multiple backup APIs, monitoring alerts

2. **Model Drift**
   - Mitigation: Weekly retraining, accuracy tracking, auto-alerts

3. **Database Corruption**
   - Mitigation: Daily backups, transaction logging

### Sports-Specific Risks

1. **NBA Load Management**
   - Players resting unpredictably
   - Mitigation: Scrape injury reports 2 hours before games

2. **NFL Injuries**
   - Last-minute inactive lists
   - Mitigation: Check inactives 90 min before kickoff

3. **NHL Goalie Changes**
   - Starter pulled last minute
   - Mitigation: Already handled in current system

---

## Next Steps (Immediate Actions)

### Week 1 Priorities

**Day 1-2: NBA API Research**
- [ ] Test NBA.com Stats API endpoints
- [ ] Fetch sample player stats
- [ ] Fetch sample game logs
- [ ] Verify data quality

**Day 3-4: Database Setup**
- [ ] Create NBA tables in database
- [ ] Test insert/query operations
- [ ] Set up indexes

**Day 5-7: First Data Script**
- [ ] Build `fetch_nba_player_stats.py`
- [ ] Populate database with current season
- [ ] Verify data accuracy vs ESPN/NBA.com

### Quick Win Strategy

**Start with NBA Points Only**
- Most common prop type
- Similar to NHL points
- Reuse 80% of existing code
- Get to production in 2-3 weeks

**Then expand:**
1. NBA Rebounds (week 4)
2. NBA Assists (week 5)
3. NBA combo props (week 6)

**Parallel NFL planning:**
- While NBA is in testing, begin NFL data collection

---

## File Structure (After Full Expansion)

```
PrizePicks-Research-Lab/
├── database/
│   ├── nhl_predictions.db
│   ├── nba_predictions.db
│   ├── nfl_predictions.db
│   └── multi_sport.db           # Unified database (future)
│
├── models/
│   ├── nhl/
│   │   ├── points_model_v3.pkl
│   │   └── shots_model_v3.pkl
│   ├── nba/
│   │   ├── points_model_v1.pkl
│   │   ├── rebounds_model_v1.pkl
│   │   └── assists_model_v1.pkl
│   └── nfl/
│       ├── qb_model_v1.pkl
│       ├── rb_model_v1.pkl
│       └── wr_te_model_v1.pkl
│
├── nhl/                          # Current files
│   ├── fetch_2025_26_stats.py
│   ├── train_nhl_ml_v3.py
│   └── ensemble_predictions.py
│
├── nba/                          # New NBA files
│   ├── fetch_nba_player_stats.py
│   ├── fetch_nba_game_logs.py
│   ├── compute_nba_rolling_stats.py
│   ├── train_nba_ml_v1.py
│   └── nba_ensemble_predictions.py
│
├── nfl/                          # New NFL files
│   ├── fetch_nfl_player_stats.py
│   ├── fetch_nfl_injuries.py
│   ├── fetch_game_weather.py
│   ├── train_nfl_ml_qb.py
│   └── nfl_ensemble_predictions.py
│
├── shared/                       # Shared utilities
│   ├── database_utils.py
│   ├── api_utils.py
│   └── prediction_engine.py
│
├── discord_bot_multi_sport.py   # Enhanced bot
└── daily_multi_sport_workflow.py
```

---

## Conclusion

**You have a proven system for NHL (73-75% accuracy).** Expanding to NBA and NFL follows the same playbook:

1. **Data Collection** - Fetch API data, populate database
2. **Feature Engineering** - Sport-specific + universal features
3. **Model Training** - Statistical + ML + Ensemble
4. **Integration** - Discord bot commands
5. **Testing** - Backtest, refine, deploy

**Timeline:** 3-4 months to full multi-sport platform
**Investment:** $0-80/month depending on tier
**Expected ROI:** 25-70x on paid tier
**Risk:** Low (proven architecture, established workflow)

**Recommendation:** Start with NBA Points props only (2-3 weeks), validate accuracy, then expand to full NBA and NFL.

---

**Ready to dominate across all major sports!** 🏒🏀🏈

---

*Last Updated: 2025-10-27*
*Version: 1.0 - Initial Expansion Plan*
