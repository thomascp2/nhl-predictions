# Windows Task Scheduler Setup - FULL AUTOMATION

## The Dream: Zero Manual Work

**What you want:**
- Wake up
- Check GitHub bookmark on phone
- Fresh picks already generated
- Never manually run anything

**We're making it happen!**

---

## Option 1: Automatic Setup (EASIEST - 30 seconds)

### Step 1: Run the Setup Script

Right-click PowerShell and select **"Run as Administrator"**

Then run:

```powershell
cd "C:\Users\thoma\PrizePicks-Research-Lab"
powershell -ExecutionPolicy Bypass -File setup_windows_scheduler.ps1
```

### Step 2: That's It!

The script creates a Windows Task that:
- Runs every day at **8:55 AM**
- Automatically generates picks at 9 AM, 12 PM, 3 PM, 6 PM
- Pushes to GitHub after each run
- Stops automatically at 6 PM
- Closes the window

### Step 3: Test It (Optional)

When the script asks "Want to test it now? (Y/N)", type **Y**

A command window will open and start generating picks immediately!

---

## Option 2: Manual Setup (If PowerShell Script Fails)

### Step 1: Open Task Scheduler

1. Press **Win + R**
2. Type: `taskschd.msc`
3. Press **Enter**

### Step 2: Create New Task

1. Click **"Create Task"** (right side, not "Create Basic Task")
2. Name: `NHL Picks Daily Auto-Scheduler`
3. Description: `Automatically generates NHL predictions throughout the day`
4. Check **"Run whether user is logged on or not"**
5. Check **"Do not store password"** (if available)
6. Check **"Run with highest privileges"** (optional)

### Step 3: Set Trigger

1. Go to **"Triggers"** tab
2. Click **"New"**
3. Begin the task: **On a schedule**
4. Settings: **Daily**
5. Start: **Tomorrow at 8:55 AM**
6. Recur every: **1 days**
7. Click **"OK"**

### Step 4: Set Action

1. Go to **"Actions"** tab
2. Click **"New"**
3. Action: **Start a program**
4. Program/script: `cmd.exe`
5. Add arguments: `/c "C:\Users\thoma\PrizePicks-Research-Lab\run_daily_picks.bat"`
6. Start in: `C:\Users\thoma\PrizePicks-Research-Lab`
7. Click **"OK"**

### Step 5: Configure Settings

1. Go to **"Settings"** tab
2. Check: **"Allow task to be run on demand"**
3. Check: **"Run task as soon as possible after a scheduled start is missed"**
4. Check: **"If the task fails, restart every: 10 minutes"**
5. Set: **"Stop the task if it runs longer than: 10 hours"**
6. Uncheck: **"Stop the task if it runs for: 3 days"** (if shown)
7. Click **"OK"**

### Step 6: Test It

1. Find your task in the list
2. Right-click → **"Run"**
3. A command window should open and start generating picks

---

## What Happens Daily

### Morning (8:55 AM)
- ✅ Windows Task Scheduler starts the script automatically
- ✅ Command window opens
- ✅ Script checks data freshness
- ✅ Fetches fresh data if needed (first run of day)

### Throughout Day
- ✅ **9:00 AM** - First picks generation (with fresh data)
- ✅ **12:00 PM** - Second run (uses 9 AM data if fresh)
- ✅ **3:00 PM** - Third run (checks if data >2 hours old, refetches if needed)
- ✅ **6:00 PM** - Final run (last update before games)

### After Each Run
- ✅ Saves picks to files
- ✅ Pushes to GitHub
- ✅ Updates `LATEST_PICKS.txt`
- ✅ Creates timestamped file

### Evening (After 6 PM)
- ✅ Script stops automatically
- ✅ Window closes after 30 seconds
- ✅ Task completes successfully

---

## Your New Workflow

### Before (Manual)
1. Wake up
2. Remember to run script
3. Open terminal
4. Type command
5. Wait for picks
6. Check picks

### After (Automatic)
1. Wake up
2. Open GitHub bookmark on phone
3. Read picks
4. Place bets
5. Win!

**That's it!** No manual work at all.

---

## Monitoring Your Automated Task

### Check if Task is Running

**Option 1: Task Scheduler**
1. Open Task Scheduler (`Win + R` → `taskschd.msc`)
2. Find "NHL Picks Daily Auto-Scheduler"
3. Check "Status" column (should say "Ready" or "Running")
4. Check "Last Run Result" (should be "0x0" = success)

**Option 2: Look for the Window**
- Every morning at 8:55 AM, a command window opens
- You'll see picks generation progress
- Minimize it and forget about it

**Option 3: Check GitHub**
- Open: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
- Look at "Generated:" timestamp
- Should update at 9 AM, 12 PM, 3 PM, 6 PM daily

---

## Troubleshooting

### Task Not Running?

**Check 1: Is task enabled?**
```powershell
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" | Select-Object State
```
Should show: `Ready`

If disabled:
```powershell
Enable-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
```

**Check 2: View last run result**
```powershell
Get-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" | Get-ScheduledTaskInfo
```

**Check 3: Test run manually**
```powershell
Start-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
```

### Window Opens Then Closes Immediately?

**Problem:** Python not in PATH or batch file path wrong

**Fix:**
1. Open `run_daily_picks.bat` in Notepad
2. Change line 10 to full Python path:
   ```batch
   "C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe" run_picks_throughout_day.py
   ```

### Task Runs But No Picks Generated?

**Check GitHub:** If files aren't updating, the script might be failing

**Debug:**
1. Manually run the batch file:
   ```bash
   cd C:\Users\thoma\PrizePicks-Research-Lab
   run_daily_picks.bat
   ```
2. Watch for errors
3. Check if picks files are created locally

### Computer Was Asleep at 8:55 AM?

**No problem!** Task is configured to "Run task as soon as possible after a scheduled start is missed"

When you wake your computer, the task will run automatically.

---

## Advanced: Modify Schedule

### Change Run Time

Don't want 8:55 AM? Change it:

```powershell
# Example: Change to 7:30 AM
$trigger = New-ScheduledTaskTrigger -Daily -At "7:30AM"
Set-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" -Trigger $trigger
```

### Run Only on Specific Days

Only want picks on weekdays?

1. Open Task Scheduler
2. Find your task → Properties
3. Triggers tab → Edit
4. Check "Weekly" instead of "Daily"
5. Select: Mon, Tue, Wed, Thu, Fri, Sat
6. OK

### Disable Auto-Run Temporarily

Going on vacation?

```powershell
Disable-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
```

Re-enable when back:

```powershell
Enable-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler"
```

---

## Completely Remove Auto-Run

Changed your mind? Remove the task:

```powershell
Unregister-ScheduledTask -TaskName "NHL Picks Daily Auto-Scheduler" -Confirm:$false
```

---

## File Summary

| File | Purpose |
|------|---------|
| `run_daily_picks.bat` | Batch file that Task Scheduler runs |
| `setup_windows_scheduler.ps1` | Automatic setup script (run once) |
| `run_picks_throughout_day.py` | The actual picks generator |

---

## What Gets Automated

✅ **Data Fetching** - Fresh NHL stats every morning
✅ **Predictions** - Generated 4x per day (9 AM, 12 PM, 3 PM, 6 PM)
✅ **GitHub Push** - Automatic after each run
✅ **File Updates** - LATEST_PICKS.txt + timestamped files
✅ **Cleanup** - Window closes automatically

❌ **Placing Bets** - You still need to do this (obviously!)
❌ **Checking Picks** - You need to open GitHub bookmark

---

## System Architecture (Fully Automated)

```
┌─────────────────────────────────────────────────┐
│  Windows Task Scheduler                         │
│  Trigger: Daily at 8:55 AM                      │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  run_daily_picks.bat                            │
│  - Opens command window                         │
│  - Changes to project directory                 │
│  - Runs Python script                           │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  run_picks_throughout_day.py                    │
│  - Runs at 9 AM, 12 PM, 3 PM, 6 PM             │
│  - Calls generate_picks_to_file.py each time    │
│  - Stops after 6 PM                             │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  generate_picks_to_file.py                      │
│  - Smart data refresh                           │
│  - Generate predictions                         │
│  - Push to GitHub                               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  GitHub Repository                              │
│  - LATEST_PICKS.txt (always current)            │
│  - PICKS_2025-10-27_09-00AM.txt (history)       │
│  - Accessible from anywhere                     │
└─────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  YOU (Phone/Work/Anywhere)                      │
│  - Open GitHub bookmark                         │
│  - Read picks                                   │
│  - Place bets                                   │
│  - Win! 🎉                                      │
└─────────────────────────────────────────────────┘
```

---

## Production Readiness

```
✅ Windows Task Scheduler    AUTOMATED
✅ Daily execution            AUTOMATED
✅ Data refresh              AUTOMATED
✅ Picks generation          AUTOMATED (4x daily)
✅ GitHub push               AUTOMATED
✅ Window management         AUTOMATED
✅ Error recovery            AUTOMATED
✅ Missed start handling     AUTOMATED

❌ Manual intervention       NOT NEEDED
❌ Computer must be on       TRUE (but see below)

STATUS: 100% AUTOMATED 🚀
```

---

## FAQ

**Q: What if my computer is off at 8:55 AM?**
**A:** Task won't run. You can manually run the batch file when you turn on your computer, or the task will run the next day.

**Q: Can I run this on a cloud server instead?**
**A:** Yes! Deploy to a free AWS/Azure/Google Cloud instance. Task Scheduler works on Windows Server too.

**Q: What if I forget my computer is sleeping?**
**A:** Task is configured to run when system becomes available. Wake computer, task runs.

**Q: Does this work on Mac/Linux?**
**A:** No, this uses Windows Task Scheduler. Mac uses `cron` or `launchd`, Linux uses `cron`.

**Q: Can I run multiple times per day?**
**A:** The script already does! It runs at 9 AM, 12 PM, 3 PM, 6 PM automatically.

**Q: Will this drain my battery if on laptop?**
**A:** Task is configured to run on battery, but the script only runs ~5 minutes max per execution (4x daily = 20 min total).

---

## Setup Summary

**Automatic (30 seconds):**
```powershell
cd "C:\Users\thoma\PrizePicks-Research-Lab"
powershell -ExecutionPolicy Bypass -File setup_windows_scheduler.ps1
```

**Manual (5 minutes):**
Follow the "Option 2: Manual Setup" section above

**Result:**
Wake up to fresh picks every day. Check GitHub bookmark. Place bets. Win!

---

**YOU'RE NOW 100% AUTOMATED!** 🎉

Tomorrow morning at 8:55 AM, the magic happens automatically!
