@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Please create the environment and install requirements.txt first.
    pause
    exit /b 1
)

.venv\Scripts\python.exe eod_main.py
pause
