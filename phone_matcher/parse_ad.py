import csv
from typing import Dict, List, Tuple

from . import config
from .normalize import normalize_phone
from .utils import log_error, log_verbose


# noinspection SpellCheckingInspection
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


def process_row(row: List[str], header: List[str]) -> List[Tuple[str, str, str, str]]:
    """Обрабатывает строку CSV и возвращает данные.

    Args:
        row: Строка CSV.
        header: Заголовок CSV.

    Returns:
        Список кортежей (номер, ФИО, email, enabled).
    """
    if len(row) < len(config.AD_FIELDS):
        log_verbose(f"Пропущена строка в AD: {row}")
        return []

    display_name = row[header.index(config.AD_FIELDS['display_name'])]
    phones = row[header.index(config.AD_FIELDS['phone'])]
    email = row[header.index(config.AD_FIELDS['email'])]
    enabled = row[header.index(config.AD_FIELDS['enabled'])]

    if not phones:
        return []

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
        if not norm_phone:
            log_verbose(f"Некорректный номер в AD: {phone}")
            continue
        result.append((norm_phone, display_name, email, enabled))

    return result


def parse_ad_file(ad_file: str) -> Dict[str, List[Tuple[str, str, str]]]:
    """Читает файл AD и создаёт словарь номеров.

    Args:
        ad_file: Путь к файлу AD.

    Returns:
        Словарь {номер: [(ФИО, email, Enabled), ...]}.

    Raises:
        FileNotFoundError: Если файл AD не найден.
        ValueError: Если формат AD некорректен.
    """
    ad_data = {}

    for encoding in config.ENCODINGS:
        try:
            with open(ad_file, newline='', encoding=encoding) as file_handle:
                reader = csv.reader(file_handle, delimiter=config.AD_DELIMITER, quoting=csv.QUOTE_ALL)
                header = validate_header(next(reader, None), ad_file)

                for row in reader:
                    for norm_phone, display_name, email, enabled in process_row(row, header):
                        if norm_phone not in ad_data:
                            ad_data[norm_phone] = []
                        ad_data[norm_phone].append((display_name, email, enabled))

                return ad_data
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
