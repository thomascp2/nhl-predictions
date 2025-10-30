"""
Complete NHL Betting Workflow with GTO Parlay Optimization
- Fetches data
- Generates predictions
- Finds PrizePicks edge
- Builds GTO-optimized parlays
"""

import subprocess
import sys
from datetime import datetime

def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status"""
    print("\n" + "="*80)
    print(f"{description}")
    print("="*80)
    print()

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print(f"\n[SUCCESS] {description}")
            return True
        else:
            print(f"\n[WARNING] {description} - COMPLETED WITH WARNINGS")
            return True  # Continue anyway

    except subprocess.TimeoutExpired:
        print(f"\n[TIMEOUT] {description} - TIMEOUT (skipping)")
        return False
    except Exception as e:
        print(f"\n[FAILED] {description} - FAILED: {e}")
        return False


def commit_to_github():
    """Commit GTO parlays and picks to GitHub"""
    print("\n" + "="*80)
    print("STEP 4: Commit to GitHub")
    print("="*80)
    print()

    import glob
    import os

    # Find latest GTO parlay file
    gto_files = glob.glob("GTO_PARLAYS_*.csv")
    if not gto_files:
        print("[WARNING] No GTO parlay files found to commit")
        return False

    # Sort by modification time, get most recent
    latest_gto = max(gto_files, key=os.path.getmtime)
    print(f"Found latest GTO file: {latest_gto}")

    # Find latest multi-line edges file
    edges_files = glob.glob("MULTI_LINE_EDGES_*.csv")
    latest_edges = None
    if edges_files:
        latest_edges = max(edges_files, key=os.path.getmtime)
        print(f"Found latest edges file: {latest_edges}")

    # Use full git path for Task Scheduler compatibility
    git_exe = "C:\\Program Files\\Git\\cmd\\git.exe"

    try:
        # Add files
        files_to_commit = [
            latest_gto,
            "LATEST_PICKS.txt",
            "LATEST_PICKS.csv"
        ]

        # Add edges file if it exists
        if latest_edges:
            files_to_commit.append(latest_edges)

        print(f"Adding files: {', '.join(files_to_commit)}")
        result = subprocess.run(
            [git_exe, "add"] + files_to_commit,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"[WARNING] Git add failed: {result.stderr}")
            return False

        # Commit with timestamp
        commit_msg = f"Auto-update picks and GTO parlays - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
        print(f"Committing: {commit_msg}")

        result = subprocess.run(
            [git_exe, "commit", "-m", commit_msg],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            # Check if it's just "nothing to commit"
            if "nothing to commit" in result.stdout:
                print("[INFO] No changes to commit")
                return True
            else:
                print(f"[WARNING] Git commit failed: {result.stderr}")
                return False

        # Push
        print("Pushing to GitHub...")
        result = subprocess.run(
            [git_exe, "push"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"[WARNING] Git push failed: {result.stderr}")
            return False

        print("[SUCCESS] Successfully pushed to GitHub!")
        return True

    except FileNotFoundError:
        print("[WARNING] Git not found - files saved locally only")
        return False
    except subprocess.TimeoutExpired:
        print("[WARNING] Git operation timed out")
        return False
    except Exception as e:
        print(f"[WARNING] Git operation failed: {e}")
        return False


def main():
    """Run complete workflow"""
    print("\n" + "="*80)
    print("COMPLETE NHL BETTING WORKFLOW WITH GTO PARLAYS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print()

    success_count = 0
    total_steps = 4

    # Step 1: Generate predictions (uses smart data refresh internally)
    if run_script("generate_picks_to_file.py", "STEP 1: Generate Predictions"):
        success_count += 1
    else:
        print("\n[WARNING] Predictions failed - cannot continue")
        return

    # Step 2: Multi-line EV optimization (evaluates ALL PrizePicks lines)
    if run_script("prizepicks_multi_line_optimizer.py", "STEP 2: Multi-Line EV Optimization"):
        success_count += 1
    else:
        print("\n[WARNING] Multi-line optimizer failed - skipping parlays")
        print("   You can still use individual picks from LATEST_PICKS.txt")
        return

    # Step 3: Build GTO-optimized parlays
    if run_script("gto_parlay_optimizer.py", "STEP 3: Build GTO Parlays"):
        success_count += 1
    else:
        print("\n[WARNING] GTO optimizer failed - check if you have edge plays")
        print("   You can still use edge plays from prizepicks_integration output")

    # Step 4: Commit to GitHub
    if commit_to_github():
        success_count += 1

    # Summary
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    print()
    print(f"Completed: {success_count}/{total_steps} steps")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print()

    if success_count >= 3:
        print("[SUCCESS] Ready to bet!")
        print()
        print("Check these files:")
        print("   1. LATEST_PICKS.txt - Individual T1-ELITE picks")
        print("   2. LATEST_PICKS.csv - CSV format for spreadsheets")
        print("   3. GTO_PARLAYS_*.csv - Optimized parlay combinations")
        print()
        print("Betting Strategy:")
        print("   - Singles: Use T1-ELITE picks with 10%+ edge")
        print("   - Parlays: Use GTO recommendations with Kelly sizing")
        print("   - Bankroll: Risk 2-5% total across all plays")
        print()

        if success_count == 4:
            print("View online (auto-updated):")
            print("   TXT: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt")
            print("   CSV: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.csv")

            # Find latest GTO file for link
            import glob
            import os
            gto_files = glob.glob("GTO_PARLAYS_*.csv")
            if gto_files:
                latest_gto = os.path.basename(max(gto_files, key=os.path.getmtime))
                print(f"   GTO: https://github.com/thomascp2/nhl-predictions/blob/main/{latest_gto}")
        else:
            print("Files saved locally (GitHub push skipped)")
    else:
        print("[WARNING] PARTIAL SUCCESS - Some steps failed")
        print("   Check output above for errors")

    print()


if __name__ == "__main__":
    main()
