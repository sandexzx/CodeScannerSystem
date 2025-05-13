@echo off
echo.
echo ========================================
echo Starting Product Management System...
echo ========================================
echo.


REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found!
    echo Please run setup.bat first to install dependencies
    echo.
    echo Press any key to run setup.bat automatically...
    pause >nul
    call setup.bat
    if errorlevel 1 (
        echo.
        echo Setup failed. Please resolve the issues and try again.
        pause
        exit /b 1
    )
    echo.
    echo Setup completed! Starting the application...
    echo.
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the main application
python main.py

REM If application terminated with error
if errorlevel 1 (
    echo.
    echo An error occurred while running the application
    pause
    exit /b 1
)
else (
   echo.
   echo Application terminated successfully!
)

REM Deactivate virtual environment on exit
call .venv\Scripts\deactivate.bat
echo.
echo Done! Press any key to exit...
pause >nul