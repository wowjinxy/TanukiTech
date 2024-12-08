@echo off
REM Display initialization warning
echo WARNING: If this is the first time running this script, it may take a moment to initialize.

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not added to PATH.
    pause
    exit /b 1
)

REM Create a virtual environment if it doesn't exist
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate >nul 2>&1

REM Install required dependencies quietly
pip install --quiet --upgrade pip >nul 2>&1
pip install --quiet -r requirements.txt >nul 2>&1

REM Run the main script
python main.py

pause

REM Deactivate the virtual environment
call venv\Scripts\deactivate >nul 2>&1
