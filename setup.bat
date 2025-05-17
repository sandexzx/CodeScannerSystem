@echo off

REM === Backend Python setup ===
cd backend

REM Check and create virtual environment
if not exist .venv (
    echo Creating Python virtual environment in backend\.venv...
    python -m venv .venv
) else (
    echo Python virtual environment found in backend\.venv
)

REM Install dependencies
if exist requirements.txt (
    echo Installing Python dependencies from requirements.txt...
    .venv\Scripts\pip.exe install -r requirements.txt
) else (
    echo requirements.txt not found in backend. Skipping Python dependencies installation.
)
cd ..

REM === Frontend npm setup ===
cd frontend
if exist package.json (
    echo Installing npm dependencies from package.json...
    npm install
) else (
    echo package.json not found in frontend. Skipping npm dependencies installation.
)
cd ..

echo All dependencies installed (if files were found).

