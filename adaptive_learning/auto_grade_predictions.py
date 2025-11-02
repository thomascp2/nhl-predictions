"""
Automated Prediction Grading via NHL API

This script automatically grades predictions by fetching actual stats from the NHL API.
No manual entry required - fully automated!

Usage:
    python adaptive_learning/auto_grade_predictions.py 2025-10-31

Features:
- Fetches actual player stats from NHL API
- Compares vs predictions
- Records HIT/MISS outcomes
- Handles missing data gracefully
- Can re-grade if needed
"""

import sqlite3
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = "database/nhl_predictions.db"
NHL_API_BASE = "https://api-web.nhle.com/v1"


def fetch_games_for_date(date: str) -> List[Dict]:
    """
    Fetch all NHL games for a specific date

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        List of game dictionaries with scores and player stats
    """
    try:
        # NHL API endpoint for schedule
        url = f"{NHL_API_BASE}/schedule/{date}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        games = []

        if 'gameWeek' not in data:
            print(f"No games found for {date}")
            return []

        # Filter to only games on the specific date
        # NHL API returns the entire week, but we only want this specific date
        for day in data['gameWeek']:
            if day.get('date') == date:
                if 'games' in day:
                    games.extend(day['games'])
                break

        return games

    except Exception as e:
        print(f"Error fetching games: {e}")
        return []


def fetch_game_boxscore(game_id: int) -> Optional[Dict]:
    """
    Fetch detailed boxscore for a specific game

    Args:
        game_id: NHL game ID

    Returns:
        Boxscore dictionary with player stats
    """
    try:
        url = f"{NHL_API_BASE}/gamecenter/{game_id}/boxscore"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        print(f"Error fetching boxscore for game {game_id}: {e}")
        return None


def extract_last_name(full_name: str) -> str:
    """Extract last name from a player name, handling abbreviations"""
    # Remove periods and extra spaces
    cleaned = full_name.replace('.', '').strip()
    # Split and get last word (assumes last name is last word)
    parts = cleaned.split()
    return parts[-1].lower() if parts else ""


def names_match(db_name: str, api_name: str) -> bool:
    """
    Check if two player names match, handling abbreviations

    Args:
        db_name: Full name from database (e.g., "Elias Lindholm")
        api_name: Abbreviated name from API (e.g., "E. Lindholm")

    Returns:
        True if names likely refer to same player
    """
    db_last = extract_last_name(db_name)
    api_last = extract_last_name(api_name)

    # Match if last names are the same
    if db_last and api_last and db_last == api_last:
        return True

    # Fallback: check if one name contains the other
    db_lower = db_name.lower().strip()
    api_lower = api_name.lower().strip()
    return db_lower in api_lower or api_lower in db_lower


def extract_player_stats(boxscore: Dict, player_name: str) -> Optional[Dict]:
    """
    Extract stats for a specific player from boxscore

    Args:
        boxscore: Boxscore data from NHL API
        player_name: Player name to search for

    Returns:
        Dictionary with player stats (points, shots, toi, etc.)
    """
    if not boxscore:
        return None

    # Player stats are in playerByGameStats, not directly in homeTeam/awayTeam
    if 'playerByGameStats' not in boxscore:
        return None

    stats = boxscore['playerByGameStats']

    # Check both home and away teams
    for team_key in ['homeTeam', 'awayTeam']:
        if team_key not in stats:
            continue

        team = stats[team_key]

        # Check forwards
        if 'forwards' in team:
            for player in team['forwards']:
                api_name = player.get('name', {}).get('default', '')
                if names_match(player_name, api_name):
                    return {
                        'name': api_name,
                        'goals': player.get('goals', 0),
                        'assists': player.get('assists', 0),
                        'points': player.get('goals', 0) + player.get('assists', 0),
                        'shots': player.get('sog', 0),
                        'toi': player.get('toi', '0:00'),
                        'position': 'F'
                    }

        # Check defense
        if 'defense' in team:
            for player in team['defense']:
                api_name = player.get('name', {}).get('default', '')
                if names_match(player_name, api_name):
                    return {
                        'name': api_name,
                        'goals': player.get('goals', 0),
                        'assists': player.get('assists', 0),
                        'points': player.get('goals', 0) + player.get('assists', 0),
                        'shots': player.get('sog', 0),
                        'toi': player.get('toi', '0:00'),
                        'position': 'D'
                    }

        # Check goalies
        if 'goalies' in team:
            for goalie in team['goalies']:
                api_name = goalie.get('name', {}).get('default', '')
                if names_match(player_name, api_name):
                    return {
                        'name': api_name,
                        'saves': goalie.get('saves', 0),
                        'goals_against': goalie.get('goalsAgainst', 0),
                        'toi': goalie.get('toi', '0:00'),
                        'position': 'G'
                    }

    return None


def convert_toi_to_minutes(toi_str: str) -> float:
    """
    Convert TOI string (MM:SS) to decimal minutes

    Args:
        toi_str: Time on ice string like "21:34"

    Returns:
        Decimal minutes like 21.57
    """
    try:
        if ':' in toi_str:
            parts = toi_str.split(':')
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes + (seconds / 60.0)
        else:
            return float(toi_str)
    except:
        return 0.0


def get_predictions_to_grade(date: str) -> List[Dict]:
    """
    Fetch predictions for a specific date that need grading

    Args:
        date: Game date (YYYY-MM-DD)

    Returns:
        List of prediction dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT
            p.id,
            p.game_date,
            p.player_name,
            p.team,
            p.opponent,
            p.prop_type,
            p.line,
            p.prediction,
            p.probability,
            p.confidence_tier,
            p.model_version,
            p.is_home
        FROM predictions p
        WHERE p.game_date = ?
        AND p.id NOT IN (
            SELECT prediction_id FROM prediction_outcomes
            WHERE prediction_id IS NOT NULL
        )
        ORDER BY
            p.prop_type,
            p.player_name,
            p.line
    """

    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    conn.close()

    predictions = []
    for row in rows:
        predictions.append({
            'id': row[0],
            'game_date': row[1],
            'player_name': row[2],
            'team': row[3],
            'opponent': row[4],
            'prop_type': row[5],
            'line': row[6],
            'prediction': row[7],
            'probability': row[8],
            'confidence_tier': row[9],
            'model_version': row[10],
            'is_home': row[11]
        })

    return predictions


def save_outcome(prediction: Dict, actual_stat: float, outcome: str):
    """
    Save prediction outcome to database

    Args:
        prediction: Prediction dictionary
        actual_stat: Actual stat value achieved
        outcome: 'HIT' or 'MISS'
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prediction_outcomes (
            prediction_id,
            game_date,
            player_name,
            team,
            opponent,
            prop_type,
            line,
            predicted_direction,
            predicted_probability,
            confidence_tier,
            model_version,
            actual_stat_value,
            outcome,
            was_home,
            graded_at,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prediction['id'],
        prediction['game_date'],
        prediction['player_name'],
        prediction['team'],
        prediction['opponent'],
        prediction['prop_type'],
        prediction['line'],
        prediction['prediction'],
        prediction['probability'],
        prediction['confidence_tier'],
        prediction['model_version'],
        actual_stat,
        outcome,
        prediction.get('is_home', False),
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def grade_prediction(prediction: Dict, player_stats: Dict) -> Optional[Dict]:
    """
    Grade a single prediction against actual stats

    Args:
        prediction: Prediction dictionary
        player_stats: Actual player stats from NHL API

    Returns:
        Grading result dict or None if stat not available
    """
    prop_type = prediction['prop_type'].lower()

    # Map prop types to stat keys
    if prop_type == 'points':
        actual_stat = player_stats.get('points', 0)
    elif prop_type == 'shots':
        actual_stat = player_stats.get('shots', 0)
    elif prop_type == 'goals':
        actual_stat = player_stats.get('goals', 0)
    elif prop_type == 'assists':
        actual_stat = player_stats.get('assists', 0)
    elif prop_type == 'toi':
        toi_str = player_stats.get('toi', '0:00')
        actual_stat = convert_toi_to_minutes(toi_str)
    elif prop_type == 'goalie_saves':
        actual_stat = player_stats.get('saves', 0)
    else:
        print(f"  ⚠️  Unknown prop type: {prop_type}")
        return None

    # Determine outcome
    if prediction['prediction'] == 'OVER':
        hit = actual_stat > prediction['line']
    else:  # UNDER
        hit = actual_stat < prediction['line']

    outcome = 'HIT' if hit else 'MISS'

    return {
        'actual_stat': actual_stat,
        'outcome': outcome,
        'hit': hit
    }


def main():
    print("=" * 80)
    print("AUTOMATED PREDICTION GRADING VIA NHL API")
    print("=" * 80)
    print()

    # Get date
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        # Default to yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        date = yesterday

    print(f"Auto-grading predictions for: {date}\n")

    # Load predictions
    predictions = get_predictions_to_grade(date)

    if not predictions:
        print(f"[OK] All predictions for {date} have been graded (or none exist)!")
        return

    print(f"Found {len(predictions)} predictions to grade\n")
    print("Fetching game data from NHL API...")

    # Fetch games for the date
    games = fetch_games_for_date(date)

    if not games:
        print(f"[ERROR] No games found for {date}")
        print("   Games may not be complete yet, or date format is incorrect")
        return

    print(f"Found {len(games)} games\n")
    print("Fetching boxscores and grading predictions...\n")
    print("=" * 80)

    # Process each game
    game_boxscores = {}
    for game in games:
        game_id = game.get('id')
        if game_id:
            boxscore = fetch_game_boxscore(game_id)
            if boxscore:
                game_boxscores[game_id] = boxscore

    # Grade predictions
    graded_count = 0
    not_found_count = 0
    stat_unavailable_count = 0

    for i, prediction in enumerate(predictions, 1):
        player_name = prediction['player_name']
        prop_type = prediction['prop_type']
        line = prediction['line']

        # Find player stats across all games
        player_stats = None
        for game_id, boxscore in game_boxscores.items():
            player_stats = extract_player_stats(boxscore, player_name)
            if player_stats:
                break

        if not player_stats:
            print(f"[{i}/{len(predictions)}] [WARN] {player_name} - NOT FOUND in any game")
            not_found_count += 1
            continue

        # Check if prediction has a direction (OVER/UNDER)
        if not prediction.get('prediction'):
            print(f"[{i}/{len(predictions)}] [WARN] {player_name} - No prediction direction (NULL)")
            stat_unavailable_count += 1
            continue

        # Grade the prediction
        result = grade_prediction(prediction, player_stats)

        if not result:
            print(f"[{i}/{len(predictions)}] [WARN] {player_name} - Stat unavailable for {prop_type}")
            stat_unavailable_count += 1
            continue

        # Save outcome
        save_outcome(prediction, result['actual_stat'], result['outcome'])

        # Display result
        status = "[HIT]" if result['hit'] else "[MISS]"
        print(f"[{i}/{len(predictions)}] {status} | {player_name} | {prop_type.upper()} {prediction['prediction']} {line}")
        print(f"                  Actual: {result['actual_stat']:.1f} | Predicted: {prediction['probability']*100:.1f}%")

        graded_count += 1

    # Summary
    print()
    print("=" * 80)
    print("GRADING COMPLETE!")
    print("=" * 80)
    print(f"Successfully graded: {graded_count}")
    print(f"Player not found: {not_found_count}")
    print(f"Stat unavailable: {stat_unavailable_count}")
    print(f"Total: {len(predictions)}")
    print()

    if graded_count >= 30:
        print("[OK] You have 30+ graded predictions!")
        print("   Run the learning engine to discover patterns:")
        print("   python adaptive_learning/learning_engine.py")
    else:
        print(f"[INFO] {30 - graded_count} more graded predictions needed before running learning engine")

    print()


if __name__ == "__main__":
    main()
