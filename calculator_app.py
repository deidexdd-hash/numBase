#!/usr/bin/env python3
"""
КАЛЬКУЛЯТОР НУМЕРОЛОГИИ - Пользовательское приложение
Запуск: python calculator_app.py

Функции:
- Расчет всех основных чисел
- Поиск по базе знаний
- Просмотр практик
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"

def load_data():
    """Загрузить данные"""
    data = {}
    
    files = {
        'formulas': 'formulas.json',
        'practices': 'practices.json',
        'number_meanings': 'number_meanings.json',
        'algorithms': 'algorithms.json'
    }
    
    for key, filename in files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
    
    return data

def reduce_to_single(number):
    """Свести число к однозначному"""
    while number > 9 and number not in [11, 22, 33]:
        number = sum(int(d) for d in str(number))
    return number

def calculate_birth_number(day):
    """Число рождения"""
    return reduce_to_single(day)

def calculate_life_path(day, month, year):
    """Путь жизни"""
    return reduce_to_single(day + month + year)

def calculate_destiny_number(name):
    """Число судьбы по ФИО"""
    letters = {
        'а': 1, 'б': 2, 'в': 3, 'г': 4, 'д': 5, 'е': 6, 'ё': 6,
        'ж': 7, 'з': 8, 'и': 9, 'й': 1, 'к': 2, 'л': 3, 'м': 4,
        'н': 5, 'о': 6, 'п': 7, 'р': 8, 'с': 9, 'т': 1, 'у': 2,
        'ф': 3, 'х': 4, 'ц': 5, 'ч': 6, 'ш': 7, 'щ': 8, 'ъ': 9,
        'ы': 1, 'ь': 2, 'э': 3, 'ю': 4, 'я': 5
    }
    total = sum(letters.get(c, 0) for c in name.lower() if c in letters)
    return reduce_to_single(total)

def calculate_financial_channel(day, month, year):
    """Финансовый канал"""
    A = day
    B = month
    C = sum(int(d) for d in str(year))
    D = reduce_to_single(A + B + C)
    return {'A': A, 'B': B, 'C': C, 'D': D}

def show_menu():
    """Показать меню"""
    print("\n" + "=" * 60)
    print("  КАЛЬКУЛЯТОР НУМЕРОЛОГИИ И РОДОВЫХ ПРАКТИК")
    print("=" * 60)
    print("\n1. Полный расчет по дате рождения")
    print("2. Расчет по ФИО")
    print("3. Просмотр практик")
    print("4. Значения чисел")
    print("5. Выход")
    print()

def full_calculation(data):
    """Полный расчет"""
    print("\n" + "=" * 60)
    print("ПОЛНЫЙ РАСЧЕТ")
    print("=" * 60)
    
    try:
        day = int(input("День рождения (1-31): "))
        month = int(input("Месяц (1-12): "))
        year = int(input("Год (например, 1990): "))
        
        print("\n" + "-" * 60)
        
        # Число рождения
        birth = calculate_birth_number(day)
        print(f"Число рождения: {birth}")
        meaning = data['number_meanings'].get(str(birth), {})
        if meaning:
            print(f"  {meaning.get('title', '')}")
        
        # Путь жизни
        life = calculate_life_path(day, month, year)
        print(f"\nПуть жизни: {life}")
        meaning = data['number_meanings'].get(str(life), {})
        if meaning:
            print(f"  {meaning.get('title', '')}")
        
        # Финансовый канал
        finance = calculate_financial_channel(day, month, year)
        print(f"\nФинансовый канал:")
        print(f"  A (День) = {finance['A']}")
        print(f"  B (Месяц) = {finance['B']}")
        print(f"  C (Сумма года) = {finance['C']}")
        print(f"  D (Итог) = {finance['D']}")
        
        # Чакры
        print(f"\nБаланс чакр:")
        date_str = f"{day:02d}{month:02d}{year}"
        digits = [int(d) for d in date_str]
        chakras = [
            ("Муладхара", digits[0] + digits[1]),
            ("Свадхистана", digits[1] + digits[2]),
            ("Манипура", digits[2] + digits[3]),
            ("Анахата", digits[3] + digits[4]),
            ("Вишудха", digits[4] + digits[5]),
            ("Аджна", digits[5] + digits[6]),
            ("Сахасрара", digits[6] + digits[7])
        ]
        for name, value in chakras:
            print(f"  {name}: {value}")
        
    except ValueError:
        print("Ошибка: введите числа!")

def name_calculation(data):
    """Расчет по имени"""
    print("\n" + "=" * 60)
    print("РАСЧЕТ ПО ФИО")
    print("=" * 60)
    
    name = input("Введите ФИО: ").strip()
    
    if not name:
        print("Ошибка: введите имя!")
        return
    
    destiny = calculate_destiny_number(name)
    print(f"\nЧисло судьбы: {destiny}")
    
    meaning = data['number_meanings'].get(str(destiny), {})
    if meaning:
        print(f"  {meaning.get('title', '')}")

def show_practices(data):
    """Показать практики"""
    print("\n" + "=" * 60)
    print("ПРАКТИКИ И ТЕХНИКИ")
    print("=" * 60)
    
    practices = data.get('practices', [])
    
    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice.get('name', 'Без названия')}")
        if 'description' in practice:
            print(f"   {practice['description'][:100]}...")
        if 'category' in practice:
            print(f"   Категория: {practice['category']}")
    
    if practices:
        try:
            choice = int(input("\nВведите номер для подробностей (0 - назад): "))
            if 1 <= choice <= len(practices):
                practice = practices[choice - 1]
                print("\n" + "-" * 60)
                print(f"{practice.get('name', '')}")
                print("-" * 60)
                for key, value in practice.items():
                    if key != 'name' and value:
                        print(f"{key}: {value}")
        except ValueError:
            pass

def show_number_meanings(data):
    """Показать значения чисел"""
    print("\n" + "=" * 60)
    print("ЗНАЧЕНИЯ ЧИСЕЛ")
    print("=" * 60)
    
    meanings = data.get('number_meanings', {})
    
    for number, info in sorted(meanings.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        print(f"\n{number}. {info.get('title', '')}")
        if 'keywords' in info:
            print(f"   Ключевые слова: {', '.join(info['keywords'][:3])}")

def main():
    """Главная функция"""
    print("\nЗагрузка данных...")
    data = load_data()
    print(f"✓ Загружено: {len(data.get('formulas', []))} формул, {len(data.get('practices', []))} практик")
    
    while True:
        show_menu()
        
        try:
            choice = input("Выберите действие (1-5): ").strip()
            
            if choice == '1':
                full_calculation(data)
            elif choice == '2':
                name_calculation(data)
            elif choice == '3':
                show_practices(data)
            elif choice == '4':
                show_number_meanings(data)
            elif choice == '5':
                print("\nДо свидания!")
                break
            else:
                print("Неверный выбор!")
                
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()
