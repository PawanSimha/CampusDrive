@echo off
TITLE CampusDrive ^| Empowering Academic Collaboration
COLOR 0B

:: Ensure the script runs in the exact folder where the BAT file is located
cd /d "%~dp0"

echo ======================================================================
echo          CampusDrive: Academic Collaboration Platform
echo ======================================================================
echo.
echo Launching Local Development Hub on port 5001...
echo.
echo [INFO] Security: CSRF Protected & Role-Based Access Enabled.
echo [INFO] Infrastructure: Optimized MongoDB Atlas Integration.
echo [INFO] Documentation: Full details available in README.md
echo.
echo [SYSTEM] Verifying Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found on your PATH.
    echo Please install Python 3.x to continue.
    pause
    exit /b
)

:: Open the default browser to the local hub
start http://localhost:5001

:: Start the CampusDrive Application Service
echo [SYSTEM] Starting Flask Application Service...
python app.py

:: If the app crashes, keep the window open for diagnostic logs
if errorlevel 1 (
    echo.
    echo [CRITICAL] Application Service Interrupted.
    echo Review the logs above for diagnostic information.
    pause
)

pause
