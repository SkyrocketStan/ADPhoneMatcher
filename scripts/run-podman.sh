#!/bin/bash

# Очистка старого виртуального окружения
rm -rf .venv

# Проверка наличия Podman
if ! command -v podman &> /dev/null; then
    echo "Ошибка: Podman не установлен. Установите Podman и повторите."
    exit 1
fi

# Параметры
BASE_DIR=$(pwd)
INPUT_DIR="${BASE_DIR}/data/ad_input"
OUTPUT_DIR="${BASE_DIR}/data/results"
LOGS_DIR="${BASE_DIR}/logs"
ARCHIVE_DIR="${BASE_DIR}/data/archive"
UPLOADS_DIR="${BASE_DIR}/data/phone_data"

# Создание директорий
mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}" "${LOGS_DIR}" "${ARCHIVE_DIR}" "${UPLOADS_DIR}"

# Имя входного файла AD
AD_FILE=${1:-ad_input.csv}
AD_INPUT="${INPUT_DIR}/${AD_FILE}"

# Проверка входного файла
if [ ! -f "${AD_INPUT}" ]; then
    echo "Ошибка: входной файл ${AD_INPUT} не найден."
    exit 1
fi

# Запуск контейнера
podman run --rm \
    -v "${BASE_DIR}:/app:Z" \
    -w /app \
    python:3.7-slim \
    bash -c "python3 -m phone_matcher.main /app/data/ad_input/${AD_FILE}"