@echo off
setlocal

:: Get the directory where the script is located
cd /d "%~dp0"

echo ===========================================
echo Starting CampusConnect...
echo ===========================================

:: Check for virtual environment and activate if found
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment (venv)...
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment (.venv)...
    call ".venv\Scripts\activate.bat"
) else (
    echo [INFO] No virtual environment found. Using system Python.
)

:: Run the application
python app.py

:: Pause so the window doesn't close immediately on error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
