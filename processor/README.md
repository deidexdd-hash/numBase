# Инструмент подготовки данных v2.0

## Быстрый старт

### Windows
```batch
cd knowledge_base_v2\processor
python run.py
```

### Linux/Mac
```bash
cd knowledge_base_v2/processor
python3 run.py
```

## Структура

```
knowledge_base_v2/
├── processor/           # Инструменты обработки (запускать один раз)
│   ├── run.py          # Главный запускатель
│   ├── create_database.py  # Создание базы формул
│   └── process.py      # Извлечение из PDF (опционально)
├── data/               # Готовые данные (выход)
│   ├── formulas.json   # Все формулы расчетов
│   ├── practices.json  # Практики и техники
│   ├── algorithms.json # Алгоритмы работы
│   ├── number_meanings.json  # Значения чисел
│   └── index.json      # Мастер-индекс
└── app/                # Будущее приложение
    └── (пусто - создавать отдельно)
```

## Что содержится в данных

### formulas.json (14+ формул)
- Число рождения
- Путь жизни
- Число судьбы (по ФИО)
- Число души
- Число выражения
- Баланс чакр (7 чакр)
- Родовой финансовый канал
- Программа поколений
- 12 ансестологических циклов
- Расчет ВУЗа
- Расчет имущества
- Расчет переезда
- Расчет отношений
- Расчет бизнеса
- Расчет беременности

### practices.json (8+ практик)
- Составление генограммы
- Плетение родового пояса
- Практика благословения
- Принятие исключенных
- Поклоны
- Работа с внутренним ребенком
- Сборник медитаций
- Сборник молитв

### number_meanings.json (11 значений)
- Значения чисел 1-9
- Мастер-числа 11 и 22
- Полное описание характеристик

## Использование данных в приложении

```python
import json

# Загрузка всех формул
with open('data/formulas.json', 'r', encoding='utf-8') as f:
    formulas = json.load(f)

# Загрузка практик
with open('data/practices.json', 'r', encoding='utf-8') as f:
    practices = json.load(f)

# Загрузка значений чисел
with open('data/number_meanings.json', 'r', encoding='utf-8') as f:
    meanings = json.load(f)

# Поиск формулы
for formula in formulas:
    if formula['id'] == 'life_path':
        print(formula['name'])  # "Путь жизни"
        print(formula['formula'])  # "ДД + ММ + ГГГГ → сведение..."
```

## Добавление новых данных

Отредактируйте `processor/create_database.py` и добавьте новые записи в соответствующие списки:
- `FORMULAS_DATABASE` - для расчетов
- `PRACTICES_DATABASE` - для практик
- `ALGORITHMS_DATABASE` - для алгоритмов
- `NUMBER_MEANINGS` - для значений чисел

Затем перезапустите `run.py`
