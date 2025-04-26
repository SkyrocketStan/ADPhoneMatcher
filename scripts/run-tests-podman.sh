#!/bin/bash

# Проверка наличия Podman
if ! command -v podman &> /dev/null; then
    echo "Ошибка: Podman не установлен. Установите Podman и повторите."
    exit 1
fi

# Параметры
BASE_DIR=$(pwd)

# Запуск контейнера для тестов
podman run --rm \
    -v "${BASE_DIR}:/app:Z" \
    -w /app \
    python:3.7-slim \
    bash -c "pip install pytest pylint && python3 -m unittest discover -s tests && pylint phone_matcher/*.py tests/*.py"