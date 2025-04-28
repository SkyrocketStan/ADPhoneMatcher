import csv
from typing import Dict, List, Tuple

from . import config
from .normalize import normalize_phone
from .utils import log_error, log_verbose, log_anomaly


def validate_header(header: List[str], ad_file: str) -> List[str]:
    """Проверяет и нормализует заголовок CSV.

    Args:
        header: Список полей заголовка.
        ad_file: Путь к файлу AD.

    Returns:
        Нормализованный заголовок.

    Raises:
        ValueError: Если заголовок некорректен.
    """
    if header is None:
        log_error(f"Файл AD пуст: {ad_file}")
        raise ValueError("Некорректный формат AD")

    header = [field.strip().strip('\ufeff').strip('"') for field in header]
    log_verbose(f"Заголовок AD: {header}")

    required_fields = [
        config.AD_FIELDS['display_name'],
        config.AD_FIELDS['phone'],
        config.AD_FIELDS['email'],
        config.AD_FIELDS['enabled']
    ]
    if not all(field in header for field in required_fields):
        log_error(f"Некорректный заголовок в AD: {ad_file}, ожидалось: {required_fields}, получено: {header}")
        raise ValueError("Некорректный формат AD")

    return header


def process_row(row: List[str], header: List[str]) -> Tuple[List[Tuple[str, str, str, str]], int]:
    """Обрабатывает строку CSV и возвращает данные и количество аномалий.

    Args:
        row: Строка CSV.
        header: Заголовок CSV.

    Returns:
        Кортеж: (список кортежей (номер, ФИО, email, enabled), количество аномалий).
    """
    anomaly_count = 0
    if len(row) < len(config.AD_FIELDS):
        log_verbose(f"Пропущена строка в AD: {row}")
        return [], anomaly_count

    display_name = row[header.index(config.AD_FIELDS['display_name'])]
    phones = row[header.index(config.AD_FIELDS['phone'])]
    email = row[header.index(config.AD_FIELDS['email'])]
    enabled = row[header.index(config.AD_FIELDS['enabled'])]

    row_str = f'"{display_name}";"{phones}";"{email}";"{enabled}"'

    if not phones:
        return [], anomaly_count

    phone_list = [phones]
    for delimiter in config.AD_PHONE_DELIMITERS:
        if delimiter in phones:
            phone_list = phones.split(delimiter)
            break

    result = []
    for phone in phone_list:
        if not phone.strip():
            log_verbose(f"Пустой номер в AD: {row}")
            continue
        norm_phone = normalize_phone(phone)
        if not norm_phone or len(norm_phone) < config.VALID_PHONE_NUMBER_LENGTH:
            log_anomaly(row_str)
            anomaly_count += 1
            continue
        result.append((norm_phone, display_name, email, enabled))

    return result, anomaly_count


def parse_ad_file(ad_file: str) -> Tuple[Dict[str, List[Tuple[str, str, str]]], int]:
    """Читает файл AD и создаёт словарь номеров с количеством аномалий.

    Args:
        ad_file: Путь к файлу AD.

    Returns:
        Кортеж: (словарь {номер: [(ФИО, email, Enabled), ...]}, общее количество аномалий).

    Raises:
        FileNotFoundError: Если файл AD не найден.
        ValueError: Если формат AD некорректен.
    """
    ad_data = {}
    total_anomaly_count = 0

    for encoding in config.ENCODINGS:
        try:
            with open(ad_file, newline='', encoding=encoding) as file_handle:
                reader = csv.reader(file_handle, delimiter=config.AD_DELIMITER, quoting=csv.QUOTE_ALL)
                header = validate_header(next(reader, None), ad_file)

                for row in reader:
                    row_data, anomaly_count = process_row(row, header)
                    total_anomaly_count += anomaly_count
                    for norm_phone, display_name, email, enabled in row_data:
                        if norm_phone not in ad_data:
                            ad_data[norm_phone] = []
                        ad_data[norm_phone].append((display_name, email, enabled))

                return ad_data, total_anomaly_count
        except UnicodeDecodeError:
            log_verbose(f"Ошибка кодировки {encoding} в {ad_file}, пробую следующую")
            continue
        except FileNotFoundError:
            log_error(f"Файл AD не найден: {ad_file}")
            raise
        except Exception as exc:
            log_error(f"Ошибка чтения AD {ad_file}: {exc}")
            raise

    log_error(f"Не удалось прочитать {ad_file} ни в одной кодировке")
    raise ValueError("Невозможно декодировать файл AD")
