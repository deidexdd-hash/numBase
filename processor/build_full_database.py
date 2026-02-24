#!/usr/bin/env python3
"""
ИЗВЛЕЧЕНИЕ ТЕКСТА ИЗ ВСЕХ PDF С OCR
Создает полнотекстовую базу данных SQLite с распознаванием сканов.
"""

import os
import re
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Пути
PDF_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Users/New/Desktop/пдф")
OUTPUT_DIR = Path("knowledge_base_v2/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class OCRProcessor:
    """OCR обработка для сканированных PDF"""
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
        
    def _check_tesseract(self) -> bool:
        """Проверить доступность Tesseract"""
        try:
            import pytesseract
            # Проверяем версию
            version = pytesseract.get_tesseract_version()
            print(f"  ✓ Tesseract найден: {version}")
            
            # Проверяем наличие русского языка
            langs = pytesseract.get_languages()
            if 'rus' in langs:
                print(f"  ✓ Русский язык доступен")
                return True
            else:
                print(f"  ⚠ Русский язык не установлен! Доступны: {langs}")
                print(f"    Установите: tesseract-ocr-rus")
                return False
        except Exception as e:
            print(f"  ⚠ Tesseract не найден: {e}")
            print(f"    Установите Tesseract-OCR с русским языком")
            print(f"    См. инструкцию: OCR_SETUP.md")
            return False
    
    def extract_with_ocr(self, pdf_path: Path, dpi: int = 300) -> str:
        """Извлечь текст из PDF используя OCR"""
        if not self.tesseract_available:
            return ""
        
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            print(f"    OCR обработка ({dpi} DPI)...", end=" ", flush=True)
            
            text = ""
            images = convert_from_path(pdf_path, dpi=dpi, poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
            
            for i, image in enumerate(images, 1):
                # Распознаем с русским языком
                page_text = pytesseract.image_to_string(
                    image, 
                    lang='rus',
                    config='--psm 6'  # Предполагаем один блок текста
                )
                text += page_text + "\n"
                print(f"{i}", end="", flush=True)
            
            print(f" ✓")
            return text
            
        except Exception as e:
            print(f"\n    ✗ Ошибка OCR: {e}")
            return ""

class PDFTextExtractor:
    """Извлечение текста из PDF с OCR fallback"""
    
    def __init__(self):
        self.pdf_dir = PDF_DIR
        self.total_files = 0
        self.processed = 0
        self.ocr_processed = 0
        self.errors = 0
        self.ocr = OCRProcessor()
        
    def get_all_pdfs(self) -> List[Path]:
        """Получить список всех PDF"""
        files = [f for f in self.pdf_dir.iterdir() 
                if f.suffix.lower() == '.pdf']
        return sorted(files, key=lambda x: x.name.lower())
    
    def extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Извлечь текст используя PyPDF2"""
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"    Ошибка PyPDF2: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Очистить текст от лишних символов"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы и переносы
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Удаляем управляющие символы
        text = ''.join(char for char in text if char.isprintable() or char == '\n')
        
        # Удаляем OCR-артефакты
        text = re.sub(r'[_|]{3,}', '', text)  # Линии разделители
        
        return text.strip()
    
    def extract_from_pdf(self, pdf_path: Path) -> Tuple[str, Dict]:
        """Извлечь текст и метаданные из PDF"""
        stats = {
            'filename': pdf_path.name,
            'pages': 0,
            'chars': 0,
            'method': 'none',
            'status': 'ok'
        }
        
        # Пробуем PyPDF2 сначала
        text = self.extract_with_pypdf2(pdf_path)
        
        if text.strip() and len(text) > 100:
            # Текстовый PDF - используем как есть
            stats['method'] = 'text'
            text = self.clean_text(text)
            stats['chars'] = len(text)
        else:
            # Сканированный PDF - используем OCR
            print(f"    (скан - запускаю OCR...)")
            text = self.ocr.extract_with_ocr(pdf_path, dpi=300)
            
            if text.strip():
                stats['method'] = 'ocr'
                stats['chars'] = len(text)
                self.ocr_processed += 1
            else:
                stats['method'] = 'failed'
                stats['status'] = 'empty_after_ocr'
        
        return text, stats
    
    def categorize_content(self, text: str, filename: str) -> List[str]:
        """Определить категории содержимого"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        categories = {
            'numerology': ['число', 'цифра', 'нумеролог', 'рождения', 'путь жизни', 'судьба'],
            'calculations': ['расчет', 'расчёт', 'формула', 'вычисл', 'алгоритм', 'точка'],
            'practices': ['практика', 'медитация', 'молитва', 'техника', 'ритуал', 'поклон'],
            'diagnostics': ['диагностика', 'анализ', 'карта', 'генограмма', 'прокляти'],
            'ancestral': ['род', 'родовой', 'предки', 'семья', 'поколен', 'родитель'],
            'financial': ['деньги', 'финанс', 'бизнес', 'инвестиции', 'доход', 'канал'],
            'health': ['здоровье', 'болезнь', 'травма', 'исцеление', 'психолог'],
            'relationships': ['отношения', 'брак', 'партнер', 'семья', 'близнец'],
            'energy': ['чакр', 'энерг', 'канал', 'поток', 'вибрац'],
            'psychology': ['психолог', 'травма', 'внутренний', 'ребенок', 'сценарий']
        }
        
        detected = []
        for cat, keywords in categories.items():
            score = sum(2 for kw in keywords if kw in text_lower)
            score += sum(3 for kw in keywords if kw in filename_lower)
            if score > 2:
                detected.append((cat, score))
        
        detected.sort(key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in detected[:3]]
    
    def determine_type(self, filename: str) -> str:
        """Определить тип документа"""
        fname = filename.lower()
        
        type_patterns = {
            'calculator': ['расчет', 'расчёт', 'калькулятор'],
            'practice': ['практика', 'медитация', 'молитва'],
            'algorithm': ['алгоритм', 'схема', 'выбор', 'структура'],
            'template': ['карта', 'генограмма', 'матрица'],
            'reference': ['сборник', 'книга', 'значения'],
            'guide': ['как', 'руководство', 'инструкция']
        }
        
        for doc_type, patterns in type_patterns.items():
            if any(p in fname for p in patterns):
                return doc_type
        return 'reference'

class SQLiteBuilder:
    """Создание SQLite базы данных"""
    
    def __init__(self):
        self.db_path = OUTPUT_DIR / "knowledge_base.db"
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Подключиться к базе"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def create_tables(self):
        """Создать таблицы"""
        # Основная таблица документов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                title TEXT,
                doc_type TEXT,
                categories TEXT,
                content TEXT,
                content_length INTEGER,
                extraction_method TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для полнотекстового поиска
        self.cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                filename,
                title,
                content,
                content='documents',
                content_rowid='id'
            )
        ''')
        
        # Триггеры для синхронизации FTS
        self.cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, filename, title, content)
                VALUES (new.id, new.filename, new.title, new.content);
            END
        ''')
        
        self.cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, filename, title, content)
                VALUES ('delete', old.id, old.filename, old.title, old.content);
            END
        ''')
        
        # Таблица индекса категорий
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_index (
                category TEXT,
                doc_id INTEGER,
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            )
        ''')
        
        self.conn.commit()
        
    def insert_document(self, filename: str, title: str, doc_type: str, 
                       categories: List[str], content: str, content_length: int,
                       extraction_method: str) -> int:
        """Добавить документ в базу"""
        self.cursor.execute('''
            INSERT INTO documents 
            (filename, title, doc_type, categories, content, content_length, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filename, title, doc_type, json.dumps(categories), content, content_length, extraction_method))
        
        doc_id = self.cursor.lastrowid
        
        # Добавить в индекс категорий
        for cat in categories:
            self.cursor.execute(
                'INSERT INTO category_index (category, doc_id) VALUES (?, ?)',
                (cat, doc_id)
            )
        
        self.conn.commit()
        return doc_id
    
    def get_stats(self) -> Dict:
        """Получить статистику"""
        self.cursor.execute('SELECT COUNT(*), SUM(content_length) FROM documents')
        total, total_chars = self.cursor.fetchone()
        
        self.cursor.execute('''
            SELECT doc_type, COUNT(*) FROM documents GROUP BY doc_type
        ''')
        by_type = dict(self.cursor.fetchall())
        
        self.cursor.execute('''
            SELECT extraction_method, COUNT(*) FROM documents GROUP BY extraction_method
        ''')
        by_method = dict(self.cursor.fetchall())
        
        self.cursor.execute('''
            SELECT category, COUNT(DISTINCT doc_id) 
            FROM category_index 
            GROUP BY category
        ''')
        by_category = dict(self.cursor.fetchall())
        
        return {
            'total_documents': total,
            'total_chars': total_chars,
            'total_mb': round(total_chars / (1024 * 1024), 2),
            'by_type': by_type,
            'by_method': by_method,
            'by_category': by_category
        }
    
    def close(self):
        """Закрыть соединение"""
        if self.conn:
            self.conn.close()

class HybridKnowledgeBuilder:
    """Главный строитель гибридной базы знаний"""
    
    def __init__(self):
        self.extractor = PDFTextExtractor()
        self.db = SQLiteBuilder()
        self.stats = {
            'processed': 0,
            'errors': 0,
            'empty': 0,
            'total_chars': 0
        }
        
    def build(self):
        """Построить полную базу знаний"""
        print("=" * 80)
        print("СОЗДАНИЕ ПОЛНОТЕКСТОВОЙ БАЗЫ ДАННЫХ С OCR")
        print("Извлечение текста из всех PDF")
        print("=" * 80)
        print()
        
        # Проверяем OCR
        print("Проверка OCR:")
        if self.extractor.ocr.tesseract_available:
            print("  ✓ Tesseract с русским языком доступен")
            print("  ✓ OCR будет выполнен для сканированных PDF")
        else:
            print("  ⚠ Tesseract не найден - см. OCR_SETUP.md")
            print("  ⚠ Сканированные PDF будут пропущены")
        print()
        
        # Получаем список файлов
        pdfs = self.extractor.get_all_pdfs()
        total = len(pdfs)
        print(f"Найдено PDF файлов: {total}")
        print(f"Примерный размер: ~210 MB")
        print()
        
        # Подключаемся к БД
        print("Создание SQLite базы данных...")
        self.db.connect()
        self.db.create_tables()
        print("✓ База данных создана")
        print()
        
        # Обрабатываем каждый PDF
        print("Извлечение текста из PDF...")
        print("-" * 80)
        
        for i, pdf_path in enumerate(pdfs, 1):
            print(f"[{i:2d}/{total}] {pdf_path.name[:45]}...", end=" ", flush=True)
            
            try:
                # Извлекаем текст (с OCR при необходимости)
                text, file_stats = self.extractor.extract_from_pdf(pdf_path)
                
                if not text.strip():
                    self.stats['empty'] += 1
                    print(f"⚠ (пустой)")
                    continue
                
                # Категоризируем
                categories = self.extractor.categorize_content(text, pdf_path.name)
                doc_type = self.extractor.determine_type(pdf_path.name)
                
                # Добавляем в базу
                doc_id = self.db.insert_document(
                    filename=pdf_path.name,
                    title=pdf_path.stem.replace('_', ' '),
                    doc_type=doc_type,
                    categories=categories,
                    content=text,
                    content_length=len(text),
                    extraction_method=file_stats['method']
                )
                
                self.stats['processed'] += 1
                self.stats['total_chars'] += len(text)
                method_icon = "📝" if file_stats['method'] == 'text' else "🔍"
                print(f"{method_icon} {len(text):,} символов")
                
            except Exception as e:
                self.stats['errors'] += 1
                print(f"✗ Ошибка: {e}")
        
        print()
        print("-" * 80)
        print("ИТОГИ ОБРАБОТКИ:")
        print(f"  Обработано: {self.stats['processed']}")
        print(f"  Пустых: {self.stats['empty']}")
        print(f"  Ошибок: {self.stats['errors']}")
        print(f"  OCR обработано: {self.extractor.ocr_processed}")
        print(f"  Всего символов: {self.stats['total_chars']:,}")
        print()
        
        # Статистика базы
        db_stats = self.db.get_stats()
        print("СТАТИСТИКА БАЗЫ ДАННЫХ:")
        print(f"  Документов: {db_stats['total_documents']}")
        print(f"  Объем текста: {db_stats['total_mb']:.2f} MB")
        print(f"  По методам: {db_stats['by_method']}")
        print(f"  По типам: {db_stats['by_type']}")
        print()
        
        # Создаем мастер-индекс
        self._create_master_index(db_stats)
        
        self.db.close()
        print("✅ Готово! База данных создана.")
        
    def _create_master_index(self, db_stats: Dict):
        """Создать мастер-индекс всех данных"""
        master_index = {
            "version": "2.1",
            "created": datetime.now().isoformat(),
            "ocr_enabled": self.extractor.ocr.tesseract_available,
            "structure": {
                "lightweight": {
                    "description": "Лёгкие JSON для калькулятора",
                    "files": [
                        "formulas.json (15 формул)",
                        "practices.json (8 практик)",
                        "number_meanings.json (11 значений)",
                        "algorithms.json (2 алгоритма)"
                    ],
                    "size_kb": 41
                },
                "fulltext": {
                    "description": "Полнотекстовая база SQLite с OCR",
                    "file": "knowledge_base.db",
                    "documents": db_stats['total_documents'],
                    "size_mb": db_stats['total_mb'],
                    "extraction_methods": db_stats['by_method'],
                    "categories": list(db_stats['by_category'].keys())
                }
            }
        }
        
        with open(OUTPUT_DIR / 'master_index.json', 'w', encoding='utf-8') as f:
            json.dump(master_index, f, ensure_ascii=False, indent=2)
        
        print("✓ Мастер-индекс обновлен")

def main():
    builder = HybridKnowledgeBuilder()
    builder.build()
    
    print("\n" + "=" * 80)
    print("ГИБРИДНАЯ СИСТЕМА ГОТОВА!")
    print("=" * 80)
    print()
    print("Создано:")
    print("  📄 Lightweight: JSON файлы (41 KB) - для калькулятора")
    print("  🗄️  Full-text: SQLite база - для поиска по всем PDF (с OCR)")
    print()
    print("Использование:")
    print("  Калькулятор → knowledge_base.py + data/*.json")
    print("  Поиск → SQLite knowledge_base.db")
    print()
    print("Запустить тест:")
    print("  python knowledge_base.py")

if __name__ == '__main__':
    main()
