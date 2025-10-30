"""
Setup 7 automated scheduled tasks for NHL picks
"""

import subprocess
import sys

PYTHON_PATH = r"C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe"
SCRIPT_PATH = r"C:\Users\thoma\PrizePicks-Research-Lab\run_complete_workflow_gto.py"

TIMES = [
    ("08:00", "8 AM"),
    ("10:00", "10 AM"),
    ("12:00", "12 PM"),
    ("14:00", "2 PM"),
    ("16:00", "4 PM"),
    ("18:00", "6 PM"),
    ("19:00", "7 PM")
]

print("="*80)
print("SETTING UP AUTOMATED NHL PICKS SCHEDULE")
print("="*80)
print()
print("Creating 7 scheduled tasks to run at:")
for time, label in TIMES:
    print(f"  - {label}")
print()

success_count = 0

for time, label in TIMES:
    task_name = f"NHL Picks Auto {time}"

    # Build command
    cmd = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", f'"{PYTHON_PATH}" "{SCRIPT_PATH}"',
        "/sc", "daily",
        "/st", time,
        "/f"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print(f"[SUCCESS] Created: {task_name}")
            success_count += 1
        else:
            print(f"[FAILED] {task_name}")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
    except Exception as e:
        print(f"[ERROR] {task_name}: {e}")

print()
print("="*80)
print("SETUP COMPLETE")
print("="*80)
print()
print(f"Successfully created {success_count}/{len(TIMES)} scheduled tasks")
print()

# Verify tasks
print("Verifying tasks...")
result = subprocess.run(
    ["schtasks", "/query", "/fo", "list", "/v", "/tn", "NHL Picks Auto*"],
    capture_output=True,
    text=True
)

if "NHL Picks Auto" in result.stdout:
    print("[SUCCESS] Tasks created and verified!")
else:
    print("[WARNING] Could not verify tasks - check Task Scheduler manually")

print()
print("="*80)
print("WHAT HAPPENS AUTOMATICALLY")
print("="*80)
print()
print("Every run (7 times per day):")
print("  1. Fetch fresh NHL data (if >2 hours old)")
print("  2. Generate T1-ELITE predictions")
print("  3. Find PrizePicks edge plays (7%+ edge)")
print("  4. Build GTO-optimized parlays")
print("  5. Save everything to database")
print("  6. Export CSV files")
print("  7. Commit to GitHub")
print()
print("YOUR workflow:")
print("  1. Check picks on GitHub or local files")
print("  2. Place bets on PrizePicks")
print("  3. Log each parlay: python log_parlay.py")
print("  4. Next day grade: python grade_all_picks.py 2025-10-30")
print()
print("View picks online:")
print("  https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt")
print("  https://github.com/thomascp2/nhl-predictions/blob/main/GTO_PARLAYS_*.csv")
print()
print("Test manually:")
print("  schtasks /run /tn \"NHL Picks Auto 08:00\"")
print()
