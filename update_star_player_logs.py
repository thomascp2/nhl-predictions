"""
Update Game Logs for 50 Stars Only
===================================

Efficiently updates game logs for only the 50 star players.

Benefits:
- Fast: ~30 seconds (vs 10+ minutes for all players)
- Targeted: Only updates players we actually use
- Incremental: Only fetches new games since last update
- Automated: Can run daily or weekly

Usage:
    python update_star_player_logs.py
    python update_star_player_logs.py --force  # Force full refresh
"""

import sqlite3
import requests
from datetime import datetime, timedelta
import sys
from typing import List, Dict

DB_PATH = "database/nhl_predictions.db"


class StarPlayerLogUpdater:
    """Update game logs for 50 stars only"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

        # Import stars list
        from stars_only_filter import STARS
        self.stars = STARS

    def get_player_id(self, player_name: str) -> int:
        """Get NHL API player ID from name"""

        cursor = self.conn.cursor()

        # Try to get from player_stats table
        cursor.execute("""
            SELECT player_id
            FROM player_stats
            WHERE player_name = ?
            LIMIT 1
        """, (player_name,))

        result = cursor.fetchone()
        if result:
            return result[0]

        # If not found, search NHL API
        print(f"  Searching NHL API for: {player_name}")
        try:
            # Search by name
            search_url = f"https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=1&q={player_name.replace(' ', '%20')}"
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data and len(data) > 0:
                player_id = data[0].get('playerId')
                if player_id:
                    print(f"    Found: {player_id}")
                    return player_id

        except Exception as e:
            print(f"    Error searching for {player_name}: {e}")

        return None

    def get_last_game_date(self, player_id: int) -> str:
        """Get date of last game log in database"""

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT MAX(game_date)
            FROM player_game_logs
            WHERE player_id = ?
        """, (player_id,))

        result = cursor.fetchone()
        if result and result[0]:
            return result[0]

        # Default to start of season if no logs
        return "2024-10-01"

    def fetch_game_logs(self, player_id: int, player_name: str, since_date: str) -> List[Dict]:
        """Fetch game logs from NHL API"""

        print(f"  Fetching logs for {player_name} since {since_date}...")

        try:
            # NHL API endpoint for player game logs
            url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/20242025/2"

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            game_logs = data.get('gameLog', [])

            # Filter to games after since_date
            since_datetime = datetime.strptime(since_date, '%Y-%m-%d')

            new_logs = []
            for game in game_logs:
                game_date_str = game.get('gameDate')
                if not game_date_str:
                    continue

                game_date = datetime.strptime(game_date_str, '%Y-%m-%d')

                # Only include games after last update
                if game_date > since_datetime:
                    new_logs.append({
                        'player_id': player_id,
                        'player_name': player_name,
                        'game_id': game.get('gameId'),
                        'game_date': game_date_str,
                        'opponent': game.get('opponentAbbrev'),
                        'is_home': 1 if game.get('homeRoadFlag') == 'H' else 0,
                        'goals': game.get('goals', 0),
                        'assists': game.get('assists', 0),
                        'points': game.get('points', 0),
                        'shots': game.get('shots', 0),
                        'plus_minus': game.get('plusMinus', 0),
                        'pim': game.get('pim', 0),
                        'toi': game.get('toi', '00:00'),
                        'pp_goals': game.get('powerPlayGoals', 0),
                        'pp_points': game.get('powerPlayPoints', 0),
                        'sh_goals': game.get('shorthandedGoals', 0),
                        'game_winning_goals': game.get('gameWinningGoals', 0),
                        'ot_goals': game.get('otGoals', 0)
                    })

            print(f"    Found {len(new_logs)} new games")
            return new_logs

        except Exception as e:
            print(f"    Error fetching logs for {player_name}: {e}")
            return []

    def save_game_logs(self, logs: List[Dict]):
        """Save game logs to database"""

        if not logs:
            return

        cursor = self.conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_game_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                player_name TEXT,
                game_id TEXT,
                game_date TEXT,
                opponent TEXT,
                is_home INTEGER,
                goals INTEGER,
                assists INTEGER,
                points INTEGER,
                shots INTEGER,
                plus_minus INTEGER,
                pim INTEGER,
                toi TEXT,
                pp_goals INTEGER,
                pp_points INTEGER,
                sh_goals INTEGER,
                game_winning_goals INTEGER,
                ot_goals INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_id, game_id)
            )
        """)

        # Insert logs
        inserted = 0
        for log in logs:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO player_game_logs
                    (player_id, player_name, game_id, game_date, opponent, is_home,
                     goals, assists, points, shots, plus_minus, pim, toi,
                     pp_goals, pp_points, sh_goals, game_winning_goals, ot_goals)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log['player_id'], log['player_name'], log['game_id'],
                    log['game_date'], log['opponent'], log['is_home'],
                    log['goals'], log['assists'], log['points'], log['shots'],
                    log['plus_minus'], log['pim'], log['toi'],
                    log['pp_goals'], log['pp_points'], log['sh_goals'],
                    log['game_winning_goals'], log['ot_goals']
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Duplicate, skip
                pass
            except Exception as e:
                print(f"    Error inserting log: {e}")

        self.conn.commit()
        print(f"    Saved {inserted} new game logs")

    def update_all_stars(self, force_full: bool = False):
        """Update game logs for all 50 stars"""

        print(f"\n{'='*80}")
        print(f"UPDATING STAR PLAYER GAME LOGS")
        print(f"{'='*80}\n")
        print(f"Players to update: {len(self.stars)}")
        print(f"Mode: {'FULL REFRESH' if force_full else 'INCREMENTAL UPDATE'}\n")

        total_new_games = 0
        successful = 0
        failed = 0

        for i, player_name in enumerate(self.stars, 1):
            print(f"[{i}/{len(self.stars)}] {player_name}")

            # Get player ID
            player_id = self.get_player_id(player_name)
            if not player_id:
                print(f"    Could not find player ID, skipping")
                failed += 1
                continue

            # Get last game date
            if force_full:
                since_date = "2024-10-01"  # Start of season
            else:
                since_date = self.get_last_game_date(player_id)

            # Fetch new game logs
            logs = self.fetch_game_logs(player_id, player_name, since_date)

            # Save to database
            if logs:
                self.save_game_logs(logs)
                total_new_games += len(logs)
                successful += 1
            else:
                print(f"    No new games to add")
                successful += 1

        print(f"\n{'='*80}")
        print(f"UPDATE COMPLETE")
        print(f"{'='*80}\n")
        print(f"Players processed: {successful + failed}/{len(self.stars)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total new games added: {total_new_games}")
        print(f"\n{'='*80}\n")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Update star player logs"""

    # Check for --force flag
    force_full = '--force' in sys.argv

    updater = StarPlayerLogUpdater()
    updater.update_all_stars(force_full=force_full)
    updater.close()


if __name__ == "__main__":
    main()
