"""
Модуль для работы с внешними API (валюты и акции).
"""

import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def get_currency_rate(currency: str) -> Optional[float]:
    """
    Получает текущий курс валюты к рублю.

    Args:
        currency: Код валюты (USD, EUR и т.д.)

    Returns:
        Курс валюты или None при ошибке
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        return None

    url = f"https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": api_key}
    params = {"base": "RUB", "symbols": currency}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {}).get(currency)
    except (requests.RequestException, KeyError, ValueError):
        return None


def get_stock_price(symbol: str) -> Optional[float]:
    """
    Получает текущую цену акции.

    Args:
        symbol: Тикер акции (AAPL, GOOGL и т.д.)

    Returns:
        Цена акции или None при ошибке
    """
    api_key = os.getenv("STOCK_API_KEY")
    if not api_key:
        return None

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        price = data.get("Global Quote", {}).get("05. price")
        return float(price) if price else None
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None


def get_currencies_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """
    Получает курсы для списка валют.

    Args:
        currencies: Список кодов валют

    Returns:
        Список словарей [{"currency": "USD", "rate": 73.21}, ...]
    """
    result = []
    for currency in currencies:
        rate = get_currency_rate(currency)
        if rate is not None:
            result.append({"currency": currency, "rate": round(rate, 2)})
    return result


def get_stocks_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """
    Получает цены для списка акций.

    Args:
        stocks: Список тикеров акций

    Returns:
        Список словарей [{"stock": "AAPL", "price": 150.12}, ...]
    """
    result = []
    for stock in stocks:
        price = get_stock_price(stock)
        if price is not None:
            result.append({"stock": stock, "price": round(price, 2)})
    return result
