"""
ГИБРИДНАЯ БИБЛИОТЕКА БАЗЫ ЗНАНИЙ
Работает с:
  - JSON файлами (41KB) - быстрый доступ к формулам
  - SQLite базой (полный текст из 83 PDF) - полнотекстовый поиск

Пример использования:
  from knowledge_base import HybridKnowledgeBase
  
  kb = HybridKnowledgeBase()
  
  # Быстрые расчеты
  result = kb.calculate_life_path(15, 6, 1990)
  
  # Полнотекстовый поиск
  docs = kb.search_documents("финансовый канал")
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).parent / "data"

class HybridKnowledgeBase:
    """Главный класс для работы с гибридной базой знаний"""
    
    def __init__(self):
        # Загружаем легкие JSON
        self.formulas = self._load_json('formulas.json')
        self.practices = self._load_json('practices.json')
        self.algorithms = self._load_json('algorithms.json')
        self.number_meanings = self._load_json('number_meanings.json')
        self.master_index = self._load_json('master_index.json')
        
        # Подключаемся к SQLite (опционально)
        self.db_conn = None
        self.db_cursor = None
        self._connect_db()
    
    def _load_json(self, filename: str) -> Any:
        """Загрузить JSON файл"""
        filepath = DATA_DIR / filename
        if not filepath.exists():
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _connect_db(self):
        """Подключиться к SQLite базе"""
        db_path = DATA_DIR / "knowledge_base.db"
        if db_path.exists():
            try:
                self.db_conn = sqlite3.connect(str(db_path))
                self.db_conn.row_factory = sqlite3.Row
                self.db_cursor = self.db_conn.cursor()
            except Exception as e:
                print(f"⚠ Не удалось подключиться к БД: {e}")
    
    # ========== LIGHTWEIGHT: ФОРМУЛЫ И РАСЧЕТЫ ==========
    
    def get_formula(self, formula_id: str) -> Optional[Dict]:
        """Получить формулу по ID"""
        for formula in self.formulas:
            if formula.get('id') == formula_id:
                return formula
        return None
    
    def find_formulas(self, query: str) -> List[Dict]:
        """Найти формулы по названию"""
        query = query.lower()
        results = []
        for formula in self.formulas:
            if (query in formula.get('name', '').lower() or 
                query in formula.get('description', '').lower()):
                results.append(formula)
        return results
    
    def calculate_birth_number(self, day: int) -> Dict:
        """Рассчитать число рождения"""
        result = self._reduce_to_single(day)
        return {
            'value': result,
            'formula': self.get_formula('birth_number'),
            'meaning': self.number_meanings.get(str(result))
        }
    
    def calculate_life_path(self, day: int, month: int, year: int) -> Dict:
        """Рассчитать путь жизни"""
        total = day + month + year
        result = self._reduce_to_single(total)
        
        return {
            'value': result,
            'details': {
                'day': day,
                'month': month, 
                'year': year,
                'total': total
            },
            'formula': self.get_formula('life_path'),
            'meaning': self.number_meanings.get(str(result))
        }
    
    def calculate_destiny_number(self, fullname: str) -> Dict:
        """Рассчитать число судьбы по ФИО"""
        # Russkij alfavit
        letter_table_ru = {
            'а': 1, 'б': 2, 'в': 3, 'г': 4, 'д': 5, 'е': 6, 'ё': 6,
            'ж': 7, 'з': 8, 'и': 9, 'й': 1, 'к': 2, 'л': 3, 'м': 4,
            'н': 5, 'о': 6, 'п': 7, 'р': 8, 'с': 9, 'т': 1, 'у': 2,
            'ф': 3, 'х': 4, 'ц': 5, 'ч': 6, 'ш': 7, 'щ': 8, 'ъ': 9,
            'ы': 1, 'ь': 2, 'э': 3, 'ю': 4, 'я': 5
        }
        
        # Latinskij alfavit (Chaldejskaya sistema)
        letter_table_en = {
            'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8,
            'i': 9, 'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7,
            'q': 8, 'r': 9, 's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6,
            'y': 7, 'z': 8
        }
        
        # Obedinjaem tablicy
        letter_table = {**letter_table_ru, **letter_table_en}
        
        total = sum(letter_table.get(c, 0) for c in fullname.lower() if c in letter_table)
        result = self._reduce_to_single(total)
        
        return {
            'value': result,
            'fullname': fullname,
            'total': total,
            'formula': self.get_formula('destiny_number'),
            'meaning': self.number_meanings.get(str(result))
        }
    
    def calculate_financial_channel(self, day: int, month: int, year: int) -> Dict:
        """Рассчитать финансовый канал"""
        A = day
        B = month
        C = sum(int(d) for d in str(year))
        D = self._reduce_to_single(A + B + C)
        
        return {
            'A': A, 'B': B, 'C': C, 'D': D,
            'formula': self.get_formula('financial_channel')
        }
    
    def calculate_chakras(self, day: int, month: int, year: int) -> Dict:
        """Рассчитать баланс чакр"""
        date_str = f"{day:02d}{month:02d}{year}"
        digits = [int(d) for d in date_str]
        
        chakras = {
            1: digits[0] + digits[1],  # Муладхара
            2: digits[1] + digits[2],  # Свадхистана
            3: digits[2] + digits[3],  # Манипура
            4: digits[3] + digits[4],  # Анахата
            5: digits[4] + digits[5],  # Вишудха
            6: digits[5] + digits[6],  # Аджна
            7: digits[6] + digits[7],  # Сахасрара
        }
        
        return {
            'chakras': chakras,
            'formula': self.get_formula('chakra_balance')
        }
    
    @staticmethod
    def _reduce_to_single(number: int) -> int:
        """Свести число к однозначному"""
        while number > 9 and number not in [11, 22, 33]:
            number = sum(int(d) for d in str(number))
        return number
    
    # ========== FULLTEXT: ПОИСК ПО PDF ==========
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Полнотекстовый поиск по всем PDF"""
        if not self.db_cursor:
            return []
        
        try:
            self.db_cursor.execute('''
                SELECT d.id, d.filename, d.title, d.doc_type, d.categories,
                       d.content_length
                FROM documents_fts
                JOIN documents d ON documents_fts.rowid = d.id
                WHERE documents_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (query, limit))
            
            results = []
            for row in self.db_cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'filename': row['filename'],
                    'title': row['title'],
                    'type': row['doc_type'],
                    'categories': json.loads(row['categories']) if row['categories'] else [],
                    'content_length': row['content_length']
                })
            return results
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """Получить полный текст документа по ID"""
        if not self.db_cursor:
            return None
        
        try:
            self.db_cursor.execute(
                'SELECT * FROM documents WHERE id = ?', (doc_id,)
            )
            row = self.db_cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'filename': row['filename'],
                    'title': row['title'],
                    'type': row['doc_type'],
                    'categories': json.loads(row['categories']) if row['categories'] else [],
                    'content': row['content'],
                    'content_length': row['content_length']
                }
        except Exception as e:
            print(f"Ошибка: {e}")
        return None
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Найти документы по категории"""
        if not self.db_cursor:
            return []
        
        try:
            self.db_cursor.execute('''
                SELECT d.id, d.filename, d.title, d.doc_type, d.categories
                FROM documents d
                JOIN category_index ci ON d.id = ci.doc_id
                WHERE ci.category = ?
            ''', (category,))
            
            results = []
            for row in self.db_cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'filename': row['filename'],
                    'title': row['title'],
                    'type': row['doc_type'],
                    'categories': json.loads(row['categories']) if row['categories'] else []
                })
            return results
        except Exception as e:
            print(f"Ошибка: {e}")
            return []
    
    def get_all_categories(self) -> List[str]:
        """Получить список всех категорий"""
        if not self.db_cursor:
            return []
        
        try:
            self.db_cursor.execute(
                'SELECT DISTINCT category FROM category_index ORDER BY category'
            )
            return [row[0] for row in self.db_cursor.fetchall()]
        except:
            return []
    
    # ========== СТАТИСТИКА ==========
    
    def get_stats(self) -> Dict:
        """Полная статистика"""
        stats = {
            'lightweight': {
                'formulas': len(self.formulas),
                'practices': len(self.practices),
                'algorithms': len(self.algorithms),
                'number_meanings': len(self.number_meanings),
                'size_kb': 41
            },
            'fulltext': None
        }
        
        if self.db_cursor:
            try:
                self.db_cursor.execute('SELECT COUNT(*), SUM(content_length) FROM documents')
                row = self.db_cursor.fetchone()
                stats['fulltext'] = {
                    'documents': row[0],
                    'total_chars': row[1],
                    'size_mb': round(row[1] / (1024 * 1024), 2) if row[1] else 0
                }
            except:
                pass
        
        return stats
    
    def close(self):
        """Zakryt soedinenie s bazoj dannyh"""
        if self.db_conn:
            self.db_conn.close()


# ========== ДЕМОНСТРАЦИЯ ==========

if __name__ == '__main__':
    print("=" * 70)
    print("ГИБРИДНАЯ БАЗА ЗНАНИЙ - ДЕМО")
    print("=" * 70)
    
    kb = HybridKnowledgeBase()
    
    # Статистика
    stats = kb.get_stats()
    print("\n📊 СТАТИСТИКА:")
    print(f"  JSON данные:")
    print(f"    • Формул: {stats['lightweight']['formulas']}")
    print(f"    • Практик: {stats['lightweight']['practices']}")
    print(f"    • Размер: {stats['lightweight']['size_kb']} KB")
    
    if stats['fulltext']:
        print(f"\n  SQLite база:")
        print(f"    • Документов: {stats['fulltext']['documents']}")
        print(f"    • Текста: {stats['fulltext']['total_chars']:,} символов")
        print(f"    • Размер: {stats['fulltext']['size_mb']} MB")
    
    # Расчет
    print("\n" + "=" * 70)
    print("🧮 РАСЧЕТЫ (из JSON - мгновенно):")
    print("=" * 70)
    
    life = kb.calculate_life_path(15, 6, 1990)
    print(f"\nПуть жизни: {life['value']}")
    print(f"  Значение: {life['meaning']['title']}")
    
    finance = kb.calculate_financial_channel(15, 6, 1990)
    print(f"\nФинансовый канал: D = {finance['D']}")
    print(f"  A={finance['A']}, B={finance['B']}, C={finance['C']}")
    
    # Поиск
    if stats['fulltext']:
        print("\n" + "=" * 70)
        print("🔍 ПОИСК (из SQLite - полнотекстовый):")
        print("=" * 70)
        
        query = "финансовый канал"
        results = kb.search_documents(query, limit=3)
        print(f"\nПоиск: '{query}'")
        print(f"Найдено: {len(results)} документов\n")
        
        for doc in results:
            print(f"  📄 {doc['title']}")
            print(f"     Тип: {doc['type']}, Категории: {', '.join(doc['categories'])}")
            print()
        
        # Категории
        cats = kb.get_all_categories()
        print(f"Все категории ({len(cats)}): {', '.join(cats[:5])}...")
    
    print("\n" + "=" * 70)
    print("Готово!")
    print("=" * 70)
