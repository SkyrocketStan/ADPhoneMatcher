import logging
import os
import shutil
from typing import List
from . import config

def setup_logger(verbose: bool, log_file: str) -> None:
    """Настраивает логирование.

    Args:
        verbose: Включить подробные логи.
        log_file: Путь к файлу логов.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def log_info(message: str) -> None:
    """Логирует информационное сообщение."""
    logging.info(message)

def log_error(message: str) -> None:
    """Логирует ошибку."""
    logging.error(f"Ошибка: {message}")

def log_verbose(message: str) -> None:
    """Логирует подробное сообщение."""
    logging.debug(message)

def find_phone_files(exclude_dirs: List[str], start_dir: str = '.') -> List[str]:
    """Ищет файлы выгрузки (.csv, .txt).

    Args:
        exclude_dirs: Директории для исключения.
        start_dir: Начальная директория.

    Returns:
        Список путей к файлам.
    """
    phone_files = []
    exclude_dirs = [os.path.abspath(d) for d in exclude_dirs]
    
    for root, _, files in os.walk(start_dir):
        if any(os.path.abspath(root).startswith(d) for d in exclude_dirs):
            continue
        for file in files:
            if file.endswith(('.csv', '.txt')):
                phone_files.append(os.path.join(root, file))
    
    return sorted(phone_files)

def move_file_to_archive(file_path: str, archive_dir: str) -> None:
    """Перемещает файл в архив.

    Args:
        file_path: Путь к файлу.
        archive_dir: Директория архива.
    """
    try:
        ensure_dir(archive_dir)
        file_name = os.path.basename(file_path)
        archive_path = os.path.join(archive_dir, file_name)
        counter = 1
        base_name, ext = os.path.splitext(file_name)
        while os.path.exists(archive_path):
            archive_path = os.path.join(archive_dir, f"{base_name}_{counter}{ext}")
            counter += 1
        shutil.move(file_path, archive_path)
        log_info(f"Файл перемещён в архив: {file_path}")
    except Exception as e:
        log_error(f"Ошибка перемещения {file_path}: {e}")
        raise

def delete_file(file_path: str) -> None:
    """Удаляет файл.

    Args:
        file_path: Путь к файлу.
    """
    try:
        os.remove(file_path)
        log_info(f"Файл удалён: {file_path}")
    except Exception as e:
        log_error(f"Ошибка удаления {file_path}: {e}")
        raise

def ensure_dir(directory: str) -> None:
    """Создаёт директорию, если она не существует.

    Args:
        directory: Путь к директории.
    """
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
