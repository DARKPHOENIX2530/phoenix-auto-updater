@echo off
REM Phoenix Auto-Updater Launcher (Standalone)
REM Download this once, run it, and it keeps your Phoenix installation updated from GitHub

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Run the auto-updater
echo Starting Phoenix Auto-Updater...
python phoenix_auto_updater.py

pause