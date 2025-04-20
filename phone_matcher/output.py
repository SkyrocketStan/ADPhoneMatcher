import csv
import os
from typing import List, Tuple
from . import config
from .utils import log_error, ensure_dir

def write_output_file(
    matches: List[Tuple[str, str, str, str]], output_file: str
) -> int:
    """Записывает итоговый CSV-файл с сортировкой.

    Args:
        matches: Список (номер, ФИО, email, Активный).
        output_file: Путь к итоговому файлу.

    Returns:
        Количество строк в файле (без заголовка).

    Raises:
        OSError: Если ошибка записи.
    """
    ensure_dir(os.path.dirname(output_file))
    temp_file = output_file + ".tmp"
    
    try:
        with open(temp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=config.OUTPUT_DELIMITER, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(config.OUTPUT_FIELDS)
            writer.writerows(matches)
        
        sorted_matches = sorted(matches, key=lambda x: x[0])
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=config.OUTPUT_DELIMITER, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(config.OUTPUT_FIELDS)
            writer.writerows(sorted_matches)
        
        os.remove(temp_file)
        os.chmod(output_file, config.FILE_PERMISSIONS)
        return len(matches)
    except Exception as e:
        log_error(f"Ошибка записи {output_file}: {e}")
        raise
