@echo off
REM Start script for Cloud Image Processing Platform (Windows)
REM This script sets up and starts the Flask backend server

echo ==========================================
echo   Cloud Image Processing Platform
echo ==========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: No virtual environment found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created
)

REM Install/update dependencies
echo.
echo Checking dependencies...
pip install -r requirements.txt --quiet
echo Dependencies ready

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    set /p CONTINUE="Do you want to continue with default settings? (y/n): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

REM Start the server
echo.
echo ==========================================
echo Starting Flask server...
echo ==========================================
echo.

python app.py

pause