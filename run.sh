#!/bin/bash

# Очистка лог-файла nohup.out в директории backend
if [ -f backend/nohup.out ]; then
    rm backend/nohup.out
fi

# Проверка и освобождение порта 5001 если он занят
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "Порт 5001 занят, освобождаем..."
    kill $(lsof -t -i:5001)
    sleep 2
fi

# Запуск backend (FastAPI для сканирования)
cd backend
source .venv/bin/activate
nohup python3 -m uvicorn api_main:app --reload --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!
echo "Backend (FastAPI) запущен с PID $FASTAPI_PID"

# Запуск backend (Flask для настроек)
echo "Запуск Flask сервера на порту 5001..."
nohup python3 api.py --port 5001 --host 127.0.0.1 > flask.log 2>&1 &
FLASK_PID=$!
echo "Backend (Flask) запущен с PID $FLASK_PID"

# Проверка что Flask сервер запустился
sleep 2
if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "Ошибка: Flask сервер не запустился на порту 5001"
    echo "Логи Flask сервера:"
    cat flask.log
    exit 1
fi

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