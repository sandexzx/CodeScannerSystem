@echo off
echo.
echo ========================================
echo Checking Python installation...
echo ========================================

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set pyver=%%i
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Found Python %pyver%

REM Check Python version
for /f "tokens=1,2 delims=." %%a in ("%pyver%") do (
    set pyver_major=%%a
    set pyver_minor=%%b
)

if %pyver_major% LSS 3 (
    echo Error: Python 3.8 or higher is required!
    echo Current version: %pyver%
    pause
    exit /b 1
) else (
    if %pyver_major% EQU 3 (
        if %pyver_minor% LSS 8 (
            echo Error: Python 3.8 or higher is required!
            echo Current version: %pyver%
            pause
            exit /b 1
        )
    )
)
echo Python version is compatible.
echo.

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
python -c "import pandas; import pygame; import rich; import openpyxl; print('All dependencies successfully installed!')" 2>nul
if errorlevel 1 (
    echo Error: Some dependencies failed to install
    pause
    exit /b 1
)

echo.
echo Checking for sound files...
if not exist sounds\success.wav (
    echo Warning: sounds\success.wav not found - you'll need to create this file
)
if not exist sounds\error.wav (
    echo Warning: sounds\error.wav not found - you'll need to create this file
)
if not exist sounds\box_full.wav (
    echo Warning: sounds\box_full.wav not found - you'll need to create this file
)

echo.
echo Setup completed successfully!
echo Run 'run.bat' to start the application
echo.
pause 