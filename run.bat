@echo off
echo Starting Product Management System...

REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the application
python main.py

REM If application terminated with error
if errorlevel 1 (
    echo.
    echo An error occurred while running the application
    pause
    exit /b 1
)

REM Deactivate virtual environment on exit
call .venv\Scripts\deactivate.bat 