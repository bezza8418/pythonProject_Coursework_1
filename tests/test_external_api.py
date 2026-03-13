"""
Тесты для модуля external_api.
"""

# import pytest
from unittest.mock import MagicMock, patch

from requests.exceptions import RequestException

from src.external_api import get_currencies_rates, get_currency_rate, get_stock_price, get_stocks_prices


class TestGetCurrencyRate:
    """Тесты для функции get_currency_rate."""

    @patch("src.external_api.requests.get")
    def test_get_currency_rate_success(self, mock_get):
        """Тест успешного получения курса валюты."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"USD": 0.0124}}
        mock_get.return_value = mock_response

        result = get_currency_rate("USD")
        assert result == 0.0124

    @patch("src.external_api.requests.get")
    def test_get_currency_rate_no_api_key(self, mock_get, monkeypatch):
        """Тест при отсутствии API ключа."""
        monkeypatch.setenv("EXCHANGE_RATES_API_KEY", "")
        result = get_currency_rate("USD")
        assert result is None
        mock_get.assert_not_called()

    @patch("src.external_api.requests.get")
    def test_get_currency_rate_request_exception(self, mock_get):
        """Тест при ошибке запроса."""
        mock_get.side_effect = RequestException("Connection error")
        result = get_currency_rate("USD")
        assert result is None

    @patch("src.external_api.requests.get")
    def test_get_currency_rate_invalid_response(self, mock_get):
        """Тест при некорректном ответе API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = get_currency_rate("USD")
        assert result is None


class TestGetStockPrice:
    """Тесты для функции get_stock_price."""

    @patch("src.external_api.requests.get")
    def test_get_stock_price_success(self, mock_get):
        """Тест успешного получения цены акции."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Global Quote": {"05. price": "255.76"}}
        mock_get.return_value = mock_response

        result = get_stock_price("AAPL")
        assert result == 255.76

    @patch("src.external_api.requests.get")
    def test_get_stock_price_no_api_key(self, mock_get, monkeypatch):
        """Тест при отсутствии API ключа."""
        monkeypatch.setenv("STOCK_API_KEY", "")
        result = get_stock_price("AAPL")
        assert result is None
        mock_get.assert_not_called()

    @patch("src.external_api.requests.get")
    def test_get_stock_price_request_exception(self, mock_get):
        """Тест при ошибке запроса."""
        mock_get.side_effect = RequestException("Connection error")
        result = get_stock_price("AAPL")
        assert result is None

    @patch("src.external_api.requests.get")
    def test_get_stock_price_invalid_response(self, mock_get):
        """Тест при некорректном ответе API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = get_stock_price("AAPL")
        assert result is None


class TestGetCurrenciesRates:
    """Тесты для функции get_currencies_rates."""

    @patch("src.external_api.get_currency_rate")
    def test_get_currencies_rates_success(self, mock_get_rate):
        """Тест получения курсов нескольких валют."""
        mock_get_rate.side_effect = [0.0124, 0.0108]

        result = get_currencies_rates(["USD", "EUR"])

        assert len(result) == 2
        assert result[0]["currency"] == "USD"
        assert result[0]["rate"] == 0.0124
        assert result[1]["currency"] == "EUR"
        assert result[1]["rate"] == 0.0108

    @patch("src.external_api.get_currency_rate")
    def test_get_currencies_rates_with_none(self, mock_get_rate):
        """Тест когда часть курсов не получена."""
        mock_get_rate.side_effect = [0.0124, None]

        result = get_currencies_rates(["USD", "EUR"])

        assert len(result) == 1
        assert result[0]["currency"] == "USD"


class TestGetStocksPrices:
    """Тесты для функции get_stocks_prices."""

    @patch("src.external_api.get_stock_price")
    def test_get_stocks_prices_success(self, mock_get_price):
        """Тест получения цен нескольких акций."""
        mock_get_price.side_effect = [255.76, 303.55]

        result = get_stocks_prices(["AAPL", "GOOGL"])

        assert len(result) == 2
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] == 255.76
        assert result[1]["stock"] == "GOOGL"
        assert result[1]["price"] == 303.55

    @patch("src.external_api.get_stock_price")
    def test_get_stocks_prices_with_none(self, mock_get_price):
        """Тест когда часть цен не получена."""
        mock_get_price.side_effect = [255.76, None]

        result = get_stocks_prices(["AAPL", "GOOGL"])

        assert len(result) == 1
        assert result[0]["stock"] == "AAPL"
