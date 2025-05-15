#!/bin/bash

# Запуск backend (FastAPI для сканирования)
cd backend
source .venv/bin/activate
nohup python3 -m uvicorn api_main:app --reload --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!
echo "Backend (FastAPI) запущен с PID $FASTAPI_PID"

# Запуск backend (Flask для настроек)
nohup python3 api.py &
FLASK_PID=$!
echo "Backend (Flask) запущен с PID $FLASK_PID"
cd ..

# Запуск frontend
cd frontend
nohup npm run dev &
FRONTEND_PID=$!
echo "Frontend (npm run dev) запущен с PID $FRONTEND_PID"
cd ..

# Ожидание завершения процессов
trap "kill $FASTAPI_PID $FLASK_PID $FRONTEND_PID" SIGINT SIGTERM
wait $FASTAPI_PID $FLASK_PID $FRONTEND_PID 