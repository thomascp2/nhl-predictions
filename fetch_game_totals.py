"""
Fetch and Calculate Game Total O/U
Uses team offensive/defensive stats to estimate game totals
Updates games table with game_ou_total
"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"

def calculate_game_total(away_team, home_team, conn):
    """
    Calculate expected game total based on team stats
    Formula: (Away Goals/Game + Home Goals Against/Game) + (Home Goals/Game + Away Goals Against/Game)
    """
    cursor = conn.cursor()

    # Get away team stats
    cursor.execute("""
        SELECT goals_per_game, goals_against_per_game
        FROM team_stats
        WHERE team = ? AND season = '2025-2026'
    """, (away_team,))
    away_stats = cursor.fetchone()

    # Get home team stats
    cursor.execute("""
        SELECT goals_per_game, goals_against_per_game
        FROM team_stats
        WHERE team = ? AND season = '2025-2026'
    """, (home_team,))
    home_stats = cursor.fetchone()

    # If stats not found, use league average (6.0 total)
    if not away_stats or not home_stats:
        return 6.0

    away_gpg, away_ga = away_stats
    home_gpg, home_ga = home_stats

    # Calculate expected goals for each team
    # Away team expected: (their offense + home defense) / 2
    # Home team expected: (their offense + away defense) / 2
    away_expected = (away_gpg + home_ga) / 2
    home_expected = (home_gpg + away_ga) / 2

    # Add home ice advantage (approx +0.2 goals)
    home_expected += 0.2

    # Total expected goals
    total = away_expected + home_expected

    # Round to nearest 0.5 (standard betting line)
    total = round(total * 2) / 2

    # Clamp between 5.0 and 7.5 (reasonable NHL range)
    total = max(5.0, min(7.5, total))

    return total


def update_game_totals(start_date=None, end_date=None):
    """
    Update game_ou_total for all games

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build query
    query = "SELECT game_id, game_date, away_team, home_team FROM games WHERE 1=1"
    params = []

    if start_date:
        query += " AND game_date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND game_date <= ?"
        params.append(end_date)

    query += " ORDER BY game_date"

    cursor.execute(query, params)
    games = cursor.fetchall()

    print(f"Calculating game totals for {len(games)} games...")
    print()

    updated = 0
    for game_id, game_date, away_team, home_team in games:
        total = calculate_game_total(away_team, home_team, conn)

        cursor.execute("""
            UPDATE games
            SET game_ou_total = ?, updated_at = CURRENT_TIMESTAMP
            WHERE game_id = ?
        """, (total, game_id))

        updated += 1
        if updated % 100 == 0:
            print(f"Updated {updated}/{len(games)} games...")

    conn.commit()

    print()
    print(f"[SUCCESS] Updated {updated} games with O/U totals")
    print()

    # Show sample
    cursor.execute("""
        SELECT game_date, away_team, home_team, game_ou_total
        FROM games
        WHERE game_ou_total IS NOT NULL
        ORDER BY game_date DESC
        LIMIT 10
    """)

    print("Sample games with O/U:")
    print("-" * 80)
    for game_date, away, home, total in cursor.fetchall():
        print(f"{game_date}: {away} @ {home} - O/U {total}")

    conn.close()

    return updated


def update_todays_games():
    """Quick update for today's games only"""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Updating O/U for games on {today}")
    return update_game_totals(start_date=today, end_date=today)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "today":
        update_todays_games()
    else:
        # Update all games
        update_game_totals()
