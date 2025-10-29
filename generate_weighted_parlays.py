"""
Weighted Parlay Generator
Optimizes parlays with 65% shots / 35% points weighting
Shots are more consistent, so we prioritize them for parlays
"""

import sqlite3
from datetime import datetime
from itertools import combinations
import random

DB_PATH = "database/nhl_predictions.db"

# Parlay odds (standard PrizePicks/betting site multipliers)
PARLAY_ODDS = {
    2: 3.0,   # 2-leg parlay = 3x payout
    3: 6.0,   # 3-leg parlay = 6x payout
    4: 10.0,  # 4-leg parlay = 10x payout
    5: 20.0,  # 5-leg parlay = 20x payout
    6: 40.0,  # 6-leg parlay = 40x payout
}


def get_todays_picks(min_prob=0.70):
    """Get today's T1-ELITE picks separated by prop type"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    # Get shots picks
    cursor.execute("""
        SELECT
            player_name, team, opponent, prop_type, line,
            probability, expected_value, reasoning
        FROM predictions
        WHERE game_date = ?
        AND confidence_tier = 'T1-ELITE'
        AND prop_type = 'shots'
        AND probability >= ?
        ORDER BY probability DESC
    """, (today, min_prob))

    shots_picks = [
        {
            'player': row[0],
            'team': row[1],
            'opponent': row[2],
            'prop': f"{row[3].upper()} {row[4]}",
            'probability': row[5],
            'ev': row[6],
            'reasoning': row[7],
            'type': 'shots'
        }
        for row in cursor.fetchall()
    ]

    # Get points picks
    cursor.execute("""
        SELECT
            player_name, team, opponent, prop_type, line,
            probability, expected_value, reasoning
        FROM predictions
        WHERE game_date = ?
        AND confidence_tier = 'T1-ELITE'
        AND prop_type = 'points'
        AND probability >= ?
        ORDER BY probability DESC
    """, (today, min_prob))

    points_picks = [
        {
            'player': row[0],
            'team': row[1],
            'opponent': row[2],
            'prop': f"{row[3].upper()} {row[4]}",
            'probability': row[5],
            'ev': row[6],
            'reasoning': row[7],
            'type': 'points'
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return shots_picks, points_picks


def calculate_parlay_probability(picks):
    """Calculate combined probability of all picks hitting"""
    prob = 1.0
    for pick in picks:
        prob *= pick['probability']
    return prob


def calculate_parlay_ev(picks, parlay_size):
    """Calculate expected value of parlay"""
    combined_prob = calculate_parlay_probability(picks)
    payout_multiplier = PARLAY_ODDS.get(parlay_size, 1.0)

    # EV = (probability of win * payout) - 1
    ev = (combined_prob * payout_multiplier) - 1

    return ev, combined_prob


def generate_weighted_parlays(shots_picks, points_picks, parlay_size=3, num_parlays=10, shots_weight=0.65):
    """
    Generate weighted parlays

    Args:
        shots_picks: List of shots picks
        points_picks: List of points picks
        parlay_size: Number of legs (2-6)
        num_parlays: Number of parlays to generate
        shots_weight: Weight for shots (0.65 = 65% shots, 35% points)
    """

    # Calculate how many of each type
    num_shots = int(parlay_size * shots_weight)
    num_points = parlay_size - num_shots

    # Ensure we have enough picks
    if len(shots_picks) < num_shots or len(points_picks) < num_points:
        print(f"[WARNING] Not enough picks for {parlay_size}-leg parlay")
        print(f"Need {num_shots} shots, {num_points} points")
        print(f"Have {len(shots_picks)} shots, {len(points_picks)} points")
        return []

    parlays = []

    # Generate combinations
    # Take top picks first (already sorted by probability)
    shots_top = shots_picks[:min(20, len(shots_picks))]
    points_top = points_picks[:min(20, len(points_picks))]

    # Generate all possible combinations
    shots_combos = list(combinations(shots_top, num_shots))
    points_combos = list(combinations(points_top, num_points))

    # Sample combinations to avoid explosion
    max_combos = 1000
    if len(shots_combos) > max_combos:
        shots_combos = random.sample(shots_combos, max_combos)
    if len(points_combos) > max_combos:
        points_combos = random.sample(points_combos, max_combos)

    # Combine shots + points
    all_parlays = []
    for shot_combo in shots_combos[:100]:  # Limit to avoid memory issues
        for point_combo in points_combos[:100]:
            picks = list(shot_combo) + list(point_combo)

            # Check for team conflicts (don't parlay players from same team)
            teams = set(p['team'] for p in picks)
            if len(teams) < len(picks):
                continue  # Skip if duplicate teams

            ev, prob = calculate_parlay_ev(picks, parlay_size)

            all_parlays.append({
                'picks': picks,
                'probability': prob,
                'ev': ev,
                'payout_multiplier': PARLAY_ODDS[parlay_size]
            })

    # Sort by EV (best value first)
    all_parlays.sort(key=lambda x: x['ev'], reverse=True)

    return all_parlays[:num_parlays]


def format_parlay_output(parlays, parlay_size):
    """Format parlays for display"""
    output = []

    output.append("=" * 80)
    output.append(f"{parlay_size}-LEG PARLAYS (65% SHOTS / 35% POINTS WEIGHTED)")
    output.append("=" * 80)
    output.append("")

    for idx, parlay in enumerate(parlays, 1):
        picks = parlay['picks']
        prob = parlay['probability']
        ev = parlay['ev']
        payout = parlay['payout_multiplier']

        # Count shots vs points
        num_shots = sum(1 for p in picks if p['type'] == 'shots')
        num_points = len(picks) - num_shots

        output.append(f"PARLAY #{idx}")
        output.append(f"Combined Probability: {prob*100:.1f}% | EV: {ev:+.2f} | Payout: {payout}x")
        output.append(f"Mix: {num_shots} Shots + {num_points} Points")
        output.append("-" * 80)

        for i, pick in enumerate(picks, 1):
            output.append(f"  Leg {i}: {pick['player']} ({pick['team']} vs {pick['opponent']})")
            output.append(f"         {pick['prop']} - {pick['probability']*100:.1f}% prob | {pick['reasoning']}")

        # Show payout example
        bet_amount = 10
        potential_win = bet_amount * payout
        output.append("")
        output.append(f"  ${bet_amount} bet = ${potential_win:.2f} payout if all legs hit")
        output.append("=" * 80)
        output.append("")

    return "\n".join(output)


def main():
    """Generate weighted parlays for today"""

    print()
    print("=" * 80)
    print("WEIGHTED PARLAY GENERATOR")
    print("Strategy: 65% Shots (consistent) / 35% Points (upside)")
    print("=" * 80)
    print()

    # Get picks
    shots_picks, points_picks = get_todays_picks(min_prob=0.70)

    print(f"Available picks:")
    print(f"  Shots: {len(shots_picks)}")
    print(f"  Points: {len(points_picks)}")
    print()

    if len(shots_picks) == 0 or len(points_picks) == 0:
        print("[ERROR] Not enough picks to generate parlays")
        return

    # Generate parlays for different sizes
    all_output = []

    for size in [2, 3, 4, 5]:
        print(f"Generating {size}-leg parlays...")

        parlays = generate_weighted_parlays(
            shots_picks,
            points_picks,
            parlay_size=size,
            num_parlays=5,  # Top 5 for each size
            shots_weight=0.65
        )

        if parlays:
            output = format_parlay_output(parlays, size)
            all_output.append(output)
            print(f"  Generated {len(parlays)} parlays")

    # Save to file
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"PARLAYS_{today}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(all_output))

    print()
    print(f"[SUCCESS] Parlays saved to {filename}")
    print()

    # Also save to LATEST_PARLAYS.txt
    with open("LATEST_PARLAYS.txt", 'w', encoding='utf-8') as f:
        f.write("\n\n".join(all_output))

    print(f"[SUCCESS] Also saved to LATEST_PARLAYS.txt")
    print()

    # Print summary
    print("=" * 80)
    print("PARLAY SUMMARY")
    print("=" * 80)
    print(f"Files created: {filename}, LATEST_PARLAYS.txt")
    print()
    print("Strategy Notes:")
    print("  - Shots picks = 65% of each parlay (more consistent)")
    print("  - Points picks = 35% of each parlay (upside potential)")
    print("  - No duplicate teams in same parlay (reduces correlation risk)")
    print("  - Sorted by Expected Value (best value first)")
    print()


if __name__ == "__main__":
    main()
