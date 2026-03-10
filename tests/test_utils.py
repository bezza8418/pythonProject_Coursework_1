"""
Тесты для вспомогательных функций.
"""

import json
from datetime import datetime

import pandas as pd
import pytest

from src.utils import get_greeting, load_user_settings, get_transactions_for_period, calculate_cards_info

class TestGetGreeting:
    """Тесты для функции get_greeting."""

    @pytest.mark.parametrize("hour, expected", [
        (6, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (4, "Доброй ночи"),
    ])
    def test_greeting_by_hour(self, hour, expected):
        """Тест приветствия в разное время суток."""
        dt = datetime(2024, 1, 1, hour, 0, 0)
        assert get_greeting(dt) == expected


class TestLoadUserSettings:
    """Тесты для функции load_user_settings."""

    def test_load_settings_returns_dict(self):
        """Тест, что функция возвращает словарь с нужными ключами."""
        settings = load_user_settings()

        assert isinstance(settings, dict)
        assert "user_currencies" in settings
        assert "user_stocks" in settings

    def test_load_settings_currencies_is_list(self):
        """Тест, что валюты возвращаются в виде списка."""
        settings = load_user_settings()
        assert isinstance(settings["user_currencies"], list)

    def test_load_settings_stocks_is_list(self):
        """Тест, что акции возвращаются в виде списка."""
        settings = load_user_settings()
        assert isinstance(settings["user_stocks"], list)

    def test_load_settings_default_values(self):
        """Тест, что возвращаются значения по умолчанию."""
        settings = load_user_settings()

        # Проверяем, что списки не пустые
        assert len(settings["user_currencies"]) > 0
        assert len(settings["user_stocks"]) > 0

        # Проверяем наличие ожидаемых значений
        assert "USD" in settings["user_currencies"] or "EUR" in settings["user_currencies"]
        assert "AAPL" in settings["user_stocks"] or "GOOGL" in settings["user_stocks"]

    def test_load_settings_without_file_returns_defaults(self, monkeypatch):
        """Тест, что при отсутствии файла возвращаются настройки по умолчанию."""

        # Мокаем open, чтобы вызвать FileNotFoundError
        def mock_open(*args, **kwargs):
            raise FileNotFoundError()

        monkeypatch.setattr("builtins.open", mock_open)

        settings = load_user_settings()
        assert "user_currencies" in settings
        assert "user_stocks" in settings
        assert len(settings["user_currencies"]) > 0

    def test_load_settings_with_invalid_json_returns_defaults(self, monkeypatch, tmp_path):
        """Тест, что при битом JSON возвращаются настройки по умолчанию."""
        # Создаем временный файл с битым JSON
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        # Мокаем open, чтобы вернуть наш битый файл
        original_open = open

        def mock_open(*args, **kwargs):
            if args[0] == "user_settings.json":
                return original_open(invalid_file, *args[1:], **kwargs)
            return original_open(*args, **kwargs)

        monkeypatch.setattr("builtins.open", mock_open)

        settings = load_user_settings()
        assert "user_currencies" in settings
        assert "user_stocks" in settings
        assert len(settings["user_currencies"]) > 0


class TestGetTransactionsForPeriod:
    """Тесты для функции get_transactions_for_period."""

    @pytest.fixture
    def sample_df(self):
        """Фикстура с тестовыми транзакциями."""
        data = {
            'Дата операции': ['01.03.2024', '15.03.2024', '20.03.2024', '01.04.2024'],
            'Сумма операции': [100, 200, 300, 400],
            'Категория': ['Еда', 'Транспорт', 'Еда', 'Развлечения']
        }
        return pd.DataFrame(data)

    def test_filter_by_month(self, sample_df):
        """Тест фильтрации за март 2024."""
        result = get_transactions_for_period(sample_df, datetime(2024, 3, 20))

        assert len(result) == 3  # Только мартовские транзакции
        assert result.iloc[0]['Сумма операции'] == 100
        assert result.iloc[1]['Сумма операции'] == 200
        assert result.iloc[2]['Сумма операции'] == 300

    def test_filter_empty_result(self, sample_df):
        """Тест фильтрации, когда нет транзакций за период."""
        result = get_transactions_for_period(sample_df, datetime(2023, 1, 1))

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)


class TestCalculateCardsInfo:
    """Тесты для функции calculate_cards_info."""

    @pytest.fixture
    def sample_df_with_cards(self):
        """Фикстура с тестовыми транзакциями по картам."""
        data = {
            'Номер карты': [1234567890123456, 1234567890123456, 9876543210987654, 9876543210987654],
            'Сумма платежа': [-1500, -2300, -800, 5000],  # 5000 - поступление, не расход
            'Категория': ['Супермаркеты', 'Рестораны', 'Транспорт', 'Пополнение']
        }
        return pd.DataFrame(data)

    def test_calculate_cards_info(self, sample_df_with_cards):
        """Тест расчета информации по картам."""
        result = calculate_cards_info(sample_df_with_cards)

        # Должно быть 2 карты
        assert len(result) == 2

        # Первая карта
        card1 = next(c for c in result if c['last_digits'] == '3456')
        assert card1['total_spent'] == 3800  # 1500 + 2300
        assert card1['cashback'] == 38.0  # 3800 / 100

        # Вторая карта
        card2 = next(c for c in result if c['last_digits'] == '7654')
        assert card2['total_spent'] == 800  # только расход -800
        assert card2['cashback'] == 8.0  # 800 / 100
