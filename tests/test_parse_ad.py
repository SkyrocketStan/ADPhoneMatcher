# pylint: disable=consider-using-with
import unittest
import tempfile
import os
import csv
import glob
from unittest.mock import patch
from phone_matcher.parse_ad import parse_ad_file, validate_header, process_row
from phone_matcher import config
from phone_matcher.utils import setup_anomaly_logger

class TestParseAd(unittest.TestCase):
    """Тесты для модуля parse_ad."""
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_ad_file = os.path.join(self.temp_dir.name, "test_ad.csv")
        self.logs_dir = os.path.join(self.temp_dir.name, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        with open(self.test_ad_file, "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.writer(file_handle, delimiter=config.AD_DELIMITER, quoting=csv.QUOTE_ALL)
            writer.writerow(["DisplayName", "telephoneNumber", "mail", "Enabled"])
            writer.writerow(["Иванов Иван", "123456;789012", "ivanov.ivan@company.com", "True"])
            writer.writerow(["Петрова Анна", "XX123;12345", "anna.petрова@company.com", "False"])
            writer.writerow(["Сидоров Петр", "", "petr.sidorov@company.com", "True"])

    def test_validate_header(self):
        """Проверяет валидацию заголовка."""
        header = ["DisplayName", "telephoneNumber", "mail", "Enabled"]
        result = validate_header(header, self.test_ad_file)
        self.assertEqual(result, header)

    def test_process_row(self):
        """Проверяет обработку строки."""
        row = ["Иванов Иван", "123456;789012", "ivanov.ivan@company.com", "True"]
        header = ["DisplayName", "telephoneNumber", "mail", "Enabled"]
        with patch("phone_matcher.parse_ad.log_anomaly") as mock_log_anomaly:
            result, anomaly_count = process_row(row, header)
            self.assertEqual(len(result), 2)
            self.assertIn(("123456", "Иванов Иван", "ivanov.ivan@company.com", "True"), result)
            self.assertIn(("789012", "Иванов Иван", "ivanov.ivan@company.com", "True"), result)
            self.assertEqual(anomaly_count, 0)
            mock_log_anomaly.assert_not_called()

    def test_process_row_with_anomalies(self):
        """Проверяет обработку строки с аномалиями."""
        row = ["Петрова Анна", "XX123;12345", "anna.petрова@company.com", "False"]
        header = ["DisplayName", "telephoneNumber", "mail", "Enabled"]
        row_str = '"Петрова Анна";"XX123;12345";"anna.petрова@company.com";"False"'
        with patch("phone_matcher.parse_ad.log_anomaly") as mock_log_anomaly:
            result, anomaly_count = process_row(row, header)
            self.assertEqual(len(result), 0)
            self.assertEqual(anomaly_count, 2)
            mock_log_anomaly.assert_any_call(row_str)
            self.assertEqual(mock_log_anomaly.call_count, 2)

    def test_process_row_empty_phone(self):
        """Проверяет обработку строки с пустым номером."""
        row = ["Сидоров Петр", "", "petr.sidorov@company.com", "True"]
        header = ["DisplayName", "telephoneNumber", "mail", "Enabled"]
        with patch("phone_matcher.parse_ad.log_anomaly") as mock_log_anomaly:
            result, anomaly_count = process_row(row, header)
            self.assertEqual(len(result), 0)
            self.assertEqual(anomaly_count, 0)
            mock_log_anomaly.assert_not_called()

    def test_parse_ad_file(self):
        """Проверяет парсинг AD-файла и создание лога аномалий."""
        with patch("phone_matcher.config.LOGS_DIR", self.logs_dir):
            setup_anomaly_logger()
            ad_data, anomaly_count = parse_ad_file(self.test_ad_file)
            self.assertIn("123456", ad_data)
            self.assertIn("789012", ad_data)
            self.assertEqual(ad_data["123456"][0][0], "Иванов Иван")
            self.assertEqual(anomaly_count, 2)
            anomaly_logs = glob.glob(os.path.join(self.logs_dir, "anomalies_*.log"))
            self.assertEqual(len(anomaly_logs), 1)
            with open(anomaly_logs[0], "r", encoding="utf-8") as log_file:
                log_content = log_file.read()
                self.assertIn('Некорректный номер в строке: "Петрова Анна";"XX123;12345";"anna.petрова@company.com";"False"', log_content)

    def tearDown(self):
        self.temp_dir.cleanup()
