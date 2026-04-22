# Shop Analytics

Учебный проект по аналитике продаж: данные хранятся в PostgreSQL, обрабатываются в Python через pandas/SQLAlchemy, визуализируются через matplotlib.

## Что считает проект

- Дневную выручку (агрегация по дням).
- Накопительную выручку за весь период.
- Скользящее среднее за 7 дней (тренд).
- ТОП-5 товаров по выручке.

На выходе — два графика: `sales_analytics.png` (динамика + накопительная) и `top_products.png` (топ-5 товаров).

## Структура проекта

```
shop_analytics_project/
├── main.py                  # основной скрипт аналитики
├── init_db.sql              # схема БД + тестовые данные (10 000 продаж)
├── analytics_queries.sql    # примеры SQL-запросов к БД
├── requirements.txt         # зависимости Python
└── README.md
```

## Установка

### 1. Склонировать репозиторий

```bash
git clone https://github.com/<ваш_логин>/shop_analytics_project.git
cd shop_analytics_project
```

### 2. Создать виртуальное окружение и установить зависимости

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Развернуть базу данных

Нужен установленный PostgreSQL. Создать базу и накатить схему:

```bash
psql -U postgres -c "CREATE DATABASE shop_analytics;"
psql -U postgres -d shop_analytics -f init_db.sql
```

Или через pgAdmin: создать базу `shop_analytics` → открыть Query Tool → выполнить `init_db.sql`.

### 4. Настроить подключение

В `main.py` при необходимости поправить строку подключения под свои реквизиты:

```python
db_url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/shop_analytics'
```

### 5. Запустить

```bash
python main.py
```

## Зависимости

- pandas
- sqlalchemy
- psycopg2-binary
- matplotlib
