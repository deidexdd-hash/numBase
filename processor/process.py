#!/usr/bin/env python3
"""
ИНСТРУМЕНТ ОБРАБОТКИ PDF
Конвертирует все PDF файлы в структурированные данные для быстрого доступа.
Запускать один раз для подготовки данных.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Конфигурация
PDF_DIR = Path("C:/Users/New/Desktop/пдф")
OUTPUT_DIR = Path("knowledge_base_v2/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Formula:
    """Структура формулы расчета"""
    name: str
    formula: str
    description: str
    example: str
    inputs: List[str]
    output: str
    source_file: str
    category: str

@dataclass
class Calculator:
    """Структура калькулятора"""
    name: str
    description: str
    formula_ref: str
    inputs: List[Dict]
    output_type: str
    source_file: str

@dataclass
class Practice:
    """Структура практики/техники"""
    name: str
    description: str
    steps: List[str]
    duration: str
    source_file: str
    category: str

@dataclass
class KnowledgeItem:
    """Структура элемента знаний"""
    title: str
    content: str
    category: str
    subcategory: str
    source_file: str
    tags: List[str]

class PDFExtractor:
    """Извлечение текста из PDF"""
    
    def __init__(self):
        self.pdf_dir = PDF_DIR
        
    def get_all_pdfs(self) -> List[Path]:
        """Получить список всех PDF"""
        files = [f for f in self.pdf_dir.iterdir() 
                if f.suffix.lower() == '.pdf']
        return sorted(files, key=lambda x: x.name.lower())
    
    def extract_text(self, pdf_path: Path) -> str:
        """Извлечь текст из PDF файла"""
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"  Ошибка извлечения {pdf_path.name}: {e}")
            return ""

class FormulaExtractor:
    """Извлечение формул и расчетов из текста"""
    
    def __init__(self):
        # Шаблоны формул
        self.patterns = {
            'birth_number': {
                'patterns': [r'число рождения', r'день рождения', r'цифра дня'],
                'formula': 'День рождения → сведение к однозначному',
                'inputs': ['day'],
                'example': '25 → 2+5 = 7'
            },
            'life_path': {
                'patterns': [r'путь жизни', r'жизненный путь'],
                'formula': 'ДД + ММ + ГГГГ → сведение к однозначному',
                'inputs': ['day', 'month', 'year'],
                'example': '15+06+1990=2011 → 2+0+1+1 = 4'
            },
            'destiny_number': {
                'patterns': [r'число судьбы', r'по фио', r'по имени'],
                'formula': 'Сумма букв ФИО по таблице → сведение',
                'inputs': ['fullname'],
                'example': 'ИВАН = 9+3+1+6 = 19 → 1'
            },
            'soul_number': {
                'patterns': [r'число души', r'души'],
                'formula': 'Сумма гласных букв ФИО → сведение',
                'inputs': ['fullname'],
                'example': 'Гласные в имени → сумма'
            },
            'financial_channel': {
                'patterns': [r'финансовый канал', r'точки входа'],
                'formula': 'A=День, B=Месяц, C=Сумма(Год), D=A+B+C',
                'inputs': ['day', 'month', 'year'],
                'example': 'A=15, B=6, C=28, D=49→4'
            },
            'chakras': {
                'patterns': [r'чакр', r'энергетическ'],
                'formula': 'Соседние цифры даты рождения',
                'inputs': ['day', 'month', 'year'],
                'example': '15061990 → 1+5, 5+0, 0+6...'
            },
            'generational': {
                'patterns': [r'поколений', r'программа поколений'],
                'formula': 'Сумма всех цифр даты → аркан (1-22)',
                'inputs': ['day', 'month', 'year'],
                'example': '1+5+0+6+1+9+9+0=31→4'
            }
        }
    
    def extract_from_text(self, text: str, filename: str) -> List[Formula]:
        """Извлечь формулы из текста"""
        formulas = []
        text_lower = text.lower()
        
        for formula_id, info in self.patterns.items():
            # Проверяем паттерны
            for pattern in info['patterns']:
                if pattern in text_lower:
                    # Определяем категорию
                    category = self._determine_category(text_lower, filename)
                    
                    formula = Formula(
                        name=self._format_name(formula_id),
                        formula=info['formula'],
                        description=self._extract_description(text, pattern),
                        example=info['example'],
                        inputs=info['inputs'],
                        output='number',
                        source_file=filename,
                        category=category
                    )
                    formulas.append(formula)
                    break
        
        return formulas
    
    def _determine_category(self, text: str, filename: str) -> str:
        """Определить категорию формулы"""
        if 'финанс' in text or 'деньг' in text or 'бизнес' in filename.lower():
            return 'financial'
        elif 'чакр' in text or 'энерг' in text:
            return 'energy'
        elif 'род' in text or 'предк' in text or 'ансест' in filename.lower():
            return 'ancestral'
        elif 'фио' in text or 'им' in text:
            return 'name'
        else:
            return 'numerology'
    
    def _format_name(self, formula_id: str) -> str:
        """Форматировать название формулы"""
        names = {
            'birth_number': 'Число рождения',
            'life_path': 'Путь жизни',
            'destiny_number': 'Число судьбы',
            'soul_number': 'Число души',
            'financial_channel': 'Финансовый канал',
            'chakras': 'Баланс чакр',
            'generational': 'Программа поколений'
        }
        return names.get(formula_id, formula_id)
    
    def _extract_description(self, text: str, pattern: str) -> str:
        """Извлечь описание формулы из текста"""
        # Ищем предложение с паттерном
        sentences = text.split('.')
        for sentence in sentences:
            if pattern in sentence.lower():
                return sentence.strip()[:200]
        return "Описание формулы"

class ContentCategorizer:
    """Категоризация контента"""
    
    def __init__(self):
        self.categories = {
            'numerology': {
                'keywords': ['число', 'цифра', 'нумеролог', 'рождения'],
                'weight': 0
            },
            'calculations': {
                'keywords': ['расчет', 'расчёт', 'формула', 'вычисл', 'алгоритм'],
                'weight': 0
            },
            'practices': {
                'keywords': ['практика', 'медитация', 'молитва', 'техника', 'ритуал'],
                'weight': 0
            },
            'diagnostics': {
                'keywords': ['диагностика', 'анализ', 'карта', 'генограмма', 'тест'],
                'weight': 0
            },
            'ancestral': {
                'keywords': ['род', 'родовой', 'предки', 'ансестолог', 'семья'],
                'weight': 0
            },
            'financial': {
                'keywords': ['деньги', 'финанс', 'бизнес', 'инвестиции', 'доход'],
                'weight': 0
            },
            'health': {
                'keywords': ['здоровье', 'болезнь', 'травма', 'исцеление'],
                'weight': 0
            },
            'relationships': {
                'keywords': ['отношения', 'брак', 'партнер', 'семья'],
                'weight': 0
            }
        }
    
    def categorize(self, text: str, filename: str) -> List[str]:
        """Категоризировать документ"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        detected = []
        
        for cat, info in self.categories.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in text_lower:
                    score += 2
                if keyword in filename_lower:
                    score += 3
            
            if score > 0:
                detected.append((cat, score))
        
        # Сортируем по весу
        detected.sort(key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in detected[:3]]  # Топ-3 категории
    
    def determine_type(self, filename: str) -> str:
        """Определить тип документа по названию"""
        fname = filename.lower()
        
        if any(x in fname for x in ['расчет', 'расчёт', 'калькулятор']):
            return 'calculator'
        elif any(x in fname for x in ['практика', 'медитация', 'молитва']):
            return 'practice'
        elif any(x in fname for x in ['алгоритм', 'схема', 'выбор']):
            return 'algorithm'
        elif any(x in fname for x in ['карта', 'генограмма', 'матрица']):
            return 'template'
        elif any(x in fname for x in ['сборник', 'книга', 'глава']):
            return 'collection'
        else:
            return 'reference'

class DataProcessor:
    """Главный процессор данных"""
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.formula_extractor = FormulaExtractor()
        self.categorizer = ContentCategorizer()
        
        # Хранилища данных
        self.formulas_db = []
        self.calculators_db = []
        self.practices_db = []
        self.knowledge_db = []
        self.index_db = {
            'by_category': {},
            'by_type': {},
            'by_keyword': {}
        }
    
    def process_all(self):
        """Обработать все PDF файлы"""
        pdfs = self.extractor.get_all_pdfs()
        total = len(pdfs)
        
        print(f"\nНАЙДЕНО PDF ФАЙЛОВ: {total}")
        print("=" * 60)
        
        for i, pdf_path in enumerate(pdfs, 1):
            print(f"\n[{i:2d}/{total}] Обработка: {pdf_path.name}")
            self._process_single_pdf(pdf_path)
        
        print("\n" + "=" * 60)
        print("СТАТИСТИКА ОБРАБОТКИ:")
        print(f"  Формул найдено: {len(self.formulas_db)}")
        print(f"  Калькуляторов: {len(self.calculators_db)}")
        print(f"  Практик: {len(self.practices_db)}")
        print(f"  Записей знаний: {len(self.knowledge_db)}")
        
        self._save_all_data()
    
    def _process_single_pdf(self, pdf_path: Path):
        """Обработать один PDF"""
        filename = pdf_path.name
        
        # Извлечение текста
        text = self.extractor.extract_text(pdf_path)
        
        if not text:
            print("  ⚠ Пустой или сканированный PDF")
            return
        
        print(f"  ✓ Извлечено {len(text)} символов")
        
        # Категоризация
        categories = self.categorizer.categorize(text, filename)
        doc_type = self.categorizer.determine_type(filename)
        
        print(f"  Категории: {', '.join(categories) if categories else 'не определены'}")
        print(f"  Тип: {doc_type}")
        
        # Извлечение формул
        formulas = self.formula_extractor.extract_from_text(text, filename)
        if formulas:
            print(f"  Найдено формул: {len(formulas)}")
            self.formulas_db.extend(formulas)
        
        # Создание записи знаний
        knowledge_item = KnowledgeItem(
            title=pdf_path.stem.replace('_', ' '),
            content=text[:10000],  # Ограничиваем размер
            category=categories[0] if categories else 'general',
            subcategory=categories[1] if len(categories) > 1 else '',
            source_file=filename,
            tags=categories
        )
        self.knowledge_db.append(knowledge_item)
        
        # Обновление индексов
        self._update_index(filename, doc_type, categories, len(self.knowledge_db)-1)
    
    def _update_index(self, filename: str, doc_type: str, categories: List[str], doc_id: int):
        """Обновить индексы"""
        # По типу
        if doc_type not in self.index_db['by_type']:
            self.index_db['by_type'][doc_type] = []
        self.index_db['by_type'][doc_type].append(doc_id)
        
        # По категориям
        for cat in categories:
            if cat not in self.index_db['by_category']:
                self.index_db['by_category'][cat] = []
            self.index_db['by_category'][cat].append(doc_id)
        
        # По ключевым словам из названия
        words = filename.lower().replace('.pdf', '').replace('_', ' ').split()
        for word in words:
            if len(word) > 3:
                if word not in self.index_db['by_keyword']:
                    self.index_db['by_keyword'][word] = []
                self.index_db['by_keyword'][word].append(doc_id)
    
    def _save_all_data(self):
        """Сохранить все данные в JSON"""
        print("\nСОХРАНЕНИЕ ДАННЫХ...")
        
        # Формулы
        formulas_data = [asdict(f) for f in self.formulas_db]
        self._save_json('formulas.json', formulas_data)
        
        # Знания
        knowledge_data = [asdict(k) for k in self.knowledge_db]
        self._save_json('knowledge.json', knowledge_data)
        
        # Индексы
        self._save_json('index.json', self.index_db)
        
        # Мастер-индекс
        master_index = {
            'metadata': {
                'processed_date': datetime.now().isoformat(),
                'total_files': len(self.knowledge_db),
                'total_formulas': len(self.formulas_db),
                'categories': list(self.index_db['by_category'].keys()),
                'types': list(self.index_db['by_type'].keys())
            },
            'files': [k.title for k in self.knowledge_db]
        }
        self._save_json('master_index.json', master_index)
        
        print(f"✓ Все данные сохранены в: {OUTPUT_DIR}")
    
    def _save_json(self, filename: str, data: Any):
        """Сохранить JSON файл"""
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ {filename}")

def main():
    print("=" * 60)
    print("ИНСТРУМЕНТ ОБРАБОТКИ PDF")
    print("Подготовка данных для базы знаний")
    print("=" * 60)
    
    processor = DataProcessor()
    processor.process_all()
    
    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("Данные сохранены и готовы к использованию.")
    print("=" * 60)

if __name__ == '__main__':
    main()
