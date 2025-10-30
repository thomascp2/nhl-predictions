@echo off
REM Create 7 daily scheduled tasks for NHL picks automation

echo ================================================================================
echo SETTING UP AUTOMATED NHL PICKS SCHEDULE
echo ================================================================================
echo.
echo This will create 7 scheduled tasks to run at:
echo   - 8:00 AM
echo   - 10:00 AM
echo   - 12:00 PM
echo   - 2:00 PM
echo   - 4:00 PM
echo   - 6:00 PM
echo   - 7:00 PM
echo.

set PYTHON=C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe
set SCRIPT=C:\Users\thoma\PrizePicks-Research-Lab\run_complete_workflow_gto.py
set WORKDIR=C:\Users\thoma\PrizePicks-Research-Lab

echo Deleting old tasks (if they exist)...
schtasks /delete /tn "NHL Picks Auto 08:00" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 10:00" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 12:00" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 14:00" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 16:00" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 18:00" /f >nul 2>&1
schtasks /delete /tn "NHL Picks Auto 19:00" /f >nul 2>&1
echo.

echo Creating new scheduled tasks...
echo.

REM 8:00 AM
schtasks /create /tn "NHL Picks Auto 08:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 08:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 08:00) else (echo [FAILED] NHL Picks Auto 08:00)

REM 10:00 AM
schtasks /create /tn "NHL Picks Auto 10:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 10:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 10:00) else (echo [FAILED] NHL Picks Auto 10:00)

REM 12:00 PM
schtasks /create /tn "NHL Picks Auto 12:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 12:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 12:00) else (echo [FAILED] NHL Picks Auto 12:00)

REM 2:00 PM
schtasks /create /tn "NHL Picks Auto 14:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 14:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 14:00) else (echo [FAILED] NHL Picks Auto 14:00)

REM 4:00 PM
schtasks /create /tn "NHL Picks Auto 16:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 16:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 16:00) else (echo [FAILED] NHL Picks Auto 16:00)

REM 6:00 PM
schtasks /create /tn "NHL Picks Auto 18:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 18:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 18:00) else (echo [FAILED] NHL Picks Auto 18:00)

REM 7:00 PM
schtasks /create /tn "NHL Picks Auto 19:00" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc daily /st 19:00 /f
if %errorlevel% equ 0 (echo [SUCCESS] Created: NHL Picks Auto 19:00) else (echo [FAILED] NHL Picks Auto 19:00)

echo.
echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo View all tasks:
schtasks /query /fo table /tn "NHL Picks Auto*"
echo.
echo ================================================================================
echo WHAT HAPPENS AUTOMATICALLY
echo ================================================================================
echo.
echo Every run (7 times per day):
echo   1. Fetch fresh NHL data (if ^>2 hours old)
echo   2. Generate T1-ELITE predictions
echo   3. Find PrizePicks edge plays (7%% edge)
echo   4. Build GTO-optimized parlays
echo   5. Save everything to database
echo   6. Export CSV files
echo   7. Commit to GitHub
echo.
echo YOUR workflow:
echo   1. Check picks on GitHub or local files
echo   2. Place bets on PrizePicks
echo   3. Log each parlay: python log_parlay.py
echo   4. Next day grade: python grade_all_picks.py 2025-10-30
echo.
echo View picks online:
echo   PICKS: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
echo   PARLAYS: https://github.com/thomascp2/nhl-predictions/blob/main/GTO_PARLAYS_*.csv
echo.
echo Test manually:
echo   schtasks /run /tn "NHL Picks Auto 08:00"
echo.
pause
