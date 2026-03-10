"""
Модуль для генерации JSON-ответов для веб-страниц.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd

from src.external_api import get_currencies_rates, get_stocks_prices
from src.utils import (
    get_greeting,
    load_user_settings,
    get_transactions_for_period,
    calculate_cards_info,
    get_top_transactions
)

logger = logging.getLogger(__name__)


def main_page(date_str: str) -> str:
    """
    Главная страница. Возвращает JSON с данными для отображения.

    Args:
        date_str: Строка с датой и временем в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        JSON-строка с данными
    """
    try:
        # Парсим дату
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        logger.info(f"Главная страница вызвана с датой: {dt}")

        # Загружаем настройки пользователя
        settings = load_user_settings()

        # Загружаем транзакции из Excel
        df = pd.read_excel("data/operations.xlsx")

        # Фильтруем транзакции за нужный период
        df_filtered = get_transactions_for_period(df, dt)

        # Формируем ответ
        response = {
            "greeting": get_greeting(dt),
            "cards": calculate_cards_info(df_filtered),
            "top_transactions": get_top_transactions(df_filtered),
            "currency_rates": get_currencies_rates(settings["user_currencies"]),
            "stock_prices": get_stocks_prices(settings["user_stocks"])
        }

        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка в main_page: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
