import os
from datetime import datetime

# Кодировки
ENCODINGS = ['utf-8-sig', 'utf-8', 'windows-1251']

# Разделители
AD_DELIMITER = ';'  # Разделитель полей в AD-файле
AD_PHONE_DELIMITERS = [';', '#']  # Разделители номеров в telephoneNumber
UPLOAD_DELIMITER = ','  # Разделитель в файлах выгрузки
OUTPUT_DELIMITER = ','  # Разделитель в выходном CSV

# Поля
AD_FIELDS = {
    'display_name': 'DisplayName',
    'phone': 'telephoneNumber',
    'email': 'mail',
    'enabled': 'Enabled'
}
UPLOAD_PHONE_FIELDS = ['number', 'phone', 'f_extension']  # Возможные имена столбцов с номерами в выгрузках
OUTPUT_FIELDS = ['Номер', 'ФИО', 'email', 'Активный']  # Имена полей в выходном CSV

# Символы для нормализации
NORMALIZE_CHARS = set('+-() " ')  # Удаляемые символы при нормализации

# Длина валидного номера телефона
VALID_PHONE_NUMBER_LENGTH = 6

# Директории
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'data', 'ad_input')
UPLOADS_DIR = os.path.join(BASE_DIR, 'data', 'phone_data')
RESULTS_DIR = os.path.join(BASE_DIR, 'data', 'results')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'data', 'archive')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
EXCLUDE_DIRS = [RESULTS_DIR, ARCHIVE_DIR]  # Исключаемые папки при поиске выгрузок

# Логи
LOG_FILE = os.path.join(LOGS_DIR, f"matcher_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
LOG_FORMAT = '[%(asctime)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MAX_LOGS = 5   # Максимальное количество логов в папке logs

# Выходной файл
OUTPUT_FILE_PREFIX = 'output'
DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'
FILE_PERMISSIONS = 0o666  # Права на выходной CSV
