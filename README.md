# ADPhoneMatcher

ADPhoneMatcher — это Python-приложение для сопоставления телефонных номеров из CSV-выгрузки Active Directory (AD) с данными из других источников (`.csv` или `.txt`). Проект работает на чистом Python без сторонних библиотек, обрабатывает входные файлы, нормализует номера, создаёт выходные CSV с результатами, архивирует обработанные файлы и ведёт логирование.

## Основные возможности

- **Обработка AD-выгрузки**: Чтение CSV с настраиваемыми полями (`name`, `phone`, `email`, `active`) через `config.py`.
- **Поиск выгрузок**: Обработка `.csv` и `.txt` в папке `input/`, исключая `output/` и `archive/`.
- **Нормализация номеров**: Удаление символов `+-() " "` (настраивается в `config.py`).
- **Вывод**: CSV в `output/` с настраиваемыми полями (`phone`, `name`, `email`, `active`).
- **Логирование**:
  - Логи в `logs/log_YYYY-MM-DD_HH-MM-SS.log` (до 5 файлов, настраивается в `config.py`).
  - Консоль: относительные пути (`./input/...`), `INFO` без `-v`, `DEBUG` с `-v`.
  - Лог: абсолютные пути (`[BASE_DIR]/...`), всегда `DEBUG`.
- **Архивирование**: Перемещение обработанных файлов в `archive/` с уникальными именами.
- **Права**: Выходные файлы и логи с правами `0o666`.
- **Производительность**: Обработка `[N]` номеров за 0 секунд.

## Требования

- Python 3.7+
- ОС: Linux (тестировалось в Astra Linux и Linux Mint)

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/SkyrocketStan/ADPhoneMatcher.git
   cd ADPhoneMatcher
   ```

2. Создайте необходимые папки:

   ```bash
   mkdir -p input output archive logs
   ```

## Использование

1. Подготовьте входной файл (`input.csv`) с колонками, указанными в `config.py`:
   - `name` (имя пользователя)
   - `phone` (номера, разделённые `;` или `#`)
   - `email` (электронная почта)
   - `active` (True/False)

   Пример:

   ```
   name,phone,email,active
   [NAME],[PHONE];[PHONE2],[EMAIL],True
   ```

2. Поместите выгрузки (`.csv` или `.txt`) в `input/`.

3. Запустите скрипт:

   ```bash
   python3 -m phone_matcher.main input.csv
   ```

   С флагом `-v` для подробного вывода:

   ```bash
   python3 -m phone_matcher.main input.csv -v
   ```

4. Результаты:
   - CSV в `output/output_YYYY-MM-DD_HH-MM-SS.csv`
   - Логи в `logs/log_YYYY-MM-DD_HH-MM-SS.log`
   - Обработанные файлы в `archive/`

## Пример вывода

**Консоль** (с `-v`):

```
[2025-04-20 12:00:00] === Начало работы ===
[2025-04-20 12:00:00] Обработка файла: input.csv
[2025-04-20 12:00:00] Найдено уникальных номеров: [N]
[2025-04-20 12:00:00] Некорректный номер: [INVALID_REASON]
...
```

**Лог** (`logs/log_2025-04-20_12-00-00.log`):

```
[2025-04-20 12:00:00] === Начало работы ===
[2025-04-20 12:00:00] Обработка файла: [BASE_DIR]/input.csv
[2025-04-20 12:00:00] Некорректный номер: [INVALID_REASON]
...
```

**CSV** (`output/output_2025-04-20_12-00-00.csv`):

```
phone,name,email,active
[PHONE],[NAME],[EMAIL],True
...
```

## Структура проекта

```
ADPhoneMatcher/
├── logs/                    # Логи (log_YYYY-MM-DD_HH-MM-SS.log)
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
├── input/                   # Входные выгрузки
├── output/                  # Выходные CSV
├── archive/                 # Архив обработанных файлов
├── docs/                    # Документация
│   ├── Technical_Specification.md  # Техническое задание
├── scripts/                 # Утилиты для развертывания
├── .gitignore               # Игнорируемые файлы
├── README.md                # Основная документация
├── LICENSE                  # Лицензия (MIT)
├── CHANGELOG.md             # История изменений
├── CONTRIBUTING.md          # Инструкции для контрибьюторов
├── run.sh                   # Скрипт запуска
```

## Утилиты для развертывания

В директории `scripts/` находятся:
- `pack_project.py`: Упаковывает файлы `phone_matcher/*.py` и `run.sh` в `project_files.txt`.
- `deploy.py`: Разворачивает проект, создавая `phone_matcher/` и `uploads/`.
- `run.sh`: Запускает `main.py` с файлом `ad_input.csv`.

Использование:
1. Упаковка: `python3 scripts/pack_project.py`
2. Копия `deploy.py`: `cp scripts/deploy.py deploy.txt`
3. Отправка: Перешлите `project_files.txt` и `deploy.txt`.
4. Развёртывание: `python3 deploy.py project_files.txt`


## Лицензия

MIT License (см. `LICENSE`).

## Контакты

- Разработчик: Stanislav Rakitov
- Репозиторий: <https://github.com/SkyrocketStan/ADPhoneMatcher>
