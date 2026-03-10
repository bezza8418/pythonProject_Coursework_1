"""
Вспомогательные функции для обработки транзакций.
"""

import json
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd


def get_greeting(dt: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        dt: Объект datetime с текущим временем

    Returns:
        "Доброе утро", "Добрый день", "Добрый вечер" или "Доброй ночи"
    """
    hour = dt.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает настройки пользователя из файла user_settings.json.

    Returns:
        Словарь с настройками: {"user_currencies": [...], "user_stocks": [...]}
    """
    default_settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    }

    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)

        # Проверяем, что настройки имеют нужную структуру
        if "user_currencies" not in settings:
            settings["user_currencies"] = default_settings["user_currencies"]
        if "user_stocks" not in settings:
            settings["user_stocks"] = default_settings["user_stocks"]

        return settings
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не найден или битый, возвращаем настройки по умолчанию
        return default_settings


def get_transactions_for_period(df: pd.DataFrame, target_date: datetime) -> pd.DataFrame:
    """
    Фильтрует транзакции за период с начала месяца до целевой даты.

    Args:
        df: DataFrame с транзакциями (должен содержать колонку 'Дата операции')
        target_date: Целевая дата

    Returns:
        Отфильтрованный DataFrame
    """
    # Убеждаемся, что колонка с датой в правильном формате
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)

    # Начало месяца
    start_of_month = datetime(target_date.year, target_date.month, 1)

    # Фильтруем
    mask = (df['Дата операции'] >= start_of_month) & (df['Дата операции'] <= target_date)

    return df[mask].copy()


def calculate_cards_info(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Рассчитывает информацию по картам: последние цифры, расходы, кешбэк.

    Args:
        df: DataFrame с транзакциями (должен содержать колонки 'Номер карты' и 'Сумма платежа')

    Returns:
        Список словарей с информацией по каждой карте
    """
    # Группируем по картам
    cards_info = []

    # Получаем уникальные карты (игнорируем пустые значения)
    cards = df['Номер карты'].dropna().unique()

    for card in cards:
        # Фильтруем транзакции по карте (только расходы, не поступления)
        card_transactions = df[
            (df['Номер карты'] == card) &
            (df['Сумма платежа'] < 0)  # Расходы - отрицательные суммы
            ]

        total_spent = abs(card_transactions['Сумма платежа'].sum())
        cashback = round(total_spent / 100, 2)  # 1 рубль на каждые 100 рублей

        cards_info.append({
            "last_digits": str(int(card))[-4:],  # Последние 4 цифры
            "total_spent": round(total_spent, 2),
            "cashback": cashback
        })

    return cards_info
