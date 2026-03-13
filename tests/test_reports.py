"""
Тесты для модуля reports.
"""

import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import report_decorator, spending_by_category


class TestSpendingByCategory:
    """Тесты для функции spending_by_category."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        data = {
            "Дата операции": [
                "01.01.2024",
                "15.01.2024",
                "01.02.2024",
                "15.02.2024",
                "01.03.2024",
                "15.03.2024",
                "01.04.2024",
            ],
            "Сумма платежа": [-1000, -500, -2000, -300, -1500, -700, -5000],
            "Категория": [
                "Супермаркеты",
                "Транспорт",
                "Супермаркеты",
                "Рестораны",
                "Супермаркеты",
                "Транспорт",
                "Супермаркеты",
            ],
            "Описание": ["Пятерочка", "Такси", "Ашан", "KFC", "Перекресток", "Метро", "Ozon"],
        }
        return pd.DataFrame(data)

    def test_filter_by_category(self, sample_transactions):
        """Тест фильтрации по категории."""
        result = spending_by_category(sample_transactions, "Супермаркеты", "2024-04-01")

        # Должны быть только за февраль, март, апрель (3 шт.)
        assert len(result) == 3
        assert all(result["Категория"] == "Супермаркеты")

        # Проверяем конкретные месяцы
        months = result["Дата операции"].dt.month.tolist()
        assert 2 in months  # февраль
        assert 3 in months  # март
        assert 4 in months  # апрель

    def test_filter_last_3_months(self, sample_transactions):
        """Тест фильтрации за последние 3 месяца."""
        result = spending_by_category(sample_transactions, "Супермаркеты", "2024-03-15")

        # Должны быть: 01.01, 01.02, 01.03 (3 шт.)
        assert len(result) == 3

        dates = result["Дата операции"].dt.strftime("%d.%m.%Y").tolist()
        assert "01.01.2024" in dates
        assert "01.02.2024" in dates
        assert "01.03.2024" in dates
        assert "01.04.2024" not in dates

    def test_no_transactions_in_period(self, sample_transactions):
        """Тест, когда нет транзакций за период."""
        result = spending_by_category(sample_transactions, "Рестораны", "2024-01-15")

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    @patch("src.reports.datetime")
    def test_default_date_today(self, mock_datetime, sample_transactions):
        """Тест с датой по умолчанию (сегодня)."""
        # Подменяем datetime.now()
        mock_datetime.now.return_value = datetime(2024, 3, 20)

        result = spending_by_category(sample_transactions, "Супермаркеты")

        assert len(result) == 3  # 01.01, 01.02, 01.03
        assert len(result) > 0

    def test_invalid_date_format(self, sample_transactions):
        """Тест с неверным форматом даты."""
        with pytest.raises(ValueError):
            spending_by_category(sample_transactions, "Супермаркеты", "01.04.2024")


class TestReportDecorator:
    """Тесты для декоратора отчетов."""

    def test_decorator_default_filename(self, tmp_path):
        """Тест декоратора с именем файла по умолчанию."""

        @report_decorator(output_dir=str(tmp_path))
        def test_func():
            return {"test": "data"}

        test_func()  # не сохраняем результат

        file_path = tmp_path / "test_func.json"
        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"test": "data"}

    def test_decorator_custom_filename(self, tmp_path):
        """Тест декоратора с пользовательским именем файла."""

        @report_decorator(filename="custom_report.json", output_dir=str(tmp_path))
        def test_func():
            return {"test": "data"}

        test_func()

        file_path = tmp_path / "custom_report.json"
        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"test": "data"}

    def test_decorator_with_dataframe(self, tmp_path):
        """Тест декоратора с DataFrame."""

        @report_decorator(output_dir=str(tmp_path))
        def test_func():
            return pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

        test_func()

        file_path = tmp_path / "test_func.json"
        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["col1"] == 1
        assert data[1]["col2"] == 4

    def test_decorator_with_list_data(self, tmp_path):
        """Тест декоратора со списком данных."""

        @report_decorator(output_dir=str(tmp_path))
        def test_func():
            return [1, 2, 3, 4, 5]

        test_func()

        file_path = tmp_path / "test_func.json"
        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == [1, 2, 3, 4, 5]

    def test_decorator_creates_output_dir(self, tmp_path):
        """Тест создания директории, если её нет."""
        output_dir = tmp_path / "custom_dir" / "nested"

        @report_decorator(output_dir=str(output_dir))
        def test_func():
            return {"test": "data"}

        test_func()

        file_path = output_dir / "test_func.json"
        assert file_path.exists()
        assert output_dir.exists()
