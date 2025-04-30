import logging
import os
import glob
import shutil
from datetime import datetime
from typing import List
from . import config

class RelativePathFormatter(logging.Formatter):
    """Форматирует сообщения, заменяя абсолютные пути на относительные для консоли."""
    def format(self, record):
        message = record.msg
        base_dir = config.BASE_DIR
        for word in message.split():
            if os.path.isabs(word):
                rel_path = os.path.relpath(word, base_dir)
                message = message.replace(word, f"./{rel_path}")
        record.msg = message
        return super().format(record)

def manage_log_files(logs_dir: str, log_file: str) -> None:
    """Удаляет самые старые лог-файлы, чтобы осталось не более config.MAX_LOGS."""
    os.makedirs(logs_dir, exist_ok=True)
    log_files = sorted(glob.glob(os.path.join(logs_dir, "matcher_*.log")), key=os.path.getmtime)
    if log_file not in log_files:
        log_files.append(log_file)
    if len(log_files) >= config.MAX_LOGS:
        for old_log in log_files[:-config.MAX_LOGS]:
            try:
                if old_log != log_file:
                    os.remove(old_log)
            except (OSError, PermissionError) as exc:
                logging.getLogger().error("Ошибка удаления старого лога %s: %s", old_log, exc)

def setup_logger(verbose: bool) -> None:
    """Настраивает логгер для вывода в консоль и файл."""
    logs_dir = config.LOGS_DIR
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(logs_dir, f"matcher_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = []

    os.makedirs(logs_dir, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    manage_log_files(logs_dir, log_file)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = RelativePathFormatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

def setup_anomaly_logger() -> None:
    """Настраивает логгер для аномалий."""
    logger = logging.getLogger("anomaly")
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
        logger.removeHandler(handler)
    logger.handlers = []
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logs_dir = config.LOGS_DIR
    timestamp = datetime.now().strftime(config.DATE_FORMAT)
    log_file = os.path.join(logs_dir, f"anomalies_{timestamp}.log")
    os.makedirs(logs_dir, exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] Некорректный номер в строке: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    os.chmod(log_file, config.FILE_PERMISSIONS)

def ensure_dir(directory: str) -> None:
    """Создаёт директорию, если она не существует."""
    os.makedirs(directory, exist_ok=True)

def log_info(message: str) -> None:
    """Логирует сообщение уровня INFO."""
    logging.getLogger().info(message)

def log_error(message: str) -> None:
    """Логирует сообщение уровня ERROR."""
    logging.getLogger().error(message)

def log_verbose(message: str) -> None:
    """Логирует сообщение уровня DEBUG."""
    logging.getLogger().debug(message)

def log_anomaly(message: str) -> None:
    """Логирует аномалию."""
    logging.getLogger("anomaly").info(message)

def find_phone_files(exclude_dirs: List[str], uploads_dir: str) -> List[str]:
    """Находит файлы .csv и .txt в uploads_dir, исключая exclude_dirs."""
    phone_files = []
    for ext in ["*.csv", "*.txt"]:
        files = glob.glob(os.path.join(uploads_dir, ext))
        for file in files:
            if not any(os.path.abspath(file).startswith(os.path.abspath(d)) for d in exclude_dirs):
                phone_files.append(os.path.abspath(file))
    return phone_files

def move_file_to_archive(file_path: str, archive_dir: str) -> None:
    """Перемещает файл в архив с уникальным именем."""
    os.makedirs(archive_dir, exist_ok=True)
    base_name = os.path.basename(file_path)
    dest_path = os.path.join(archive_dir, base_name)
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(base_name)
        dest_path = os.path.join(archive_dir, f"{name}_{counter}{ext}")
        counter += 1
    try:
        shutil.move(file_path, dest_path)
        log_info(f"Файл перемещён в архив: {file_path}")
    except (OSError, PermissionError) as exc:
        log_error(f"Ошибка перемещения файла {file_path} в архив: {exc}")
