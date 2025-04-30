# ADPhoneMatcher

![Pylint Check](https://github.com/SkyrocketStan/ADPhoneMatcher/actions/workflows/pylint.yml/badge.svg)

ADPhoneMatcher — это Python-приложение для сопоставления телефонных номеров из CSV-выгрузки Active Directory (AD) с данными из других источников (`.csv` или `.txt`). Проект работает на чистом Python без сторонних библиотек, обрабатывает входные файлы, нормализует номера, создаёт выходные CSV с результатами, архивирует обработанные файлы и ведёт логирование.

## Основные возможности

- **Обработка AD-выгрузки**: Чтение CSV с настраиваемыми полями (`name`, `phone`, `email`, `active`) через `config.py`.
- **Поиск выгрузок**: Обработка `.csv` и `.txt` в папке `data/phone_data/`, исключая `data/results/` и `data/archive/`.
- **Нормализация номеров**: Удаление символов `+-() " "` (настраивается в `config.py`).
- **Обнаружение аномалий**: Проверка номеров в поле `telephoneNumber` на соответствие стандартам (цифровые номера длиной, заданной в `config.py`). Аномалии (например, наличие букв или неверная длина) записываются в лог `logs/anomalies_YYYY-MM-DD_HH-MM-SS.log`. Общее количество аномалий выводится в консоль.
- **Вывод**: CSV в `data/results/` с настраиваемыми полями (`phone`, `name`, `email`, `active`).
- **Логирование**:
  - Логи в `logs/log_YYYY-MM-DD_HH-MM-SS.log` (до 5 файлов, настраивается в `config.py`).
  - Консоль: относительные пути (`./data/ad_input/...`), `INFO` без `-v`, `DEBUG` с `-v`.
  - Лог: абсолютные пути (`[BASE_DIR]/...`), всегда `DEBUG`.
- **Архивирование**: Перемещение обработанных файлов в `data/archive/` с уникальными именами.
- **Права**: Выходные файлы и логи с правами `0o666`.
- **Производительность**: Обработка 1000 номеров за ~0.1 секунды.

## Требования

- Python 3.7+
- ОС: Linux (тестировалось в Astra Linux и Linux Mint)
- Podman (для контейнеризированного запуска)

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/SkyrocketStan/ADPhoneMatcher.git
   cd ADPhoneMatcher
   ```

2. Очистите старое виртуальное окружение (если существует):

   ```bash
   rm -rf .venv
   ```

3. Создайте необходимые папки:

   ```bash
   mkdir -p data/ad_input data/phone_data data/results data/archive logs
   ```

4. Убедитесь, что Podman установлен:

   ```bash
   podman --version
   ```

   Если Podman не установлен:

   ```bash
   sudo apt-get install podman  # Для Debian/Ubuntu-based систем
   ```

## Использование

### Вариант 1: Запуск с системным Python

1. Подготовьте входной файл (`data/ad_input/ad_input.csv`) с колонками, указанными в `config.py`:
   - `name` (имя пользователя)
   - `phone` (номера, разделённые `;` или `#`)
   - `email` (электронная почта)
   - `active` (True/False)

   Пример:

   ```plaintext
   name,phone,email,active
   Иванов Иван,123456;789012,ivanov.ivan@company.com,True
   ```

2. Поместите выгрузки (`.csv` или `.txt`) в `data/phone_data/`.

3. Запустите скрипт:

   ```bash
   python3 -m phone_matcher.main data/ad_input/ad_input.csv
   ```

   С флагом `-v` для подробного вывода:

   ```bash
   python3 -m phone_matcher.main data/ad_input/ad_input.csv -v
   ```

### Вариант 2: Запуск с Podman

1. Убедитесь, что входной файл `data/ad_input/ad_input.csv` существует (или укажите другое имя).

2. Запустите скрипт `run-podman.sh`:

   ```bash
   bash scripts/run-podman.sh [имя_файла.csv]
   ```

   Пример с другим файлом:

   ```bash
   bash scripts/run-podman.sh data/ad_input/my_ad_file.csv
   ```

   Скрипт:
   - Очищает `.venv/` (для продакшена).
   - Создаёт необходимые директории.
   - Запускает проект в контейнере Podman с Python 3.7.

3. Результаты:
   - CSV в `data/results/output_YYYY-MM-DD_HH-MM-SS.csv`
   - Логи в `logs/log_YYYY-MM-DD_HH-MM-SS.log`
   - Лог аномалий в `logs/anomalies_YYYY-MM-DD_HH-MM-SS.log` (если обнаружены аномалии)
   - Обработанные файлы в `data/archive/`

## Пример вывода

**Консоль** (с `-v`):

```plaintext
[2025-04-26 12:00:00] === Начало работы ===
[2025-04-26 12:00:00] Обработка файла: ./data/ad_input/ad_input.csv
[2025-04-26 12:00:00] Обнаружено аномалий в номерах AD: 3
[2025-04-26 12:00:00] Найдено уникальных номеров: 1000
[2025-04-26 12:00:00] Некорректный номер: содержит буквы
...
```

**Лог** (`logs/log_2025-04-26_12-00-00.log`):

```plaintext
[2025-04-26 12:00:00] === Начало работы ===
[2025-04-26 12:00:00] Обработка файла: /path/to/ADPhoneMatcher/data/ad_input/ad_input.csv
[2025-04-26 12:00:00] Обнаружено аномалий в номерах AD: 3
[2025-04-26 12:00:00] Некорректный номер: содержит буквы
...
```

**Лог аномалий** (`logs/anomalies_2025-04-26_12-00-00.log`):

```plaintext
[2025-04-26 12:00:00] Некорректный номер в строке: "Пользователь Иван Иванович";"XX123";"1-23-45";"Отдел ИТ";"False";;"ivan.ivanov@company.com"
[2025-04-26 12:00:00] Некорректный номер в строке: "Пользователь Анна Петрова";"12345";"2-34-56";"Отдел продаж";"True";;"anna.petрова@company.com"
```

**CSV** (`data/results/output_2025-04-26_12-00-00.csv`):

```plaintext
phone,name,email,active
123456,Иванов Иван,ivanov.ivan@company.com,True
...
```

## Тестирование

Проект включает юнит-тесты для всех основных модулей (`main`, `utils`, `output`, `parse_ad`, `parse_phone`, `match`) в директории `tests/`.

### Локальное тестирование

1. Установите зависимости для разработки:

   ```bash
   pip install pytest pylint
   ```

2. Запустите тесты:

   ```bash
   python3 -m unittest discover -s tests
   ```

3. Проверьте код с `pylint`:

   ```bash
   pylint phone_matcher/*.py tests/*.py
   ```

### Тестирование в Podman

1. Запустите скрипт `run-tests-podman.sh`:

   ```bash
   bash scripts/run-tests-podman.sh
   ```

   Скрипт устанавливает `pytest` и `pylint` в контейнере и запускает тесты и линтер.

Тесты покрывают критическую функциональность и обеспечивают оценку `pylint` 10/10.

## Структура проекта

```plaintext
ADPhoneMatcher/
├── logs/                    # Логи (log_YYYY-MM-DD_HH-MM-SS.log, anomalies_YYYY-MM-DD_HH-MM-SS.log)
├── phone_matcher/           # Пакет Python
│   ├── __init__.py         # Инициализация пакета
│   ├── main.py             # Точка входа
│   ├── utils.py            # Утилиты (логирование, пути)
│   ├── config.py           # Конфигурация
│   ├── parse_ad.py         # Парсинг входного файла
│   ├── normalize.py        # Нормализация номеров
│   ├── parse_phone.py      # Парсинг номеров
│   ├── output.py           # Формирование CSV
│   ├── match.py            # Сопоставление номеров
├── data/ad_input/           # Входной файл AD (например, ad_input.csv)
├── data/phone_data/         # Файлы выгрузок номеров (.csv, .txt)
├── data/results/            # Выходные CSV
├── data/archive/            # Архив обработанных файлов
├── tests/                   # Юнит-тесты
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_utils.py
│   ├── test_output.py
│   ├── test_parse_ad.py
│   ├── test_parse_phone.py
│   ├── test_match.py
├── docs/                    # Документация
│   ├── Technical_Specification.md  # Техническое задание
├── scripts/                 # Утилиты для развертывания
│   ├── pack_project.py     # Упаковка проекта
│   ├── pack_full_project.py # Полный листинг
│   ├── deploy.py           # Развёртывание
│   ├── run.sh              # Скрипт запуска
│   ├── run-podman.sh       # Запуск в Podman
│   ├── run-tests-podman.sh # Тесты в Podman
├── .gitignore               # Игнорируемые файлы
├── README.md                # Основная документация
├── LICENSE                  # Лицензия (MIT)
├── CHANGELOG.md             # История изменений
├── CONTRIBUTING.md          # Инструкции для контрибьюторов
```

## Утилиты для развертывания

В директории `scripts/` находятся:

- `pack_project.py`: Упаковывает файлы `phone_matcher/*.py` и `run.sh` в `project_files.txt`.
- `pack_full_project.py`: Создаёт полный листинг проекта в `full_project_files.txt`.
- `deploy.py`: Разворачивает проект, создавая `phone_matcher/` и `data/phone_data/`.
- `run.sh`: Запускает `main.py` с файлом `ad_input.csv`.
- `run-podman.sh`: Запускает проект в контейнере Podman.
- `run-tests-podman.sh`: Запускает тесты и линтер в Podman.

Использование:

1. Упаковка: `python3 scripts/pack_project.py`
2. Полный листинг: `python3 scripts/pack_full_project.py`
3. Копия `deploy.py`: `cp scripts/deploy.py deploy.txt`
4. Отправка: Перешлите `project_files.txt` и `deploy.txt`.
5. Развёртывание: `python3 deploy.py project_files.txt`
6. Запуск в Podman: `bash scripts/run-podman.sh [имя_файла.csv]`
7. Тесты в Podman: `bash scripts/run-tests-podman.sh`

## Лицензия

MIT License (см. `LICENSE`).

## Контакты

- Разработчик: Stanislav Rakitov
- Репозиторий: <https://github.com/SkyrocketStan/ADPhoneMatcher>
