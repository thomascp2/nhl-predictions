"""
SIMPLE WRAPPER: Generate Today's Picks (with Smart Date Selection)
====================================================================
This is the main script you'll run every day.

What it does:
  1. Uses smart date picker to determine target date (today or tomorrow)
  2. Checks if data is fresh (auto-refreshes if stale)
  3. Runs all 3 prediction models (Statistical, Ensemble, Goalie)
  4. Generates LATEST_PICKS.txt and LATEST_PICKS.csv
  5. Pushes to GitHub

Output Files:
  - LATEST_PICKS.txt (easy to read on phone)
  - LATEST_PICKS.csv (spreadsheet)
  - PICKS_[timestamp].txt/csv (backup)

Expected: 5-10 T1-ELITE picks, 114 total predictions
Runtime: ~45 seconds
"""

import subprocess
import sys
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("GENERATING NHL PICKS (Smart Date Selection)")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%I:%M %p')}")
    print()

    # Get smart target date
    print("Determining target date...")
    date_result = subprocess.run(
        [sys.executable, "smart_date_picker.py", "--verbose"],
        capture_output=True,
        text=True
    )

    if date_result.returncode != 0:
        print("[WARN] Could not determine smart date, using today")
        target_date = datetime.now().strftime('%Y-%m-%d')
    else:
        # Last line of output is the date
        lines = date_result.stdout.strip().split('\n')
        target_date = lines[-1]
        print(f"Target date: {target_date}")

    print()

    # Run the main picks generator with target date
    result = subprocess.run(
        [sys.executable, "generate_picks_to_file.py", "--date", target_date],
        capture_output=False,
        text=True
    )

    print()
    print("="*80)
    if result.returncode == 0:
        print("[SUCCESS] Picks generated!")
        print()
        print("View picks:")
        print("  - Local: LATEST_PICKS.txt")
        print("  - GitHub: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt")
    else:
        print("[ERROR] Something went wrong - check output above")

    print("="*80)
    print()

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
