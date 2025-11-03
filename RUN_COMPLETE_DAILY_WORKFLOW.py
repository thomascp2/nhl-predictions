"""
COMPLETE DAILY WORKFLOW
=======================

ONE COMMAND to run BOTH strategies:
  1. Stars-Only (simple, 3-8 high-quality picks)
  2. Market vs Model (find +EV edges)

Then shows you:
  - Picks from Stars filter
  - Picks from Market vs Model
  - Picks that appear in BOTH (highest confidence!)

Usage:
    python RUN_COMPLETE_DAILY_WORKFLOW.py
"""

import subprocess
import sys
import os
from datetime import datetime
from smart_date_picker import get_smart_prediction_date


class TeeOutput:
    """Write to both console and file simultaneously"""
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log = open(file_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


class TeeError:
    """Write stderr to both console and file simultaneously"""
    def __init__(self, file_path):
        self.terminal = sys.stderr
        self.log = open(file_path, 'a', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def run_command(description, command):
    """Run a command and track success"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}\n")

    result = subprocess.run(command, capture_output=False)

    if result.returncode != 0:
        print(f"\n[WARN] {description} had issues, but continuing...\n")
        return False
    return True


def push_log_to_github(log_file):
    """Push the log file to GitHub"""
    try:
        print("\n" + "="*80)
        print("PUSHING LOG TO GITHUB")
        print("="*80 + "\n")

        # Add the log file
        subprocess.run(["git", "add", log_file], check=True)

        # Commit with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %I:%M %p')
        commit_msg = f"Workflow log - {timestamp}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        # Push to GitHub
        subprocess.run(["git", "push"], check=True)

        print(f"[OK] Log pushed to GitHub: {log_file}\n")
        print("="*80 + "\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Failed to push log to GitHub: {e}\n")
        return False


def main():
    # Create timestamped log file
    timestamp = datetime.now().strftime('%Y%m%d_%I%M%p')
    log_file = f"WORKFLOW_LOG_{timestamp}.txt"

    # Redirect stdout and stderr to log file (and still show on console)
    tee_out = TeeOutput(log_file)
    tee_err = TeeError(log_file)
    sys.stdout = tee_out
    sys.stderr = tee_err

    try:
        print("\n" + "="*80)
        print("COMPLETE DAILY NHL BETTING WORKFLOW")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print(f"Log File: {log_file}")
        print("="*80)
        print()
        print("This workflow runs BOTH strategies:")
        print("  [1] Strategy 1: Stars-Only Filter (simplified)")
        print("  [2] Strategy 2: Market vs Model (find +EV edges)")
        print()
        print("="*80)

        # Use smart date picker to ensure all components use the same target date
        target_date = get_smart_prediction_date(cutoff_hour=19, verbose=True)
        print(f"\nTarget date: {target_date}")
        print("="*80)

        # STEP 1: Generate predictions (ONE TIME for both strategies)
        print("\n" + "="*80)
        print("STEP 1/5: GENERATING PREDICTIONS")
        print("="*80)
        print("Running all 3 prediction models (Statistical, Ensemble, Goalie)...")
        print()

        run_command(
            "Generate Predictions",
            [sys.executable, "RUN_DAILY_PICKS.py", target_date]
        )

        # STEP 2: Fetch PrizePicks lines (for Market vs Model)
        print("\n" + "="*80)
        print("STEP 2/5: FETCHING PRIZEPICKS LINES")
        print("="*80)
        print("Getting current market lines from PrizePicks...")
        print()

        run_command(
            "Fetch PrizePicks Lines",
            [sys.executable, "fetch_prizepicks_current_lines.py", target_date]
        )

        # STEP 3: Run Stars Filter
        print("\n" + "="*80)
        print("STEP 3/5: STRATEGY 1 - STARS FILTER")
        print("="*80)
        print("Filtering to 50 stars in favorable matchups...")
        print()

        run_command(
            "Stars Filter",
            [sys.executable, "stars_only_filter.py", target_date]
        )

        # STEP 4: Run Market vs Model
        print("\n" + "="*80)
        print("STEP 4/5: STRATEGY 2 - MARKET VS MODEL")
        print("="*80)
        print("Finding edges (where your model beats the market)...")
        print()

        run_command(
            "Market vs Model",
            [sys.executable, "market_vs_model.py", target_date]
        )

        # STEP 5: Export comprehensive analysis to CSV
        print("\n" + "="*80)
        print("STEP 5/5: EXPORTING COMPREHENSIVE ANALYSIS")
        print("="*80)
        print("Creating complete CSV with all data...")
        print()

        run_command(
            "Export Complete Analysis",
            [sys.executable, "export_complete_analysis.py", target_date]
        )

        # SUMMARY
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE!")
        print("="*80)
        print()
        print("WHAT YOU HAVE NOW:")
        print()
        print("  1. STARS PICKS (Strategy 1):")
        print("     - 50 elite players only")
        print("     - Favorable matchups only (O/U >=5.5, ML -175 to +150)")
        print("     - High confidence (T2-STRONG or better)")
        print("     - Result: ~3-8 picks")
        print()
        print("  2. EDGE PICKS (Strategy 2):")
        print("     - Where YOUR model beats the MARKET")
        print("     - Positive expected value (+EV)")
        print("     - Edge >=5% over market")
        print("     - Result: ~0-10 picks")
        print()
        print("="*80)
        print("BETTING STRATEGY:")
        print("="*80)
        print()
        print("  TIER 1: Picks in BOTH lists (highest confidence)")
        print("    -> Bet these with standard stakes")
        print()
        print("  TIER 2: Edge picks >=10% (strong +EV)")
        print("    -> Bet these even if not in stars list")
        print()
        print("  TIER 3: Stars picks with favorable matchups")
        print("    -> Bet these if no edge data available")
        print()
        print("  SKIP: Edge picks <5% or stars picks in unfavorable matchups")
        print()
        print("="*80)
        print("FILES CREATED:")
        print("="*80)
        print()
        print("  - LATEST_PICKS.txt (T1-ELITE picks only)")
        print("  - LATEST_PICKS.csv (T1-ELITE picks only)")
        print(f"  - PICKS_{datetime.now().strftime('%Y-%m-%d_%I-%M%p')}.txt")
        print(f"  - COMPLETE_ANALYSIS_{datetime.now().strftime('%Y%m%d_%I%M%p')}.csv (ALL STARS + EDGES + MATCHUPS)")
        print(f"  - {log_file} (Complete workflow log)")
        print()
        print("="*80)
        print("NEXT STEPS:")
        print("="*80)
        print()
        print("  1. Open COMPLETE_ANALYSIS CSV - contains ALL data:")
        print("     - All stars picks (all tiers)")
        print("     - Market edges (even the bad ones)")
        print("     - Matchup data (O/U, ML, favorable/unfavorable)")
        print("     - PrizePicks available lines")
        print("     - Recommendations (BET/CONSIDER/SKIP)")
        print()
        print("  2. Filter CSV by 'Recommendation' column:")
        print("     - BET - HIGHEST CONFIDENCE = Bet these first")
        print("     - BET - HUGE EDGE = Bet these (>=20% edge)")
        print("     - BET - STRONG EDGE = Bet these (>=10% edge)")
        print()
        print("  3. Cross-check with PrizePicks for current lines")
        print()
        print("  4. Track results to validate edges")
        print()
        print("="*80)
        print(f"Finished: {datetime.now().strftime('%I:%M %p')}")
        print("="*80)
        print()

        return 0

    finally:
        # Restore stdout/stderr
        sys.stdout = tee_out.terminal
        sys.stderr = tee_err.terminal

        # Close log files
        tee_out.close()
        tee_err.close()

        # Push log to GitHub
        push_log_to_github(log_file)


if __name__ == "__main__":
    sys.exit(main())
