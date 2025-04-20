import argparse
import os
import time
import sys
from datetime import datetime
from . import config
from .utils import setup_logger, log_info, log_error, find_phone_files, move_file_to_archive
from .parse_ad import parse_ad_file
from .parse_phone import parse_phone_file
from .match import match_phones
from .output import write_output_file

def main():
    """Основная функция скрипта."""
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Сопоставление номеров телефонов с данными AD")
    parser.add_argument("ad_file", help="Путь к файлу AD")
    parser.add_argument("-v", "--verbose", action="store_true", help="Подробный вывод")
    parser.add_argument("--uploads-dir", default=config.UPLOADS_DIR, help="Папка с файлами выгрузок")
    args = parser.parse_args()

    setup_logger(args.verbose, config.LOG_FILE)
    log_info("=== Начало работы ===")

    # Проверка существования входного файла
    ad_file_path = os.path.abspath(args.ad_file)
    if not os.path.exists(ad_file_path):
        log_error(f"Ошибка: входной файл {args.ad_file} не найден")
        log_info("=== Работа завершена с ошибкой ===")
        sys.exit(1)

    log_info(f"Обработка AD файла: {args.ad_file}")

    phone_files = find_phone_files(config.EXCLUDE_DIRS, args.uploads_dir)
    log_info(f"Найдено файлов с номерами: {len(phone_files)}")
    if not phone_files:
        log_error(f"Файлы выгрузки не найдены в {args.uploads_dir}")
        return

    try:
        ad_data = parse_ad_file(args.ad_file, args.verbose)
        log_info(f"Найдено уникальных номеров в AD: {len(ad_data)}")
    except Exception as e:
        log_error(f"Ошибка обработки AD: {e}")
        return

    phones = []
    total_phone_lines = 0
    for phone_file in phone_files:
        try:
            file_phones = parse_phone_file(phone_file, args.verbose)
            phones.extend(file_phones)
            total_phone_lines += len(file_phones)
            log_info(f"Извлечено {len(file_phones)} номеров из {phone_file}")
            move_file_to_archive(phone_file, config.ARCHIVE_DIR)
        except Exception as e:
            log_error(f"Ошибка обработки {phone_file}: {e}")
            continue

    if not phones:
        log_error("Не найдено номеров в выгрузках")
        return

    log_info(f"Общее количество номеров в файлах выгрузки: {total_phone_lines}")
    matches = match_phones(phones, ad_data)

    matched_count = sum(1 for m in matches if m[1] or m[2] or m[3])
    unmatched_count = len(matches) - matched_count
    log_info(f"Найдено совпадений с номерами AD: {matched_count}")
    log_info(f"Номеров без совпадений в AD: {unmatched_count}")

    timestamp = datetime.now().strftime(config.DATE_FORMAT)
    output_file = os.path.join(config.RESULTS_DIR, f"{timestamp}_{config.OUTPUT_FILE_PREFIX}.csv")
    try:
        count = write_output_file(matches, output_file)
        unique_phones = len(set(phone for phone, _ in phones))
        extra_rows = count - unique_phones
        log_msg = f"Количество строк в итоговом файле: {count}"
        if extra_rows > 0:
            log_msg += f" (включая {extra_rows} дополнительные строки из-за дубликатов в AD)"
        log_info(log_msg)
        log_info(f"Результат сохранён в {output_file}")
    except Exception as e:
        log_error(f"Ошибка записи результата: {e}")

    execution_time = int(time.time() - start_time)
    log_info(f"Общее время выполнения: {execution_time} секунд")
    log_info("=== Работа завершена ===")

if __name__ == "__main__":
    main()