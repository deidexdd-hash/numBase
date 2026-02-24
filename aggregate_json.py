#!/usr/bin/env python3
"""
AGGREGATE JSON - Агрегация всех данных в JSON
Запуск: python aggregate_json.py [папка_с_pdf]

Создает единый JSON файл со всеми данными.
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# Пути
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = DATA_DIR / "complete_knowledge_base.json"

def get_pdf_folder():
    """Получить путь к папке с PDF"""
    print("\n" + "="*60)
    print("ВЫБОР ПАПКИ С PDF (для OCR)")
    print("="*60)
    print()
    print("Если у вас есть сканированные PDF, укажите путь к ним.")
    print("Если оставить пустым, будет использована только база формул.")
    print()
    print("Примеры путей:")
    print("  Windows: C:/Users/Имя/Desktop/пдф")
    print("  Linux/Mac: /home/имя/documents/pdfs")
    print()
    
    default_path = "C:/Users/New/Desktop/пдф"
    user_input = input(f"Путь к PDF (Enter для пропуска) [{default_path}]: ").strip()
    
    if not user_input:
        print("\n⚠ Пропускаем PDF, используем только JSON данные")
        return None
    
    folder_path = Path(user_input).expanduser().resolve()
    
    if not folder_path.exists():
        print(f"\n❌ Папка не найдена: {folder_path}")
        retry = input("Попробовать снова? (y/n): ").strip().lower()
        if retry in ['y', 'yes', 'д', 'да']:
            return get_pdf_folder()
        else:
            print("⚠ Пропускаем PDF")
            return None
    
    pdf_files = list(folder_path.glob("*.pdf"))
    print(f"\n✓ Папка найдена: {folder_path}")
    print(f"✓ Найдено PDF: {len(pdf_files)}")
    
    return folder_path

def load_json(filename):
    """Загрузить JSON файл"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_from_sqlite():
    """Загрузить данные из SQLite"""
    db_path = DATA_DIR / "knowledge_base.db"
    documents = []
    
    if not db_path.exists():
        print("⚠ SQLite база не найдена")
        return documents
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, title, doc_type, categories, content, content_length
            FROM documents
        ''')
        
        for row in cursor.fetchall():
            doc = {
                'id': row['id'],
                'filename': row['filename'],
                'title': row['title'],
                'type': row['doc_type'],
                'categories': json.loads(row['categories']) if row['categories'] else [],
                'content': row['content'],
                'content_length': row['content_length']
            }
            documents.append(doc)
        
        conn.close()
        print(f"✓ Загружено {len(documents)} документов из SQLite")
        
    except Exception as e:
        print(f"⚠ Ошибка загрузки SQLite: {e}")
    
    return documents

def load_from_txt(pdf_folder: Optional[Path] = None):
    """Загрузить данные из TXT файлов (результатов OCR)"""
    documents = []
    
    if not pdf_folder or not pdf_folder.exists():
        print("⚠ Папка с PDF не указана или не существует, пропускаем .txt")
        return documents
    
    txt_dir = pdf_folder / "ocr_results"
    if not txt_dir.exists():
        txt_dir = pdf_folder
    
    txt_files = list(txt_dir.glob("*.txt"))
    
    if not txt_files:
        print("⚠ TXT файлы не найдены")
        return documents
    
    print(f"✓ Найдено {len(txt_files)} TXT файлов")
    
    for i, txt_file in enumerate(txt_files, 1):
        try:
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            filename = txt_file.stem + ".pdf"
            
            doc = {
                'id': i,
                'filename': filename,
                'title': txt_file.stem,
                'type': 'pdf',
                'categories': [],
                'content': content,
                'content_length': len(content)
            }
            documents.append(doc)
            
        except Exception as e:
            print(f"⚠ Ошибка чтения {txt_file.name}: {e}")
    
    print(f"✓ Загружено {len(documents)} документов из TXT")
    return documents

def load_from_html(pdf_folder: Optional[Path] = None):
    """Загрузить данные из HTML файлов"""
    documents = []
    
    if not pdf_folder or not pdf_folder.exists():
        return documents
    
    html_files = list(pdf_folder.glob("*.html")) + list(pdf_folder.glob("*.htm"))
    
    if not html_files:
        return documents
    
    print(f"✓ Найдено {len(html_files)} HTML файлов")
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("⚠ Установите beautifulsoup4 для обработки HTML: pip install beautifulsoup4")
        return documents
    
    for i, html_file in enumerate(html_files, 1):
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Извлекаем текст из HTML
            text = soup.get_text(separator='\n', strip=True)
            
            doc = {
                'id': 10000 + i,  # ID > 10000 для HTML
                'filename': html_file.name,
                'title': html_file.stem,
                'type': 'html',
                'categories': [],
                'content': text,
                'content_length': len(text)
            }
            documents.append(doc)
            
        except Exception as e:
            print(f"⚠ Ошибка чтения {html_file.name}: {e}")
    
    print(f"✓ Загружено {len(documents)} документов из HTML")
    return documents

def save_to_sqlite(documents: List[Dict]):
    """Сохранить документы в SQLite"""
    if not documents:
        return
    
    db_path = DATA_DIR / "knowledge_base.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Создаем таблицу если нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                filename TEXT,
                title TEXT,
                doc_type TEXT,
                categories TEXT,
                content TEXT,
                content_length INTEGER
            )
        ''')
        
        for doc in documents:
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (filename, title, doc_type, categories, content, content_length)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                doc.get('filename', ''),
                doc.get('title', ''),
                doc.get('type', 'pdf'),
                json.dumps(doc.get('categories', [])),
                doc.get('content', ''),
                doc.get('content_length', 0)
            ))
        
        conn.commit()
        conn.close()
        print(f"✓ Сохранено {len(documents)} документов в SQLite")
        
    except Exception as e:
        print(f"⚠ Ошибка сохранения в SQLite: {e}")

def check_ocr_available():
    """Проверить доступность OCR"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except:
        return False

def run_ocr_if_needed(pdf_folder):
    """Создать SQLite базу из PDF"""
    if not pdf_folder:
        return False
    
    db_path = DATA_DIR / "knowledge_base.db"
    
    # Проверяем есть ли уже база
    if db_path.exists():
        print(f"\n⚠ База данных уже существует: {db_path}")
        choice = input("Пересоздать? (y/n): ").strip().lower()
        if choice not in ['y', 'yes', 'д', 'да']:
            print("Используем существующую базу")
            return True
    
    # Проверяем OCR
    if not check_ocr_available():
        print("\n❌ OCR не доступен!")
        print("Для распознавания PDF установите:")
        print("  1. Tesseract-OCR с русским языком")
        print("  2. Python библиотеки: pip install pytesseract pdf2image pillow")
        print("\nПродолжить без OCR? (будут использованы только JSON данные)")
        choice = input("(y/n): ").strip().lower()
        if choice not in ['y', 'yes', 'д', 'да']:
            print("Отменено")
            return False
        return True
    
    # Создаем SQLite базу из PDF
    print("\n" + "="*60)
    print("СОЗДАНИЕ БАЗЫ ДАННЫХ ИЗ PDF")
    print("="*60)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "processor/build_full_database.py", str(pdf_folder)],
            cwd=Path(__file__).parent
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def aggregate():
    """Создать полную агрегацию данных"""
    print("=" * 60)
    print("АГРЕГАЦИЯ ДАННЫХ В JSON")
    print("=" * 60)
    print()
    
    # Определяем папку с PDF
    pdf_folder = None
    if len(sys.argv) > 1:
        # Путь из аргументов
        pdf_folder = Path(sys.argv[1])
        print(f"✓ Используем папку: {pdf_folder}")
    else:
        # Интерактивный выбор
        pdf_folder = get_pdf_folder()
    
    # Запускаем OCR если нужно
    if pdf_folder:
        run_ocr_if_needed(pdf_folder)
    
    # Загружаем данные
    print("\n" + "="*60)
    print("ЗАГРУЗКА ДАННЫХ")
    print("="*60)
    
    # Загружаем из SQLite
    documents = load_from_sqlite()
    
    # Также обрабатываем TXT файлы и добавляем в базу
    if pdf_folder:
        txt_documents = load_from_txt(pdf_folder)
        if txt_documents:
            save_to_sqlite(txt_documents)
            # Объединяем с существующими
            existing_ids = {doc['id'] for doc in documents}
            for doc in txt_documents:
                if doc['id'] not in existing_ids:
                    documents.append(doc)
        
        # Обрабатываем HTML файлы
        html_documents = load_from_html(pdf_folder)
        if html_documents:
            save_to_sqlite(html_documents)
            existing_ids = {doc['id'] for doc in documents}
            for doc in html_documents:
                if doc['id'] not in existing_ids:
                    documents.append(doc)
    
    data = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'version': '2.0',
            'source': 'Ancestral Numerology Knowledge Base'
        },
        'formulas': load_json('formulas.json'),
        'practices': load_json('practices.json'),
        'number_meanings': load_json('number_meanings.json'),
        'algorithms': load_json('algorithms.json'),
        'documents': documents
    }
    
    # Статистика
    stats = {
        'formulas': len(data['formulas']),
        'practices': len(data['practices']),
        'number_meanings': len(data['number_meanings']),
        'algorithms': len(data['algorithms']),
        'documents': len(data['documents'])
    }
    
    print(f"\n📊 Статистика:")
    print(f"  Формул: {stats['formulas']}")
    print(f"  Практик: {stats['practices']}")
    print(f"  Значений чисел: {stats['number_meanings']}")
    print(f"  Алгоритмов: {stats['algorithms']}")
    print(f"  Документов PDF: {stats['documents']}")
    
    # Сохраняем
    print(f"\n💾 Сохранение в: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    file_size = OUTPUT_FILE.stat().st_size / 1024 / 1024
    print(f"✓ Готово! Размер файла: {file_size:.2f} MB")
    print()
    print("Использование:")
    print(f"  with open('{OUTPUT_FILE.name}', 'r', encoding='utf-8') as f:")
    print("      data = json.load(f)")
    print("      formulas = data['formulas']")
    print("      practices = data['practices']")
    print("      documents = data['documents']")

if __name__ == '__main__':
    aggregate()
    input("\nНажмите Enter для выхода...")
