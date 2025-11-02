"""
Smart Date Picker for NHL Predictions
Intelligently selects target date based on game start times

Usage:
    python smart_date_picker.py [--cutoff HOUR]

Returns:
    Date string in YYYY-MM-DD format for prediction generation

Logic:
    - Fetch today's NHL schedule from API
    - If any game has already started (after cutoff time), return tomorrow's date
    - Otherwise, return today's date
    - Default cutoff: 7 PM local time
"""

import requests
from datetime import datetime, timedelta
import argparse
import sys


def get_local_time():
    """Get current local time"""
    return datetime.now()


def fetch_nhl_schedule(date_str):
    """
    Fetch NHL schedule for a specific date

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        List of game dictionaries or None if error
    """
    try:
        url = f'https://api-web.nhle.com/v1/schedule/{date_str}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract games from API response
        games = []
        for game_week in data.get('gameWeek', []):
            games.extend(game_week.get('games', []))

        return games

    except Exception as e:
        print(f"Warning: Could not fetch NHL schedule: {e}", file=sys.stderr)
        return None


def parse_game_time(game_time_str):
    """
    Parse game time from NHL API format

    Args:
        game_time_str: ISO 8601 format string (e.g., "2025-11-02T00:00:00Z")

    Returns:
        datetime object or None
    """
    try:
        # Parse ISO format (UTC)
        return datetime.strptime(game_time_str, '%Y-%m-%dT%H:%M:%SZ')
    except:
        return None


def have_games_started(games, cutoff_hour=19):
    """
    Check if any games have already started

    Args:
        games: List of game dictionaries from NHL API
        cutoff_hour: Hour of day (24-hour format) to use as cutoff

    Returns:
        Boolean - True if any game has started or will start within 1 hour
    """
    now = datetime.now()
    current_hour = now.hour

    # Simple check: if it's past the cutoff hour, games have likely started
    if current_hour >= cutoff_hour:
        return True

    # Additional check: look at actual game times if available
    if not games:
        return False

    for game in games:
        game_time_str = game.get('startTimeUTC')
        if not game_time_str:
            continue

        game_time_utc = parse_game_time(game_time_str)
        if not game_time_utc:
            continue

        # Convert to local time (approximate - assume UTC-6 for Central)
        # For more accuracy, you could use pytz library
        game_time_local = game_time_utc - timedelta(hours=6)

        # If game starts within the next hour, consider it "started"
        time_until_game = (game_time_local - now).total_seconds() / 60  # minutes
        if time_until_game <= 60:
            return True

    return False


def get_smart_prediction_date(cutoff_hour=19, verbose=False):
    """
    Intelligently determine which date to generate predictions for

    Args:
        cutoff_hour: Hour of day (24-hour format) to use as cutoff
        verbose: Print decision logic

    Returns:
        Date string in YYYY-MM-DD format
    """
    now = get_local_time()
    today_str = now.strftime('%Y-%m-%d')
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')

    if verbose:
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Cutoff hour: {cutoff_hour}:00")

    # Fetch today's schedule
    today_games = fetch_nhl_schedule(today_str)

    if today_games is None:
        # Could not fetch schedule - use time-based heuristic
        if verbose:
            print("Could not fetch NHL schedule, using time-based heuristic")

        if now.hour >= cutoff_hour:
            if verbose:
                print(f"After cutoff time ({cutoff_hour}:00) - predicting for tomorrow")
            return tomorrow_str
        else:
            if verbose:
                print(f"Before cutoff time ({cutoff_hour}:00) - predicting for today")
            return today_str

    # Check if games have started
    games_started = have_games_started(today_games, cutoff_hour)

    if games_started:
        if verbose:
            print(f"Games have started or will start soon - predicting for tomorrow")
            print(f"Target date: {tomorrow_str}")
        return tomorrow_str
    else:
        if verbose:
            print(f"Games have not started yet - predicting for today")
            print(f"Target date: {today_str}")
        return today_str


def main():
    parser = argparse.ArgumentParser(
        description='Smart date picker for NHL predictions'
    )
    parser.add_argument(
        '--cutoff',
        type=int,
        default=19,
        help='Cutoff hour in 24-hour format (default: 19 = 7 PM)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print decision logic'
    )

    args = parser.parse_args()

    target_date = get_smart_prediction_date(
        cutoff_hour=args.cutoff,
        verbose=args.verbose
    )

    # Print just the date (for easy parsing by other scripts)
    print(target_date)


if __name__ == '__main__':
    main()
