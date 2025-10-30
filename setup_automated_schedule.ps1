# Setup Automated NHL Picks Schedule
# Runs complete workflow multiple times daily

$pythonPath = "C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe"
$scriptPath = "C:\Users\thoma\PrizePicks-Research-Lab\run_complete_workflow_gto.py"
$workingDir = "C:\Users\thoma\PrizePicks-Research-Lab"

# Times to run throughout the day
$runTimes = @(
    @{Hour="08"; Minute="00"; Label="8 AM"},
    @{Hour="10"; Minute="00"; Label="10 AM"},
    @{Hour="12"; Minute="00"; Label="12 PM"},
    @{Hour="14"; Minute="00"; Label="2 PM"},
    @{Hour="16"; Minute="00"; Label="4 PM"},
    @{Hour="18"; Minute="00"; Label="6 PM"},
    @{Hour="19"; Minute="00"; Label="7 PM"}
)

Write-Host "="*80
Write-Host "SETTING UP AUTOMATED NHL PICKS SCHEDULE"
Write-Host "="*80
Write-Host ""
Write-Host "This will create scheduled tasks to run the complete workflow at:"
foreach ($time in $runTimes) {
    Write-Host "  - $($time.Label)"
}
Write-Host ""

# Delete existing tasks if they exist
Write-Host "Removing old tasks (if any)..."
$existingTasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.TaskName -like "NHL Picks Auto *" }
foreach ($task in $existingTasks) {
    Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false
    Write-Host "  Removed: $($task.TaskName)"
}
Write-Host ""

# Create new tasks for each time
Write-Host "Creating new scheduled tasks..."
Write-Host ""

$successCount = 0

foreach ($time in $runTimes) {
    $taskName = "NHL Picks Auto $($time.Hour):$($time.Minute)"

    try {
        # Create trigger
        $trigger = New-ScheduledTaskTrigger -Daily -At "$($time.Hour):$($time.Minute)"

        # Create action
        $action = New-ScheduledTaskAction `
            -Execute $pythonPath `
            -Argument "`"$scriptPath`"" `
            -WorkingDirectory $workingDir

        # Create principal (run as current user)
        $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

        # Create settings
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable

        # Register task
        Register-ScheduledTask `
            -TaskName $taskName `
            -Trigger $trigger `
            -Action $action `
            -Principal $principal `
            -Settings $settings `
            -Description "Automated NHL picks generation, edge detection, and GTO parlay optimization - runs at $($time.Label) daily" `
            -Force | Out-Null

        Write-Host "[SUCCESS] Created: $taskName"
        $successCount++
    }
    catch {
        Write-Host "[ERROR] Failed to create: $taskName"
        Write-Host "  Error: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "="*80
Write-Host "SETUP COMPLETE"
Write-Host "="*80
Write-Host ""
Write-Host "Successfully created $successCount out of $($runTimes.Count) scheduled tasks"
Write-Host ""

# Display all tasks
$tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.TaskName -like "NHL Picks Auto *" }
if ($tasks) {
    Write-Host "Scheduled tasks:"
    Write-Host ""
    foreach ($task in $tasks) {
        $info = Get-ScheduledTaskInfo -TaskName $task.TaskName
        Write-Host "  Task: $($task.TaskName)"
        Write-Host "    State: $($task.State)"
        Write-Host "    Next Run: $($info.NextRunTime)"
        Write-Host ""
    }
}

Write-Host "="*80
Write-Host "WHAT HAPPENS AUTOMATICALLY"
Write-Host "="*80
Write-Host ""
Write-Host "Every run ($successCount times per day):"
Write-Host "  1. Fetch fresh NHL data (if >2 hours old)"
Write-Host "  2. Generate T1-ELITE predictions"
Write-Host "  3. Find PrizePicks edge plays (7%+ edge)"
Write-Host "  4. Build GTO-optimized parlays"
Write-Host "  5. Save everything to database"
Write-Host "  6. Export CSV files"
Write-Host "  7. Commit to GitHub"
Write-Host ""
Write-Host "YOUR workflow:"
Write-Host "  1. Check picks on GitHub or local files"
Write-Host "  2. Place bets on PrizePicks"
Write-Host "  3. Log each parlay: python log_parlay.py"
Write-Host "  4. Next day grade: python grade_all_picks.py 2025-10-30"
Write-Host ""
Write-Host "View picks online:"
Write-Host "  PICKS: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt"
Write-Host "  PARLAYS: https://github.com/thomascp2/nhl-predictions/blob/main/GTO_PARLAYS_*.csv"
Write-Host ""
Write-Host "Test manually:"
Write-Host "  Start-ScheduledTask -TaskName 'NHL Picks Auto 08:00'"
Write-Host ""
Write-Host "View all tasks:"
Write-Host "  Get-ScheduledTask | Where-Object { `$_.TaskName -like 'NHL Picks Auto *' }"
Write-Host ""
