"""
Тесты для модуля services.
"""

import json
import pytest

from src.services import simple_search


class TestSimpleSearch:
    """Тесты для функции simple_search."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                'Дата операции': '01.03.2024',
                'Сумма платежа': -1500,
                'Категория': 'Супермаркеты',
                'Описание': 'Пятерочка'
            },
            {
                'Дата операции': '02.03.2024',
                'Сумма платежа': -500,
                'Категория': 'Транспорт',
                'Описание': 'Яндекс.Такси'
            },
            {
                'Дата операции': '03.03.2024',
                'Сумма платежа': -200,
                'Категория': 'Фастфуд',
                'Описание': 'KFC'
            },
            {
                'Дата операции': '04.03.2024',
                'Сумма платежа': -3000,
                'Категория': 'Супермаркеты',
                'Описание': 'Перекресток'
            }
        ]

    def test_search_by_description(self, sample_transactions):
        """Тест поиска по описанию."""
        result = simple_search(sample_transactions, "Пятерочка")
        data = json.loads(result)

        assert len(data) == 1
        assert data[0]['Категория'] == 'Супермаркеты'
        assert data[0]['Описание'] == 'Пятерочка'

    def test_search_by_category(self, sample_transactions):
        """Тест поиска по категории."""
        result = simple_search(sample_transactions, "Супермаркеты")
        data = json.loads(result)

        assert len(data) == 2
        assert all(t['Категория'] == 'Супермаркеты' for t in data)

    def test_search_case_insensitive(self, sample_transactions):
        """Тест регистронезависимого поиска."""
        result = simple_search(sample_transactions, "ПЯТЕРОЧКА")
        data = json.loads(result)

        assert len(data) == 1
        assert data[0]['Описание'] == 'Пятерочка'

    def test_search_no_results(self, sample_transactions):
        """Тест поиска без результатов."""
        result = simple_search(sample_transactions, "несуществующий запрос")
        data = json.loads(result)

        assert data == []

    def test_search_empty_query(self, sample_transactions):
        """Тест с пустым запросом."""
        result = simple_search(sample_transactions, "")
        data = json.loads(result)

        assert data == []

    def test_search_empty_transactions(self):
        """Тест с пустым списком транзакций."""
        result = simple_search([], "тест")
        data = json.loads(result)

        assert data == []
