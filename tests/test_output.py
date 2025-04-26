# pylint: disable=consider-using-with
import unittest
import tempfile
import os
import csv
from unittest.mock import patch
from phone_matcher.output import write_output_file
from phone_matcher import config

class TestOutput(unittest.TestCase):
    """Тесты для модуля output."""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_file = os.path.join(self.temp_dir.name, "output.csv")
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def test_write_output_file(self):
        """Проверяет запись выходного файла."""
        matches = [("123456", "Иванов Иван", "ivanov.ivan@company.com", "True")]
        with patch("phone_matcher.utils.ensure_dir"):
            count = write_output_file(matches, self.output_file)
            self.assertEqual(count, 1)
            with open(self.output_file, "r", encoding="utf-8") as file_handle:
                reader = csv.reader(file_handle, delimiter=config.OUTPUT_DELIMITER)
                header = next(reader)
                self.assertEqual(header, config.OUTPUT_FIELDS)
                rows = list(reader)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0], ["123456", "Иванов Иван", "ivanov.ivan@company.com", "True"])

    def tearDown(self):
        self.temp_dir.cleanup()
