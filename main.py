"""
Основной модуль для запуска всех функциональностей проекта.
Демонстрирует работу веб-страниц, сервисов и отчетов.
"""

# import os
import json
from datetime import datetime, timedelta
import random

import pandas as pd

from src.views import main_page
from src.services import simple_search
from src.reports import spending_by_category
from src.external_api import get_currencies_rates, get_stocks_prices


def generate_test_transactions() -> pd.DataFrame:
    """Генерирует тестовые транзакции для демонстрации."""
    categories = ["Супермаркеты", "Транспорт", "Рестораны", "Развлечения", "Переводы"]
    descriptions = [
        "Пятерочка", "Ашан", "Яндекс.Такси", "KFC", "Ozon",
        "Перевод другу", "Метро", "Лента", "Burger King", "Wildberries"
    ]

    data = []
    start_date = datetime.now() - timedelta(days=90)

    for i in range(50):  # Генерируем 50 транзакций
        date = start_date + timedelta(days=random.randint(0, 90))
        category = random.choice(categories)
        description = random.choice(descriptions)
        amount = round(random.uniform(-5000, -100), 2)  # Расходы
        if category == "Переводы":
            amount = round(random.uniform(-20000, -1000), 2)  # Крупные переводы

        data.append({
            'Дата операции': date.strftime('%d.%m.%Y'),
            'Сумма платежа': amount,
            'Категория': category,
            'Описание': description,
            'Номер карты': random.choice(['1234', '5678', '9012'])
        })

    df = pd.DataFrame(data)
    print(f"✅ Сгенерировано {len(df)} тестовых транзакций")
    return df


def demo_views():
    """Демонстрация работы веб-страницы 'Главная'."""
    print("\n" + "="*60)
    print("🏠 ДЕМОНСТРАЦИЯ ВЕБ-СТРАНИЦЫ 'ГЛАВНАЯ'")
    print("="*60)

    # Текущая дата для демонстрации
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        result = main_page(current_date)
        data = json.loads(result)

        print(f"\n👋 Приветствие: {data.get('greeting')}")
        print(f"\n💳 Информация по картам: {len(data.get('cards', []))} карт")

        cards = data.get('cards', [])
        for card in cards:
            print(f"Карта *{card.get('last_digits')}: {card.get('total_spent')} руб. (кешбэк: {card.get('cashback')})")

        print(f"\n📊 Топ транзакций: {len(data.get('top_transactions', []))} шт")
        for i, t in enumerate(data.get('top_transactions', [])[:3], 1):
            print(f"   {i}. {t.get('date')} {t.get('description')[:30]}... {t.get('amount')} руб.")

        print(f"\n💵 Курсы валют: {data.get('currency_rates')}")
        print(f"📈 Акции: {data.get('stock_prices')}")

        print("\n✅ views.py работает корректно")
    except Exception as e:
        print(f"❌ Ошибка в views.py: {e}")


def demo_services():
    """Демонстрация работы сервисов."""
    print("\n" + "="*60)
    print("🔍 ДЕМОНСТРАЦИЯ СЕРВИСА 'ПРОСТОЙ ПОИСК'")
    print("="*60)

    # Генерируем тестовые данные
    df = generate_test_transactions()

    if df.empty:
        print("❌ Нет данных для поиска")
        return

    # Преобразуем DataFrame в список словарей
    transactions = df.to_dict(orient='records')

    # Поиск по слову "Перевод"
    search_query = "Перевод"
    try:
        result = simple_search(transactions, search_query)
        found = json.loads(result)

        print(f"\n🔎 Поиск по запросу '{search_query}': найдено {len(found)} транзакций")

        # Покажем первые 3 найденные транзакции
        for i, t in enumerate(found[:3], 1):
            print(f"  {i}. {t.get('Категория', 'N/A')}: {t.get('Описание', 'N/A')} {t.get('Сумма платежа')} руб.")

        print("\n✅ services.py работает корректно")
    except Exception as e:
        print(f"❌ Ошибка в services.py: {e}")


def demo_reports():
    """Демонстрация работы отчетов."""
    print("\n" + "="*60)
    print("📊 ДЕМОНСТРАЦИЯ ОТЧЕТА 'ТРАТЫ ПО КАТЕГОРИИ'")
    print("="*60)

    # Генерируем тестовые данные
    df = generate_test_transactions()

    if df.empty:
        print("❌ Нет данных для отчета")
        return

    # Анализ трат по категории "Супермаркеты"
    try:
        result = spending_by_category(df, "Супермаркеты", datetime.now().strftime("%Y-%m-%d"))

        print("\n🛒 Траты по категории 'Супермаркеты' за последние 3 месяца:")
        print(f"   Найдено транзакций: {len(result)}")

        if not result.empty:
            total = result['Сумма платежа'].abs().sum()
            print(f"   Общая сумма: {total:.2f} руб.")

        print("\n✅ reports.py работает корректно")
        print("📁 Отчет сохранен в data/spending_by_category.json")
    except Exception as e:
        print(f"❌ Ошибка в reports.py: {e}")


def demo_external_api():
    """Демонстрация работы с внешними API."""
    print("\n" + "="*60)
    print("🌐 ДЕМОНСТРАЦИЯ РАБОТЫ С ВНЕШНИМИ API")
    print("="*60)

    try:
        # Проверяем курсы валют
        currencies = ["USD", "EUR"]
        rates = get_currencies_rates(currencies)

        if rates:
            print("\n💵 Курсы валют:")
            for rate in rates:
                print(f"   {rate['currency']}: {rate['rate']} RUB")
        else:
            print("\n❌ Не удалось получить курсы валют (проверьте API ключ)")

        # Проверяем цены акций
        stocks = ["AAPL", "GOOGL"]
        prices = get_stocks_prices(stocks)

        if prices:
            print("\n📈 Цены акций:")
            for price in prices:
                print(f"   {price['stock']}: ${price['price']}")
        else:
            print("\n❌ Не удалось получить цены акций (проверьте API ключ)")

    except Exception as e:
        print(f"❌ Ошибка в external_api.py: {e}")


def main():
    """Главная функция, запускающая все демонстрации."""
    print("="*60)
    print("🚀 ЗАПУСК ВСЕХ ФУНКЦИОНАЛЬНОСТЕЙ ПРОЕКТА")
    print("="*60)

    # Демонстрация веб-страниц
    demo_views()

    # Демонстрация сервисов
    demo_services()

    # Демонстрация отчетов
    demo_reports()

    # Демонстрация внешних API
    demo_external_api()

    print("\n" + "="*60)
    print("✅ Все демонстрации завершены")
    print("="*60)


if __name__ == "__main__":
    main()
