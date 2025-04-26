# pylint: disable=consider-using-with
import unittest
import tempfile
import os
import csv
from phone_matcher.parse_ad import parse_ad_file, validate_header, process_row
from phone_matcher import config

class TestParseAd(unittest.TestCase):
    """Тесты для модуля parse_ad."""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_ad_file = os.path.join(self.temp_dir.name, "test_ad.csv")
        with open(self.test_ad_file, "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.writer(file_handle, delimiter=config.AD_DELIMITER)
            writer.writerow(["DisplayName", "telephoneNumber", "mail", "Enabled"])
            writer.writerow(["Иванов Иван", "123456;789012", "ivanov.ivan@company.com", "True"])

    def test_validate_header(self):
        """Проверяет валидацию заголовка."""
        header = ["DisplayName", "telephoneNumber", "mail", "Enabled"]
        self.assertTrue(validate_header(header, self.test_ad_file))

    def test_process_row(self):
        """Проверяет обработку строки."""
        row = ["Иванов Иван", "123456;789012", "ivanov.ivan@company.com", "True"]
        header = ["DisplayName", "telephoneNumber", "mail", "Enabled"]
        result = process_row(row, header)
        self.assertEqual(len(result), 2)
        self.assertIn(("123456", "Иванов Иван", "ivanov.ivan@company.com", "True"), result)
        self.assertIn(("789012", "Иванов Иван", "ivanov.ivan@company.com", "True"), result)

    def test_parse_ad_file(self):
        """Проверяет парсинг AD-файла."""
        ad_data = parse_ad_file(self.test_ad_file)
        self.assertIn("123456", ad_data)
        self.assertIn("789012", ad_data)
        self.assertEqual(ad_data["123456"][0][0], "Иванов Иван")

    def tearDown(self):
        self.temp_dir.cleanup()
