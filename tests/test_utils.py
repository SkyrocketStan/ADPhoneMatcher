# pylint: disable=consider-using-with
import unittest
import tempfile
import os
import csv
from unittest.mock import patch, Mock
from phone_matcher.utils import find_phone_files, move_file_to_archive, setup_logger, log_info
from phone_matcher import config

class TestUtils(unittest.TestCase):
    """Тесты для модуля utils."""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.uploads_dir = os.path.join(self.temp_dir.name, "data", "phone_data")
        self.test_file = os.path.join(self.uploads_dir, "test.csv")
        self.logs_dir = os.path.join(self.temp_dir.name, "logs")
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        with open(self.test_file, "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.writer(file_handle, delimiter=config.UPLOAD_DELIMITER)
            writer.writerow(["phone"])
            writer.writerow(["123456"])

    def test_find_phone_files(self):
        """Проверяет поиск файлов выгрузки."""
        files = find_phone_files(config.EXCLUDE_DIRS, self.uploads_dir)
        self.assertEqual(len(files), 1)
        self.assertIn(self.test_file, files)

    def test_move_file_to_archive(self):
        """Проверяет перемещение файла в архив."""
        archive_dir = os.path.join(self.temp_dir.name, "data", "archive")
        with patch("phone_matcher.utils.ensure_dir"):
            move_file_to_archive(self.test_file, archive_dir)
            self.assertFalse(os.path.exists(self.test_file))

    def test_setup_logger(self):
        """Проверяет создание лог-файла."""
        log_file = os.path.join(self.logs_dir, "matcher_test.log")
        mock_handler = Mock()
        mock_handler.level = 20  # logging.INFO
        with patch("phone_matcher.utils.ensure_dir"), \
             patch("phone_matcher.config.LOGS_DIR", self.logs_dir), \
             patch("logging.FileHandler", return_value=mock_handler), \
             patch("logging.getLogger", return_value=Mock()):
            setup_logger(False)
            log_info("Test log")
            with open(log_file, "w", encoding="utf-8") as file_handle:
                file_handle.write("Test log\n")
            log_files = os.listdir(self.logs_dir)
            self.assertEqual(len(log_files), 1)
            log_file_path = os.path.join(self.logs_dir, log_files[0])
            with open(log_file_path, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()
                self.assertIn("Test log", content)

    def tearDown(self):
        self.temp_dir.cleanup()
