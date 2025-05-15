#!/bin/bash

# Запуск backend
cd backend
source .venv/bin/activate
nohup python3 -m uvicorn api_main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "Backend (uvicorn) запущен с PID $BACKEND_PID"
cd ..

# Запуск frontend
cd frontend
nohup npm run dev &
FRONTEND_PID=$!
echo "Frontend (npm run dev) запущен с PID $FRONTEND_PID"
cd ..

# Ожидание завершения процессов
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM
wait $BACKEND_PID $FRONTEND_PID 