@echo off
echo ========================================================================
echo Education RAG System - Quick Setup Script (Windows)
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo + Python found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo X Failed to create virtual environment
    pause
    exit /b 1
)

echo + Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo X Failed to activate virtual environment
    pause
    exit /b 1
)

echo + Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo + All dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo + .env file created
    echo.
    echo ! IMPORTANT: Edit .env file and add your ANTHROPIC_API_KEY
    echo   Get your API key from: https://console.anthropic.com/
    echo.
) else (
    echo + .env file already exists
    echo.
)

REM Run tests
echo ========================================================================
echo Running system tests...
echo ========================================================================
echo.

python scripts\test_system.py

echo.
echo ========================================================================
echo Setup Complete!
echo ========================================================================
echo.
echo Next steps:
echo 1. Edit .env file and add your ANTHROPIC_API_KEY
echo 2. Put your PDF textbooks in the .\uploads\ directory
echo 3. Run: python scripts\main_pipeline.py --pdf uploads\your_file.pdf --class 8 --subject Math
echo 4. Or start the API server: python api_server.py
echo.
echo For detailed instructions, see README.md
echo.
echo ========================================================================
pause
