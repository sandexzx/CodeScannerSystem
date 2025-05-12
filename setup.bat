@echo off
echo Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists
) else (
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Verifying installation...
python -c "import pandas; import pygame; import watchdog; import openpyxl" 2>nul
if errorlevel 1 (
    echo Error: Some dependencies failed to install
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo To activate the virtual environment, run: .venv\Scripts\activate.bat
echo.
pause 