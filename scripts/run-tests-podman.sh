#!/bin/bash

# Проверка наличия Podman
if ! command -v podman &> /dev/null; then
    echo "Ошибка: Podman не установлен. Установите Podman и повторите."
    exit 1
fi

# Параметры
BASE_DIR=$(pwd)
IMAGE_NAME="adphonematcher:test"

# Создание директорий
mkdir -p "${BASE_DIR}/data/ad_input" "${BASE_DIR}/data/phone_data" "${BASE_DIR}/data/results" "${BASE_DIR}/data/archive" "${BASE_DIR}/logs"

# Проверка наличия образа
if ! podman image exists "${IMAGE_NAME}"; then
    echo "Сборка образа ${IMAGE_NAME}..."
    podman build -t "${IMAGE_NAME}" .
fi

# Запуск контейнера для тестов
podman run --rm \
    -v "${BASE_DIR}:/app:Z" \
    -w /app \
    "${IMAGE_NAME}" \
    bash -c "python3 -m unittest discover -s tests && pylint phone_matcher/*.py tests/*.py"