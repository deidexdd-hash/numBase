#!/usr/bin/env python3
"""
ПРОВЕРКА И УСТАНОВКА OCR
Скрипт для проверки готовности OCR к работе.
"""

import sys
import subprocess
from pathlib import Path

def check_tesseract():
    """Проверить Tesseract"""
    print("\n🔍 Проверка Tesseract-OCR:")
    print("-" * 60)
    
    try:
        import pytesseract
        print("  ✓ Python библиотека pytesseract установлена")
        
        try:
            version = pytesseract.get_tesseract_version()
            print(f"  ✓ Tesseract найден: версия {version}")
            
            langs = pytesseract.get_languages()
            print(f"  ✓ Доступно языков: {len(langs)}")
            
            if 'rus' in langs:
                print(f"  ✅ Русский язык (rus) доступен!")
                return True
            else:
                print(f"  ❌ Русский язык НЕ найден!")
                print(f"     Доступны: {', '.join(langs[:10])}...")
                return False
                
        except Exception as e:
            print(f"  ❌ Tesseract не найден в системе")
            print(f"     Ошибка: {e}")
            return False
            
    except ImportError:
        print("  ❌ Библиотека pytesseract не установлена")
        print("     Установите: pip install pytesseract")
        return False

def check_poppler():
    """Проверить Poppler"""
    print("\n🔍 Проверка Poppler:")
    print("-" * 60)
    
    try:
        from pdf2image import convert_from_path
        print("  ✓ Python библиотека pdf2image установлена")
        
        import shutil
        poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"
        
        if shutil.which('pdftoppm'):
            print("  ✓ Poppler (pdftoppm) найден в PATH")
            return True
        elif Path(poppler_path).exists():
            print(f"  ✓ Poppler найден в: {poppler_path}")
            return True
        else:
            print("  ❌ Poppler не найден в PATH")
            print("     Скачайте: https://github.com/oschwartz10612/poppler-windows")
            print("     Распакуйте в C:\\poppler и добавьте C:\\poppler\\bin в PATH")
            return False
            
    except ImportError:
        print("  ❌ Библиотека pdf2image не установлена")
        print("     Установите: pip install pdf2image")
        return False

def install_python_packages():
    """Установить Python пакеты"""
    print("\n📦 Установка Python пакетов:")
    print("-" * 60)
    
    packages = ['pytesseract', 'pdf2image', 'pillow']
    
    for package in packages:
        print(f"  Установка {package}...", end=" ")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', package],
                check=True
            )
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")

def show_install_instructions():
    """Показать инструкции по установке"""
    print("\n" + "=" * 60)
    print("📋 ИНСТРУКЦИИ ПО УСТАНОВКЕ OCR")
    print("=" * 60)
    
    print("""
1️⃣  Установить Tesseract-OCR:
    
    Скачайте: https://github.com/UB-Mannheim/tesseract/wiki
    
    При установке:
    • Выберите путь: C:\\Program Files\\Tesseract-OCR
    • ☑️ Обязательно отметьте "Russian" в списке языков
    • Дождитесь завершения установки

2️⃣  Добавить Tesseract в PATH:
    
    Панель управления → Система → Доп. параметры системы
    → Переменные среды → Path → Изменить → Создать
    → Добавить: C:\\Program Files\\Tesseract-OCR

3️⃣  Установить Poppler:
    
    Скачайте: https://github.com/oschwartz10612/poppler-windows/releases
    
    Распакуйте в: C:\\poppler
    Добавьте в PATH: C:\\poppler\\bin

4️⃣  Установить Python пакеты:
    
    pip install pytesseract pdf2image pillow

5️⃣  Перезапустить терминал и проверить:
    
    python check_ocr.py
""")

def main():
    """Главная функция проверки"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА ГОТОВНОСТИ OCR")
    print("=" * 60)
    
    # Проверяем компоненты
    tesseract_ok = check_tesseract()
    poppler_ok = check_poppler()
    
    print("\n" + "=" * 60)
    
    if tesseract_ok and poppler_ok:
        print("✅ OCR ПОЛНОСТЬЮ ГОТОВ К РАБОТЕ!")
        print("=" * 60)
        print("\nМожно запускать:")
        print("  python processor/ocr_utils.py --help")
        print("  python processor/build_full_database.py")
        return 0
    else:
        print("❌ OCR НЕ ГОТОВ")
        print("=" * 60)
        
        if not tesseract_ok or not poppler_ok:
            show_install_instructions()
            
            print("\n💡 Быстрая установка Python пакетов:")
            response = input("Установить Python пакеты сейчас? (y/n): ")
            if response.lower() == 'y':
                install_python_packages()
                print("\n🔄 Перепроверяем...")
                return main()  # Рекурсивный вызов для повторной проверки
        
        return 1

if __name__ == '__main__':
    sys.exit(main())
