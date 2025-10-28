"""
Auto-run picks generator every few hours until 6 PM
Run this in the morning and let it go - it will update picks throughout the day
"""

import subprocess
import sys
import time
from datetime import datetime, time as dt_time

def should_continue():
    """Check if we should keep running (before 6 PM)"""
    now = datetime.now().time()
    cutoff = dt_time(18, 0)  # 6:00 PM
    return now < cutoff

def run_picks_generator():
    """Run the picks generator script"""
    print(f"\n{'='*80}")
    print(f"Running picks generator at {datetime.now().strftime('%I:%M %p')}")
    print('='*80)

    result = subprocess.run(
        [sys.executable, "generate_picks_to_file.py"],
        capture_output=False,
        text=True
    )

    if result.returncode == 0:
        print("\nPicks generator completed successfully!")
    else:
        print("\nPicks generator had some issues, but picks may still be available")

def main():
    print("=" * 80)
    print("NHL PICKS - AUTO SCHEDULER")
    print("=" * 80)
    print("This will generate picks every 3 hours until 6:00 PM")
    print("You can close this window anytime to stop")
    print("=" * 80)

    # Run times: 9 AM, 12 PM, 3 PM, 6 PM
    run_times = [
        dt_time(9, 0),   # 9:00 AM
        dt_time(12, 0),  # 12:00 PM
        dt_time(15, 0),  # 3:00 PM
        dt_time(18, 0),  # 6:00 PM
    ]

    print("\nScheduled run times:")
    for t in run_times:
        print(f"  - {t.strftime('%I:%M %p')}")
    print()

    # Run immediately first
    print("Running initial picks generation now...")
    run_picks_generator()

    # Then wait and run at scheduled times
    while should_continue():
        now = datetime.now().time()

        # Find next run time
        next_run = None
        for t in run_times:
            if now < t:
                next_run = t
                break

        if next_run is None:
            print("\n" + "=" * 80)
            print("All scheduled runs complete for today (after 6 PM)")
            print("=" * 80)
            break

        # Calculate wait time
        now_dt = datetime.now()
        next_run_dt = datetime.combine(now_dt.date(), next_run)
        wait_seconds = (next_run_dt - now_dt).total_seconds()

        if wait_seconds > 0:
            wait_minutes = int(wait_seconds / 60)
            print(f"\nNext run at {next_run.strftime('%I:%M %p')} ({wait_minutes} minutes)")
            print("Waiting... (Press Ctrl+C to stop)")

            try:
                time.sleep(wait_seconds)
                run_picks_generator()
            except KeyboardInterrupt:
                print("\n\nStopped by user")
                break
        else:
            # We're past this run time, try next one
            continue

    print("\n" + "=" * 80)
    print("Scheduler finished. Check TODAYS_PICKS.txt for latest picks!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
