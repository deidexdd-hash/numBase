# Нумерология и Ансестология — Knowledge Base v3.0

База знаний: **83+ PDF** → SQLite FTS5 | Калькулятор | AI-консультант | Telegram Bot

## Быстрый старт

```bash
pip install -r requirements.txt
python main.py
# → http://localhost:8000
```

## Настройка

1. Скопируйте `.env.example` → `.env`
2. Добавьте бесплатный AI ключ (выберите один):

**Google Gemini Flash** (рекомендуется, 1M токенов/день бесплатно):
```
GEMINI_API_KEY=ваш_ключ
```
Получить: https://aistudio.google.com/app/apikey

**Groq — Llama 3.1** (быстрый, 14400 запросов/день бесплатно):
```
GROQ_API_KEY=ваш_ключ
```
Получить: https://console.groq.com/

## Telegram Bot

Когда будет готов токен:
```
# В .env:
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather

# Запуск:
python telegram_bot.py
```

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /api/calculate?day=15&month=6&year=1990` | Полный расчёт |
| `GET /api/search?q=карма` | Поиск по базе (FTS5) |
| `POST /api/ask` | AI-консультант |
| `GET /api/formulas` | Список формул |
| `GET /api/number-meanings` | Значения чисел 1-9, 11, 22, 33 |
| `GET /api/practices` | Практики с родом |
| `POST /api/knowledge/add` | Пополнить базу знаний |
| `GET /api/export?day=15&month=6&year=1990` | Текстовый отчёт |
| `GET /api/ai-status` | Статус AI провайдера |
| `GET /docs` | Swagger документация |

## Расчёты

- **Число рождения** — характеристика личности по дню рождения
- **Путь жизни** — главное предназначение: ДД+ММ+ГГГГ
- **Финансовый канал** — A(день)+B(месяц)+C(цифры года)
- **Личный год** — текущий энергетический цикл
- **Число судьбы** — по ФИО (халдейская система)
- **Чакры** — баланс по цифрам даты рождения

## Структура

```
├── main.py              # FastAPI сервер (единая точка входа)
├── knowledge_base.py    # HybridKnowledgeBase — расчёты + поиск
├── ai_consultant.py     # AI (Gemini/Groq/local fallback)
├── telegram_bot.py      # Telegram Bot
├── app/
│   └── index.html       # Web SPA (PWA, тёмная тема)
├── data/
│   ├── knowledge_base.db    # SQLite + FTS5 (83+ PDF)
│   ├── formulas.json        # Нумерологические формулы
│   ├── number_meanings.json # Значения чисел (1-9, 11, 22, 33)
│   └── practices.json       # Практики с родом
├── processor/
│   └── build_full_database.py # Пересборка БД из OCR
├── .env                 # Конфигурация (создать из .env.example)
├── DevelopmentPlan.xml  # Лог разработки
└── requirements.txt
```

## Пополнение базы знаний

В Web-интерфейсе: меню **"Пополнить базу"** → введите заголовок и текст → нажмите **Добавить**.

Через API:
```bash
curl -X POST http://localhost:8000/api/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{"title":"Мой материал","content":"Подробное описание...","category":"ancestrology"}'
```
