@echo off

:: Aktiválja a virtuális környezetet, ha létezik
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

:: Process command line arguments
set ENABLE_DASHBOARD=true
set DASHBOARD_PORT=7777

:: Check for command line arguments
if "%1"=="--no-dashboard" set ENABLE_DASHBOARD=false
if "%1"=="--port" set DASHBOARD_PORT=%2

:: Set environment variables for diagnostics configuration
set PROJECT_S_DIAGNOSTICS_DASHBOARD=%ENABLE_DASHBOARD%
set PROJECT_S_DIAGNOSTICS_PORT=%DASHBOARD_PORT%

echo Starting Project-S Agent...
if "%ENABLE_DASHBOARD%"=="true" (
    echo Diagnostics dashboard will be available at http://localhost:%DASHBOARD_PORT%
)

:: Elindítja a Project-S agentet
python main.py