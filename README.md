# Курсовая работа: Анализ банковских транзакций

## 📋 Описание
Приложение для анализа транзакций из Excel-файла. Генерирует JSON-данные для веб-страниц, формирует отчеты и предоставляет сервисы для поиска и анализа.

## 🚀 Установка

```bash
git clone <your-repo-url>
cd pythonProject_Coursework_1
poetry install
```

## 📚 Функциональность
**Веб-страницы (views.py)**
- Главная: приветствие по времени суток, расходы по картам, топ-5 транзакций, курсы валют и акции S&P500
- События: анализ расходов и поступлений по категориям

**Сервисы (services.py)**
- Простой поиск: поиск транзакций по описанию
- Инвесткопилка: округление трат до заданного порога

**Отчеты (reports.py)**
- Траты по категории: анализ расходов за последние 3 месяца
- Декоратор отчетов: автоматическое сохранение результатов в JSON-файлы (папка data/)

**Внешние API (external_api.py)**
- Получение курсов валют (USD, EUR)
- Получение цен акций S&P500 (AAPL, GOOGL, MSFT, TSLA)

## 🧪 Тестирование
```bash
# Запуск всех тестов
poetry run pytest

# Запуск с отчетом о покрытии
poetry run pytest --cov=src --cov-report=term-missing

# Генерация HTML-отчета
poetry run pytest --cov=src --cov-report=html
```

## 📊 Покрытие тестами
Статистика покрытия (92%)

| Модуль            | Строк   | Пропущено | Покрытие |
|-------------------|---------|-----------|----------|
| `external_api.py` | 58      | 10        | 83%      |
| `reports.py`      | 38      | 0         | 100%     |
| `services.py`     | 16      | 0         | 100%     |
| `utils.py`        | 53      | 2         | 96%      |
| `views.py`        | 28      | 3         | 89%      |
| **ИТОГО**         | **193** | **58**    | **92%**  |

✅ Требование: >80% — выполнено

## 🔧 Инструменты качества кода
```bash
# Проверка стиля
poetry run flake8 src/ tests/

# Форматирование
poetry run black src/ tests/
poetry run isort src/ tests/

# Проверка типов
poetry run mypy src/
```

## 📁 Структура проекта
```
pythonProject_Coursework_1/
├── data/                    # Данные и отчеты
│   ├── operations.xlsx      # Исходные транзакции
│   └── *.json               # Сгенерированные отчеты
├── src/                     # Исходный код
│   ├── __init__.py
│   ├── external_api.py      # Работа с API
│   ├── reports.py           # Отчеты
│   ├── services.py          # Сервисы
│   ├── utils.py             # Вспомогательные функции
│   └── views.py             # Веб-страницы
├── tests/                   # Тесты
│   ├── test_external_api.py
│   ├── test_reports.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_views.py
├── .env                     # API ключи (не в git)
├── .env_template            # Шаблон .env
├── .flake8                  # Конфигурация flake8
├── .gitignore               # Игнорируемые файлы
├── main.py                  # Демонстрация всех функций
├── poetry.lock              # Зависимости poetry
├── pyproject.toml           # Конфигурация проекта
└── README.md                # Документация
```

## 🔑 Настройка API ключей
1. Скопируйте .env_template в .env
2. Заполните свои ключи:

```env
EXCHANGE_RATES_API_KEY=ваш_ключ_apilayer
STOCK_API_KEY=ваш_ключ_alphavantage
```
## 🚀 Запуск демонстрации
```bash
poetry run python main.py
```

## 📄 Лицензия
Проект разработан в учебных целях.

## 📞 Контакты
Автор: bezza8418