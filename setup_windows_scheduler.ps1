# Setup Windows Task Scheduler for NHL Picks
# Run this ONCE to set up automatic daily execution

Write-Host "================================================================================" -ForegroundColor Green
Write-Host "NHL PICKS - Windows Task Scheduler Setup" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Task will be created but may have limited permissions" -ForegroundColor Yellow
    Write-Host ""
}

# Task details
$taskName = "NHL Picks Daily Auto-Scheduler"
$taskDescription = "Automatically generates NHL predictions throughout the day (9 AM - 6 PM)"
$scriptPath = "C:\Users\thoma\PrizePicks-Research-Lab\run_daily_picks.bat"

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""

# Create the trigger (daily at 8:55 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "8:55AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 10)

# Create principal (run whether user is logged in or not)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Limited

# Register the task
try {
    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

    if ($existingTask) {
        Write-Host "[INFO] Task already exists - unregistering old task" -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    # Register new task
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal | Out-Null

    Write-Host "[SUCCESS] Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Name: $taskName" -ForegroundColor Cyan
    Write-Host "Run Time:  Daily at 8:55 AM" -ForegroundColor Cyan
    Write-Host "Duration:  Runs until 6:00 PM" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "What happens now:" -ForegroundColor Yellow
    Write-Host "  1. Every morning at 8:55 AM, the task runs automatically" -ForegroundColor White
    Write-Host "  2. A window opens showing picks generation progress" -ForegroundColor White
    Write-Host "  3. Picks are generated at 9 AM, 12 PM, 3 PM, 6 PM" -ForegroundColor White
    Write-Host "  4. Each run updates GitHub (view from anywhere)" -ForegroundColor White
    Write-Host "  5. Window closes automatically after 6 PM" -ForegroundColor White
    Write-Host ""
    Write-Host "You can minimize the window when it opens - it runs in background!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Want to test it now? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host

    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host ""
        Write-Host "Starting test run..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $taskName
        Write-Host "[SUCCESS] Task started! Check for the command window." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Task will run automatically tomorrow at 8:55 AM" -ForegroundColor Cyan
    }

} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to create task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running PowerShell as Administrator:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor White
    Write-Host "  2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
