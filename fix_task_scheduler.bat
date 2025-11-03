@echo off
REM Fix NHL Task Scheduler - Set Daily Recurring Triggers
REM Must run as Administrator

echo ================================================================================
echo FIXING NHL TASK SCHEDULER
echo ================================================================================
echo.

REM Delete old tasks
echo [1/3] Deleting old tasks...
schtasks /delete /tn "NHL Morning Run 0700" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 1200" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 1500" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 1800" /f >nul 2>&1
schtasks /delete /tn "NHL Adaptive Learning 2300" /f >nul 2>&1
schtasks /delete /tn "NHL TEST RUN 2000" /f >nul 2>&1
echo [OK] Old tasks deleted
echo.

REM Create TEST task for TONIGHT at 8:00 PM
echo [2/3] Creating TEST task for TONIGHT 8:00 PM...
schtasks /create /tn "NHL TEST RUN 2000" /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe RUN_DAILY_PICKS.py" /sc once /st 20:00 /sd 11/02/2025 /rl highest /f
echo [OK] Created: NHL TEST RUN 2000 (runs TONIGHT at 8:00 PM)
echo.

REM Create new tasks with DAILY triggers and WORKING DIRECTORY
echo [3/3] Creating new daily tasks...

schtasks /create /tn "NHL Morning Run 0700" /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe RUN_DAILY_PICKS.py" /sc daily /st 07:00 /rl highest /f
echo [OK] Created: NHL Morning Run 0700

schtasks /create /tn "NHL Picks Auto 1200" /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe RUN_DAILY_PICKS.py" /sc daily /st 12:00 /rl highest /f
echo [OK] Created: NHL Picks Auto 1200

schtasks /create /tn "NHL Picks Auto 1500" /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe RUN_DAILY_PICKS.py" /sc daily /st 15:00 /rl highest /f
echo [OK] Created: NHL Picks Auto 1500

schtasks /create /tn "NHL Picks Auto 1800" /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe RUN_DAILY_PICKS.py" /sc daily /st 18:00 /rl highest /f
echo [OK] Created: NHL Picks Auto 1800

schtasks /create /tn "NHL Adaptive Learning 2300" /tr "cmd /c cd /d C:\Users\thoma\PrizePicks-Research-Lab && C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe adaptive_learning\auto_grade_predictions.py" /sc daily /st 23:00 /rl highest /f
echo [OK] Created: NHL Adaptive Learning 2300

echo.
echo ================================================================================
echo [SUCCESS] All tasks created!
echo ================================================================================
echo.
echo TEST TASK (to verify fix works):
echo   - TONIGHT 8:00 PM   - Test run (one-time)
echo.
echo DAILY TASKS (will run automatically every day):
echo   - Tomorrow 7:00 AM  - Generate picks
echo   - Tomorrow 12:00 PM - Refresh picks
echo   - Tomorrow 3:00 PM  - Refresh picks
echo   - Tomorrow 6:00 PM  - Refresh picks
echo   - Tonight 11:00 PM  - Grade yesterday
echo.
echo AFTER 8 PM TONIGHT: Check for new files to confirm test worked!
echo   - PICKS_2025-11-02_08-00PM.txt
echo   - LATEST_PICKS.txt
echo.
echo Press any key to verify tasks...
pause >nul

python check_scheduled_tasks.py

pause
