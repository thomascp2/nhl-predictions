# NHL PrizePicks Betting System - Complete Guide V1.0

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Database Schema](#database-schema)
4. [Core Components](#core-components)
5. [Daily Workflow](#daily-workflow)
6. [Running the System](#running-the-system)
7. [Grading & Performance Tracking](#grading--performance-tracking)
8. [Dependencies & Requirements](#dependencies--requirements)
9. [Troubleshooting](#troubleshooting)

---

## System Overview

### What This System Does

**Complete NHL betting automation from data fetch to optimized parlay recommendations**:

1. **Fetches fresh NHL data** (player stats, team stats, schedules, goalie matchups)
2. **Generates predictions** using statistical + ML ensemble models
3. **Finds PrizePicks edge plays** by comparing our predictions to PrizePicks lines
4. **Builds GTO-optimized parlays** using frequency allocation and Kelly sizing
5. **Stores everything to database** for tracking and grading
6. **Grades results** against actual NHL game outcomes
7. **Auto-commits to GitHub** for remote access

### Key Features

- **Smart Data Refresh**: Only fetches new data when needed (>2 hours old)
- **T1-ELITE Picks**: 10%+ edge individual plays
- **GTO Parlay Optimizer**: Frequency-based portfolio construction
- **Real Payout Integration**: Handles standard/goblin/demon modes
- **Individual Odds Tracking**: Reverse engineers PrizePicks multipliers
- **Comprehensive Grading**: Tracks hit rate, ROI, profit/loss
- **Full Automation**: Windows Task Scheduler integration

---

## Architecture & Data Flow

### End-to-End Pipeline

```
NHL API + THE ODDS API
   |
   v
[0] GAME ODDS FETCH (fetch_daily_odds.py) ⭐ NEW!
   - Fetches real betting lines (ML, spreads, totals)
   - Uses The Odds API (500 free calls/month)
   - Smart caching (1 call per day = 30/month)
   - Saves to odds_api_game_odds table
   |
   v
[1] DATA FETCH (smart_data_refresh.py)
   - Player stats (rolling averages, L5 games)
   - Team stats (offensive/defensive metrics)
   - Goalie stats (save %, recent form)
   - Schedule (upcoming games, home/away)
   |
   v
DATABASE (nhl_predictions.db)
   - odds_api_game_odds ⭐ NEW!
   - player_stats
   - team_stats
   - goalie_stats
   - games
   |
   v
[2] PREDICTION GENERATION (generate_picks_to_file.py)
   - Statistical model (weighted averages)
   - ML ensemble (XGBoost + LightGBM)
   - Matchup adjustments (uses real betting lines) ⭐ ENHANCED!
   - Confidence scoring
   |
   v
DATABASE + FILES
   - predictions table
   - LATEST_PICKS.txt
   - LATEST_PICKS.csv
   |
   v
[3] PRIZEPICKS INTEGRATION (prizepicks_integration_v2.py)
   - Fetches PrizePicks lines
   - Identifies odds_type (standard/goblin/demon)
   - Calculates edge (our prob - implied prob)
   - Filters for 7%+ edge
   |
   v
DATABASE
   - prizepicks_edges table
   |
   v
[4] GTO PARLAY OPTIMIZATION (gto_parlay_optimizer.py)
   - Loads edge plays from database
   - Assigns frequency based on EV
   - Generates uncorrelated parlays
   - Calculates Kelly bet sizing
   - Exports CSV + saves to database
   |
   v
DATABASE + FILES + GITHUB
   - gto_parlays table
   - GTO_PARLAYS_*.csv
   - Commits to GitHub
   |
   v
[5] GRADING (grade_all_picks.py)
   - Fetches NHL game results
   - Grades predictions (HIT/MISS)
   - Grades edges (HIT/MISS)
   - Grades parlays (HIT/MISS)
   - Updates database with results
```

---

## Database Schema

### Core Tables

#### 1. **predictions**
**Purpose**: Stores all generated predictions with full context

**Key Columns**:
- `id` (INTEGER): Primary key
- `game_date` (TEXT): YYYY-MM-DD
- `player_name` (TEXT): Full player name
- `team` (TEXT): Player's team
- `opponent` (TEXT): Opposing team
- `prop_type` (TEXT): shots, points, goals, assists
- `line` (REAL): Over/under line (e.g., 3.5)
- `prediction` (TEXT): OVER or UNDER
- `probability` (REAL): Model confidence (0-1)
- `expected_value` (REAL): EV score
- `confidence_tier` (TEXT): T1-ELITE, T2, T3
- `result` (TEXT): HIT or MISS (after grading)
- `actual_value` (REAL): Actual stat from game
- `graded_at` (TEXT): When graded

**Dependencies**: None (root table)

**Populated By**: `generate_picks_to_file.py`

---

#### 2. **prizepicks_edges**
**Purpose**: Stores picks with positive edge against PrizePicks lines

**Key Columns**:
- `id` (INTEGER): Primary key
- `date` (TEXT): YYYY-MM-DD
- `player_name` (TEXT): Full player name
- `prop_type` (TEXT): shots, points, etc.
- `line` (REAL): PrizePicks line
- `odds_type` (TEXT): standard, goblin, demon
- `our_probability` (REAL): Our model's probability
- `pp_implied_probability` (REAL): PrizePicks implied probability
- `edge` (REAL): Difference (positive = edge)
- `expected_value` (REAL): EV calculation
- `payout_multiplier` (REAL): Individual pick multiplier
- `result` (TEXT): HIT or MISS (after grading)
- `actual_value` (REAL): Actual stat from game

**Dependencies**: Joins with `predictions` table

**Populated By**: `prizepicks_integration_v2.py`

---

#### 3. **gto_parlays**
**Purpose**: Stores GTO-optimized parlay recommendations

**Key Columns**:
- `id` (INTEGER): Primary key
- `date` (TEXT): YYYY-MM-DD
- `parlay_id` (TEXT): P001, P002, etc.
- `num_legs` (INTEGER): 2, 3, or 4
- `picks_json` (TEXT): JSON array of picks
- `combined_probability` (REAL): Product of individual probabilities
- `payout_multiplier` (REAL): Total parlay payout
- `expected_value` (REAL): Parlay EV
- `kelly_fraction` (REAL): Kelly multiplier (0.25 = quarter Kelly)
- `recommended_bet_size` (REAL): Dollar amount to bet
- `parlay_tier` (TEXT): ELITE, T1, T2, T3
- `result` (TEXT): HIT or MISS (after grading)
- `actual_payout` (REAL): Payout received if hit

**Dependencies**: References players/props from `prizepicks_edges`

**Populated By**: `gto_parlay_optimizer.py`

---

#### 4. **prizepicks_observed_odds**
**Purpose**: Tracks reverse-engineered individual pick multipliers

**Key Columns**:
- `date` (TEXT): YYYY-MM-DD
- `player_name` (TEXT): Full player name
- `prop_type` (TEXT): shots, points, etc.
- `line` (REAL): The line (e.g., 3.5)
- `implied_multiplier` (REAL): Individual pick multiplier (e.g., 1.5x)
- `confidence` (REAL): Confidence in estimate (0-1)
- `observations` (INTEGER): Number of observations

**Dependencies**: None

**Populated By**: `log_parlay.py` (manual user input)

---

#### 5. **prizepicks_parlay_observations**
**Purpose**: Stores actual parlay payouts observed on PrizePicks

**Key Columns**:
- `date` (TEXT): YYYY-MM-DD
- `num_legs` (INTEGER): Number of picks in parlay
- `actual_payout` (REAL): Actual payout multiplier
- `picks_json` (TEXT): JSON array of picks
- `created_at` (TEXT): Timestamp

**Dependencies**: None

**Populated By**: `log_parlay.py` (manual user input)

---

#### 6. **player_stats**
**Purpose**: Current season stats for all NHL players

**Key Columns**:
- `player_name` (TEXT): Full player name
- `games_played` (INTEGER): GP
- `goals` (INTEGER): Total goals
- `assists` (INTEGER): Total assists
- `points` (INTEGER): Total points
- `shots` (INTEGER): Total shots
- `last_updated` (TEXT): Timestamp

**Dependencies**: None (fetched from NHL API)

**Populated By**: `smart_data_refresh.py`

---

### Supporting Tables

- `games`: Schedule and results
- `team_stats`: Team offensive/defensive metrics
- `goalie_stats`: Goalie save percentages
- `player_rolling_stats`: L5, L10 rolling averages
- `player_game_logs`: Game-by-game history

---

## Core Components

### 1. Database Setup (`database_setup.py`)

**Purpose**: Ensures all required tables exist with correct schema

**When to Run**:
- First time setup
- After system updates that change schema
- If tables get corrupted

**What It Does**:
```python
# Creates gto_parlays table if not exists
# Adds grading columns to prizepicks_edges
# Validates all expected tables
```

**Command**:
```bash
python database_setup.py
```

**Expected Output**:
```
[SUCCESS] gto_parlays table ready
[SUCCESS] Added result column to prizepicks_edges
[OK] predictions (435 rows)
[OK] prizepicks_edges (55 rows)
[OK] gto_parlays (0 rows)
```

---

### 2. Data Refresh (`smart_data_refresh.py`)

**Purpose**: Fetches fresh data from NHL API only when needed

**When to Run**:
- Automatically runs as part of workflow
- Manually if you need to force refresh

**What It Does**:
1. Checks when data was last updated
2. If >2 hours old, fetches new data:
   - Player stats (season totals)
   - Rolling stats (L5, L10 games)
   - Team stats (offensive/defensive ratings)
   - Goalie stats (save %, recent form)
   - Schedule (upcoming games)
3. Updates database tables
4. Logs refresh time

**API Endpoints Used**:
- `https://api-web.nhle.com/v1/player/{player_id}/landing` - Player stats
- `https://api-web.nhle.com/v1/club-stats/{team}/20252026/2` - Team stats
- `https://api-web.nhle.com/v1/schedule/{date}` - Schedule

**Dependencies**:
- None (independent component)

**Command**:
```bash
python smart_data_refresh.py
```

---

### 3. Prediction Generation (`generate_picks_to_file.py`)

**Purpose**: Generates T1-ELITE picks using statistical + ML models

**When to Run**:
- Daily before games (automated at 8:55 AM)
- Manually when you want fresh picks

**What It Does**:

**Step 1: Smart Data Refresh**
- Calls `smart_data_refresh.py` internally
- Ensures data is fresh before predictions

**Step 2: Feature Engineering**
- Loads player stats from database
- Calculates rolling averages (L5, L10 games)
- Computes matchup adjustments (team defense, goalie quality)
- Builds feature matrix for ML models

**Step 3: Statistical Model**
- Weighted average of:
  - Season average (40%)
  - L10 average (35%)
  - L5 average (25%)
- Adjusts for home/away
- Adjusts for rest days
- Adjusts for opponent defense

**Step 4: ML Ensemble**
- XGBoost model (trained on historical data)
- LightGBM model (trained on historical data)
- Ensemble prediction = weighted average

**Step 5: Confidence Scoring**
- Calculates probability for OVER
- Determines EV score
- Assigns confidence tier:
  - T1-ELITE: 10%+ edge
  - T2: 5-10% edge
  - T3: 3-5% edge

**Step 6: Database Save**
- Inserts predictions into `predictions` table
- Batch ID for tracking

**Step 7: File Export**
- Exports to `LATEST_PICKS.txt` (formatted)
- Exports to `LATEST_PICKS.csv` (spreadsheet format)
- Creates timestamped archive files

**Dependencies**:
- `player_stats` table (from smart_data_refresh)
- `team_stats` table
- `goalie_stats` table
- `games` table

**Command**:
```bash
python generate_picks_to_file.py
```

**Expected Output**:
```
[SUCCESS] Generated 47 predictions
[SUCCESS] Saved to database
[SUCCESS] Exported LATEST_PICKS.txt
[SUCCESS] Exported LATEST_PICKS.csv
```

---

### 4. PrizePicks Integration (`prizepicks_integration_v2.py`)

**Purpose**: Finds edge plays by comparing our predictions to PrizePicks lines

**When to Run**:
- After generating predictions
- Part of automated workflow

**What It Does**:

**Step 1: Load Predictions**
- Queries `predictions` table for today's T1-ELITE picks
- Filters for 10%+ edge plays

**Step 2: Fetch PrizePicks Lines**
- Calls PrizePicks API: `https://api.prizepicks.com/projections`
- Parameters: `league_id=8` (NHL), `per_page=250`
- Returns all available player props

**Step 3: Match Players & Props**
- Fuzzy matches player names
- Matches prop types (shots, points, etc.)
- Identifies line discrepancies

**Step 4: Calculate Edge**
- Our probability (from prediction model)
- PrizePicks implied probability (from odds_type)
  - Standard: ~66.67% implied (1.5x multiplier)
  - Goblin: ~60% implied (lower payout)
  - Demon: ~75% implied (higher payout)
- Edge = Our prob - PP implied prob

**Step 5: Calculate EV**
- EV = (Our prob × Payout) - 1
- Kelly score = Edge / (Payout - 1)

**Step 6: Filter & Save**
- Keeps picks with 7%+ edge
- Saves to `prizepicks_edges` table

**Step 7: Export**
- Prints to console (formatted output)
- Saves for GTO optimizer

**API Endpoints**:
- `https://api.prizepicks.com/projections?league_id=8`

**Dependencies**:
- `predictions` table (from generate_picks_to_file.py)
- PrizePicks API (external)

**Command**:
```bash
python prizepicks_integration_v2.py
```

**Expected Output**:
```
[INFO] Found 12 edge plays with 7%+ edge
[SUCCESS] Saved 12 edges to database

TOP EDGES:
  Matthews SHOTS O3.5 [STD] - 15.2% edge | 38.5% EV
  Nylander POINTS O0.5 [STD] - 12.8% edge | 32.1% EV
```

---

### 5. GTO Parlay Optimizer (`gto_parlay_optimizer.py`)

**Purpose**: Builds GTO-optimized parlays with frequency allocation

**When to Run**:
- After PrizePicks integration finds edges
- Part of automated workflow

**What It Does**:

**Step 1: Load Edge Plays**
- Queries `prizepicks_edges` table
- Loads picks with 7%+ edge
- Loads game_id for correlation checking

**Step 2: Frequency Allocation**
- Assigns target frequency based on EV:
  - EV >= 15%: Max frequency (20 uses)
  - EV >= 10%: High frequency (16 uses)
  - EV >= 7%: Medium frequency (12 uses)
- Similar to GTO poker hand ranges

**Step 3: Generate Candidate Parlays**
- Creates 2-leg combinations (100 candidates)
- Creates 3-leg combinations (50 candidates)
- Creates 4-leg combinations (25 candidates)
- Filters for:
  - Minimum EV threshold (10%)
  - No same-game parlays (correlation)
  - No same-team parlays (correlation)

**Step 4: Calculate Payouts**
- Uses `PrizePicksPayoutCalculator` for real payouts
- Handles mixed odds_types (standard + goblin = weighted avg)
- Calculates combined probability (product of individual probs)
- Calculates parlay EV

**Step 5: Optimize Selection (Greedy Algorithm)**
- Sorts parlays by EV (highest first)
- Selects parlays one by one
- Tracks pick frequency usage
- Stops when:
  - Target parlay count reached
  - Pick frequencies exhausted
  - No more valid parlays

**Step 6: Kelly Bet Sizing**
- For each selected parlay:
  - Kelly % = Edge / (Payout - 1)
  - Recommended bet = Bankroll × Kelly % × Kelly Fraction
  - Uses quarter Kelly (0.25) for safety

**Step 7: Export & Save**
- Exports CSV file with parlay details
- Saves to `gto_parlays` database table
- Includes picks_json for grading later

**Dependencies**:
- `prizepicks_edges` table
- `predictions` table (for game_id correlation check)
- `prizepicks_payouts.py` module

**Command**:
```bash
python gto_parlay_optimizer.py
python gto_parlay_optimizer.py 2025-10-30  # Specific date
python gto_parlay_optimizer.py 2025-10-30 2000  # Custom bankroll
```

**Expected Output**:
```
[INFO] Loaded 12 edge plays
[INFO] Generated 175 candidate parlays
[INFO] Selected 14 optimal parlays (8x 2-leg, 4x 3-leg, 2x 4-leg)

PARLAY #1 (2-leg)
  Leg 1: Matthews SHOTS O3.5 [standard]
  Leg 2: Marchenko SHOTS O2.5 [standard]

  Probability: 75.3%
  Payout:      2.25x
  EV:          +69.5%
  Kelly Bet:   $47.23 (4.7% of bankroll)

[SUCCESS] Exported GTO_PARLAYS_2025-10-30_09-15AM.csv
[SUCCESS] Saved 14 parlays to database
```

---

### 6. Complete Workflow (`run_complete_workflow_gto.py`)

**Purpose**: Master automation script that runs everything in sequence

**When to Run**:
- Daily (automated via Task Scheduler at 8:55 AM)
- Manually when you want fresh picks

**What It Does**:

**Step 0 (Optional): Fetch Daily Game Odds** ⭐ NEW!
- Can be run separately: `fetch_daily_odds.py`
- Fetches real betting lines from The Odds API
- Moneylines, spreads, totals for all NHL games
- Uses 1 API call (stays under 500/month limit)
- Saves to database for TOI and game script analysis

**Step 1: Generate Predictions**
- Runs `generate_picks_to_file.py`
- Smart data refresh included
- Uses real betting lines from database
- Saves predictions to database
- Exports LATEST_PICKS files

**Step 2: Find PrizePicks Edge**
- Runs `prizepicks_integration_v2.py`
- Matches predictions to PrizePicks lines
- Saves edges to database

**Step 3: Build GTO Parlays**
- Runs `gto_parlay_optimizer.py`
- Generates optimized parlays
- Saves parlays to database
- Exports GTO_PARLAYS CSV

**Step 4: Commit to GitHub**
- Finds latest GTO_PARLAYS CSV
- Adds files: LATEST_PICKS.txt, LATEST_PICKS.csv, GTO_PARLAYS_*.csv
- Commits with timestamp
- Pushes to GitHub

**Error Handling**:
- If Step 1 fails: Stops (can't continue without predictions)
- If Step 2 fails: Skips parlays, but picks still usable
- If Step 3 fails: Edges still usable
- If Step 4 fails: Files saved locally

**Dependencies**:
- All component scripts must exist
- Git must be installed and configured
- Database must be set up

**Command**:
```bash
python run_complete_workflow_gto.py
```

**Expected Output**:
```
================================================================================
COMPLETE NHL BETTING WORKFLOW WITH GTO PARLAYS
================================================================================
Started: 2025-10-30 09:00 AM

[STEP 1: Generate Predictions]
...
[SUCCESS] Generate Predictions

[STEP 2: Find PrizePicks Edge]
...
[SUCCESS] Find PrizePicks Edge

[STEP 3: Build GTO Parlays]
...
[SUCCESS] Build GTO Parlays

[STEP 4: Commit to GitHub]
[SUCCESS] Successfully pushed to GitHub!

================================================================================
WORKFLOW SUMMARY
================================================================================
Completed: 4/4 steps
Time: 2025-10-30 09:05 AM

[SUCCESS] Ready to bet!

Check these files:
   1. LATEST_PICKS.txt - Individual T1-ELITE picks
   2. LATEST_PICKS.csv - CSV format for spreadsheets
   3. GTO_PARLAYS_2025-10-30_09-00AM.csv - Optimized parlay combinations

View online (auto-updated):
   TXT: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
   CSV: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.csv
   GTO: https://github.com/thomascp2/nhl-predictions/blob/main/GTO_PARLAYS_2025-10-30_09-00AM.csv
```

---

### 7. Grading System (`grade_all_picks.py`)

**Purpose**: Grades all picks/edges/parlays against actual NHL results

**When to Run**:
- After games finish (usually next morning)
- Manually for specific date

**What It Does**:

**Step 1: Fetch Game Results**
- Calls NHL API: `https://api-web.nhle.com/v1/score/{date}`
- Gets all games for the date
- Checks if games are final

**Step 2: Fetch Player Stats**
- For each game, calls: `https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore`
- Extracts player stats (goals, assists, points, shots)
- Builds lookup dictionary

**Step 3: Grade Predictions**
- Queries `predictions` table for ungraded picks
- Matches player names (fuzzy matching)
- Compares actual value to line
- Determines HIT or MISS
- Updates database with result

**Step 4: Grade PrizePicks Edges**
- Same process for `prizepicks_edges` table
- Grades OVER picks against actual values
- Updates database with result

**Step 5: Grade GTO Parlays**
- Queries `gto_parlays` table
- Parses picks_json
- Checks if ALL legs hit
- Determines HIT or MISS for parlay
- Updates database with result and actual_payout

**Step 6: Summary Report**
- Calculates hit rates for each category
- Calculates profit/ROI
- Prints detailed summary

**API Endpoints**:
- `https://api-web.nhle.com/v1/score/{date}`
- `https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore`

**Dependencies**:
- `predictions` table
- `prizepicks_edges` table
- `gto_parlays` table
- NHL API (external)

**Command**:
```bash
python grade_all_picks.py 2025-10-29
python grade_all_picks.py  # Defaults to today
```

**Expected Output**:
```
================================================================================
COMPREHENSIVE GRADING SYSTEM - 2025-10-29
================================================================================

[STEP 1] Fetching game results from NHL API...
[INFO] Found 8 games for 2025-10-29
[WARNING] Only 8/8 games are final

[STEP 2] Fetching player stats...
[INFO] Loaded stats for 182 players

[STEP 3] Grading predictions...
[RESULTS] Graded: 47 | Hits: 31 | Misses: 16 | Not found: 2
[SUMMARY] Hit Rate: 65.9%

[STEP 4] Grading PrizePicks edges...
[RESULTS] Graded: 12 | Hits: 9 | Misses: 3 | Not found: 0
[SUMMARY] Hit Rate: 75.0%
[SUMMARY] Profit: +6.19 units
[SUMMARY] ROI: +51.6%

[STEP 5] Grading GTO parlays...
[RESULTS] Graded: 14 | Hits: 4 | Misses: 10
[SUMMARY] Hit Rate: 28.6%

================================================================================
GRADING COMPLETE
================================================================================

PREDICTIONS:
  Graded: 47
  Hits: 31
  Misses: 16
  Hit Rate: 65.9%

PRIZEPICKS EDGES:
  Graded: 12
  Hits: 9
  Misses: 3
  Hit Rate: 75.0%
  Profit: +6.19 units
  ROI: +51.6%

GTO PARLAYS:
  Graded: 14
  Hits: 4
  Misses: 10
  Hit Rate: 28.6%
```

---

### 8. Odds Tracking (`log_parlay.py`)

**Purpose**: Interactive tool for logging actual parlay payouts from PrizePicks

**When to Run**:
- After placing each bet on PrizePicks
- Takes 30 seconds per parlay

**What It Does**:

**Interactive Session**:
1. Prompts for date (defaults to today)
2. Prompts for actual payout multiplier (e.g., 2.25)
3. Prompts for number of legs
4. For each leg:
   - Player name
   - Prop type
   - Line

**Reverse Engineering**:
- For 2-leg parlays: Individual = sqrt(payout)
- For 3+ leg parlays: Individual = payout^(1/n)
- Saves to `prizepicks_parlay_observations`
- Calculates implied multipliers
- Saves to `prizepicks_observed_odds`

**Confidence Scoring**:
- 2-leg: 70% confidence (reasonable assumption)
- 3+ leg: 50% confidence (rougher estimate)
- Improves with multiple observations

**Dependencies**:
- `prizepicks_odds_scraper.py` module
- `prizepicks_parlay_observations` table
- `prizepicks_observed_odds` table

**Command**:
```bash
python log_parlay.py
```

**Example Session**:
```
================================================================================
PRIZEPICKS PARLAY OBSERVATION LOGGER
================================================================================

Date (YYYY-MM-DD) or press Enter for today: [Enter]
  Using today's date: 2025-10-30

Actual payout multiplier (e.g., 2.25 for $1 wins $2.25): 2.25

Number of legs in parlay: 2

Leg 1:
  Player name: Auston Matthews
  Prop type (shots/points/goals/assists/blocks/hits): shots
  Line (e.g., 3.5): 3.5

Leg 2:
  Player name: Kirill Marchenko
  Prop type: shots
  Line: 2.5

================================================================================
CONFIRM YOUR PARLAY:
================================================================================
Date: 2025-10-30
Payout: 2.25x
Legs: 2

  1. Auston Matthews SHOTS O3.5
  2. Kirill Marchenko SHOTS O2.5

Is this correct? (y/n): y

[SUCCESS] Added parlay observation: 2-leg, 2.25x payout
  Implied individual odds: ~1.50x each

================================================================================
LEARNED INDIVIDUAL ODDS:
================================================================================
Auston Matthews SHOTS O3.5
  Implied multiplier: 1.50x
  Confidence: 70%

Kirill Marchenko SHOTS O2.5
  Implied multiplier: 1.50x
  Confidence: 70%

================================================================================
[SUCCESS] Parlay logged successfully!
================================================================================

Keep logging more parlays to improve accuracy!
Goal: 50-100 observations for solid ML training data
```

---

## Daily Workflow

### Automated (Recommended)

**Setup**: Windows Task Scheduler runs at **8:55 AM daily**

**What Happens**:
1. Task Scheduler triggers `run_complete_workflow_gto.py`
2. System generates predictions
3. Finds PrizePicks edges
4. Builds GTO parlays
5. Commits to GitHub
6. Completes in ~5 minutes

**Check Your Picks**:
- Visit GitHub (from phone/computer):
  - https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
  - https://github.com/thomascp2/nhl-predictions/blob/main/GTO_PARLAYS_*.csv
- Or check local files:
  - `C:\Users\thoma\PrizePicks-Research-Lab\LATEST_PICKS.txt`
  - `C:\Users\thoma\PrizePicks-Research-Lab\GTO_PARLAYS_*.csv`

---

### Manual Run

**When**: Any time you want fresh picks

**Command**:
```bash
cd C:\Users\thoma\PrizePicks-Research-Lab
python run_complete_workflow_gto.py
```

**Duration**: ~3-5 minutes

---

### After Placing Bets

**IMPORTANT**: Log every parlay you place!

**Command**:
```bash
python log_parlay.py
```

**Why**: Builds training data for individual pick odds

**Goal**: 50-100 observations this month for ML model

---

### Next Day Grading

**When**: After games finish (usually next morning)

**Command**:
```bash
python grade_all_picks.py 2025-10-29
```

**What It Does**:
- Fetches game results
- Grades all picks/edges/parlays
- Updates database
- Prints performance summary

---

## Running the System

### First Time Setup

1. **Validate Database**:
```bash
python database_setup.py
```

2. **Fetch Initial Data**:
```bash
python smart_data_refresh.py
```

3. **Run Complete Workflow**:
```bash
python run_complete_workflow_gto.py
```

4. **Check Output**:
```bash
cat LATEST_PICKS.txt
cat GTO_PARLAYS_*.csv
```

---

### Daily Use

**Morning**:
- System runs automatically at 8:55 AM
- Check GitHub or local files for picks

**During Day**:
- Place bets on PrizePicks
- Log each parlay: `python log_parlay.py`

**Next Day**:
- Grade previous day: `python grade_all_picks.py 2025-10-29`
- Review performance

---

## Grading & Performance Tracking

### View Graded Results

**Query Database**:
```bash
# View predictions with results
python -c "import sqlite3; import pandas as pd; conn = sqlite3.connect('database/nhl_predictions.db'); df = pd.read_sql('SELECT player_name, prop_type, line, prediction, probability, result, actual_value FROM predictions WHERE game_date = \"2025-10-29\" ORDER BY probability DESC', conn); print(df)"

# View edges with results
python -c "import sqlite3; import pandas as pd; conn = sqlite3.connect('database/nhl_predictions.db'); df = pd.read_sql('SELECT player_name, prop_type, line, edge, result, actual_value FROM prizepicks_edges WHERE date = \"2025-10-29\" ORDER BY edge DESC', conn); print(df)"

# View parlays with results
python -c "import sqlite3; import pandas as pd; conn = sqlite3.connect('database/nhl_predictions.db'); df = pd.read_sql('SELECT parlay_id, num_legs, combined_probability, payout_multiplier, expected_value, result FROM gto_parlays WHERE date = \"2025-10-29\"', conn); print(df)"
```

---

### Performance Metrics

**Hit Rate**:
```sql
SELECT
    COUNT(CASE WHEN result = 'HIT' THEN 1 END) * 100.0 / COUNT(*) as hit_rate
FROM prizepicks_edges
WHERE date BETWEEN '2025-10-01' AND '2025-10-31'
```

**ROI**:
```sql
SELECT
    SUM(CASE WHEN result = 'HIT' THEN 0.91 ELSE -1 END) as profit,
    SUM(CASE WHEN result = 'HIT' THEN 0.91 ELSE -1 END) * 100.0 / COUNT(*) as roi_pct
FROM prizepicks_edges
WHERE date BETWEEN '2025-10-01' AND '2025-10-31'
```

---

## Dependencies & Requirements

### Python Packages

**Required**:
```
pandas
numpy
requests
sqlite3 (built-in)
```

**Optional** (for ML models):
```
scikit-learn
xgboost
lightgbm
```

**Install**:
```bash
pip install pandas numpy requests scikit-learn xgboost lightgbm
```

---

### External Services

**NHL API** (Free):
- No API key required
- Rate limits unknown (be reasonable)
- Endpoints:
  - `https://api-web.nhle.com/v1/*`

**PrizePicks API** (Free):
- No API key required
- Public projections endpoint
- May have rate limits
- Endpoint:
  - `https://api.prizepicks.com/projections`

---

### Files Required

**Core Scripts**:
- `database_setup.py`
- `smart_data_refresh.py`
- `generate_picks_to_file.py`
- `prizepicks_integration_v2.py`
- `gto_parlay_optimizer.py`
- `run_complete_workflow_gto.py`
- `grade_all_picks.py`
- `log_parlay.py`

**Supporting Modules**:
- `prizepicks_payouts.py` - Payout calculator
- `prizepicks_odds_scraper.py` - Odds tracking

**Database**:
- `database/nhl_predictions.db`

---

## Troubleshooting

### Database Issues

**Error**: `no such table: gto_parlays`
**Fix**:
```bash
python database_setup.py
```

**Error**: `database is locked`
**Fix**: Close all scripts accessing the database, wait 10 seconds, try again

---

### API Issues

**Error**: `403 Forbidden` from PrizePicks
**Fix**: Wait 5 minutes, try again. They may have rate limits.

**Error**: `No games found` from NHL API
**Fix**: Check date format (YYYY-MM-DD), ensure games exist for that date

---

### Workflow Failures

**Step 1 Fails** (Predictions):
```bash
# Check if data is fresh
python -c "import sqlite3; conn = sqlite3.connect('database/nhl_predictions.db'); cursor = conn.cursor(); cursor.execute('SELECT MAX(last_updated) FROM player_stats'); print(cursor.fetchone())"

# Force refresh
python smart_data_refresh.py

# Try again
python generate_picks_to_file.py
```

**Step 2 Fails** (PrizePicks):
```bash
# Check if predictions exist
python -c "import sqlite3; import pandas as pd; conn = sqlite3.connect('database/nhl_predictions.db'); df = pd.read_sql('SELECT COUNT(*) FROM predictions WHERE game_date = \"2025-10-30\"', conn); print(df)"

# Try manually
python prizepicks_integration_v2.py
```

**Step 3 Fails** (GTO Parlays):
```bash
# Check if edges exist
python -c "import sqlite3; import pandas as pd; conn = sqlite3.connect('database/nhl_predictions.db'); df = pd.read_sql('SELECT COUNT(*) FROM prizepicks_edges WHERE date = \"2025-10-30\"', conn); print(df)"

# Try manually
python gto_parlay_optimizer.py
```

**Step 4 Fails** (GitHub):
```bash
# Check git status
git status

# Manual commit
git add LATEST_PICKS.txt LATEST_PICKS.csv GTO_PARLAYS_*.csv
git commit -m "Manual update"
git push
```

---

### Task Scheduler Issues

**Check if Task is Running**:
```powershell
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" | Format-List
```

**View Last Run Result**:
```powershell
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" | Get-ScheduledTaskInfo
```

**Test Task Manually**:
```powershell
Start-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
```

---

## Summary

You now have a **complete, production-ready NHL betting system**:

✅ **End-to-end automation** (data → predictions → edges → parlays)
✅ **Database tracking** (all picks stored and graded)
✅ **GTO optimization** (frequency allocation + Kelly sizing)
✅ **Real PrizePicks payouts** (standard/goblin/demon modes)
✅ **Odds tracking system** (reverse engineering individual multipliers)
✅ **Comprehensive grading** (predictions + edges + parlays)
✅ **GitHub integration** (access from anywhere)
✅ **Task Scheduler automation** (100% hands-free)

**Files generated daily**:
- `LATEST_PICKS.txt` / `.csv` - T1-ELITE individual picks
- `GTO_PARLAYS_*.csv` - Optimized parlay recommendations
- Database updates (all tables)
- GitHub commits (remote access)

**Performance tracking**:
- Hit rates for predictions, edges, parlays
- ROI and profit/loss calculations
- Historical trends

**Next steps**:
1. Run system daily (automated)
2. Place bets using GTO parlays
3. Log every parlay with `log_parlay.py`
4. Grade results next day
5. Build 50-100 parlay observations
6. Train ML model for individual pick odds
7. Iterate and improve!

**The system is ready. Time to make some +EV bets!**
