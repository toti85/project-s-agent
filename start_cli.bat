@echo off
:: Project-S Unified CLI Launcher
:: ==============================
:: Windows batch script for easy CLI access

setlocal enabledelayedexpansion

:: Check if virtual environment exists and activate it
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

:: Set up environment variables (add your API keys here)
if "%OPENAI_API_KEY%"=="" (
    set OPENAI_API_KEY=
)
if "%OPENROUTER_API_KEY%"=="" (
    set OPENROUTER_API_KEY=
)

:: Display banner
echo.
echo ===============================================================
echo Project-S Unified CLI - Windows Launcher
echo ===============================================================
echo.

:: Check for API keys
if "%OPENAI_API_KEY%"=="" (
    if "%OPENROUTER_API_KEY%"=="" (
        echo WARNING: No API keys configured!
        echo Please set OPENAI_API_KEY or OPENROUTER_API_KEY environment variables.
        echo You can also edit this batch file to set them.
        echo.
    )
)

:: Parse command line arguments
if "%1"=="" goto :show_menu
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="help" goto :show_help

:: Direct command execution
echo Executing: python cli_main.py %*
python cli_main.py %*
goto :end

:show_menu
echo Choose launch mode:
echo.
echo 1 - Interactive Mode (recommended)
echo 2 - Direct Command Mode
echo 3 - Show Available Models
echo 4 - Show Available Workflows
echo 5 - Export CLI Configuration
echo 6 - Help
echo 7 - Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto :interactive
if "%choice%"=="2" goto :direct
if "%choice%"=="3" goto :models
if "%choice%"=="4" goto :workflows
if "%choice%"=="5" goto :export
if "%choice%"=="6" goto :show_help
if "%choice%"=="7" goto :end
echo Invalid choice!
goto :show_menu

:interactive
echo Starting interactive mode...
python cli_main.py --interactive
goto :end

:direct
echo Enter your command (or 'back' to return to menu):
set /p command="Command: "
if "%command%"=="back" goto :show_menu
echo Executing: %command%
python cli_main.py %command%
echo.
echo Press any key to continue...
pause >nul
goto :show_menu

:models
echo Listing available models...
python cli_main.py --list-models
echo.
echo Press any key to continue...
pause >nul
goto :show_menu

:workflows
echo Listing available workflows...
python cli_main.py --list-workflows
echo.
echo Press any key to continue...
pause >nul
goto :show_menu

:export
echo Exporting CLI configuration...
python cli_main.py --export
echo.
echo Press any key to continue...
pause >nul
goto :show_menu

:show_help
echo.
echo PROJECT-S UNIFIED CLI HELP
echo =========================
echo.
echo BASIC USAGE:
echo   start_cli.bat                    - Show this menu
echo   start_cli.bat --interactive      - Start interactive mode
echo   start_cli.bat ask "question"     - Ask AI a question
echo   start_cli.bat cmd "command"      - Execute system command
echo   start_cli.bat file read path     - Read file
echo   start_cli.bat workflow type      - Run workflow
echo.
echo EXAMPLES:
echo   start_cli.bat ask "What is Python?"
echo   start_cli.bat workflow code-generator "Create FastAPI server"
echo   start_cli.bat file read README.md
echo   start_cli.bat cmd "dir"
echo.
echo OPTIONS:
echo   --interactive     Start interactive mode
echo   --list-models     Show available AI models
echo   --list-workflows  Show available workflows
echo   --export          Export CLI configuration
echo   --help            Show this help
echo.
echo For more detailed help, use: start_cli.bat --help
echo.
echo Press any key to continue...
pause >nul
goto :show_menu

:end
:: Deactivate virtual environment if it was activated
if exist venv\Scripts\activate (
    deactivate 2>nul
)

echo.
echo Project-S CLI session ended.
