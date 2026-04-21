@echo off
REM Johnny's Pi Startup Script
cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Pi Report] Python not found
    pause
    exit /b 1
)

python pi_startup.py
pause
