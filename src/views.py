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
        try:
            df = pd.read_excel("data/operations.xlsx")
            logger.info(f"Загружено {len(df)} транзакций")
        except FileNotFoundError:
            logger.error("Файл data/operations.xlsx не найден")
            return json.dumps({"error": "Файл с данными не найден"}, ensure_ascii=False)

        # Фильтруем транзакции за нужный период
        df_filtered = get_transactions_for_period(df, dt)
        logger.info(f"Отфильтровано {len(df_filtered)} транзакций за период")

        # Формируем ответ
        response = {
            "greeting": get_greeting(dt),
            "cards": calculate_cards_info(df_filtered),
            "top_transactions": get_top_transactions(df_filtered),
            "currency_rates": get_currencies_rates(settings["user_currencies"]),
            "stock_prices": get_stocks_prices(settings["user_stocks"])
        }

        return json.dumps(response, ensure_ascii=False, indent=2, default=str)

    except ValueError as e:
        logger.error(f"Ошибка формата даты: {e}")
        return json.dumps({"error": f"Неверный формат даты: {e}"}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Неожиданная ошибка в main_page: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
