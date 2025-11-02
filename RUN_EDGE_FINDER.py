"""
SIMPLE WRAPPER: Find Edges & Parlays
=====================================
Run this AFTER generating picks to find betting opportunities.

What it does:
  1. Analyzes predictions vs PrizePicks lines
  2. Finds positive EV opportunities
  3. Builds optimized parlays with Kelly bet sizing

Output Files:
  - MULTI_LINE_EDGES_[timestamp].csv
  - GTO_PARLAYS_[timestamp].csv

Expected: 5-20 edges, 10-50 parlays
Runtime: ~50 seconds
"""

import subprocess
import sys
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("FINDING EDGES & PARLAYS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%I:%M %p')}")
    print()

    success_count = 0

    # Step 1: Multi-line edge detection
    print("STEP 1: Finding positive EV edges...")
    print("-"*40)
    result1 = subprocess.run(
        [sys.executable, "prizepicks_multi_line_optimizer.py"],
        capture_output=False,
        text=True
    )
    if result1.returncode == 0:
        success_count += 1
        print("[OK] Edge detection complete")
    else:
        print("[WARNING] Edge detection had issues")

    print()

    # Step 2: GTO parlay optimization
    print("STEP 2: Building GTO parlays...")
    print("-"*40)
    result2 = subprocess.run(
        [sys.executable, "gto_parlay_optimizer.py"],
        capture_output=False,
        text=True
    )
    if result2.returncode == 0:
        success_count += 1
        print("[OK] Parlay optimization complete")
    else:
        print("[WARNING] Parlay optimization had issues")

    print()
    print("="*80)
    if success_count == 2:
        print("[SUCCESS] Edge finder complete!")
        print()
        print("Check files:")
        print("  - MULTI_LINE_EDGES_[timestamp].csv")
        print("  - GTO_PARLAYS_[timestamp].csv")
    else:
        print(f"[PARTIAL SUCCESS] {success_count}/2 steps completed")

    print("="*80)
    print()

    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
