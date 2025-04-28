import argparse
import os
import time
import sys
from datetime import datetime
from . import config
from .utils import setup_anomaly_logger, setup_logger, log_info, log_error, find_phone_files, move_file_to_archive
from .parse_ad import parse_ad_file
from .parse_phone import parse_phone_file
from .match import match_phones
from .output import write_output_file

def parse_arguments():
    """Парсит аргументы командной строки.

    Returns:
        Объект аргументов.
    """
    parser = argparse.ArgumentParser(description="Сопоставление номеров телефонов с данными AD")
    parser.add_argument("ad_file", help="Путь к файлу AD")
    parser.add_argument("-v", "--verbose", action="store_true", help="Подробный вывод")
    parser.add_argument("--uploads-dir", default=config.UPLOADS_DIR, help="Папка с файлами выгрузок")
    return parser.parse_args()

def process_ad_file(ad_file: str) -> dict:
    """Обрабатывает AD-файл.

    Args:
        ad_file: Путь к файлу AD.

    Returns:
        Словарь данных AD.

    Raises:
        IOError, OSError: Если файл не удаётся прочитать.
    """
    ad_file_path = os.path.abspath(ad_file)
    if not os.path.exists(ad_file_path):
        log_error(f"Ошибка: входной файл {ad_file} не найден")
        log_info("=== Работа завершена с ошибкой ===")
        sys.exit(1)

    log_info(f"Обработка AD файла: {ad_file}")
    ad_data, anomaly_count = parse_ad_file(ad_file)
    log_info(f"Найдено уникальных номеров в AD: {len(ad_data)}")
    if anomaly_count > 0:
        log_info(f"Обнаружено аномалий в номерах AD: {anomaly_count}")
    return ad_data

def process_phone_files(uploads_dir: str) -> list:
    """Обрабатывает файлы выгрузки.

    Args:
        uploads_dir: Папка с файлами выгрузки.

    Returns:
        Список номеров телефонов.
    """
    phone_files = find_phone_files(config.EXCLUDE_DIRS, uploads_dir)
    log_info(f"Найдено файлов с номерами: {len(phone_files)}")
    if not phone_files:
        log_error(f"Файлы выгрузки не найдены в {uploads_dir}. Завершение работы.")
        log_info("=== Работа завершена ===")
        sys.exit(1)

    phones = []
    total_phone_lines = 0
    for phone_file in phone_files:
        try:
            file_phones = parse_phone_file(phone_file)
            phones.extend(file_phones)
            total_phone_lines += len(file_phones)
            log_info(f"Извлечено {len(file_phones)} номеров из {phone_file}")
            move_file_to_archive(phone_file, config.ARCHIVE_DIR)
        except (IOError, OSError, ValueError) as exc:
            log_error(f"Ошибка обработки {phone_file}: {exc}")
            continue

    log_info(f"Общее количество номеров в файлах выгрузки: {total_phone_lines}")
    return phones

def write_results(phones: list, ad_data: dict, timestamp: str):
    """Сопоставляет номера, записывает результаты и логирует статистику.

    Args:
        phones: Список номеров.
        ad_data: Данные AD.
        timestamp: Метка времени для имени файла.
    """
    if not phones:
        log_error("Не найдено номеров в выгрузках")
        return

    matches = match_phones(phones, ad_data)
    matched_count = sum(1 for m in matches if m[1] or m[2] or m[3])
    unmatched_count = len(matches) - matched_count
    log_info(f"Найдено совпадений с номерами AD: {matched_count}")
    log_info(f"Номеров без совпадений в AD: {unmatched_count}")

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
    except (IOError, PermissionError) as exc:
        log_error(f"Ошибка записи результата: {exc}")

def main():
    """Основная функция скрипта."""
    start_time = time.time()
    args = parse_arguments()
    setup_logger(args.verbose)
    setup_anomaly_logger()
    log_info("=== Начало работы ===")

    try:
        phones = process_phone_files(args.uploads_dir)
        ad_data = process_ad_file(args.ad_file)
        timestamp = datetime.now().strftime(config.DATE_FORMAT)
        write_results(phones, ad_data, timestamp)
    except (IOError, OSError) as exc:
        log_error(f"Ошибка обработки: {exc}")
        log_info("=== Работа завершена с ошибкой ===")
        sys.exit(1)

    execution_time = int(time.time() - start_time)
    log_info(f"Общее время выполнения: {execution_time} секунд")
    log_info("=== Работа завершена ===")

if __name__ == "__main__":
    main()
