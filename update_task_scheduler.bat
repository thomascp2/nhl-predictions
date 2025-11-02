@echo off
REM Update Task Scheduler to use new simplified scripts
REM Run this as Administrator

echo ================================================================================
echo UPDATING NHL TASK SCHEDULER
echo ================================================================================
echo.

set PYTHON_PATH=C:\Users\thoma\AppData\Local\Programs\Python\Python313\python.exe
set PROJECT_PATH=C:\Users\thoma\PrizePicks-Research-Lab

echo Deleting old tasks...
schtasks /delete /tn "NHL Morning Run 0700" /f
schtasks /delete /tn "NHL Picks Auto 1200" /f
schtasks /delete /tn "NHL Picks Auto 1500" /f
schtasks /delete /tn "NHL Picks Auto 1800" /f
schtasks /delete /tn "NHL Adaptive Learning 2300" /f

echo.
echo Creating new tasks with updated scripts...
echo.

REM Task 1: Morning Run (7 AM)
echo [1/5] Creating NHL Morning Run 0700...
schtasks /create /tn "NHL Morning Run 0700" /tr "\"%PYTHON_PATH%\" \"%PROJECT_PATH%\RUN_DAILY_PICKS.py\"" /sc daily /st 07:00 /f /rl HIGHEST
if %errorlevel% equ 0 (echo [OK] Task created successfully) else (echo [ERROR] Task creation failed)

REM Task 2: Midday Run (12 PM)
echo [2/5] Creating NHL Picks Auto 1200...
schtasks /create /tn "NHL Picks Auto 1200" /tr "\"%PYTHON_PATH%\" \"%PROJECT_PATH%\RUN_DAILY_PICKS.py\"" /sc daily /st 12:00 /f /rl HIGHEST
if %errorlevel% equ 0 (echo [OK] Task created successfully) else (echo [ERROR] Task creation failed)

REM Task 3: Afternoon Run (3 PM)
echo [3/5] Creating NHL Picks Auto 1500...
schtasks /create /tn "NHL Picks Auto 1500" /tr "\"%PYTHON_PATH%\" \"%PROJECT_PATH%\RUN_DAILY_PICKS.py\"" /sc daily /st 15:00 /f /rl HIGHEST
if %errorlevel% equ 0 (echo [OK] Task created successfully) else (echo [ERROR] Task creation failed)

REM Task 4: Evening Run (6 PM)
echo [4/5] Creating NHL Picks Auto 1800...
schtasks /create /tn "NHL Picks Auto 1800" /tr "\"%PYTHON_PATH%\" \"%PROJECT_PATH%\RUN_DAILY_PICKS.py\"" /sc daily /st 18:00 /f /rl HIGHEST
if %errorlevel% equ 0 (echo [OK] Task created successfully) else (echo [ERROR] Task creation failed)

REM Task 5: Adaptive Learning (11 PM)
echo [5/5] Creating NHL Adaptive Learning 2300...
schtasks /create /tn "NHL Adaptive Learning 2300" /tr "\"%PYTHON_PATH%\" \"%PROJECT_PATH%\adaptive_learning\auto_grade_predictions.py\"" /sc daily /st 23:00 /f /rl HIGHEST
if %errorlevel% equ 0 (echo [OK] Task created successfully) else (echo [ERROR] Task creation failed)

echo.
echo ================================================================================
echo TASK SCHEDULER UPDATE COMPLETE
echo ================================================================================
echo.
echo Updated Schedule:
echo   7:00 AM  - RUN_DAILY_PICKS.py (generates predictions + pushes to GitHub)
echo  12:00 PM  - RUN_DAILY_PICKS.py (generates predictions + pushes to GitHub)
echo   3:00 PM  - RUN_DAILY_PICKS.py (generates predictions + pushes to GitHub)
echo   6:00 PM  - RUN_DAILY_PICKS.py (generates predictions + pushes to GitHub)
echo  11:00 PM  - auto_grade_predictions.py (grades yesterday's picks)
echo.
echo View picks on GitHub:
echo   https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
echo.
echo ================================================================================

pause
