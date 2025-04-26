import unittest
from phone_matcher.match import match_phones

class TestMatch(unittest.TestCase):
    """Тесты для модуля match."""
    def test_match_phones(self):
        """Проверяет сопоставление номеров."""
        phones = [("123456", "source1")]
        ad_data = {
            "123456": [("Иванов Иван", "ivanov.ivan@company.com", "True")]
        }
        matches = match_phones(phones, ad_data)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], ("123456", "Иванов Иван", "ivanov.ivan@company.com", "True"))

    def test_no_match(self):
        """Проверяет отсутствие совпадений."""
        phones = [("987654", "source1")]
        ad_data = {
            "123456": [("Иванов Иван", "ivanov.ivan@company.com", "True")]
        }
        matches = match_phones(phones, ad_data)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], ("987654", "", "", ""))
