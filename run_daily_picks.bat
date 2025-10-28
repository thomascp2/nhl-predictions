@echo off
REM NHL Picks Auto-Scheduler - Runs 9 AM to 6 PM
REM This batch file is triggered by Windows Task Scheduler

REM Set UTF-8 encoding to prevent emoji crashes
chcp 65001 >nul 2>&1

echo ================================================================================
echo NHL PICKS - DAILY AUTO-SCHEDULER
echo ================================================================================
echo.
echo Starting at %TIME%
echo This window will stay open until 6 PM
echo.
echo You can minimize this window and forget about it!
echo.

cd /d "C:\Users\thoma\PrizePicks-Research-Lab"

REM Set Python to use UTF-8 encoding
set PYTHONIOENCODING=utf-8

python run_picks_throughout_day.py

echo.
echo ================================================================================
echo Daily picks generation complete
echo Window will close in 30 seconds...
echo ================================================================================
timeout /t 30
