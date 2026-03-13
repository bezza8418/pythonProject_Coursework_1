"""
Тесты для модуля views.
"""

import json
from unittest.mock import patch  # только patch

import pandas as pd

from src.views import main_page


class TestMainPage:
    """Тесты для функции main_page."""

    @patch("src.views.pd.read_excel")
    @patch("src.views.get_currencies_rates")
    @patch("src.views.get_stocks_prices")
    @patch("src.views.load_user_settings")
    def test_main_page_success(self, mock_load_settings, mock_get_stocks, mock_get_currencies, mock_read_excel):
        """Тест успешного выполнения main_page."""
        # Настройка моков
        mock_load_settings.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}

        mock_get_currencies.return_value = [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]

        mock_get_stocks.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "GOOGL", "price": 2742.39}]

        # Создаем тестовый DataFrame
        test_data = {
            "Дата операции": ["01.03.2024", "15.03.2024", "20.03.2024"],
            "Сумма платежа": [-1000, -500, 2000],
            "Категория": ["Еда", "Транспорт", "Зарплата"],
            "Номер карты": [1234567890123456, 1234567890123456, None],
            "Описание": ["Продукты", "Такси", "Зарплата"],
        }
        mock_read_excel.return_value = pd.DataFrame(test_data)

        # Вызываем функцию
        result = main_page("2024-03-20 15:30:00")

        # Проверяем результат
        assert isinstance(result, str)
        data = json.loads(result)

        assert "greeting" in data
        assert data["greeting"] == "Добрый день"
        assert "cards" in data
        assert "top_transactions" in data
        assert "currency_rates" in data
        assert "stock_prices" in data

        # Проверяем, что моки вызывались
        mock_read_excel.assert_called_once()
        mock_load_settings.assert_called_once()
        mock_get_currencies.assert_called_once_with(["USD", "EUR"])
        mock_get_stocks.assert_called_once_with(["AAPL", "GOOGL"])

    @patch("src.views.pd.read_excel")
    def test_main_page_file_not_found(self, mock_read_excel):
        """Тест обработки ошибки отсутствия файла."""
        mock_read_excel.side_effect = FileNotFoundError()

        result = main_page("2024-03-20 15:30:00")
        data = json.loads(result)

        assert "error" in data
        assert "Файл с данными не найден" in data["error"]

    def test_main_page_invalid_date_format(self):
        """Тест обработки неверного формата даты."""
        result = main_page("20.03.2024 15:30:00")  # Неправильный формат
        data = json.loads(result)

        assert "error" in data
        assert "Неверный формат даты" in data["error"]
