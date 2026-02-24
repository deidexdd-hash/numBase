#!/usr/bin/env python3
"""
ПРЕДВАРИТЕЛЬНАЯ БАЗА ДАННЫХ ФОРМУЛ
Содержит все известные формулы из PDF файлов.
Запускать для создания начальной базы данных.
"""

import json
from pathlib import Path

OUTPUT_DIR = Path("knowledge_base_v2/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Полная база формул на основе анализа PDF файлов
FORMULAS_DATABASE = [
    # НУМЕРОЛОГИЯ - Основные числа
    {
        "id": "birth_number",
        "name": "Число рождения",
        "category": "numerology",
        "subcategory": "basic",
        "description": "Характеристика личности по дню рождения",
        "formula": "День рождения → сведение к однозначному числу",
        "formula_code": "reduce_to_single(day)",
        "inputs": [
            {"name": "day", "type": "number", "min": 1, "max": 31, "label": "День рождения"}
        ],
        "output": {"type": "number", "range": "1-9, 11, 22, 33"},
        "example": {"input": {"day": 25}, "output": 7, "calculation": "25 → 2+5 = 7"},
        "meaning": "Показывает внешние проявления, поведение, отношение к миру",
        "source_files": ["Число рождения.pdf", "цифра1.pdf", "цифра2.pdf", "цифра4.pdf", "цифра5.pdf", "цифра6.pdf", "цифра7.pdf", "цифра 3.pdf", "цифра 8.pdf", "цифра9..pdf"]
    },
    {
        "id": "life_path",
        "name": "Путь жизни",
        "category": "numerology",
        "subcategory": "basic",
        "description": "Главное предназначение и задачи жизни",
        "formula": "ДД + ММ + ГГГГ → сведение к однозначному",
        "formula_code": "reduce_to_single(day + month + year)",
        "inputs": [
            {"name": "day", "type": "number", "min": 1, "max": 31, "label": "День"},
            {"name": "month", "type": "number", "min": 1, "max": 12, "label": "Месяц"},
            {"name": "year", "type": "number", "min": 1900, "max": 2100, "label": "Год"}
        ],
        "output": {"type": "number", "range": "1-9, 11, 22, 33"},
        "example": {"input": {"day": 15, "month": 6, "year": 1990}, "output": 4, "calculation": "15+6+1990=2011 → 2+0+1+1=4"},
        "meaning": "Основное предназначение, жизненный путь, уроки",
        "source_files": ["Личные циклы.pdf", "Как_число_рождения_влияет_на_человека.pdf"]
    },
    {
        "id": "destiny_number",
        "name": "Число судьбы",
        "category": "numerology",
        "subcategory": "name",
        "description": "Судьба и жизненная миссия по имени",
        "formula": "Сумма букв ФИО по таблице → сведение к однозначному",
        "formula_code": "reduce_to_single(sum(letter_values[name]))",
        "inputs": [
            {"name": "fullname", "type": "text", "label": "ФИО полностью"}
        ],
        "output": {"type": "number", "range": "1-9, 11, 22"},
        "example": {"input": {"fullname": "Иванов Иван Иванович"}, "output": 1, "calculation": "Сумма букв → сведение"},
        "meaning": "Миссия, предназначение, что нужно достичь в жизни",
        "source_files": ["РасчетФИО.pdf", "предназначение.pdf"],
        "letter_table": {
            "1": ["А", "И", "Й", "Ы"],
            "2": ["Б", "К", "У", "Ь"],
            "3": ["В", "Л", "Ф", "Э"],
            "4": ["Г", "М", "Х", "Ъ"],
            "5": ["Д", "Н", "Ц"],
            "6": ["Е", "Ё", "О", "Ч"],
            "7": ["Ж", "П", "Ш"],
            "8": ["З", "Р", "Щ"],
            "9": ["С", "Т", "Ю"]
        }
    },
    {
        "id": "soul_number",
        "name": "Число души",
        "category": "numerology",
        "subcategory": "name",
        "description": "Внутренние желания и потребности",
        "formula": "Сумма гласных букв ФИО → сведение",
        "formula_code": "reduce_to_single(sum(vowels_in_name))",
        "inputs": [
            {"name": "fullname", "type": "text", "label": "ФИО полностью"}
        ],
        "output": {"type": "number", "range": "1-9, 11, 22"},
        "example": {"input": {"fullname": "Иванов Иван"}, "output": 3, "calculation": "Гласные: И,А,О,И,А → сумма → сведение"},
        "meaning": "Внутренние желания, мотивы, что действительно важно",
        "source_files": ["РасчетФИО.pdf"],
        "vowels": ["А", "Е", "Ё", "И", "О", "У", "Ы", "Э", "Ю", "Я"]
    },
    {
        "id": "expression_number",
        "name": "Число выражения",
        "category": "numerology",
        "subcategory": "name",
        "description": "Способ самовыражения и таланты",
        "formula": "Сумма согласных букв ФИО → сведение",
        "formula_code": "reduce_to_single(sum(consonants_in_name))",
        "inputs": [
            {"name": "fullname", "type": "text", "label": "ФИО полностью"}
        ],
        "output": {"type": "number", "range": "1-9, 11, 22"},
        "meaning": "Способности, таланты, как выражаешь себя миру",
        "source_files": ["РасчетФИО.pdf"]
    },
    
    # ЧАКРЫ
    {
        "id": "chakra_balance",
        "name": "Баланс чакр",
        "category": "energy",
        "subcategory": "chakras",
        "description": "Энергетический баланс по 7 чакрам",
        "formula": "Соседние цифры даты рождения: 1+2, 2+3, 3+4...",
        "formula_code": "chakras[i] = digits[i] + digits[i+1]",
        "inputs": [
            {"name": "day", "type": "number", "min": 1, "max": 31, "label": "День"},
            {"name": "month", "type": "number", "min": 1, "max": 12, "label": "Месяц"},
            {"name": "year", "type": "number", "min": 1900, "max": 2100, "label": "Год"}
        ],
        "output": {"type": "array", "count": 7, "names": ["Муладхара", "Свадхистана", "Манипура", "Анахата", "Вишудха", "Аджна", "Сахасрара"]},
        "example": {"input": {"day": 15, "month": 6, "year": 1990}, "output": [6, 5, 6, 10, 19, 10, 9], "calculation": "15061990 → 1+5, 5+0, 0+6, 6+1, 1+9, 9+9, 9+0"},
        "meaning": "Энергетический потенциал по каждому центру",
        "source_files": ["чакры.pdf", "энергетический просмотр.pdf"]
    },
    
    # РОДОВЫЕ РАСЧЕТЫ
    {
        "id": "financial_channel",
        "name": "Родовой финансовый канал",
        "category": "ancestral",
        "subcategory": "financial",
        "description": "Точки входа в родовой финансовый канал",
        "formula": "A=День, B=Месяц, C=Сумма цифр года, D=A+B+C → сведение",
        "formula_code": "A=day, B=month, C=sum(year_digits), D=reduce(A+B+C)",
        "inputs": [
            {"name": "day", "type": "number", "min": 1, "max": 31, "label": "День"},
            {"name": "month", "type": "number", "min": 1, "max": 12, "label": "Месяц"},
            {"name": "year", "type": "number", "min": 1900, "max": 2100, "label": "Год"}
        ],
        "output": {"type": "object", "fields": ["A", "B", "C", "D"]},
        "example": {"input": {"day": 15, "month": 6, "year": 1990}, "output": {"A": 15, "B": 6, "C": 19, "D": 4}, "calculation": "A=15, B=6, C=1+9+9+0=19, D=15+6+19=40→4"},
        "meaning": "Денежный потенциал и точки входа в родовой канал",
        "source_files": ["Родовой финансовый канал.pdf", "Точки входа в финансовый канал.pdf", "энергия денег в Роду.pdf"]
    },
    {
        "id": "generational_program",
        "name": "Программа поколений",
        "category": "ancestral",
        "subcategory": "generational",
        "description": "Родовая программа по арканам (1-22)",
        "formula": "Сумма всех цифр даты → сведение к аркану (1-22)",
        "formula_code": "reduce_to_22(sum(all_date_digits))",
        "inputs": [
            {"name": "day", "type": "number", "min": 1, "max": 31, "label": "День"},
            {"name": "month", "type": "number", "min": 1, "max": 12, "label": "Месяц"},
            {"name": "year", "type": "number", "min": 1900, "max": 2100, "label": "Год"}
        ],
        "output": {"type": "number", "range": "1-22"},
        "example": {"input": {"day": 15, "month": 6, "year": 1990}, "output": 4, "calculation": "1+5+0+6+1+9+9+0=31 → 3+1=4"},
        "meaning": "Родовые задачи и программы через арканы Таро",
        "source_files": ["Программы поколений Рода.pdf", "12 Ансестологических циклов.pdf", "Какие_события_формируют_Родовые_программы.pdf"]
    },
    {
        "id": "ancestral_cycles",
        "name": "12 Ансестологических циклов",
        "category": "ancestral",
        "subcategory": "cycles",
        "description": "Циклы развития по годам",
        "formula": "Базовое число = сведение(День+Месяц), Цикл = Базовое + номер цикла",
        "formula_code": "base = reduce(day+month), cycle[i] = reduce(base + i)",
        "inputs": [
            {"name": "day", "type": "number", "min": 1, "max": 31, "label": "День"},
            {"name": "month", "type": "number", "min": 1, "max": 12, "label": "Месяц"}
        ],
        "output": {"type": "array", "count": 12},
        "example": {"input": {"day": 15, "month": 6}, "output": [3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5], "calculation": "15+6=21→3, 3+1=4..."},
        "source_files": ["12 Ансестологических циклов.pdf", "Личные циклы.pdf"]
    },
    
    # СПЕЦИАЛЬНЫЕ РАСЧЕТЫ
    {
        "id": "vuz_calculation",
        "name": "Расчет ВУЗа/образования",
        "category": "calculations",
        "subcategory": "education",
        "description": "Подходящее направление обучения",
        "formula": "На основе числа судьбы и пути жизни",
        "inputs": [
            {"name": "life_path", "type": "number", "label": "Путь жизни"},
            {"name": "destiny", "type": "number", "label": "Число судьбы"}
        ],
        "source_files": ["Расчет ВУЗа.pdf", "выбор профессии.pdf"]
    },
    {
        "id": "property_calculation",
        "name": "Расчет имущества/недвижимости",
        "category": "calculations",
        "subcategory": "property",
        "description": "Благоприятность приобретения",
        "formula": "На основе текущего цикла и финансового канала",
        "inputs": [
            {"name": "year", "type": "number", "label": "Год покупки"}
        ],
        "source_files": ["РасчетИмущество.pdf"]
    },
    {
        "id": "relocation_calculation",
        "name": "Расчет переезда",
        "category": "calculations",
        "subcategory": "relocation",
        "description": "Благоприятность переезда",
        "formula": "Совместимость текущего и нового места",
        "inputs": [
            {"name": "current_city", "type": "text", "label": "Текущий город"},
            {"name": "new_city", "type": "text", "label": "Новый город"},
            {"name": "date", "type": "date", "label": "Дата переезда"}
        ],
        "source_files": ["Расчеты переезда и поездки.pdf"]
    },
    {
        "id": "relationship_calculation",
        "name": "Расчет отношений",
        "category": "calculations",
        "subcategory": "relationships",
        "description": "Совместимость партнеров",
        "formula": "Сравнение путей жизни и чисел рождения",
        "inputs": [
            {"name": "person1_birth", "type": "date", "label": "Дата рождения 1"},
            {"name": "person2_birth", "type": "date", "label": "Дата рождения 2"}
        ],
        "source_files": ["расчеты по отношениям.pdf", "Типы_отношений_Основные_типы_отношений.pdf", "Картаблизнецов.pdf"]
    },
    {
        "id": "business_calculation",
        "name": "Расчет бизнеса",
        "category": "calculations",
        "subcategory": "business",
        "description": "Благоприятность для бизнеса",
        "formula": "Финансовый канал + цикл + число судьбы",
        "inputs": [
            {"name": "day", "type": "number", "label": "День"},
            {"name": "month", "type": "number", "label": "Месяц"},
            {"name": "year", "type": "number", "label": "Год"}
        ],
        "source_files": ["расчеты по бизнесу.pdf", "Расчет по инвестициям.pdf", "РасчетРисков.pdf"]
    },
    {
        "id": "pregnancy_calculation",
        "name": "Расчет по беременности",
        "category": "calculations",
        "subcategory": "health",
        "description": "Благоприятные периоды",
        "formula": "На основе личных циклов и чакр",
        "inputs": [
            {"name": "mother_birth", "type": "date", "label": "Дата рождения матери"},
            {"name": "planned_date", "type": "date", "label": "Планируемая дата"}
        ],
        "source_files": ["Расчёт по беременности.pdf", "расширенная схема проработки нерожденных детей.pdf"]
    },
]

# Практики и техники
PRACTICES_DATABASE = [
    {
        "id": "genogram_practice",
        "name": "Практика составления генограммы",
        "category": "practice",
        "duration": "30-60 минут",
        "materials": ["бумага", "ручки разных цветов"],
        "steps": [
            "Нарисовать основу - себя в центре",
            "Добавить родителей над собой",
            "Добавить бабушек/дедушек",
            "Отметить ключевые события",
            "Обозначить отношения линиями"
        ],
        "source_files": ["Практика генограмма.pdf", "ГенограммаНерожд.pdf", "Правила_составления_и_хранения_генограммы_для_работы_с_Родом.pdf"]
    },
    {
        "id": "rod_belt",
        "name": "Практика плетения Родового пояса",
        "category": "practice",
        "duration": "1-3 часа",
        "materials": ["нити разных цветов", "бусины"],
        "source_files": ["Практика плетения Родового пояса.pdf", "Памятка пояса по цветам.pdf"]
    },
    {
        "id": "blessing_practice",
        "name": "Практика благословения",
        "category": "practice",
        "duration": "15-30 минут",
        "steps": [
            "Встать перед фото предков или в южной части комнаты",
            "Свеча или лампада",
            "Прочитать молитву благословения",
            "Попросить поддержки у рода"
        ],
        "source_files": ["Практика благословения.pdf", "Молитвы родителям.pdf", "Особые молитвы и практики.pdf"]
    },
    {
        "id": "acceptance_practice",
        "name": "Практика принятия исключенных",
        "category": "practice",
        "duration": "20-40 минут",
        "description": "Проработка отношений с исключенными из рода",
        "source_files": ["Практика принятия исключенных.pdf", "Исключённые_Кого_не_приняли_в_Родовую_систему_.pdf", "Схема_выбора_практики_принятия_исключенных_в_Родовую_систему.pdf"]
    },
    {
        "id": "bowing_practice",
        "name": "Практика поклонов",
        "category": "practice",
        "duration": "10-30 минут",
        "steps": [
            "Встать ровно, закрыть глаза",
            "Визуализировать родовую линию",
            "Выполнить поклоны в каждую сторону",
            "Почувствовать связь с родом"
        ],
        "source_files": ["Практика поклонов.pdf"]
    },
    {
        "id": "inner_child",
        "name": "Беседа с внутренним ребенком",
        "category": "practice",
        "duration": "30 минут",
        "description": "Техника работы с внутренним ребенком",
        "source_files": ["Как_беседовать_со_своим_внутренним_ребенком.pdf"]
    },
    {
        "id": "meditation_collection",
        "name": "Сборник медитаций",
        "category": "practice",
        "type": "collection",
        "items": ["Медитация на связь с родом", "Медитация на исцеление", "Медитация на принятие"],
        "source_files": ["СБорникМедитаций.pdf", "Памятка по записи медитации.pdf"]
    },
    {
        "id": "prayer_collection",
        "name": "Сборник молитв",
        "category": "practice",
        "type": "collection",
        "source_files": ["СборникМолитв.pdf", "ТЕРАПЕВТИЧЕСКИЙ ЭФФЕКТ МОЛИТВЫ.pdf"]
    }
]

# Алгоритмы и схемы
ALGORITHMS_DATABASE = [
    {
        "id": "selection_scheme",
        "name": "Схема выбора техники проработки",
        "category": "algorithm",
        "type": "decision_tree",
        "description": "Алгоритм выбора подходящей практики",
        "steps": [
            "Определить тип запроса",
            "Выбрать категорию (родовые/личные)",
            "Определить уровень проработки",
            "Подобрать технику"
        ],
        "source_files": ["Алгоритм подбора схемы проработки.pdf", "Алгоритм_выбора_техники_проработки.pdf", "СхемаВыбора.pdf", "УпрощеннаяСхема.pdf"]
    },
    {
        "id": "analysis_structure",
        "name": "Структура эффективного анализа",
        "category": "algorithm",
        "type": "methodology",
        "steps": [
            "Сбор информации о клиенте",
            "Составление генограммы",
            "Определение ключевых событий",
            "Анализ родовых программ",
            "Подбор практик"
        ],
        "source_files": ["Структура эффективного анализа.pdf"]
    }
]

# Значения чисел
NUMBER_MEANINGS = {
    "1": {
        "title": "Единица - Лидерство",
        "keywords": ["лидер", "индивидуальность", "независимость", "амбиции"],
        "positive": ["целеустремленность", "инициативность", "смелость"],
        "negative": ["эгоизм", "тирания", "упрямство"],
        "professions": ["руководитель", "предприниматель", "политик"],
        "source_files": ["цифра1.pdf"]
    },
    "2": {
        "title": "Двойка - Дипломатия",
        "keywords": ["гармония", "сотрудничество", "чувствительность"],
        "positive": ["такт", "дипломатия", "интуиция"],
        "negative": ["зависимость", "нерешительность", "избегание конфликтов"],
        "professions": ["дипломат", "психолог", "юрист"],
        "source_files": ["цифра2.pdf"]
    },
    "3": {
        "title": "Тройка - Творчество",
        "keywords": ["самовыражение", "оптимизм", "коммуникация"],
        "positive": ["креативность", "харизма", "веселье"],
        "negative": ["поверхностность", "расточительность", "беспечность"],
        "professions": ["артист", "писатель", "маркетолог"],
        "source_files": ["цифра 3.pdf"]
    },
    "4": {
        "title": "Четверка - Стабильность",
        "keywords": ["практичность", "порядок", "трудолюбие"],
        "positive": ["надежность", "терпение", "дисциплина"],
        "negative": ["застой", "консерватизм", "занудство"],
        "professions": ["инженер", "бухгалтер", "строитель"],
        "source_files": ["цифра4.pdf"]
    },
    "5": {
        "title": "Пятерка - Свобода",
        "keywords": ["перемены", "адаптивность", "приключения"],
        "positive": ["гибкость", "любознательность", "энергичность"],
        "negative": ["беспокойность", "нетерпеливость", "экстремизм"],
        "professions": ["журналист", "туристический агент", "консультант"],
        "source_files": ["цифра5.pdf"]
    },
    "6": {
        "title": "Шестерка - Забота",
        "keywords": ["семья", "ответственность", "исцеление"],
        "positive": ["забота", "сострадание", "надежность"],
        "negative": ["тревожность", "контроль", "жертвенность"],
        "professions": ["врач", "учитель", "социальный работник"],
        "source_files": ["цифра6.pdf"]
    },
    "7": {
        "title": "Семерка - Анализ",
        "keywords": ["мудрость", "духовность", "интуиция"],
        "positive": ["аналитичность", "глубина", "интеллект"],
        "negative": ["отчуждение", "педантизм", "скептицизм"],
        "professions": ["ученый", "философ", "исследователь"],
        "source_files": ["цифра7.pdf"]
    },
    "8": {
        "title": "Восьмерка - Власть",
        "keywords": ["успех", "управление", "карма"],
        "positive": ["организованность", "эффективность", "влияние"],
        "negative": ["жадность", "авторитаризм", "работоголизм"],
        "professions": ["менеджер", "банкир", "администратор"],
        "source_files": ["цифра 8.pdf"]
    },
    "9": {
        "title": "Девятка - Служение",
        "keywords": ["гуманизм", "завершение", "сострадание"],
        "positive": ["альтруизм", "толерантность", "универсальность"],
        "negative": ["разрозненность", "разочарование", "самопожертвование"],
        "professions": ["филантроп", "художник", "духовный учитель"],
        "source_files": ["цифра9..pdf"]
    },
    "11": {
        "title": "11 - Мастер-число интуиции",
        "keywords": ["вдохновение", "просветление", "высшая интуиция"],
        "source_files": ["Число рождения.pdf"]
    },
    "22": {
        "title": "22 - Мастер-число строителя",
        "keywords": ["великие дела", "материализация", "глобальность"],
        "source_files": ["Число рождения.pdf"]
    }
}

def save_database():
    """Сохранить все базы данных в JSON"""
    print("Сохранение баз данных...")
    
    # Формулы
    with open(OUTPUT_DIR / 'formulas.json', 'w', encoding='utf-8') as f:
        json.dump(FORMULAS_DATABASE, f, ensure_ascii=False, indent=2)
    print(f"  ✓ formulas.json ({len(FORMULAS_DATABASE)} формул)")
    
    # Практики
    with open(OUTPUT_DIR / 'practices.json', 'w', encoding='utf-8') as f:
        json.dump(PRACTICES_DATABASE, f, ensure_ascii=False, indent=2)
    print(f"  ✓ practices.json ({len(PRACTICES_DATABASE)} практик)")
    
    # Алгоритмы
    with open(OUTPUT_DIR / 'algorithms.json', 'w', encoding='utf-8') as f:
        json.dump(ALGORITHMS_DATABASE, f, ensure_ascii=False, indent=2)
    print(f"  ✓ algorithms.json ({len(ALGORITHMS_DATABASE)} алгоритмов)")
    
    # Значения чисел
    with open(OUTPUT_DIR / 'number_meanings.json', 'w', encoding='utf-8') as f:
        json.dump(NUMBER_MEANINGS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ number_meanings.json ({len(NUMBER_MEANINGS)} значений)")
    
    # Мастер-индекс
    master_index = {
        "version": "1.0",
        "created": "2025-02-17",
        "total_formulas": len(FORMULAS_DATABASE),
        "total_practices": len(PRACTICES_DATABASE),
        "total_algorithms": len(ALGORITHMS_DATABASE),
        "categories": list(set(f['category'] for f in FORMULAS_DATABASE)),
        "files": {
            "formulas": "formulas.json",
            "practices": "practices.json",
            "algorithms": "algorithms.json",
            "number_meanings": "number_meanings.json"
        }
    }
    
    with open(OUTPUT_DIR / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)
    print(f"  ✓ index.json")
    
    print(f"\n✅ Все данные сохранены в: {OUTPUT_DIR}")

if __name__ == '__main__':
    print("=" * 60)
    print("СОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("Из PDF: Ансестология и Нумерология")
    print("=" * 60)
    print()
    
    save_database()
    
    print()
    print("Готово! Теперь можно создавать приложение.")
    print("Данные находятся в: knowledge_base_v2/data/")
