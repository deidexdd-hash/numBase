#!/usr/bin/env python3
"""
OCR SCANNER - Распознавание сканированных PDF
Запуск: python run_ocr.py [папка_с_pdf]
"""

import sys
import os
from pathlib import Path

# Проверка версии Python
if sys.version_info >= (3, 14):
    print("⚠ Предупреждение: Python 3.14+ может не поддерживаться некоторыми библиотеками")
    print(f"  Ваша версия: {sys.version}")
    print("  Рекомендуется: Python 3.8-3.12")
    print()

# Проверка и установка зависимостей
print("Проверка OCR компонентов...")

# Пробуем импортировать
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    print("✓ Все библиотеки установлены")
    DEPS_OK = True
except ImportError as e:
    print(f"⚠ Некоторые библиотеки не найдены: {e}")
    print()
    print("Для работы OCR необходимо установить:")
    print("  pip install pytesseract pdf2image pillow")
    print()
    print("Или скачать готовые сборки Tesseract:")
    print("  https://github.com/UB-Mannheim/tesseract/wiki")
    print()
    
    install = input("Попробовать установить автоматически? (y/n): ").strip().lower()
    if install in ['y', 'yes', 'д', 'да']:
        print("Установка...")
        import subprocess
        try:
            # Устанавливаем без Pillow (может требовать компиляции)
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytesseract", "pdf2image"], check=True)
            print("✓ Установлено")
            # Пробуем снова
            try:
                import pytesseract
                from pdf2image import convert_from_path
                DEPS_OK = True
            except ImportError:
                print("✗ Не удалось импортировать после установки")
                DEPS_OK = False
        except Exception as e:
            print(f"✗ Ошибка установки: {e}")
            DEPS_OK = False
    else:
        DEPS_OK = False

def get_folder_path():
    """Получить путь к папке с PDF"""
    print("\n" + "="*60)
    print("ВЫБОР ПАПКИ С PDF ФАЙЛАМИ")
    print("="*60)
    print()
    
    # Показываем примеры путей
    print("Примеры путей:")
    print("  Windows: C:/Users/Имя/Documents/PDFs")
    print("  Windows: C:/Users/Имя/Desktop/пдф")
    print("  Linux/Mac: /home/имя/documents")
    print()
    
    # Спрашиваем путь
    default_path = "C:/Users/New/Desktop/пдф"
    user_input = input(f"Введите путь к папке с PDF [{default_path}]: ").strip()
    
    # Используем путь по умолчанию если ничего не ввели
    if not user_input:
        user_input = default_path
    
    # Нормализуем путь
    folder_path = Path(user_input).expanduser().resolve()
    
    # Проверяем существование
    if not folder_path.exists():
        print(f"\n❌ Ошибка: папка не найдена: {folder_path}")
        print("\nПопробуйте снова:")
        return get_folder_path()
    
    if not folder_path.is_dir():
        print(f"\n❌ Ошибка: это не папка: {folder_path}")
        return get_folder_path()
    
    # Проверяем наличие PDF
    pdf_files = list(folder_path.glob("*.pdf"))
    print(f"\n✓ Папка найдена: {folder_path}")
    print(f"✓ Найдено PDF файлов: {len(pdf_files)}")
    
    if len(pdf_files) == 0:
        print("\n⚠ В этой папке нет PDF файлов!")
        retry = input("Выбрать другую папку? (y/n): ").strip().lower()
        if retry in ['y', 'yes', 'д', 'да']:
            return get_folder_path()
        else:
            return None
    
    # Показываем первые 5 файлов
    print("\nНайденные файлы:")
    for i, pdf in enumerate(pdf_files[:5], 1):
        print(f"  {i}. {pdf.name}")
    if len(pdf_files) > 5:
        print(f"  ... и еще {len(pdf_files) - 5} файлов")
    
    # Подтверждение
    confirm = input(f"\nОбработать эти {len(pdf_files)} PDF? (y/n): ").strip().lower()
    if confirm in ['y', 'yes', 'д', 'да']:
        return folder_path
    else:
        return get_folder_path()

def check_tesseract():
    """Проверка Tesseract"""
    if not DEPS_OK:
        print("❌ Библиотеки не установлены")
        return False
        
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        langs = pytesseract.get_languages()
        if 'rus' in langs:
            print(f"✓ Tesseract {version} (русский язык доступен)")
            return True
        else:
            print("✗ Русский язык не установлен")
            print("  Установите Tesseract с русским языком")
            return False
    except Exception as e:
        print("✗ Tesseract не найден")
        print(r"""
Установите Tesseract-OCR:
1. Скачайте: https://github.com/UB-Mannheim/tesseract/wiki
2. При установке выберите "Russian"
3. Добавьте в PATH: C:\Program Files\Tesseract-OCR
""")
        return False

def ocr_pdf(pdf_path, output_dir=None):
    """Распознать один PDF"""
    if not DEPS_OK:
        print("❌ Библиотеки не загружены")
        return False
        
    pdf_path = Path(pdf_path)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{pdf_path.stem}.txt"
    else:
        output_file = pdf_path.with_suffix('.txt')
    
    print(f"\n📄 {pdf_path.name}")
    print(f"   Конвертация в изображения...", end=" ", flush=True)
    
    try:
        images = convert_from_path(pdf_path, dpi=300, poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
        print(f"✓ ({len(images)} стр)")
        
        print(f"   Распознавание текста...", end=" ", flush=True)
        text_parts = []
        
        for i, image in enumerate(images, 1):
            page_text = pytesseract.image_to_string(image, lang='rus', config='--psm 6')
            text_parts.append(page_text)
            print(f"{i}", end="", flush=True)
        
        full_text = "\n\n".join(text_parts)
        
        # Очистка текста
        full_text = full_text.replace('  ', ' ')
        full_text = '\n'.join(line.strip() for line in full_text.split('\n'))
        
        # Сохранение
        output_file.write_text(full_text, encoding='utf-8')
        print(f" ✓")
        print(f"   💾 Сохранено: {output_file} ({len(full_text)} символов)")
        
        return True
        
    except Exception as e:
        print(f"\n   ✗ Ошибка: {e}")
        return False

def process_directory(input_dir, output_dir=None):
    """Обработать все PDF в папке"""
    if not DEPS_OK:
        print("❌ Невозможно продолжить без библиотек")
        return
        
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        print(f"❌ Папка не найдена: {input_dir}")
        return
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ PDF файлы не найдены в: {input_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"НАЙДЕНО PDF: {len(pdf_files)}")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}]")
        if ocr_pdf(pdf_file, output_dir):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"✅ ГОТОВО!")
    print(f"   Успешно: {success}")
    print(f"   Ошибок: {failed}")
    if output_dir:
        print(f"   Результаты сохранены в: {output_dir}")
    print(f"{'='*60}")

def main():
    # Проверка Tesseract
    if not check_tesseract():
        print("\n❌ OCR не готов к работе")
        print("Установите Tesseract-OCR с русским языком")
        sys.exit(1)
    
    # Определение папки
    if len(sys.argv) > 1:
        if sys.argv[1] == '--file':
            # Один файл
            if len(sys.argv) > 2:
                pdf_file = sys.argv[2]
                ocr_pdf(pdf_file)
            else:
                print("Укажите файл: python run_ocr.py --file document.pdf")
        else:
            # Папка из аргументов
            input_dir = sys.argv[1]
            output_dir = Path(input_dir) / "ocr_results"
            process_directory(input_dir, output_dir)
    else:
        # Интерактивный выбор
        input_dir = get_folder_path()
        if input_dir:
            output_dir = input_dir / "ocr_results"
            process_directory(input_dir, output_dir)
        else:
            print("\nОтменено пользователем")

if __name__ == '__main__':
    main()
    input("\nНажмите Enter для выхода...")
