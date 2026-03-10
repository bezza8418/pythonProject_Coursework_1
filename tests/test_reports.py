"""
Тесты для модуля reports.
"""

import json
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest

from src.reports import spending_by_category, report_decorator


class TestSpendingByCategory:
    """Тесты для функции spending_by_category."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        data = {
            'Дата операции': [
                '01.01.2024', '15.01.2024', '01.02.2024', '15.02.2024',
                '01.03.2024', '15.03.2024', '01.04.2024'
            ],
            'Сумма платежа': [-1000, -500, -2000, -300, -1500, -700, -5000],
            'Категория': [
                'Супермаркеты', 'Транспорт', 'Супермаркеты', 'Рестораны',
                'Супермаркеты', 'Транспорт', 'Супермаркеты'
            ],
            'Описание': [
                'Пятерочка', 'Такси', 'Ашан', 'KFC',
                'Перекресток', 'Метро', 'Ozon'
            ]
        }
        return pd.DataFrame(data)

    def test_filter_by_category(self, sample_transactions):
        """Тест фильтрации по категории."""
        result = spending_by_category(sample_transactions, 'Супермаркеты', '2024-04-01')

        # Должны быть только за февраль, март, апрель (3 шт.)
        assert len(result) == 3
        assert all(result['Категория'] == 'Супермаркеты')

        # Проверяем конкретные месяцы
        months = result['Дата операции'].dt.month.tolist()
        assert 2 in months  # февраль
        assert 3 in months  # март
        assert 4 in months  # апрель

    def test_filter_last_3_months(self, sample_transactions):
        """Тест фильтрации за последние 3 месяца."""
        result = spending_by_category(sample_transactions, 'Супермаркеты', '2024-03-15')

        # Должны быть: 01.01, 01.02, 01.03 (3 шт.)
        assert len(result) == 3

        dates = result['Дата операции'].dt.strftime('%d.%m.%Y').tolist()
        assert '01.01.2024' in dates
        assert '01.02.2024' in dates
        assert '01.03.2024' in dates
        assert '01.04.2024' not in dates

    def test_no_transactions_in_period(self, sample_transactions):
        """Тест, когда нет транзакций за период."""
        result = spending_by_category(sample_transactions, 'Рестораны', '2024-01-15')

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    @patch('src.reports.datetime')
    def test_default_date_today(self, mock_datetime, sample_transactions):
        """Тест с датой по умолчанию (сегодня)."""
        # Подменяем datetime.now()
        mock_datetime.now.return_value = datetime(2024, 3, 20)

        result = spending_by_category(sample_transactions, 'Супермаркеты')

        assert len(result) == 3  # 01.01, 01.02, 01.03
        assert len(result) > 0

    def test_invalid_date_format(self, sample_transactions):
        """Тест с неверным форматом даты."""
        with pytest.raises(ValueError):
            spending_by_category(sample_transactions, 'Супермаркеты', '01.04.2024')


class TestReportDecorator:
    """Тесты для декоратора отчетов."""

    @patch('builtins.open', new_callable=MagicMock)
    def test_decorator_default_filename(self, mock_open):
        """Тест декоратора с именем файла по умолчанию."""

        @report_decorator()
        def test_func():
            return {"test": "data"}

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = test_func()

        mock_open.assert_called_once_with("test_func.json", 'w', encoding='utf-8')
        # Проверяем, что write вызывался хотя бы один раз
        assert mock_file.write.called
        # Или проверяем, что количество вызовов > 0
        assert mock_file.write.call_count > 0

    @patch('builtins.open', new_callable=MagicMock)
    def test_decorator_custom_filename(self, mock_open):
        """Тест декоратора с пользовательским именем файла."""

        @report_decorator(filename="custom_report.json")
        def test_func():
            return {"test": "data"}

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = test_func()

        mock_open.assert_called_once_with("custom_report.json", 'w', encoding='utf-8')
        # Проверяем, что write вызывался хотя бы один раз
        assert mock_file.write.called
        assert mock_file.write.call_count > 0

    @patch('builtins.open', new_callable=MagicMock)
    def test_decorator_with_dataframe(self, mock_open):
        """Тест декоратора с DataFrame."""

        @report_decorator()
        def test_func():
            return pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = test_func()

        mock_open.assert_called_once()
        assert mock_file.write.called
        assert mock_file.write.call_count > 0

