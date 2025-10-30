# Automated NHL Picks - Manual Setup Guide

## Problem
Automated task creation is hitting Windows permissions. Follow these manual steps instead.

---

## Option 1: PowerShell (Recommended - Run as Administrator)

**Open PowerShell as Administrator**, then run:

```powershell
$pythonPath = "C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe"
$scriptPath = "C:\Users\thoma\PrizePicks-Research-Lab\run_complete_workflow_gto.py"

# Create triggers
$trigger1 = New-ScheduledTaskTrigger -Daily -At "08:00"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "10:00"
$trigger3 = New-ScheduledTaskTrigger -Daily -At "12:00"
$trigger4 = New-ScheduledTaskTrigger -Daily -At "14:00"
$trigger5 = New-ScheduledTaskTrigger -Daily -At "16:00"
$trigger6 = New-ScheduledTaskTrigger -Daily -At "18:00"
$trigger7 = New-ScheduledTaskTrigger -Daily -At "19:00"

# Create action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory "C:\Users\thoma\PrizePicks-Research-Lab"

# Register tasks
Register-ScheduledTask -TaskName "NHL Picks Auto 08:00" -Trigger $trigger1 -Action $action -Description "Automated NHL picks - 8 AM"
Register-ScheduledTask -TaskName "NHL Picks Auto 10:00" -Trigger $trigger2 -Action $action -Description "Automated NHL picks - 10 AM"
Register-ScheduledTask -TaskName "NHL Picks Auto 12:00" -Trigger $trigger3 -Action $action -Description "Automated NHL picks - 12 PM"
Register-ScheduledTask -TaskName "NHL Picks Auto 14:00" -Trigger $trigger4 -Action $action -Description "Automated NHL picks - 2 PM"
Register-ScheduledTask -TaskName "NHL Picks Auto 16:00" -Trigger $trigger5 -Action $action -Description "Automated NHL picks - 4 PM"
Register-ScheduledTask -TaskName "NHL Picks Auto 18:00" -Trigger $trigger6 -Action $action -Description "Automated NHL picks - 6 PM"
Register-ScheduledTask -TaskName "NHL Picks Auto 19:00" -Trigger $trigger7 -Action $action -Description "Automated NHL picks - 7 PM"

Write-Host "Done! Created 7 scheduled tasks"
```

---

## Option 2: Task Scheduler GUI (Easiest)

1. Press `Win + R`, type `taskschd.msc`, press Enter

2. Click **"Create Basic Task"** in the right panel

3. For each time (8 AM, 10 AM, 12 PM, 2 PM, 4 PM, 6 PM, 7 PM):

   **General Tab**:
   - Name: `NHL Picks Auto 08:00` (change time for each)
   - Description: "Automated NHL picks generation"

   **Triggers Tab**:
   - Click "New..."
   - Begin the task: "On a schedule"
   - Daily, starting today
   - Start time: `8:00 AM` (change for each task)
   - Click "OK"

   **Actions Tab**:
   - Click "New..."
   - Action: "Start a program"
   - Program/script: `C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe`
   - Add arguments: `run_complete_workflow_gto.py`
   - Start in: `C:\Users\thoma\PrizePicks-Research-Lab`
   - Click "OK"

   **Conditions Tab**:
   - Uncheck "Start the task only if the computer is on AC power"
   - Check "Start the task even if the computer is on batteries"

   **Settings Tab**:
   - Check "Run task as soon as possible after a scheduled start is missed"
   - Uncheck "Stop the task if it runs longer than..."

4. Click **"OK"** to save

5. Repeat for all 7 times

---

## Option 3: Copy Existing Task (Fastest)

If you have the old "NHL Picks Daily Auto-Scheduler" task:

1. Open Task Scheduler (`taskschd.msc`)
2. Find "NHL Picks Daily Auto-Scheduler"
3. Right-click → **Export**
4. Save as `nhl_template.xml`
5. Open in Notepad
6. Change the `<StartBoundary>` time
7. Change the `<RegistrationInfo><URI>` and `<Description>`
8. Save as new files (nhl_08.xml, nhl_10.xml, etc.)
9. In Task Scheduler: **Action → Import Task** for each file

---

## Verify Setup

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "NHL Picks Auto*" } | Format-Table TaskName, State, @{Name="NextRun";Expression={(Get-ScheduledTaskInfo -TaskName $_.TaskName).NextRunTime}}
```

Should show 7 tasks with next run times.

---

## Test It Works

```powershell
Start-ScheduledTask -TaskName "NHL Picks Auto 08:00"
```

This will run immediately. Check for:
- New files: `LATEST_PICKS.txt`, `GTO_PARLAYS_*.csv`
- GitHub commit (check GitHub web interface)
- Database updates

---

## What Runs Automatically

Each run executes `run_complete_workflow_gto.py` which:

1. **Smart Data Refresh** - Only if >2 hours old
2. **Generate Predictions** - T1-ELITE picks
3. **Find PrizePicks Edge** - 7%+ edge plays
4. **Build GTO Parlays** - Optimized combinations
5. **Save to Database** - predictions, edges, parlays tables
6. **Export CSV Files** - LATEST_PICKS, GTO_PARLAYS
7. **Commit to GitHub** - Auto-push all files

**Takes 3-5 minutes per run**

---

## Your Workflow

### When Tasks Run:
- Check GitHub or local files for new picks
- Review GTO parlay recommendations

### After Placing Bets:
```bash
python log_parlay.py  # For EACH bet (30 seconds)
```

### Next Day:
```bash
python grade_all_picks.py 2025-10-30
```

---

## Troubleshooting

### Tasks Not Running?

**Check if tasks exist**:
```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "NHL Picks Auto*" }
```

**Check last run result**:
```powershell
Get-ScheduledTaskInfo -TaskName "NHL Picks Auto 08:00"
```

**Check task history**:
1. Open Task Scheduler
2. Select task
3. Click "History" tab (enable if needed)

### Tasks Fail?

**Most common issues**:
1. Python path wrong → Verify: `where python`
2. Script path wrong → Verify: `dir C:\Users\thoma\PrizePicks-Research-Lab\run_complete_workflow_gto.py`
3. Git not configured → Test: `git status`
4. Network offline → Check internet connection

**Test manually**:
```bash
cd C:\Users\thoma\PrizePicks-Research-Lab
python run_complete_workflow_gto.py
```

If manual run works but task fails, it's a permissions issue. Run Task Scheduler as Administrator.

---

## Quick Setup (Copy-Paste Commands)

**Delete old tasks + create new ones (PowerShell as Admin)**:
```powershell
# Delete old
Get-ScheduledTask | Where-Object { $_.TaskName -like "NHL Picks Auto*" } | Unregister-ScheduledTask -Confirm:$false

# Create new
$action = New-ScheduledTaskAction -Execute "C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe" -Argument "run_complete_workflow_gto.py" -WorkingDirectory "C:\Users\thoma\PrizePicks-Research-Lab"

Register-ScheduledTask -TaskName "NHL Picks Auto 08:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "08:00")
Register-ScheduledTask -TaskName "NHL Picks Auto 10:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "10:00")
Register-ScheduledTask -TaskName "NHL Picks Auto 12:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "12:00")
Register-ScheduledTask -TaskName "NHL Picks Auto 14:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "14:00")
Register-ScheduledTask -TaskName "NHL Picks Auto 16:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "16:00")
Register-ScheduledTask -TaskName "NHL Picks Auto 18:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "18:00")
Register-ScheduledTask -TaskName "NHL Picks Auto 19:00" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "19:00")
```

---

## Summary

**You need**:
- 7 scheduled tasks running at: 8 AM, 10 AM, 12 PM, 2 PM, 4 PM, 6 PM, 7 PM
- Each runs: `run_complete_workflow_gto.py`
- Result: Fresh picks 7x daily, auto-saved to database, auto-pushed to GitHub

**Files created**:
- `LATEST_PICKS.txt` / `.csv` - Individual T1-ELITE picks
- `GTO_PARLAYS_*.csv` - Optimized parlay combinations
- Database updates (all tables)
- GitHub commits (every 2 hours)

**You do**:
1. Check picks (GitHub or local)
2. Place bets on PrizePicks
3. Log parlays: `python log_parlay.py`
4. Grade results: `python grade_all_picks.py 2025-10-30`

That's it - system handles everything else!
