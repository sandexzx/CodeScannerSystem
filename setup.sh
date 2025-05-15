#!/bin/bash

# === Backend Python setup ===
cd backend

# Проверка и создание виртуального окружения
if [ ! -d ".venv" ]; then
    echo "Создаю Python virtual environment в backend/.venv..."
    python3 -m venv .venv
else
    echo "Python virtual environment найден в backend/.venv"
fi

# Установка зависимостей
if [ -f "requirements.txt" ]; then
    echo "Устанавливаю Python зависимости из requirements.txt..."
    .venv/bin/pip install -r requirements.txt
else
    echo "requirements.txt не найден в backend. Пропускаю установку Python зависимостей."
fi
cd ..

# === Frontend npm setup ===
cd frontend
if [ -f "package.json" ]; then
    echo "Устанавливаю npm зависимости из package.json..."
    npm install
else
    echo "package.json не найден в frontend. Пропускаю установку npm зависимостей."
fi
cd ..

echo "Все зависимости установлены (если файлы найдены)." 