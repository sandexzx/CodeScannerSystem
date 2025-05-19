@echo off
setlocal enabledelayedexpansion

echo Starting release build and run process...

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Build frontend
echo Building frontend...
cd frontend
echo Running npm run build...
call npm run build > ..\logs\build.log 2>&1
if errorlevel 1 (
    echo Error: Frontend build failed!
    echo Please check logs\build.log for details
    cd ..
    echo Press any key to exit...
    pause > nul
    goto cleanup
)
cd ..
echo Frontend build completed successfully.

REM Check if port 5001 is in use and kill the process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":5001"') do (
    if not "%%a"=="" (
        echo Port 5001 is in use, killing process...
        taskkill /F /PID %%a
        timeout /t 2 /nobreak > nul
    )
)

REM Start backend (FastAPI for scanning)
echo Starting FastAPI backend...
cd backend
start /b "" pythonw -m uvicorn api_main:app --host 127.0.0.1 --port 8000 > ..\logs\fastapi.log 2>&1
cd ..

REM Start backend (Flask for settings)
echo Starting Flask backend...
cd backend
start /b "" pythonw api.py --port 5001 --host 127.0.0.1 > ..\logs\flask.log 2>&1
cd ..

REM Wait for Flask to start
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
        echo Error: Flask server failed to start. Check logs\flask.log for details.
        echo Press any key to exit...
        pause > nul
        goto cleanup
    )
) else (
    echo Flask server is running on port 5001
)

REM Start frontend in production mode
echo Starting frontend in production mode...
cd frontend
start /b "" npm run preview > ..\logs\frontend.log 2>&1
cd ..

echo Application started successfully!
echo Logs are available in the 'logs' directory
echo Press any key to stop all services...

pause > nul

:cleanup
REM Kill all background processes
echo Stopping all services...
taskkill /F /IM pythonw.exe > nul 2>&1
taskkill /F /IM node.exe > nul 2>&1

echo All services stopped.
echo Press any key to exit...
pause > nul 