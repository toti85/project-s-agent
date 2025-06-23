@echo off
echo Starting Project-S Multi-Model System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or later.
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found, creating one...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies if needed
pip install -r requirements-multi-model.txt

REM Create necessary directories
if not exist logs mkdir logs
if not exist memory mkdir memory
if not exist memory\state mkdir memory\state

REM Run the multi-model system
python main_multi_model.py

REM Deactivate virtual environment
call deactivate
