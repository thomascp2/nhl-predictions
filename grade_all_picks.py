"""
Comprehensive Grading System
Grades predictions, PrizePicks edges, and GTO parlays using NHL API
"""

import sys
import sqlite3
import requests
import json
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"


def fetch_game_results(date):
    """Fetch game results from NHL API"""
    url = f"https://api-web.nhle.com/v1/score/{date}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"[ERROR] NHL API returned status {response.status_code}")
            return []

        data = response.json()

        if 'games' not in data:
            print(f"[WARNING] No games found for {date}")
            return []

        games = data['games']
        print(f"[INFO] Found {len(games)} games for {date}")

        # Check if games are final
        final_games = [g for g in games if g.get('gameState') in ['FINAL', 'OFF']]

        if len(final_games) < len(games):
            print(f"[WARNING] Only {len(final_games)}/{len(games)} games are final")

        return games

    except Exception as e:
        print(f"[ERROR] Failed to fetch games: {e}")
        return []


def fetch_player_stats(game_id):
    """Fetch player stats for a specific game"""
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {}

        data = response.json()

        # Extract player stats
        player_stats = {}

        if 'playerByGameStats' in data:
            stats_data = data['playerByGameStats']

            # Process both teams
            for team_key in ['awayTeam', 'homeTeam']:
                if team_key in stats_data:
                    for position_group in ['forwards', 'defense', 'goalies']:
                        if position_group in stats_data[team_key]:
                            for player in stats_data[team_key][position_group]:
                                name = player.get('name', {}).get('default', '')
                                if name:
                                    player_stats[name] = {
                                        'goals': player.get('goals', 0),
                                        'assists': player.get('assists', 0),
                                        'points': player.get('points', 0),
                                        'shots': player.get('sog', 0),
                                        'blocks': player.get('blockedShots', 0),
                                        'hits': player.get('hits', 0)
                                    }

        return player_stats

    except Exception as e:
        print(f"[ERROR] Failed to fetch player stats for game {game_id}: {e}")
        return {}


def find_player_in_stats(player_name, all_stats):
    """Find player in stats with fuzzy matching"""
    if player_name in all_stats:
        return player_name

    # Try variations
    variations = [
        player_name,
        player_name.replace('.', ''),
        player_name.replace(' Jr.', ''),
        player_name.replace(' III', ''),
        player_name.split()[-1]  # Last name only
    ]

    for var in variations:
        matching = [p for p in all_stats.keys() if var.lower() in p.lower()]
        if matching:
            return matching[0]

    return None


def grade_predictions(date, all_player_stats):
    """Grade all predictions for the date"""
    print()
    print("="*80)
    print(f"GRADING PREDICTIONS - {date}")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get predictions for date that haven't been graded
    query = """
        SELECT id, player_name, team, opponent, prop_type, line, prediction, probability
        FROM predictions
        WHERE game_date = ?
          AND (result IS NULL OR result = '')
    """

    cursor.execute(query, (date,))
    predictions = cursor.fetchall()

    if not predictions:
        print("[INFO] No predictions to grade")
        conn.close()
        return {'graded': 0, 'hits': 0, 'misses': 0}

    print(f"[INFO] Found {len(predictions)} predictions to grade")

    graded = 0
    hits = 0
    misses = 0
    not_found = 0

    for pred_id, player_name, team, opp, prop_type, line, prediction, probability in predictions:

        # Find player in stats
        matched_name = find_player_in_stats(player_name, all_player_stats)

        if not matched_name:
            not_found += 1
            continue

        stats = all_player_stats[matched_name]

        # Get actual value
        prop_map = {
            'shots': 'shots',
            'points': 'points',
            'goals': 'goals',
            'assists': 'assists',
            'blocks': 'blocks',
            'hits': 'hits'
        }

        if prop_type not in prop_map:
            continue

        actual = stats.get(prop_map[prop_type], 0)

        # Determine result
        if prediction == 'OVER':
            result = 'HIT' if actual > line else 'MISS'
        else:
            result = 'HIT' if actual < line else 'MISS'

        # Update database
        update_query = """
            UPDATE predictions
            SET result = ?,
                actual_value = ?,
                graded_at = ?
            WHERE id = ?
        """

        cursor.execute(update_query, (result, actual, datetime.now().isoformat(), pred_id))

        graded += 1
        if result == 'HIT':
            hits += 1
        else:
            misses += 1

    conn.commit()
    conn.close()

    # Summary
    print(f"[RESULTS] Graded: {graded} | Hits: {hits} | Misses: {misses} | Not found: {not_found}")

    if graded > 0:
        hit_rate = (hits / graded) * 100
        print(f"[SUMMARY] Hit Rate: {hit_rate:.1f}%")

    return {'graded': graded, 'hits': hits, 'misses': misses, 'not_found': not_found}


def grade_prizepicks_edges(date, all_player_stats):
    """Grade PrizePicks edge plays"""
    print()
    print("="*80)
    print(f"GRADING PRIZEPICKS EDGES - {date}")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get edges for date that haven't been graded
    query = """
        SELECT id, player_name, team, opponent, prop_type, line, our_probability, edge
        FROM prizepicks_edges
        WHERE date = ?
          AND (result IS NULL OR result = '')
    """

    cursor.execute(query, (date,))
    edges = cursor.fetchall()

    if not edges:
        print("[INFO] No edges to grade")
        conn.close()
        return {'graded': 0, 'hits': 0, 'misses': 0}

    print(f"[INFO] Found {len(edges)} edges to grade")

    graded = 0
    hits = 0
    misses = 0
    not_found = 0

    for edge_id, player_name, team, opp, prop_type, line, probability, edge_pct in edges:

        # Find player in stats
        matched_name = find_player_in_stats(player_name, all_player_stats)

        if not matched_name:
            not_found += 1
            continue

        stats = all_player_stats[matched_name]

        # Get actual value
        prop_map = {
            'shots': 'shots',
            'points': 'points',
            'goals': 'goals',
            'assists': 'assists',
            'blocks': 'blocks',
            'hits': 'hits'
        }

        if prop_type not in prop_map:
            continue

        actual = stats.get(prop_map[prop_type], 0)

        # Determine result (edges are always OVER picks)
        result = 'HIT' if actual > line else 'MISS'

        # Update database
        update_query = """
            UPDATE prizepicks_edges
            SET result = ?,
                actual_value = ?,
                graded_at = ?
            WHERE id = ?
        """

        cursor.execute(update_query, (result, actual, datetime.now().isoformat(), edge_id))

        graded += 1
        if result == 'HIT':
            hits += 1
        else:
            misses += 1

    conn.commit()
    conn.close()

    # Summary
    print(f"[RESULTS] Graded: {graded} | Hits: {hits} | Misses: {misses} | Not found: {not_found}")

    if graded > 0:
        hit_rate = (hits / graded) * 100
        print(f"[SUMMARY] Hit Rate: {hit_rate:.1f}%")

    return {'graded': graded, 'hits': hits, 'misses': misses, 'not_found': not_found}


def grade_gto_parlays(date, all_player_stats):
    """Grade GTO parlays"""
    print()
    print("="*80)
    print(f"GRADING GTO PARLAYS - {date}")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get parlays for date that haven't been graded
    query = """
        SELECT id, parlay_id, picks_json, payout_multiplier, expected_value
        FROM gto_parlays
        WHERE date = ?
          AND (result IS NULL OR result = '')
    """

    cursor.execute(query, (date,))
    parlays = cursor.fetchall()

    if not parlays:
        print("[INFO] No parlays to grade")
        conn.close()
        return {'graded': 0, 'hits': 0, 'misses': 0}

    print(f"[INFO] Found {len(parlays)} parlays to grade")

    graded = 0
    hits = 0
    misses = 0

    for parlay_id_db, parlay_id, picks_json, payout, ev in parlays:

        # Parse picks
        picks = json.loads(picks_json)

        # Grade each leg
        all_legs_hit = True
        legs_not_found = 0

        for pick in picks:
            player_name = pick['player_name']
            prop_type = pick['prop_type']
            line = pick['line']

            # Find player in stats
            matched_name = find_player_in_stats(player_name, all_player_stats)

            if not matched_name:
                legs_not_found += 1
                all_legs_hit = False
                break

            stats = all_player_stats[matched_name]

            # Get actual value
            prop_map = {
                'shots': 'shots',
                'points': 'points',
                'goals': 'goals',
                'assists': 'assists',
                'blocks': 'blocks',
                'hits': 'hits'
            }

            if prop_type not in prop_map:
                all_legs_hit = False
                break

            actual = stats.get(prop_map[prop_type], 0)

            # Check if leg hit (all parlays are OVER picks)
            if actual <= line:
                all_legs_hit = False
                break

        if legs_not_found > 0:
            continue  # Skip if any leg player not found

        # Determine result
        result = 'HIT' if all_legs_hit else 'MISS'
        actual_payout = payout if all_legs_hit else 0

        # Update database
        update_query = """
            UPDATE gto_parlays
            SET result = ?,
                actual_payout = ?,
                graded_at = ?
            WHERE id = ?
        """

        cursor.execute(update_query, (result, actual_payout, datetime.now().isoformat(), parlay_id_db))

        graded += 1
        if result == 'HIT':
            hits += 1
        else:
            misses += 1

    conn.commit()
    conn.close()

    # Summary
    print(f"[RESULTS] Graded: {graded} | Hits: {hits} | Misses: {misses}")

    if graded > 0:
        hit_rate = (hits / graded) * 100
        print(f"[SUMMARY] Hit Rate: {hit_rate:.1f}%")

    return {'graded': graded, 'hits': hits, 'misses': misses}


def grade_all(date):
    """Grade everything for a date"""
    print()
    print("="*80)
    print(f"COMPREHENSIVE GRADING SYSTEM - {date}")
    print("="*80)
    print()

    # Fetch game results
    print("[STEP 1] Fetching game results from NHL API...")
    games = fetch_game_results(date)

    if not games:
        print("[ERROR] No games found or games not final yet")
        return

    # Fetch player stats for all games
    print()
    print("[STEP 2] Fetching player stats...")
    all_player_stats = {}

    for game in games:
        game_id = game.get('id')
        if game_id:
            game_stats = fetch_player_stats(game_id)
            all_player_stats.update(game_stats)

    print(f"[INFO] Loaded stats for {len(all_player_stats)} players")

    # Grade predictions
    print()
    print("[STEP 3] Grading predictions...")
    pred_results = grade_predictions(date, all_player_stats)

    # Grade PrizePicks edges
    print()
    print("[STEP 4] Grading PrizePicks edges...")
    edge_results = grade_prizepicks_edges(date, all_player_stats)

    # Grade GTO parlays
    print()
    print("[STEP 5] Grading GTO parlays...")
    parlay_results = grade_gto_parlays(date, all_player_stats)

    # Final summary
    print()
    print("="*80)
    print("GRADING COMPLETE")
    print("="*80)
    print()
    print(f"PREDICTIONS:")
    print(f"  Graded: {pred_results['graded']}")
    print(f"  Hits: {pred_results['hits']}")
    print(f"  Misses: {pred_results['misses']}")
    if pred_results['graded'] > 0:
        pred_hit_rate = (pred_results['hits'] / pred_results['graded']) * 100
        print(f"  Hit Rate: {pred_hit_rate:.1f}%")
    print()

    print(f"PRIZEPICKS EDGES:")
    print(f"  Graded: {edge_results['graded']}")
    print(f"  Hits: {edge_results['hits']}")
    print(f"  Misses: {edge_results['misses']}")
    if edge_results['graded'] > 0:
        edge_hit_rate = (edge_results['hits'] / edge_results['graded']) * 100
        print(f"  Hit Rate: {edge_hit_rate:.1f}%")
        profit = (edge_results['hits'] * 0.91) - edge_results['misses']
        roi = (profit / edge_results['graded']) * 100
        print(f"  Profit: {profit:+.2f} units")
        print(f"  ROI: {roi:+.1f}%")
    print()

    print(f"GTO PARLAYS:")
    print(f"  Graded: {parlay_results['graded']}")
    print(f"  Hits: {parlay_results['hits']}")
    print(f"  Misses: {parlay_results['misses']}")
    if parlay_results['graded'] > 0:
        parlay_hit_rate = (parlay_results['hits'] / parlay_results['graded']) * 100
        print(f"  Hit Rate: {parlay_hit_rate:.1f}%")

    print()
    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    grade_all(date)
