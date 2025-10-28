"""
Simple NHL Picks Generator - Outputs to Text File + Auto-Push to GitHub
Run this anytime you want fresh picks saved to a file and pushed to cloud
"""

import sqlite3
import subprocess
import sys
from datetime import datetime

DB_PATH = "database/nhl_predictions.db"

def generate_predictions():
    """Run both prediction models"""
    print("Generating predictions...")

    # Run statistical model
    print("Running statistical model...")
    result1 = subprocess.run(
        [sys.executable, "fresh_clean_predictions.py"],
        capture_output=True,
        text=True,
        timeout=120
    )

    # Run ensemble model
    print("Running ensemble model...")
    result2 = subprocess.run(
        [sys.executable, "ensemble_predictions.py"],
        capture_output=True,
        text=True,
        timeout=120
    )

    print("Predictions generated!")
    return result1.returncode == 0 and result2.returncode == 0

def get_todays_picks():
    """Get T1-ELITE picks from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

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

    cursor.execute(query, (today,))
    picks = cursor.fetchall()
    conn.close()

    return picks

def format_picks_to_file(picks, filename):
    """Format picks and save to text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NHL PREDICTIONS - T1-ELITE PICKS ONLY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
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
            f.write(f"Probability: {prob:.1f}% | EV: {ev:.2f}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Reasoning: {reason}\n")
            f.write("-" * 80 + "\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("BETTING STRATEGY:\n")
        f.write("- Focus on picks with 65%+ probability\n")
        f.write("- Positive EV (Expected Value) is best\n")
        f.write("- T1-ELITE tier = highest confidence\n")
        f.write("=" * 80 + "\n")

def push_to_github(timestamped_file):
    """Auto-commit and push picks to GitHub"""
    print("\nPushing to GitHub...")

    try:
        # Add files
        subprocess.run(["git", "add", timestamped_file, "LATEST_PICKS.txt"], check=True)

        # Commit with timestamp
        commit_msg = f"Auto-update picks - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        # Push
        subprocess.run(["git", "push"], check=True)

        print("Successfully pushed to GitHub!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"GitHub push failed: {e}")
        print("Picks are still saved locally in the files")
        return False

def main():
    print("Starting NHL Picks Generator...")
    print("=" * 80)

    # Generate fresh predictions
    success = generate_predictions()

    if not success:
        print("\nWARNING: Some prediction models had issues")
        print("Continuing anyway - some predictions may be available\n")

    # Get T1-ELITE picks
    print("\nFetching T1-ELITE picks from database...")
    picks = get_todays_picks()

    # Create timestamped filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%I-%M%p')
    timestamped_file = f"PICKS_{timestamp}.txt"

    # Save to timestamped file
    print(f"Writing picks to {timestamped_file}...")
    format_picks_to_file(picks, timestamped_file)

    # Also save to LATEST_PICKS.txt for easy access
    print("Writing picks to LATEST_PICKS.txt...")
    format_picks_to_file(picks, "LATEST_PICKS.txt")

    # Push to GitHub
    github_success = push_to_github(timestamped_file)

    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)

    if picks:
        print(f"\nFound {len(picks)} T1-ELITE picks for today")
    else:
        print("\nNo T1-ELITE picks available - check the file for details")

    if github_success:
        print("\nView picks online at:")
        print("https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt")
        print(f"https://github.com/thomascp2/nhl-predictions/blob/main/{timestamped_file}")
    else:
        print("\nPicks saved locally but not pushed to GitHub")

if __name__ == "__main__":
    main()
