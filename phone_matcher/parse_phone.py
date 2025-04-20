import csv
from typing import List, Tuple
from . import config
from .utils import log_error, log_verbose
from .normalize import normalize_phone

def parse_phone_file(phone_file: str, verbose: bool) -> List[Tuple[str, str]]:
    """Читает файл выгрузки и извлекает номера.

    Args:
        phone_file: Путь к файлу выгрузки.
        verbose: Включить расширенное логирование.

    Returns:
        Список кортежей (номер, имя_файла).

    Raises:
        FileNotFoundError: Если файл не найден.
    """
    phones = []
    
    for encoding in config.ENCODINGS:
        try:
            with open(phone_file, newline='', encoding=encoding) as f:
                if phone_file.endswith('.txt'):
                    lines = f.readlines()
                    for line in lines:
                        phone = line.strip()
                        if not phone:
                            log_verbose(f"Пустая строка в {phone_file}")
                            continue
                        norm_phone = normalize_phone(phone, is_ad=False)
                        if not norm_phone:
                            log_verbose(f"Некорректный номер в {phone_file}: {phone}")
                            continue
                        phones.append((norm_phone, phone_file))
                    return phones
                
                reader = csv.reader(f, delimiter=config.UPLOAD_DELIMITER, quoting=csv.QUOTE_MINIMAL)
                header = next(reader, None)
                if header is None:
                    log_verbose(f"Файл выгрузки пуст: {phone_file}")
                    return phones
                
                phone_col_idx = None
                for idx, field in enumerate(header):
                    if field.lower() in [f.lower() for f in config.UPLOAD_PHONE_FIELDS]:
                        phone_col_idx = idx
                        break
                
                if phone_col_idx is None:
                    log_verbose(f"Столбец с номерами не найден в {phone_file}, читаем первый столбец")
                    f.seek(0)
                    reader = csv.reader(f, delimiter=config.UPLOAD_DELIMITER, quoting=csv.QUOTE_MINIMAL)
                    next(reader, None)
                    phone_col_idx = 0
                
                for row in reader:
                    if not row or not row[phone_col_idx]:
                        log_verbose(f"Пустая строка в {phone_file}")
                        continue
                    phone = row[phone_col_idx].strip()
                    norm_phone = normalize_phone(phone, is_ad=False)
                    if not norm_phone:
                        log_verbose(f"Некорректный номер в {phone_file}: {phone}")
                        continue
                    phones.append((norm_phone, phone_file))
                return phones
        except UnicodeDecodeError:
            log_verbose(f"Ошибка кодировки {encoding} в {phone_file}, пробую следующую")
            continue
        except FileNotFoundError:
            log_error(f"Файл выгрузки не найден: {phone_file}")
            raise
        except Exception as e:
            log_error(f"Ошибка чтения {phone_file}: {e}")
            raise
    log_error(f"Не удалось прочитать {phone_file} ни в одной кодировке")
    return phones
