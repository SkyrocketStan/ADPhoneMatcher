# pylint: disable=consider-using-with
import unittest
import tempfile
import os
import csv
from phone_matcher.parse_phone import parse_phone_file
from phone_matcher import config

class TestParsePhone(unittest.TestCase):
    """Тесты для модуля parse_phone."""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_csv = os.path.join(self.temp_dir.name, "test.csv")
        self.test_txt = os.path.join(self.temp_dir.name, "test.txt")
        with open(self.test_csv, "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.writer(file_handle, delimiter=config.UPLOAD_DELIMITER)
            writer.writerow(["phone"])
            writer.writerow(["123456"])
        with open(self.test_txt, "w", encoding="utf-8") as file_handle:
            file_handle.write("123456\n")

    def test_parse_csv(self):
        """Проверяет парсинг CSV-выгрузки."""
        phones = parse_phone_file(self.test_csv)
        self.assertEqual(len(phones), 1)
        self.assertIn(("123456", self.test_csv), phones)

    def test_parse_txt(self):
        """Проверяет парсинг TXT-выгрузки."""
        phones = parse_phone_file(self.test_txt)
        self.assertEqual(len(phones), 1)
        self.assertIn(("123456", self.test_txt), phones)

    def tearDown(self):
        self.temp_dir.cleanup()
