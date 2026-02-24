#!/usr/bin/env python3
"""
ЗАПУСКАТЕЛЬ - Главное меню системы
Запуск: python start.py
"""

import sys
import os
from pathlib import Path

def show_banner():
    """Показать баннер"""
    print("\n" + "="*60)
    print("  🔮 АНСЕСТОЛОГИЯ И НУМЕРОЛОГИЯ")
    print("  Система обработки и анализа знаний")
    print("="*60)

def show_menu():
    """Показать меню"""
    print("\n📋 ГЛАВНОЕ МЕНЮ:")
    print("-" * 60)
    print("1. 🔍 OCR Распознавание PDF (требуется Tesseract)")
    print("2. 📊 Агрегация данных в JSON")
    print("3. 🧮 Калькулятор (CLI)")
    print("4. 🌐 Калькулятор (Web)")
    print("5. ⚙️  Проверка OCR компонентов")
    print("6. ❌ Выход")
    print("-" * 60)

def get_folder_path(prompt="Введите путь к папке:", default=None):
    """Получить путь к папке от пользователя"""
    print(f"\n{prompt}")
    if default:
        print(f"По умолчанию: {default}")
    
    print("\nПримеры путей:")
    print("  Windows: C:/Users/Имя/Desktop/пдф")
    print("  Windows: C:/Users/Имя/Documents/PDFs")
    print("  Linux/Mac: /home/имя/documents/pdfs")
    print("\n(Enter - использовать путь по умолчанию)")
    
    user_input = input("\nПуть: ").strip()
    
    if not user_input and default:
        user_input = default
    
    if not user_input:
        print("❌ Путь не указан!")
        return None
    
    folder_path = Path(user_input).expanduser().resolve()
    
    if not folder_path.exists():
        print(f"\n❌ Папка не найдена: {folder_path}")
        print("\nСоздать эту папку?")
        create = input("(y/n): ").strip().lower()
        if create in ['y', 'yes', 'д', 'да']:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Папка создана: {folder_path}")
            return folder_path
        return None
    
    if not folder_path.is_dir():
        print(f"❌ Это не папка: {folder_path}")
        return None
    
    # Проверяем PDF
    pdf_files = list(folder_path.glob("*.pdf"))
    print(f"\n✓ Папка: {folder_path}")
    print(f"✓ PDF файлов: {len(pdf_files)}")
    
    if pdf_files:
        print("\nНайденные файлы:")
        for i, pdf in enumerate(pdf_files[:5], 1):
            print(f"  {i}. {pdf.name}")
        if len(pdf_files) > 5:
            print(f"  ... и еще {len(pdf_files) - 5}")
    
    return folder_path

def run_ocr():
    """Запустить OCR"""
    print("\n" + "="*60)
    print("🔍 OCR РАСПОЗНАВАНИЕ PDF")
    print("="*60)
    
    default_path = "C:/Users/New/Desktop/пдф"
    folder = get_folder_path(
        "Выберите папку с PDF файлами для распознавания:",
        default_path
    )
    
    if not folder:
        print("\n⚠ Отменено")
        return
    
    print(f"\nЗапуск OCR для: {folder}")
    print("="*60)
    
    import subprocess
    result = subprocess.run([sys.executable, "run_ocr.py", str(folder)])
    
    if result.returncode == 0:
        print("\n✅ OCR завершен успешно!")
        output_dir = folder / "ocr_results"
        if output_dir.exists():
            print(f"   Результаты сохранены в: {output_dir}")
    else:
        print("\n❌ OCR завершился с ошибкой")

def run_aggregate():
    """Запустить агрегацию"""
    print("\n" + "="*60)
    print("📊 АГРЕГАЦИЯ ДАННЫХ В JSON")
    print("="*60)
    
    print("\nХотите включить PDF документы в агрегацию?")
    print("(Требуется OCR для сканированных PDF)")
    
    choice = input("\nВключить PDF? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes', 'д', 'да']:
        default_path = "C:/Users/New/Desktop/пдф"
        folder = get_folder_path(
            "Выберите папку с PDF:",
            default_path
        )
        
        if folder:
            import subprocess
            subprocess.run([sys.executable, "aggregate_json.py", str(folder)])
        else:
            subprocess.run([sys.executable, "aggregate_json.py"])
    else:
        print("\nЗапуск агрегации только с JSON данными...")
        import subprocess
        subprocess.run([sys.executable, "aggregate_json.py"])

def run_calculator():
    """Запустить калькулятор CLI"""
    print("\n" + "="*60)
    print("  [ZAPUSK KALKULYATORA]")
    print("="*60)
    
    import subprocess
    subprocess.run([sys.executable, "calculator_cli.py"])

def run_web():
    """Запустить Web версию"""
    print("\n" + "="*60)
    print("🌐 WEB КАЛЬКУЛЯТОР")
    print("="*60)
    
    app_path = Path(__file__).parent / "app" / "index.html"
    
    if app_path.exists():
        print(f"\nОткрываю: {app_path}")
        import webbrowser
        webbrowser.open(f"file:///{app_path}")
    else:
        print("❌ Файл не найден!")

def check_ocr():
    """Проверить OCR"""
    print("\n" + "="*60)
    print("⚙️  ПРОВЕРКА OCR КОМПОНЕНТОВ")
    print("="*60)
    
    import subprocess
    subprocess.run([sys.executable, "check_ocr.py"])

def main():
    """Главная функция"""
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    while True:
        show_banner()
        show_menu()
        
        try:
            choice = input("\nВыберите действие (1-6): ").strip()
            
            if choice == '1':
                run_ocr()
            elif choice == '2':
                run_aggregate()
            elif choice == '3':
                run_calculator()
            elif choice == '4':
                run_web()
            elif choice == '5':
                check_ocr()
            elif choice == '6':
                print("\n👋 До свидания!")
                break
            else:
                print("\n❌ Неверный выбор!")
            
            input("\nНажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            input("\nНажмите Enter для продолжения...")

if __name__ == '__main__':
    main()
