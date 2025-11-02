"""
Smart NHL Picks Generator - Auto-Refreshes Data + Outputs to GitHub
- Checks data freshness (only fetches if >2 hours old)
- Handles failures gracefully (uses cached data if API fails)
- Always generates predictions (never fails completely)
- Auto-pushes to GitHub for remote access
- Supports custom date for next-day predictions
"""

import sqlite3
import subprocess
import sys
import argparse
from datetime import datetime
from smart_data_refresh import smart_refresh

DB_PATH = "database/nhl_predictions.db"

def generate_predictions(target_date):
    """Run all prediction models for the target date"""
    print(f"Generating predictions for {target_date}...")
    print("NOTE: Prediction models currently use today's date (future: will support custom dates)")

    success_count = 0

    # Run statistical model (currently uses today's date internally)
    print("Running statistical model...")
    result1 = subprocess.run(
        [sys.executable, "fresh_clean_predictions.py"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result1.returncode == 0:
        success_count += 1

    # Run ensemble model (currently uses today's date internally)
    print("Running ensemble model...")
    result2 = subprocess.run(
        [sys.executable, "ensemble_predictions.py"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result2.returncode == 0:
        success_count += 1

    # Run Goalie Saves predictions (already supports date argument)
    print("Generating Goalie Saves predictions...")
    try:
        result3 = subprocess.run(
            [sys.executable, "goalie_saves_predictions.py", target_date],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result3.returncode == 0:
            success_count += 1
            print("[OK] Goalie Saves predictions generated!")
        else:
            print("[WARN] Goalie Saves predictions skipped (may not have data)")
    except Exception as e:
        print(f"[WARN] Goalie Saves predictions failed: {e}")

    print(f"Predictions generated! ({success_count}/3 models succeeded)")

    # Return True if at least the core models (statistical + ensemble) worked
    return result1.returncode == 0 and result2.returncode == 0

def get_todays_picks(target_date):
    """Get T1-ELITE picks from database for target date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT
            player_name,
            team,
            opponent,
            prop_type,
            line,
            probability,
            expected_value,
            confidence_tier,
            model_version,
            reasoning
        FROM predictions
        WHERE game_date = ?
        AND confidence_tier = 'T1-ELITE'
        ORDER BY probability DESC
    """

    cursor.execute(query, (target_date,))
    picks = cursor.fetchall()
    conn.close()

    return picks

def format_picks_to_file(picks, filename):
    """Format picks and save to text file"""
    # Get data freshness
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(last_updated) FROM player_stats WHERE season = '2025-2026'")
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            from datetime import datetime as dt
            last_update = dt.fromisoformat(result[0])
            hours_old = (dt.now() - last_update).total_seconds() / 3600
            data_status = f"Data Age: {hours_old:.1f} hours old (Updated: {last_update.strftime('%I:%M %p')})"

            if hours_old < 1:
                freshness = "[VERY FRESH]"
            elif hours_old < 3:
                freshness = "[FRESH]"
            else:
                freshness = "[STALE]"
        else:
            data_status = "Data Age: Unknown"
            freshness = "[UNKNOWN]"
    except:
        data_status = "Data Age: Unknown"
        freshness = "[UNKNOWN]"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NHL PREDICTIONS - T1-ELITE PICKS ONLY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
        f.write(f"{data_status} - {freshness}\n")
        f.write("=" * 80 + "\n\n")

        if not picks:
            f.write("NO T1-ELITE PICKS AVAILABLE FOR TODAY\n")
            f.write("\nTry running again later or check T2-STRONG picks\n")
            return

        f.write(f"TOTAL T1-ELITE PICKS: {len(picks)}\n")
        f.write("Accuracy Target: 73-75%\n\n")
        f.write("-" * 80 + "\n\n")

        for idx, pick in enumerate(picks, 1):
            player, team, opp, prop, line, prob, ev, tier, model, reason = pick

            f.write(f"PICK #{idx}\n")
            f.write(f"Player: {player} ({team} vs {opp})\n")
            f.write(f"Prop: {prop} - Line: {line}\n")
            f.write(f"Probability: {prob*100:.1f}% | EV: {ev:.2f}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Reasoning: {reason}\n")
            f.write("-" * 80 + "\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("BETTING STRATEGY:\n")
        f.write("- Focus on picks with 65%+ probability\n")
        f.write("- Positive EV (Expected Value) is best\n")
        f.write("- T1-ELITE tier = highest confidence\n")
        f.write("=" * 80 + "\n")

def format_picks_to_csv(picks, filename):
    """Format picks and save to CSV file"""
    import csv

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Player', 'Team', 'Opponent', 'Prop Type', 'Line',
            'Probability (%)', 'Expected Value', 'Confidence Tier',
            'Model', 'Reasoning'
        ])

        # Data rows
        for pick in picks:
            player, team, opp, prop, line, prob, ev, tier, model, reason = pick

            writer.writerow([
                player,
                team,
                opp,
                prop.upper(),
                line,
                f"{prob*100:.1f}",
                f"{ev:.2f}",
                tier,
                model if model else "Statistical",
                reason
            ])

    print(f"CSV saved with {len(picks)} picks")


def push_to_github(timestamped_file, timestamped_csv):
    """Auto-commit and push picks to GitHub"""
    print("\nPushing to GitHub...")

    # Use full git path for Task Scheduler (doesn't have PATH)
    git_exe = "C:\\Program Files\\Git\\cmd\\git.exe"

    try:
        # Add files
        subprocess.run([git_exe, "add", timestamped_file, timestamped_csv, "LATEST_PICKS.txt", "LATEST_PICKS.csv"], check=True)

        # Commit with timestamp
        commit_msg = f"Auto-update picks - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
        subprocess.run([git_exe, "commit", "-m", commit_msg], check=True)

        # Push
        subprocess.run([git_exe, "push"], check=True)

        print("Successfully pushed to GitHub!")
        return True

    except FileNotFoundError:
        print("Git not found - picks saved locally only")
        print("Files saved: LATEST_PICKS.txt, LATEST_PICKS.csv")
        return False
    except subprocess.CalledProcessError as e:
        print(f"GitHub push failed: {e}")
        print("Picks are still saved locally in the files")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate NHL predictions with smart date selection'
    )
    parser.add_argument(
        '--date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='Target date for predictions (YYYY-MM-DD format, default: today)'
    )
    args = parser.parse_args()

    target_date = args.date

    print("\n")
    print("=" * 80)
    print("SMART NHL PICKS GENERATOR")
    print("=" * 80)
    print(f"Target Date: {target_date}")
    print()

    # Step 1: Smart data refresh (only if stale)
    try:
        success_count, total_count, skipped = smart_refresh()

        if not skipped and success_count == 0:
            print("[WARNING] All data fetches failed, but continuing with cached data")
            print("Predictions may be based on outdated information")
            print()
    except Exception as e:
        print(f"[WARNING] Data refresh had issues: {e}")
        print("Continuing with cached data...")
        print()

    # Step 2: Generate fresh predictions
    print("=" * 80)
    print("GENERATING PREDICTIONS")
    print("=" * 80)
    success = generate_predictions(target_date)

    if not success:
        print("\nWARNING: Some prediction models had issues")
        print("Continuing anyway - some predictions may be available\n")

    # Get T1-ELITE picks
    print("\nFetching T1-ELITE picks from database...")
    picks = get_todays_picks(target_date)

    # Create timestamped filenames
    timestamp = datetime.now().strftime('%Y-%m-%d_%I-%M%p')
    timestamped_file = f"PICKS_{timestamp}.txt"
    timestamped_csv = f"PICKS_{timestamp}.csv"

    # Save to timestamped files
    print(f"Writing picks to {timestamped_file}...")
    format_picks_to_file(picks, timestamped_file)

    print(f"Writing picks to {timestamped_csv}...")
    format_picks_to_csv(picks, timestamped_csv)

    # Also save to LATEST_PICKS.txt and LATEST_PICKS.csv for easy access
    print("Writing picks to LATEST_PICKS.txt...")
    format_picks_to_file(picks, "LATEST_PICKS.txt")

    print("Writing picks to LATEST_PICKS.csv...")
    format_picks_to_csv(picks, "LATEST_PICKS.csv")

    # Push to GitHub
    github_success = push_to_github(timestamped_file, timestamped_csv)

    # Archive old picks (keep directory clean)
    print("\n" + "=" * 80)
    print("ARCHIVING OLD PICKS")
    print("=" * 80)
    try:
        archive_result = subprocess.run(
            [sys.executable, "archive_old_picks.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if archive_result.returncode == 0:
            # Print last few lines of output (summary)
            lines = archive_result.stdout.strip().split('\n')
            for line in lines[-3:]:
                print(line)
        else:
            print("[WARN] Archival had issues, but picks are still saved")
    except Exception as e:
        print(f"[WARN] Could not archive old files: {e}")
        print("Picks are still saved successfully")

    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)

    if picks:
        print(f"\nFound {len(picks)} T1-ELITE picks for today")
    else:
        print("\nNo T1-ELITE picks available - check the file for details")

    if github_success:
        print("\nView picks online at:")
        print("TXT: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt")
        print("CSV: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.csv")
        print(f"\nTimestamped:")
        print(f"TXT: https://github.com/thomascp2/nhl-predictions/blob/main/{timestamped_file}")
        print(f"CSV: https://github.com/thomascp2/nhl-predictions/blob/main/{timestamped_csv}")
    else:
        print("\nPicks saved locally but not pushed to GitHub")

if __name__ == "__main__":
    main()
