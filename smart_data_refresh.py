"""
Smart Data Refresh - Only fetches if data is stale
Handles failures gracefully, never crashes
"""

import subprocess
import sys
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/nhl_predictions.db"
FRESHNESS_THRESHOLD_HOURS = 2  # Only refresh if data older than 2 hours

def get_data_freshness():
    """Check when data was last updated"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check player_stats
        cursor.execute("SELECT MAX(last_updated) FROM player_stats WHERE season = '2025-2026'")
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            last_update = datetime.fromisoformat(result[0])
            hours_old = (datetime.now() - last_update).total_seconds() / 3600
            return last_update, hours_old
        else:
            return None, 999  # Very old (force refresh)

    except Exception as e:
        print(f"[WARNING] Could not check data freshness: {e}")
        return None, 0  # Assume fresh to avoid errors

def run_fetch_script(script_name, description, retry=2):
    """Run a fetch script with retry logic"""
    for attempt in range(retry):
        try:
            print(f"  Fetching {description}... (attempt {attempt + 1}/{retry})")

            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout per script
            )

            if result.returncode == 0:
                print(f"  [SUCCESS] {description} updated")
                return True
            else:
                print(f"  [WARNING] {description} had issues: {result.stderr[:100]}")
                if attempt < retry - 1:
                    print(f"  Retrying...")

        except subprocess.TimeoutExpired:
            print(f"  [WARNING] {description} timed out")
            if attempt < retry - 1:
                print(f"  Retrying...")
        except Exception as e:
            print(f"  [WARNING] {description} failed: {e}")
            if attempt < retry - 1:
                print(f"  Retrying...")

    print(f"  [FAILED] {description} failed after {retry} attempts - using cached data")
    return False

def smart_refresh():
    """
    Smart data refresh - only fetches if needed
    Returns: (success_count, total_fetches, skipped)
    """
    print("=" * 80)
    print("SMART DATA REFRESH")
    print("=" * 80)

    # Check freshness
    last_update, hours_old = get_data_freshness()

    if last_update:
        print(f"Last data update: {last_update.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"Data age: {hours_old:.1f} hours")
    else:
        print("No data found - will fetch fresh data")

    # Skip if fresh
    if hours_old < FRESHNESS_THRESHOLD_HOURS:
        print(f"\n[FRESH] Data is fresh (less than {FRESHNESS_THRESHOLD_HOURS} hours old)")
        print("Skipping data refresh - using cached data")
        print("=" * 80)
        return 0, 0, True

    print(f"\n[STALE] Data is stale (more than {FRESHNESS_THRESHOLD_HOURS} hours old)")
    print("Fetching fresh data from NHL API...")
    print()

    # Fetch data with retry logic
    success_count = 0

    # Critical fetches (needed for predictions)
    fetches = [
        ("fetch_2025_26_stats.py", "Player Stats (2025-26)"),
        ("fetch_goalie_stats.py", "Goalie Stats"),
    ]

    for script, desc in fetches:
        if run_fetch_script(script, desc):
            success_count += 1

    print()
    print("=" * 80)
    print(f"DATA REFRESH COMPLETE: {success_count}/{len(fetches)} successful")
    print("=" * 80)
    print()

    if success_count == 0:
        print("[WARNING] All data fetches failed - using cached data")
        print("Predictions will be generated but may be outdated")
        print()
    elif success_count < len(fetches):
        print("[WARNING] Some data fetches failed - predictions will use mixed data")
        print("(Some fresh, some cached)")
        print()
    else:
        print("[SUCCESS] All data updated - predictions will use fresh data")
        print()

    return success_count, len(fetches), False

if __name__ == "__main__":
    smart_refresh()
