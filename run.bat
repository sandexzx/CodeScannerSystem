@echo off

REM Check if port 5001 is in use and kill the process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":5001"') do (
    if not "%%a"=="" (
        echo Port 5001 is in use, killing process...
        taskkill /F /PID %%a
        timeout /t 2 /nobreak > nul
    )
)

REM Start backend (FastAPI for scanning)
cd backend
start "FastAPI Backend" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn api_main:app --reload --host 127.0.0.1 --port 8000"
cd ..

REM Start backend (Flask for settings)
cd backend
start "Flask Backend" cmd /k "call .venv\Scripts\activate.bat && python api.py --port 5001 --host 127.0.0.1"
cd ..

REM Wait for Flask to start (increased wait time and multiple retries)
echo Waiting for Flask server to start...
set /a retries=0
:check_flask
timeout /t 3 /nobreak > nul
netstat -ano | findstr "LISTENING" | findstr ":5001" > nul
if errorlevel 1 (
    set /a retries+=1
    if %retries% lss 5 (
        echo Waiting for Flask server... (attempt %retries% of 5)
        goto check_flask
    ) else (
        echo Warning: Could not confirm Flask server startup, but continuing anyway...
    )
) else (
    echo Flask server is running on port 5001
)

REM Start frontend
cd frontend
start "Frontend" cmd /k "npm run dev"
cd ..

echo All services started. Press Ctrl+C in each window to stop the services.
