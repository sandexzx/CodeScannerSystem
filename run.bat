@echo off
REM Запуск backend в новом окне
start cmd /k "cd backend && call .venv\Scripts\activate.bat && python -m uvicorn api_main:app --reload --host 127.0.0.1 --port 8000"

REM Запуск frontend (Vite) в новом окне
start cmd /k "cd frontend && npm run dev"

REM Ожидание завершения процессов (опционально)
pause
