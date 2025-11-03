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
from datetime import datetime


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


def main():
    print("\n" + "="*80)
    print("🏒 COMPLETE DAILY NHL BETTING WORKFLOW")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print("="*80)
    print()
    print("This workflow runs BOTH strategies:")
    print("  ✅ Strategy 1: Stars-Only Filter (simplified)")
    print("  ✅ Strategy 2: Market vs Model (find +EV edges)")
    print()
    print("="*80)

    target_date = datetime.now().strftime('%Y-%m-%d')

    # STEP 1: Generate predictions (ONE TIME for both strategies)
    print("\n" + "="*80)
    print("STEP 1/4: GENERATING PREDICTIONS")
    print("="*80)
    print("Running all 3 prediction models (Statistical, Ensemble, Goalie)...")
    print()

    run_command(
        "Generate Predictions",
        [sys.executable, "RUN_DAILY_PICKS.py"]
    )

    # STEP 2: Fetch PrizePicks lines (for Market vs Model)
    print("\n" + "="*80)
    print("STEP 2/4: FETCHING PRIZEPICKS LINES")
    print("="*80)
    print("Getting current market lines from PrizePicks...")
    print()

    run_command(
        "Fetch PrizePicks Lines",
        [sys.executable, "fetch_prizepicks_current_lines.py"]
    )

    # STEP 3: Run Stars Filter
    print("\n" + "="*80)
    print("STEP 3/4: STRATEGY 1 - STARS FILTER")
    print("="*80)
    print("Filtering to 50 stars in favorable matchups...")
    print()

    run_command(
        "Stars Filter",
        [sys.executable, "stars_only_filter.py", target_date]
    )

    # STEP 4: Run Market vs Model
    print("\n" + "="*80)
    print("STEP 4/4: STRATEGY 2 - MARKET VS MODEL")
    print("="*80)
    print("Finding edges (where your model beats the market)...")
    print()

    run_command(
        "Market vs Model",
        [sys.executable, "market_vs_model.py", target_date]
    )

    # SUMMARY
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE!")
    print("="*80)
    print()
    print("📊 WHAT YOU HAVE NOW:")
    print()
    print("  1. STARS PICKS (Strategy 1):")
    print("     - 50 elite players only")
    print("     - Favorable matchups only (O/U ≥5.5, ML -175 to +150)")
    print("     - High confidence (T2-STRONG or better)")
    print("     - Result: ~3-8 picks")
    print()
    print("  2. EDGE PICKS (Strategy 2):")
    print("     - Where YOUR model beats the MARKET")
    print("     - Positive expected value (+EV)")
    print("     - Edge ≥5% over market")
    print("     - Result: ~0-10 picks")
    print()
    print("="*80)
    print("🎯 BETTING STRATEGY:")
    print("="*80)
    print()
    print("  TIER 1: Picks in BOTH lists (highest confidence)")
    print("    → Bet these with standard stakes")
    print()
    print("  TIER 2: Edge picks ≥10% (strong +EV)")
    print("    → Bet these even if not in stars list")
    print()
    print("  TIER 3: Stars picks with favorable matchups")
    print("    → Bet these if no edge data available")
    print()
    print("  SKIP: Edge picks <5% or stars picks in unfavorable matchups")
    print()
    print("="*80)
    print("📁 FILES CREATED:")
    print("="*80)
    print()
    print("  - LATEST_PICKS.txt (all predictions)")
    print("  - LATEST_PICKS.csv (all predictions)")
    print(f"  - PICKS_{datetime.now().strftime('%Y-%m-%d_%I-%M%p')}.txt")
    print()
    print("="*80)
    print("📱 NEXT STEPS:")
    print("="*80)
    print()
    print("  1. Review picks from both strategies (see output above)")
    print("  2. Check PrizePicks for actual current lines")
    print("  3. Place bets on:")
    print("     - Picks in BOTH lists (max confidence)")
    print("     - Edge picks ≥10% (strong +EV)")
    print("  4. Track results to validate edges")
    print()
    print("="*80)
    print(f"Finished: {datetime.now().strftime('%I:%M %p')}")
    print("="*80)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
