# pylint: disable=consider-using-with
import unittest
import tempfile
import os
import sys
import csv
from unittest.mock import patch
from phone_matcher.main import parse_arguments, process_ad_file, process_phone_files, write_results, main
from phone_matcher import config

class TestMain(unittest.TestCase):
    """Тесты для модуля main."""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_ad_file = os.path.join(self.temp_dir.name, "test_ad.csv")
        self.uploads_dir = os.path.join(self.temp_dir.name, "uploads")
        self.results_dir = os.path.join(self.temp_dir.name, "results")
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        with open(self.test_ad_file, "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.writer(file_handle, delimiter=config.AD_DELIMITER)
            writer.writerow(["DisplayName", "telephoneNumber", "mail", "Enabled"])
            writer.writerow(["Иванов Иван", "123456", "ivanov.ivan@company.com", "True"])
        with open(os.path.join(self.uploads_dir, "test.csv"), "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.writer(file_handle, delimiter=config.UPLOAD_DELIMITER)
            writer.writerow(["phone"])
            writer.writerow(["123456"])

    def test_parse_arguments(self):
        """Проверяет парсинг аргументов."""
        with patch.object(sys, "argv", ["main.py", "ad.csv", "-v", "--uploads-dir", "uploads"]):
            args = parse_arguments()
            self.assertEqual(args.ad_file, "ad.csv")
            self.assertTrue(args.verbose)
            self.assertEqual(args.uploads_dir, "uploads")

    def test_process_ad_file(self):
        """Проверяет обработку AD-файла."""
        ad_data = process_ad_file(self.test_ad_file)
        self.assertIn("123456", ad_data)
        self.assertEqual(ad_data["123456"][0][0], "Иванов Иван")

    def test_process_phone_files(self):
        """Проверяет обработку выгрузок."""
        with patch("phone_matcher.utils.move_file_to_archive"):
            phones = process_phone_files(self.uploads_dir)
            self.assertIn(("123456", os.path.join(self.uploads_dir, "test.csv")), phones)

    def test_write_results(self):
        """Проверяет запись результатов."""
        phones = [("123456", "source1")]
        ad_data = {"123456": [("Иванов Иван", "ivanov.ivan@company.com", "True")]}
        timestamp = "2025-04-26_13-05-56"
        matches = [("123456", "Иванов Иван", "ivanov.ivan@company.com", "True")]

        # Используем правильные пути для моков
        with patch("phone_matcher.main.match_phones", return_value=matches) as mock_match, \
            patch("phone_matcher.main.write_output_file", return_value=1) as mock_write, \
            patch("phone_matcher.main.log_info") as mock_log_info, \
            patch("phone_matcher.main.log_error"), \
            patch("phone_matcher.config.RESULTS_DIR", self.results_dir), \
            patch("phone_matcher.config.OUTPUT_FILE_PREFIX", "output"):

            write_results(phones, ad_data, timestamp)

            # Проверка вызова match_phones
            mock_match.assert_called_once_with(phones, ad_data)

            # Проверка вызова write_output_file
            expected_output = os.path.join(self.results_dir, f"{timestamp}_output.csv")
            mock_write.assert_called_once_with(matches, expected_output)

            # Проверка логирования
            mock_log_info.assert_any_call("Найдено совпадений с номерами AD: 1")
            mock_log_info.assert_any_call(f"Результат сохранён в {expected_output}")

    def test_main_no_parameters(self):
        """Проверяет запуск без параметров."""
        with patch.object(sys, "argv", ["main.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)

    def tearDown(self):
        self.temp_dir.cleanup()
