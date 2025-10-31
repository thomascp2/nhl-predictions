# The Odds API Integration Setup Guide

Complete guide to integrating The Odds API for real player prop odds.

## Why Use The Odds API?

**Current Problem:**
- We've been estimating PrizePicks multipliers
- Using placeholder betting lines in TOI system
- Assuming standard payout models (4x, 3x, 2x)

**Solution:**
- Get real player prop odds in American odds format
- Know exact market lines for every stat (Points, Shots, TOI, etc.)
- Calculate true expected value with actual odds
- 500 free API calls per month (plenty if used smartly)

## Step 1: Get Your Free API Key

1. Visit: https://the-odds-api.com/

2. Click "Get API Key" or "Sign Up"

3. Create free account

4. Copy your API key from dashboard

5. **Free Tier Includes:**
   - 500 requests per month
   - Resets on the 1st of each month
   - All sports and markets
   - Real-time odds

## Step 2: Set Up API Key

### Option A: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('ODDS_API_KEY', 'your_key_here', 'User')
```

**Windows (Command Prompt):**
```cmd
setx ODDS_API_KEY "your_key_here"
```

**Verify it works:**
```powershell
echo $env:ODDS_API_KEY
```

### Option B: Pass Directly in Code

```python
from odds_api_integration import OddsAPIClient

client = OddsAPIClient(api_key='your_key_here')
```

### Option C: Store in .env File

Create `.env` file:
```
ODDS_API_KEY=your_key_here
```

Then in Python:
```python
from dotenv import load_dotenv
load_dotenv()

from odds_api_integration import OddsAPIClient
client = OddsAPIClient()  # Reads from environment
```

## Step 3: Test the Integration

```bash
python odds_api_integration.py
```

This will:
1. Check your API key
2. Show current API usage (X/500 calls used)
3. Fetch game odds (ML, spreads, totals)
4. Fetch player props (points, shots, assists, etc.)
5. Cache data in database

## Step 4: Smart API Usage Strategy

### Stay Under 500 Calls/Month

**Strategy: 1 Call Per Day**
```
1 call/day × 30 days = 30 calls/month
Leaves 470 calls for special situations
```

**Recommended Schedule:**
- **Daily at 8:00 AM**: Fetch all game odds + player props
- **Use cache** for rest of day
- **Refresh only if needed** (injury news, line movement)

### API Call Costs

| Endpoint | Cost | What It Gets |
|----------|------|--------------|
| Game Odds | 1 call | All NHL games for today (ML, spreads, totals) |
| Player Props (all markets) | 1 call | All player props for all games |
| Player Props (per market) | 1 call | One market (e.g., just points) for all games |

**Optimization Tips:**
1. Fetch all markets at once (1 call vs 5 separate calls)
2. Cache aggressively (24-hour cache by default)
3. Only refresh when lines move significantly
4. Use `force_refresh=False` in code

### Monthly Budget Example

```
Week 1: 7 days × 1 call = 7 calls
Week 2: 7 days × 1 call = 7 calls
Week 3: 7 days × 1 call = 7 calls
Week 4: 7 days × 1 call = 7 calls
Ad-hoc: 10 manual refreshes = 10 calls
-------------------------------------------
Total: 38 calls/month (well under 500 limit!)
```

## Available Markets

### Game Odds Markets

- **h2h**: Moneylines (home/away to win)
- **spreads**: Puck line (usually ±1.5)
- **totals**: Over/Under total goals

### Player Prop Markets

The Odds API supports these player prop markets:

- **player_points**: Total points (goals + assists)
- **player_goals**: Goals scored
- **player_assists**: Assists
- **player_shots_on_goal**: Shots on goal
- **player_power_play_points**: Power play points
- **player_blocked_shots**: Blocked shots
- **player_time_on_ice**: Time on ice (TOI)

**Note:** Not all markets available for every game/player. Depends on bookmakers.

## Code Examples

### Example 1: Get Today's Game Odds

```python
from odds_api_integration import OddsAPIClient

client = OddsAPIClient()

# Fetch game odds (uses cache if available)
game_odds = client.fetch_game_odds()

# Get specific game
tor_bos = game_odds[
    (game_odds['home_team'] == 'Toronto Maple Leafs') &
    (game_odds['away_team'] == 'Boston Bruins')
]

print(f"TOR vs BOS:")
for _, row in tor_bos.iterrows():
    print(f"  {row['bookmaker']}: ML {row['home_ml']}/{row['away_ml']}, O/U {row['over_under']}")

client.close()
```

### Example 2: Get Player Props

```python
from odds_api_integration import OddsAPIClient

client = OddsAPIClient()

# Fetch player props (uses cache if available)
props = client.fetch_player_props(
    markets='player_points,player_shots_on_goal'
)

# Get specific player
matthews_props = props[props['player_name'].str.contains('Matthews', case=False)]

print("Auston Matthews props:")
for _, row in matthews_props.iterrows():
    print(f"  {row['prop_type']} {row['line']}: O {row['over_odds']} / U {row['under_odds']}")

client.close()
```

### Example 3: Find Best Odds

```python
from odds_api_integration import OddsAPIClient

client = OddsAPIClient()

# Fetch all props
client.fetch_player_props()

# Get best odds for specific player/prop
best = client.get_best_odds_for_player(
    player_name='Auston Matthews',
    prop_type='points',
    line=1.5
)

print(f"Best odds for Matthews over 1.5 points:")
print(f"  Best Over: {best['best_over_odds']} ({best['bookmaker_over']})")
print(f"  Best Under: {best['best_under_odds']} ({best['bookmaker_under']})")

client.close()
```

### Example 4: Calculate Expected Value

```python
from odds_api_integration import OddsAPIClient

client = OddsAPIClient()

# Our model predicts 65% chance player goes over
our_probability = 0.65

# Market is offering -110 on the over
market_odds = -110

# Calculate EV
ev = client.calculate_expected_value(our_probability, market_odds)
market_prob = client.convert_american_odds_to_probability(market_odds)

print(f"Our probability: {our_probability:.1%}")
print(f"Market probability: {market_prob:.1%}")
print(f"Expected Value: {ev:+.2%}")

if ev > 0:
    print("BET OVER - Positive EV!")
else:
    print("PASS - Negative EV")

client.close()
```

### Example 5: Daily Workflow

```python
from odds_api_integration import OddsAPIClient
import pandas as pd

def daily_odds_update():
    """Run once per day to update all odds"""
    client = OddsAPIClient()

    # Fetch game odds (1 API call)
    print("Fetching game odds...")
    game_odds = client.fetch_game_odds(
        markets='h2h,spreads,totals',
        force_refresh=True  # Force fresh data
    )

    # Fetch player props (1 API call for all markets)
    print("Fetching player props...")
    player_props = client.fetch_player_props(
        markets='player_points,player_shots_on_goal,player_assists,player_time_on_ice',
        force_refresh=True
    )

    # Export for review
    game_odds.to_csv('ODDS_GAME_LINES.csv', index=False)
    player_props.to_csv('ODDS_PLAYER_PROPS.csv', index=False)

    print(f"\nFetched:")
    print(f"  {len(game_odds)} game odds records")
    print(f"  {len(player_props)} player prop records")
    print(f"  API calls remaining: {client.requests_remaining}/500")

    client.close()

if __name__ == "__main__":
    daily_odds_update()
```

## Integration with Existing Systems

### 1. Update TOI System

Replace placeholder betting lines in `fetch_toi_data.py`:

```python
# OLD: fetch_betting_lines_placeholder()
# NEW: Use real odds

from odds_api_integration import OddsAPIClient

def fetch_betting_lines_real(game_date: str) -> pd.DataFrame:
    """Fetch real betting lines from The Odds API"""
    client = OddsAPIClient()
    game_odds = client.fetch_game_odds(use_cache=True)
    client.close()

    # Filter for specific date
    game_odds['game_date'] = pd.to_datetime(game_odds['commence_time']).dt.date
    today_odds = game_odds[game_odds['game_date'] == pd.to_datetime(game_date).date()]

    return today_odds
```

### 2. Update Multi-Line Optimizer

Replace learned multipliers with real odds in `prizepicks_multi_line_optimizer.py`:

```python
# OLD: Use learned multipliers CSV
# NEW: Use real odds from API

from odds_api_integration import OddsAPIClient

def get_real_player_prop_odds(player_name: str, stat_type: str, line: float) -> Dict:
    """Get real odds instead of estimated multipliers"""
    client = OddsAPIClient()

    # Map PrizePicks stat types to Odds API prop types
    stat_map = {
        'Points': 'player_points',
        'Shots on Goal': 'player_shots_on_goal',
        'Assists': 'player_assists',
        'Goals': 'player_goals',
        'Time on Ice': 'player_time_on_ice'
    }

    prop_type = stat_map.get(stat_type, stat_type.lower().replace(' ', '_'))

    # Get best odds
    best_odds = client.get_best_odds_for_player(player_name, prop_type, line)

    # Convert to implied probability
    if best_odds['best_over_odds']:
        over_prob = client.convert_american_odds_to_probability(best_odds['best_over_odds'])

        # Calculate equivalent multiplier for PrizePicks
        # If market says 55% chance, PrizePicks might price it at 1/0.55 = 1.82x
        multiplier = 1.0 / over_prob
    else:
        multiplier = 2.0  # Default fallback

    client.close()

    return {
        'multiplier': multiplier,
        'real_odds': best_odds['best_over_odds'],
        'implied_prob': over_prob,
        'bookmaker': best_odds['bookmaker_over']
    }
```

### 3. Update GTO Parlay Optimizer

Use real odds for EV calculations:

```python
# In gto_parlay_optimizer.py

from odds_api_integration import OddsAPIClient

def calculate_parlay_ev_with_real_odds(picks: List[Dict]) -> float:
    """Calculate parlay EV using real market odds"""
    client = OddsAPIClient()

    parlay_prob = 1.0

    for pick in picks:
        # Get real market odds
        best_odds = client.get_best_odds_for_player(
            pick['player_name'],
            pick['stat_type'],
            pick['line']
        )

        if best_odds['best_over_odds']:
            market_prob = client.convert_american_odds_to_probability(
                best_odds['best_over_odds']
            )

            # Compare to our model's probability
            our_prob = pick['our_probability']

            # Only include if we have edge
            if our_prob > market_prob:
                parlay_prob *= our_prob
            else:
                # Skip this pick - no edge
                return None

    client.close()

    return parlay_prob
```

## Monitoring API Usage

### Check Current Usage

```python
from odds_api_integration import OddsAPIClient

client = OddsAPIClient()
print(f"API calls used this month: {client.requests_used_this_month}/500")
print(f"Remaining: {client.requests_remaining}")
client.close()
```

### View Usage History

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/nhl_predictions.db')

usage = pd.read_sql_query("""
    SELECT
        DATE(timestamp) as date,
        endpoint,
        SUM(requests_used) as calls,
        MIN(requests_remaining) as remaining
    FROM odds_api_usage
    WHERE month = strftime('%Y-%m', 'now')
    GROUP BY DATE(timestamp), endpoint
    ORDER BY date DESC
""", conn)

print(usage)
conn.close()
```

## Troubleshooting

### Error: "No API key provided"

**Solution:** Set environment variable:
```powershell
[System.Environment]::SetEnvironmentVariable('ODDS_API_KEY', 'your_key_here', 'User')
```

Then restart terminal/Python.

### Error: "API request limit exceeded"

**Solution:** You've used all 500 calls this month. Either:
1. Wait until next month (resets on 1st)
2. Upgrade to paid plan ($20/month = 5,000 calls)
3. Use cached data for now

### Error: "No data returned from API"

**Possible causes:**
1. No NHL games today
2. Player props not available yet (check time)
3. Bookmakers haven't posted lines yet

**Solution:** Check The Odds API website to see if data is available.

### Missing Player Props

**Issue:** Some players don't have props available

**Why:**
- Bookmakers only post props for star players
- Some stats (like TOI) less commonly offered
- Props posted closer to game time

**Solution:**
- Focus on stars with consistent prop availability
- Check multiple bookmakers
- Fall back to model estimates if no odds available

## Cost Analysis

### Free Tier: $0/month

- 500 requests/month
- Perfect for daily betting operation
- 1 call per day = 30 calls/month (94% under limit)

### Paid Tier: $20/month (if needed)

- 5,000 requests/month
- Allows for:
  - Multiple daily refreshes
  - Live betting integration
  - Line movement tracking
  - Historical odds analysis

**Recommendation:** Start with free tier. You won't need paid unless you want real-time line tracking.

## Best Practices

1. **Cache Aggressively**
   - Default 24-hour cache is fine for daily betting
   - Don't refresh unless lines move significantly

2. **Batch API Calls**
   - Fetch all markets at once (1 call vs 5 calls)
   - Fetch all games at once

3. **Smart Scheduling**
   - Run once per day at 8:00 AM
   - Lines are usually set by then
   - Leaves 470 calls/month for emergencies

4. **Monitor Usage**
   - Check `client.requests_remaining` regularly
   - Log all API calls to database
   - Set alerts if approaching limit

5. **Handle Missing Data**
   - Not all props available for all players
   - Fall back to model estimates
   - Don't make 10 calls looking for one prop

6. **Test First**
   - Use `use_cache=True` in development
   - Only `force_refresh=True` in production
   - Verify data quality before betting

## Next Steps

1. Get your free API key: https://the-odds-api.com/

2. Set environment variable with your key

3. Run test: `python odds_api_integration.py`

4. Integrate into daily workflow:
   - Update `run_complete_workflow_gto.py`
   - Replace placeholder odds
   - Use real odds for EV calculations

5. Monitor usage and optimize as needed

## Summary

**What Changes:**
- ✅ Real player prop odds instead of estimates
- ✅ Actual market lines for every stat
- ✅ True expected value calculations
- ✅ Better edge detection

**What Stays the Same:**
- ✅ Your prediction models
- ✅ Database structure
- ✅ Daily workflow
- ✅ GTO parlay optimization logic

**Result:**
- More accurate EV calculations
- Better bet selection
- Confidence in your edge
- Data-driven decisions
