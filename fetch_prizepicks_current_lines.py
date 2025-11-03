"""
Fetch Current PrizePicks Lines
===============================

Fetch real-time player prop lines from PrizePicks API.

Returns lines in format needed for market vs model comparison.
"""

import requests
import sqlite3
from datetime import datetime
from typing import Dict, List

DB_PATH = "database/nhl_predictions.db"


class PrizePicksLinesFetcher:
    """Fetch current lines from PrizePicks API"""

    def __init__(self):
        self.base_url = "https://api.prizepicks.com/projections"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://app.prizepicks.com/',
            'Origin': 'https://app.prizepicks.com'
        }

    def fetch_nhl_lines(self) -> Dict[str, Dict]:
        """
        Fetch current NHL player prop lines from PrizePicks

        Returns:
            Dict of {player_name: {prop_type: {line, stat_type}}}

        Example:
            {
                "Connor McDavid": {
                    "points": {"line": 0.5, "stat_type": "Points"},
                    "shots": {"line": 2.5, "stat_type": "Shots On Goal"}
                }
            }
        """
        params = {
            'league_id': 8,  # NHL = 8
            'per_page': 250,
            'single_stat': 'true'
        }

        try:
            print("Fetching current PrizePicks lines...")
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Parse API response
            lines = self._parse_api_response(data)

            print(f"[SUCCESS] Fetched lines for {len(lines)} players")
            return lines

        except Exception as e:
            print(f"[ERROR] Failed to fetch PrizePicks lines: {e}")
            return {}

    def _parse_api_response(self, data: Dict) -> Dict[str, Dict]:
        """Parse PrizePicks API JSON response"""

        # Build player lookup dictionary from 'included' section
        players = {}
        included = data.get('included', [])

        for item in included:
            if item.get('type') == 'new_player':
                player_id = item.get('id')
                attrs = item.get('attributes', {})
                players[player_id] = {
                    'name': attrs.get('name', 'Unknown'),
                    'team': attrs.get('team', 'UNK')
                }

        # Parse projections
        lines_by_player = {}
        projections = data.get('data', [])

        for proj in projections:
            attrs = proj.get('attributes', {})
            relationships = proj.get('relationships', {})

            # Get player info
            player_rel = relationships.get('new_player', {}).get('data', {})
            player_id = player_rel.get('id')

            if player_id not in players:
                continue

            player_info = players[player_id]
            player_name = player_info['name']

            # Get projection details
            stat_type = attrs.get('stat_type', '')
            line_score = attrs.get('line_score')

            if not line_score or not stat_type:
                continue

            # Map PrizePicks stat types to our prop types
            prop_type = self._map_stat_type(stat_type)

            if not prop_type:
                continue

            # Store line (MULTIPLE lines possible per prop!)
            if player_name not in lines_by_player:
                lines_by_player[player_name] = {}

            if prop_type not in lines_by_player[player_name]:
                lines_by_player[player_name][prop_type] = []

            # Add this line to the list
            lines_by_player[player_name][prop_type].append({
                'line': line_score,
                'stat_type': stat_type,
                'team': player_info['team']
            })

        return lines_by_player

    def _map_stat_type(self, stat_type: str) -> str:
        """
        Map PrizePicks stat types to our internal prop types

        PrizePicks stat types:
          - "Points" → points
          - "Shots On Goal" → shots
          - "Goals" → goals
          - "Assists" → assists
          - "Blocked Shots" → blocked_shots
          - etc.
        """
        mapping = {
            'Points': 'points',
            'Shots On Goal': 'shots',
            'Goals': 'goals',
            'Assists': 'assists',
            'Blocked Shots': 'blocked_shots',
            'Hits': 'hits',
            'Power Play Points': 'pp_points',
            'Saves': 'goalie_saves'
        }

        return mapping.get(stat_type, None)

    def save_to_database(self, lines: Dict[str, List[Dict]], game_date: str = None):
        """Save lines to database for historical tracking (supports multiple lines per prop)"""

        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create table if not exists (removed UNIQUE constraint to allow multiple lines)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prizepicks_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                player_name TEXT NOT NULL,
                team TEXT,
                prop_type TEXT NOT NULL,
                line REAL NOT NULL,
                stat_type TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Delete old lines for this date (to avoid duplicates)
        cursor.execute("DELETE FROM prizepicks_lines WHERE date = ?", (game_date,))

        # Insert all lines (multiple per prop now)
        saved = 0
        for player_name, props in lines.items():
            for prop_type, line_list in props.items():
                for line_details in line_list:
                    try:
                        cursor.execute("""
                            INSERT INTO prizepicks_lines
                            (date, player_name, team, prop_type, line, stat_type)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            game_date,
                            player_name,
                            line_details.get('team', 'UNK'),
                            prop_type,
                            line_details['line'],
                            line_details.get('stat_type', '')
                        ))
                        saved += 1
                    except Exception as e:
                        print(f"[WARN] Could not save {player_name} {prop_type} {line_details['line']}: {e}")

        conn.commit()
        conn.close()

        print(f"[SUCCESS] Saved {saved} lines to database")

    def display_lines(self, lines: Dict[str, List[Dict]], limit: int = 20):
        """Display fetched lines in readable format (supports multiple lines per prop)"""

        print(f"\n{'='*80}")
        print(f"PRIZEPICKS CURRENT LINES - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print(f"{'='*80}\n")

        player_count = 0
        for player_name, props in sorted(lines.items()):
            if player_count >= limit:
                print(f"\n... and {len(lines) - limit} more players")
                break

            # Get team from first prop
            team = 'UNK'
            for line_list in props.values():
                if line_list and 'team' in line_list[0]:
                    team = line_list[0]['team']
                    break

            print(f"{player_name} ({team})")

            # Show all lines for each prop
            for prop_type, line_list in props.items():
                if len(line_list) == 1:
                    print(f"  {prop_type:15} - Line: {line_list[0]['line']}")
                else:
                    # Multiple lines for this prop
                    lines_str = ", ".join([str(l['line']) for l in sorted(line_list, key=lambda x: x['line'])])
                    print(f"  {prop_type:15} - Lines: {lines_str}")

            print()
            player_count += 1

        print(f"{'='*80}\n")


def main():
    """Fetch and display current PrizePicks lines"""

    fetcher = PrizePicksLinesFetcher()

    # Fetch lines
    lines = fetcher.fetch_nhl_lines()

    if not lines:
        print("No lines fetched. Check your internet connection or PrizePicks API.")
        return

    # Display lines
    fetcher.display_lines(lines, limit=30)

    # Save to database
    fetcher.save_to_database(lines)

    print(f"Lines saved! Use market_vs_model.py to compare with your predictions.")


if __name__ == "__main__":
    main()
