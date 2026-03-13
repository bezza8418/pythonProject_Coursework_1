"""
Модуль для сервисов анализа транзакций.
"""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """
    Простой поиск транзакций по описанию или категории.

    Args:
        transactions: Список словарей с транзакциями
        query: Строка для поиска

    Returns:
        JSON-строка с найденными транзакциями
    """
    if not transactions or not query:
        return json.dumps([], ensure_ascii=False)

    query_lower = query.lower()
    result = []

    for transaction in transactions:
        description = transaction.get("Описание", "").lower()
        category = transaction.get("Категория", "").lower()

        if query_lower in description or query_lower in category:
            result.append(transaction)

    logger.info(f"Поиск по запросу '{query}' нашел {len(result)} транзакций")
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)
