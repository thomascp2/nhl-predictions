"""
STARS ONLY FILTER
=================
Simplify betting strategy: Only show picks for elite players in favorable situations

Criteria:
  1. Star player (curated list of ~30 top players)
  2. Playing in a favorable matchup (high O/U, reasonable moneyline)
  3. High confidence prediction (T1-ELITE or T2-STRONG)

This is way simpler and more profitable than predicting 100+ players per day.
"""

import sqlite3
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"

# CURATED STARS LIST - Expanded to 50 players based on database analysis
# Sources: T1-ELITE picks Oct 31-Nov 2 + known superstars + high-volume young stars
# To use old 32-player list, see stars_only_filter_compact.py

STARS = [
    # Tier 1: SUPERSTARS (Must-bet when favorable) - 15 players
    "Connor McDavid", "Nathan MacKinnon", "Auston Matthews", "Leon Draisaitl",
    "David Pastrnak", "Nikita Kucherov", "Kirill Kaprizov", "Matthew Tkachuk",
    "Artemi Panarin", "Jack Hughes", "Cale Makar", "Sidney Crosby",
    "Jack Eichel", "Elias Pettersson", "Jason Robertson",

    # Tier 2: ELITE SCORERS (Very reliable) - 18 players
    "William Nylander", "Mitch Marner", "Kyle Connor", "Mark Scheifele",
    "Sebastian Aho", "Mark Stone", "Mikko Rantanen", "Tim Stutzle",
    "John Tavares", "Brayden Point", "Tage Thompson", "Cole Caufield",
    "Adrian Kempe", "Seth Jarvis", "Matt Boldy", "Alex DeBrincat",
    "Matthew Knies", "Pavel Dorofeyev",

    # Tier 3: YOUNG STARS & HIGH-VOLUME (Good for specific props) - 17 players
    "Connor Bedard", "Macklin Celebrini", "Leo Carlsson", "Cutter Gauthier",
    "Alex Ovechkin", "Evgeni Malkin", "Brad Marchand", "Dylan Larkin",
    "Bo Horvat", "Nick Suzuki", "Kirill Marchenko", "Troy Terry",
    "William Eklund", "Zach Werenski", "Filip Forsberg", "Jake Guentzel",
    "Valeri Nichushkin"
]

# Favorable matchup criteria
FAVORABLE_MATCHUP = {
    "min_over_under": 5.5,    # Game expected to have at least 5.5 goals
    "max_favorite_ml": -175,  # Team not favored by more than -175
    "min_underdog_ml": +150   # Team not underdog worse than +150
}


def get_betting_context(team, opponent, game_date):
    """Get betting lines for context"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT away_team, home_team, away_ml, home_ml, over_under
        FROM game_betting_lines
        WHERE game_date = ?
        AND (away_team = ? OR home_team = ?)
        LIMIT 1
    """, (game_date, team, team))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    away_team, home_team, away_ml, home_ml, over_under = result

    # Determine if our team is home or away
    if team == home_team:
        our_ml = home_ml
    else:
        our_ml = away_ml

    return {
        "over_under": over_under,
        "our_ml": our_ml
    }


def is_favorable_matchup(betting_context):
    """Check if this is a favorable betting situation"""
    if not betting_context:
        return False, "No betting data"

    ou = betting_context.get("over_under")
    ml = betting_context.get("our_ml")

    # Check over/under (high-scoring game expected)
    if ou and ou < FAVORABLE_MATCHUP["min_over_under"]:
        return False, f"Low O/U ({ou})"

    # Check moneyline (not too lopsided)
    if ml:
        if ml < 0 and ml < FAVORABLE_MATCHUP["max_favorite_ml"]:
            return False, f"Heavy favorite ({ml})"
        if ml > 0 and ml > FAVORABLE_MATCHUP["min_underdog_ml"]:
            return False, f"Heavy underdog (+{ml})"

    return True, "Favorable"


def get_stars_picks(game_date, min_tier="T2-STRONG"):
    """Get picks for star players only, in favorable matchups"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tier priority
    tier_order = {"T1-ELITE": 1, "T2-STRONG": 2, "T3-SOLID": 3}
    min_tier_value = tier_order.get(min_tier, 2)

    # Get all predictions for stars
    placeholders = ",".join(["?" for _ in STARS])
    query = f"""
        SELECT
            player_name,
            team,
            opponent,
            prop_type,
            line,
            probability,
            expected_value,
            confidence_tier,
            reasoning
        FROM predictions
        WHERE game_date = ?
        AND player_name IN ({placeholders})
        ORDER BY probability DESC
    """

    cursor.execute(query, [game_date] + STARS)
    all_picks = cursor.fetchall()
    conn.close()

    # Filter by tier and matchup
    filtered_picks = []

    for pick in all_picks:
        player, team, opp, prop, line, prob, ev, tier, reason = pick

        # Check tier
        if tier_order.get(tier, 99) > min_tier_value:
            continue

        # Check betting context
        betting_ctx = get_betting_context(team, opp, game_date)
        is_favorable, matchup_note = is_favorable_matchup(betting_ctx)

        filtered_picks.append({
            "player": player,
            "team": team,
            "opponent": opp,
            "prop_type": prop,
            "line": line,
            "probability": prob,
            "ev": ev,
            "tier": tier,
            "reasoning": reason,
            "matchup": matchup_note,
            "is_favorable": is_favorable,
            "betting": betting_ctx
        })

    return filtered_picks


def display_stars_picks(picks, favorable_only=True):
    """Display picks in a clean format"""

    if favorable_only:
        picks = [p for p in picks if p["is_favorable"]]

    if not picks:
        print("\nNo star picks in favorable matchups today.")
        print("Try expanding criteria or waiting for better matchups.")
        return

    print(f"\n{'='*80}")
    print("STARS ONLY PICKS - Simplified Betting Strategy")
    print(f"{'='*80}\n")
    print(f"Total Picks: {len(picks)}")
    print(f"Strategy: Only bet elite players in favorable situations\n")
    print(f"{'-'*80}\n")

    for i, pick in enumerate(picks, 1):
        betting = pick["betting"] or {}
        ou = betting.get("over_under", "N/A")
        ml = betting.get("our_ml", "N/A")

        print(f"PICK #{i}")
        print(f"Player:   {pick['player']} ({pick['team']} vs {pick['opponent']})")
        print(f"Prop:     {pick['prop_type'].upper()} - Line: {pick['line']}")
        print(f"Prob:     {pick['probability']*100:.1f}% | Tier: {pick['tier']}")
        print(f"Matchup:  O/U={ou} | ML={ml} | {pick['matchup']}")
        print(f"Reason:   {pick['reasoning']}")

        if not pick["is_favorable"]:
            print(f"WARNING:  Unfavorable matchup - consider skipping")

        print(f"{'-'*80}\n")


def main():
    import sys

    # Get date from command line or use today
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')

    # Get picks for stars
    print(f"\nFetching star picks for {target_date}...")
    picks = get_stars_picks(target_date, min_tier="T2-STRONG")

    # Show favorable matchups only
    print(f"\n{'='*80}")
    print("FAVORABLE MATCHUPS ONLY")
    print(f"{'='*80}")
    display_stars_picks(picks, favorable_only=True)

    # Show all stars picks (including unfavorable)
    unfavorable_count = len([p for p in picks if not p["is_favorable"]])
    if unfavorable_count > 0:
        print(f"\n{'='*80}")
        print(f"ALL STARS PICKS (including {unfavorable_count} in unfavorable matchups)")
        print(f"{'='*80}")
        display_stars_picks(picks, favorable_only=False)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total stars tracked: {len(STARS)} (15 superstars, 18 elite, 17 young/volume)")
    print(f"Stars with picks today: {len(set(p['player'] for p in picks))}")
    print(f"Favorable picks: {len([p for p in picks if p['is_favorable']])}")
    print(f"Unfavorable picks: {unfavorable_count}")
    print()
    print("STRATEGY: Focus on favorable matchups only for best results.")
    print("Criteria: O/U>=5.5, ML between -175 and +150, Tier T2-STRONG or better")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
