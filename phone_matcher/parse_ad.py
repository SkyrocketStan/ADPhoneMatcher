import csv
from typing import Dict, List, Tuple, Optional
from . import config
from .utils import log_error, log_verbose
from .normalize import normalize_phone

def parse_ad_file(ad_file: str, verbose: bool) -> Dict[str, List[Tuple[str, str, str]]]:
    """Читает файл AD и создаёт словарь номеров.

    Args:
        ad_file: Путь к файлу AD.
        verbose: Включить расширенное логирование.

    Returns:
        Словарь {номер: [(ФИО, email, Enabled), ...]}.

    Raises:
        FileNotFoundError: Если файл AD не найден.
        ValueError: Если формат AD некорректен.
    """
    ad_data = {}
    
    for encoding in config.ENCODINGS:
        try:
            with open(ad_file, newline='', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=config.AD_DELIMITER, quoting=csv.QUOTE_ALL)
                header = next(reader, None)
                if header is None:
                    log_error(f"Файл AD пуст: {ad_file}")
                    raise ValueError("Некорректный формат AD")
                
                header = [field.strip().strip('\ufeff').strip('"') for field in header]
                log_verbose(f"Заголовок AD: {header}")
                
                required_fields = [config.AD_FIELDS['display_name'], config.AD_FIELDS['phone'], 
                                 config.AD_FIELDS['email'], config.AD_FIELDS['enabled']]
                if not all(field in header for field in required_fields):
                    log_error(f"Некорректный заголовок в AD: {ad_file}, ожидалось: {required_fields}, получено: {header}")
                    raise ValueError("Некорректный формат AD")
                
                for row in reader:
                    if len(row) < len(required_fields):
                        log_verbose(f"Пропущена строка в AD: {row}")
                        continue
                    display_name = row[header.index(config.AD_FIELDS['display_name'])]
                    phones = row[header.index(config.AD_FIELDS['phone'])]
                    email = row[header.index(config.AD_FIELDS['email'])]
                    enabled = row[header.index(config.AD_FIELDS['enabled'])]
                    
                    if not phones:
                        continue
                    
                    phone_list = [phones]
                    for delimiter in config.AD_PHONE_DELIMITERS:
                        if delimiter in phones:
                            phone_list = phones.split(delimiter)
                            break
                    
                    for phone in phone_list:
                        if not phone.strip():
                            log_verbose(f"Пустой номер в AD: {row}")
                            continue
                        norm_phone = normalize_phone(phone, is_ad=True)
                        if not norm_phone:
                            log_verbose(f"Некорректный номер в AD: {phone}")
                            continue
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
        except Exception as e:
            log_error(f"Ошибка чтения AD {ad_file}: {e}")
            raise
    log_error(f"Не удалось прочитать {ad_file} ни в одной кодировке")
    raise ValueError("Невозможно декодировать файл AD")
