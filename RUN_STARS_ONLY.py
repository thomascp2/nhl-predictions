"""
ONE-COMMAND STARS WORKFLOW
==========================
Runs full prediction workflow, then filters to stars only

Usage:
    python RUN_STARS_ONLY.py

What it does:
    1. Smart date selection (today or tomorrow)
    2. Data refresh (if needed)
    3. Generate predictions (all 3 models)
    4. Filter to stars in favorable matchups
    5. Display results

This is your one-stop command for simplified betting.
"""

import subprocess
import sys
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("STARS ONLY WORKFLOW - Complete End-to-End")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%I:%M %p')}")
    print()

    # Step 1: Get smart target date
    print("="*80)
    print("STEP 1: Determining target date...")
    print("="*80)

    date_result = subprocess.run(
        [sys.executable, "smart_date_picker.py", "--verbose"],
        capture_output=True,
        text=True
    )

    if date_result.returncode != 0:
        print("[WARN] Could not determine smart date, using today")
        target_date = datetime.now().strftime('%Y-%m-%d')
    else:
        lines = date_result.stdout.strip().split('\n')
        target_date = lines[-1]
        print(f"Target date: {target_date}")

    print()

    # Step 2: Run full prediction workflow
    print("="*80)
    print("STEP 2: Running full prediction workflow...")
    print("="*80)
    print("This will:")
    print("  - Refresh data if needed")
    print("  - Run statistical model")
    print("  - Run ensemble model")
    print("  - Run goalie model")
    print("  - Save to database")
    print()

    workflow_result = subprocess.run(
        [sys.executable, "generate_picks_to_file.py", "--date", target_date],
        capture_output=False,  # Show output in real-time
        text=True
    )

    if workflow_result.returncode != 0:
        print("\n[ERROR] Prediction workflow failed!")
        print("Check output above for errors.")
        return 1

    print()

    # Step 3: Filter to stars only
    print("="*80)
    print("STEP 3: Filtering to stars in favorable matchups...")
    print("="*80)
    print()

    filter_result = subprocess.run(
        [sys.executable, "stars_only_filter.py", target_date],
        capture_output=False,  # Show output in real-time
        text=True
    )

    print()
    print("="*80)
    print("WORKFLOW COMPLETE!")
    print("="*80)
    print()
    print("What just happened:")
    print(f"  1. Generated predictions for {target_date}")
    print(f"  2. Filtered to stars in favorable matchups")
    print(f"  3. Results displayed above")
    print()
    print("Files created:")
    print(f"  - LATEST_PICKS.txt (all picks)")
    print(f"  - LATEST_PICKS.csv (all picks)")
    print(f"  - PICKS_{datetime.now().strftime('%Y-%m-%d_%I-%M%p')}.txt (timestamped)")
    print()
    print("Next steps:")
    print("  - Review stars picks above")
    print("  - Check PrizePicks for actual lines")
    print("  - Place bets on favorable matchups only")
    print()
    print("="*80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
