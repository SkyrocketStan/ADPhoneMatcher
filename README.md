# Phone Matcher

Скрипт для сопоставления номеров телефонов из выгрузок с данными Active Directory (AD).

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone <repository_url>
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd phone_matcher
   ```
3. (Опционально) Установите зависимости, если появятся:
   ```bash
   pip3 install -r requirements.txt
   ```

## Использование

1. Подготовьте файл AD (`ad_data.csv`) и поместите его в корень проекта.
2. Запустите скрипт с помощью `python3`:
   ```bash
   python3 phone_matcher/main.py ad_data.csv
   ```
3. Для подробного вывода используйте флаг `-v`:
   ```bash
   python3 phone_matcher/main.py -v ad_data.csv
   ```
4. Укажите альтернативную папку выгрузок:
   ```bash
   python3 phone_matcher/main.py --uploads-dir imports/ ad_data.csv
   ```
5. Для запуска всех тестов с генерацией больших данных (80,000 записей AD, 5,000 выгрузок):
   ```bash
   python3 test_phone_matcher.py
   ```

**Заметка**: Используйте `python3`, так как на некоторых системах (например, Ubuntu, Mint) команда `python` может быть недоступна или указывать на Python 2. Если вы видите ошибку `Command 'python' not found`, убедитесь, что установлен пакет `python3` (`sudo apt install python3`).

## Конфигурация

Настройки находятся в `phone_matcher/config.py`. Основные параметры:
- `PHONE_UPLOADS_DIR`: Папка с файлами выгрузок (`phones/`).
- `RESULTS_DIR`: Папка для результатов (`results/`).
- `PHONE_NUMBER_HEADER_NAMES`: Возможные заголовки столбцов с номерами (`["f_extension", "number", "phone"]`).
- `LOG_FILE`: Файл лога (`phone_matcher.log`).

## Тестирование

Для проверки скрипта на больших данных:
```bash
python3 test_phone_matcher.py
```

Это создаст временные файлы:
- AD: ~80,000 записей.
- Выгрузки: ~5,000 номеров (CSV и TXT).
- Проверит итоговый CSV и лог.

Модульные тесты находятся в `tests/` и проверяют отдельные компоненты.
