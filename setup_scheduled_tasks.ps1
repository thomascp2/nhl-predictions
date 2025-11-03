# Setup NHL Prediction Workflow Scheduled Tasks
# Runs at 06:15, 12:30, and 16:30 CST daily starting 11/3/2025

$WorkDir = "C:\Users\thoma\PrizePicks-Research-Lab"
$PythonExe = "C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe"
$ScriptPath = "$WorkDir\RUN_COMPLETE_DAILY_WORKFLOW.py"
$StartDate = "11/03/2025"

Write-Host "="*80
Write-Host "SETTING UP NHL PREDICTION WORKFLOW SCHEDULED TASKS"
Write-Host "="*80
Write-Host ""
Write-Host "Working Directory: $WorkDir"
Write-Host "Python: $PythonExe"
Write-Host "Script: $ScriptPath"
Write-Host "Start Date: $StartDate"
Write-Host ""

# Task 1: 06:15 AM CST
Write-Host "Creating Task 1: NHL Workflow 06:15 AM CST..."
schtasks /create `
    /tn "NHL_Predictions_0615" `
    /tr "cmd /c cd /d $WorkDir && $PythonExe RUN_COMPLETE_DAILY_WORKFLOW.py" `
    /sc daily `
    /st 06:15 `
    /sd $StartDate `
    /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Task 1 created successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to create Task 1" -ForegroundColor Red
}
Write-Host ""

# Task 2: 12:30 PM CST
Write-Host "Creating Task 2: NHL Workflow 12:30 PM CST..."
schtasks /create `
    /tn "NHL_Predictions_1230" `
    /tr "cmd /c cd /d $WorkDir && $PythonExe RUN_COMPLETE_DAILY_WORKFLOW.py" `
    /sc daily `
    /st 12:30 `
    /sd $StartDate `
    /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Task 2 created successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to create Task 2" -ForegroundColor Red
}
Write-Host ""

# Task 3: 04:30 PM CST
Write-Host "Creating Task 3: NHL Workflow 04:30 PM CST..."
schtasks /create `
    /tn "NHL_Predictions_1630" `
    /tr "cmd /c cd /d $WorkDir && $PythonExe RUN_COMPLETE_DAILY_WORKFLOW.py" `
    /sc daily `
    /st 16:30 `
    /sd $StartDate `
    /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Task 3 created successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to create Task 3" -ForegroundColor Red
}
Write-Host ""

Write-Host "="*80
Write-Host "SCHEDULED TASKS CREATED"
Write-Host "="*80
Write-Host ""
Write-Host "To view tasks:"
Write-Host "  schtasks /query /tn NHL_Predictions_0615 /fo list /v"
Write-Host "  schtasks /query /tn NHL_Predictions_1230 /fo list /v"
Write-Host "  schtasks /query /tn NHL_Predictions_1630 /fo list /v"
Write-Host ""
Write-Host "To run manually:"
Write-Host "  schtasks /run /tn NHL_Predictions_0615"
Write-Host "  schtasks /run /tn NHL_Predictions_1230"
Write-Host "  schtasks /run /tn NHL_Predictions_1630"
Write-Host ""
Write-Host "To delete tasks:"
Write-Host "  schtasks /delete /tn NHL_Predictions_0615 /f"
Write-Host "  schtasks /delete /tn NHL_Predictions_1230 /f"
Write-Host "  schtasks /delete /tn NHL_Predictions_1630 /f"
Write-Host ""
Write-Host "="*80
