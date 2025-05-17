@echo off
setlocal enabledelayedexpansion

echo Stopping all services...

REM Kill FastAPI process (port 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":8000"') do (
    if not "%%a"=="" (
        echo Stopping FastAPI process...
        taskkill /F /T /PID %%a 2>nul
    )
)

REM Kill Flask process (port 5001)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":5001"') do (
    if not "%%a"=="" (
        echo Stopping Flask process...
        taskkill /F /T /PID %%a 2>nul
    )
)

REM Kill Node.js process (frontend)
set "node_killed="
for /f "tokens=2" %%a in ('tasklist ^| findstr "node.exe"') do (
    if not "%%a"=="" if not defined node_killed (
        echo Stopping Node.js process...
        taskkill /F /T /PID %%a 2>nul
        set "node_killed=1"
    )
)

REM Kill all cmd.exe processes except the current one
for /f "tokens=2" %%a in ('tasklist ^| findstr "cmd.exe"') do (
    if not "%%a"=="%CMDCMDLINE:~1%" (
        echo Stopping command prompt...
        taskkill /F /T /PID %%a 2>nul
    )
)

echo All services stopped successfully.
timeout /t 2 /nobreak > nul 