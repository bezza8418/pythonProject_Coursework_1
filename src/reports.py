"""
Модуль для отчетов по транзакциям.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None, output_dir: Optional[str] = None) -> Callable:
    """
    Декоратор для функций-отчетов. Сохраняет результат в JSON-файл в папке data/.

    Args:
        filename: Имя файла для сохранения (если не указано, используется имя функции)
        output_dir: Директория для сохранения (по умолчанию data/ в корне проекта)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Определяем имя файла
            output_file = filename or f"{func.__name__}.json"

            # Определяем директорию для сохранения
            if output_dir is None:
                # По умолчанию - папка data в корне проекта
                data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            else:
                data_dir = output_dir

            os.makedirs(data_dir, exist_ok=True)

            # Полный путь к файлу
            file_path = os.path.join(data_dir, output_file)

            # Сохраняем результат
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(result, pd.DataFrame):
                    json.dump(result.to_dict(orient="records"), f, ensure_ascii=False, indent=2, default=str)
                else:
                    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"Отчет сохранен в файл {file_path}")
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Название категории
        date: Опциональная дата отсчета (формат 'YYYY-MM-DD')

    Returns:
        DataFrame с отфильтрованными транзакциями
    """
    # Определяем дату отсчета
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d")

    # Начало периода (3 месяца назад)
    start_date = end_date - timedelta(days=90)

    # Преобразуем даты в DataFrame
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    # Фильтруем по категории и дате
    mask = (
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    )

    result = transactions[mask].copy()
    logger.info(f"Найдено {len(result)} транзакций по категории '{category}' за последние 3 месяца")

    return result
