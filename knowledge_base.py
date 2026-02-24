"""
ГИБРИДНАЯ БАЗА ЗНАНИЙ — Нумерология и Ансестология
Работает с:
  - JSON файлами (~100KB) — формулы, значения чисел, практики
  - SQLite базой — полный текст из 83+ PDF, FTS5 поиск

Пример:
  from knowledge_base import HybridKnowledgeBase
  kb = HybridKnowledgeBase()
  result = kb.calculate_all(15, 6, 1990, name="Мария Иванова")
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).parent / "data"

# Таблица букв русского алфавита (нумерология)
LETTER_TABLE_RU = {
    'а':1,'б':2,'в':3,'г':4,'д':5,'е':6,'ё':6,'ж':7,'з':8,'и':9,
    'й':1,'к':2,'л':3,'м':4,'н':5,'о':6,'п':7,'р':8,'с':9,'т':1,
    'у':2,'ф':3,'х':4,'ц':5,'ч':6,'ш':7,'щ':8,'ъ':9,'ы':1,'ь':2,
    'э':3,'ю':4,'я':5
}
# Халдейская система (английский алфавит)
LETTER_TABLE_EN = {
    'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
    'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
    's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8
}
LETTER_TABLE = {**LETTER_TABLE_RU, **LETTER_TABLE_EN}

# Мастер-числа — не сводятся
MASTER_NUMBERS = {11, 22, 33}

# Чакры
CHAKRA_NAMES = {
    1: "Муладхара (корневая) — безопасность, выживание",
    2: "Свадхистана (сакральная) — творчество, сексуальность",
    3: "Манипура (солнечное сплетение) — воля, самооценка",
    4: "Анахата (сердечная) — любовь, принятие",
    5: "Вишудха (горловая) — самовыражение, речь",
    6: "Аджна (третий глаз) — интуиция, видение",
    7: "Сахасрара (коронная) — связь с Высшим, мудрость",
}


def reduce_to_single(n: int) -> int:
    """Свести число к однозначному (мастер-числа 11, 22, 33 сохраняются)"""
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
    return n


class HybridKnowledgeBase:
    """Главный класс — гибридная база знаний"""

    def __init__(self):
        self.formulas       = self._load_json('formulas.json')
        self.practices      = self._load_json('practices.json')
        self.algorithms     = self._load_json('algorithms.json')
        self.number_meanings = self._load_json('number_meanings.json')
        self.master_index   = self._load_json('master_index.json')
        
        # Нормализация number_meanings
        if isinstance(self.number_meanings, list):
            self.number_meanings = {str(item.get('value','')): item 
                                    for item in self.number_meanings}
        
        self.db_conn   = None
        self.db_cursor = None
        self._connect_db()

    # ── Загрузка ──────────────────────────────────────────────────
    def _load_json(self, filename: str) -> Any:
        p = DATA_DIR / filename
        if not p.exists():
            return {}
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _connect_db(self):
        db_path = DATA_DIR / "knowledge_base.db"
        if db_path.exists():
            try:
                self.db_conn = sqlite3.connect(str(db_path))
                self.db_conn.row_factory = sqlite3.Row
                self.db_cursor = self.db_conn.cursor()
            except Exception as e:
                print(f"⚠ БД недоступна: {e}")

    # ── Получение интерпретации числа ─────────────────────────────
    def get_meaning(self, n: int) -> Dict:
        """Полная интерпретация числа из базы знаний"""
        m = self.number_meanings.get(str(n), {})
        return {
            "title":       m.get("title", f"Число {n}"),
            "description": m.get("description", ""),
            "keywords":    m.get("keywords", []),
            "positive":    m.get("positive", []),
            "negative":    m.get("negative", []),
            "professions": m.get("professions", []),
            "rod_programs":m.get("rod_programs", []),
            "chakra":      m.get("chakra", ""),
            "color":       m.get("color", "#c8922a"),
            "interpretation": m.get("interpretation", {}),
        }

    def get_formula(self, formula_id: str) -> Optional[Dict]:
        if isinstance(self.formulas, list):
            for f in self.formulas:
                if f.get('id') == formula_id:
                    return f
        return None

    # ── Расчёты ───────────────────────────────────────────────────
    def calculate_birth_number(self, day: int) -> Dict:
        """Число рождения: сведение дня к однозначному"""
        raw = day
        steps = []
        n = day
        while n > 9 and n not in MASTER_NUMBERS:
            digits = [int(d) for d in str(n)]
            s = sum(digits)
            steps.append(f"{'+'.join(str(d) for d in digits)} = {s}")
            n = s
        
        meaning = self.get_meaning(n)
        return {
            "value": n,
            "raw": raw,
            "steps": steps,
            "formula_text": f"{raw} → {'→ '.join(steps) + ' → ' if steps else ''}{n}",
            "meaning": meaning,
            "formula": self.get_formula("birth_number"),
        }

    def calculate_life_path(self, day: int, month: int, year: int) -> Dict:
        """Путь жизни: ДД + ММ + ГГГГ → однозначное"""
        total = day + month + year
        n = reduce_to_single(total)
        
        year_digits = sum(int(d) for d in str(year))
        steps = f"{day} + {month} + {year} = {total} → {n}"
        
        meaning = self.get_meaning(n)
        return {
            "value": n,
            "details": {"day": day, "month": month, "year": year, "total": total},
            "formula_text": steps,
            "meaning": meaning,
            "formula": self.get_formula("life_path"),
        }

    def calculate_destiny_number(self, fullname: str) -> Dict:
        """Число судьбы по ФИО (числовые значения букв)"""
        letters_sum = []
        total = 0
        for ch in fullname.lower():
            v = LETTER_TABLE.get(ch, 0)
            if v:
                letters_sum.append(v)
                total += v
        
        n = reduce_to_single(total)
        meaning = self.get_meaning(n)
        return {
            "value": n,
            "fullname": fullname,
            "letter_values": letters_sum,
            "total": total,
            "formula_text": f"Сумма букв {total} → {n}",
            "meaning": meaning,
            "formula": self.get_formula("destiny_number"),
        }

    def calculate_financial_channel(self, day: int, month: int, year: int) -> Dict:
        """Финансовый канал: A=день, B=месяц, C=цифры года, D=A+B+C→однозначное"""
        A = day
        B = month
        C = sum(int(d) for d in str(year))
        total = A + B + C
        D = reduce_to_single(total)
        
        meaning = self.get_meaning(D)
        return {
            "value": D,
            "A": A, "B": B, "C": C,
            "total": total,
            "formula_text": f"A({A}) + B({B}) + C({C}) = {total} → D={D}",
            "meaning": meaning,
            "formula": self.get_formula("financial_channel"),
        }

    def calculate_chakras(self, day: int, month: int, year: int) -> Dict:
        """Баланс чакр по цифрам даты рождения"""
        date_str = f"{day:02d}{month:02d}{year:04d}"
        digits = [int(d) for d in date_str]
        
        chakras = {}
        for i in range(1, 8):
            if i + 1 <= len(digits):
                val = digits[i-1] + digits[i]
                chakras[i] = {
                    "value": val,
                    "name": CHAKRA_NAMES.get(i, f"Чакра {i}"),
                    "digits_used": f"{digits[i-1]}+{digits[i]}"
                }
        
        return {
            "chakras": chakras,
            "date_str": date_str,
            "formula": self.get_formula("chakra_balance"),
        }

    def calculate_personal_year(self, day: int, month: int, current_year: int = None) -> Dict:
        """Личный год: день + месяц + текущий год"""
        if current_year is None:
            from datetime import date
            current_year = date.today().year
        n = reduce_to_single(day + month + current_year)
        meaning = self.get_meaning(n)
        return {
            "value": n,
            "year": current_year,
            "formula_text": f"{day} + {month} + {current_year} → {n}",
            "meaning": meaning,
        }

    def calculate_all(self, day: int, month: int, year: int, name: str = None) -> Dict:
        """Полный расчёт всех ключевых показателей"""
        result = {
            "input": {"day": day, "month": month, "year": year, "name": name},
            "birth_number":      self.calculate_birth_number(day),
            "life_path":         self.calculate_life_path(day, month, year),
            "financial_channel": self.calculate_financial_channel(day, month, year),
            "chakras":           self.calculate_chakras(day, month, year),
            "personal_year":     self.calculate_personal_year(day, month),
        }
        if name and name.strip():
            result["destiny"] = self.calculate_destiny_number(name.strip())
        else:
            result["destiny"] = None
        return result

    # ── Поиск по базе ────────────────────────────────────────────
    def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Полнотекстовый поиск по PDF-документам"""
        if not self.db_cursor:
            return self._search_json(query)
        try:
            self.db_cursor.execute("""
                SELECT d.id, d.filename, d.title, d.content_length
                FROM documents_fts f
                JOIN documents d ON f.rowid = d.id
                WHERE f MATCH ? ORDER BY rank LIMIT ?
            """, (query, limit))
            rows = self.db_cursor.fetchall()
            return [{"id": r[0], "filename": r[1], "title": r[2], 
                     "content_length": r[3]} for r in rows]
        except Exception:
            # Fallback
            try:
                self.db_cursor.execute("""
                    SELECT id, filename, title, content_length FROM documents
                    WHERE content LIKE ? OR title LIKE ? LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                return [dict(r) for r in self.db_cursor.fetchall()]
            except Exception:
                return []

    def get_document_content(self, doc_id: int) -> Optional[str]:
        """Получить полный текст документа по ID"""
        if not self.db_cursor:
            return None
        try:
            self.db_cursor.execute("SELECT content FROM documents WHERE id=?", (doc_id,))
            row = self.db_cursor.fetchone()
            return row[0] if row else None
        except Exception:
            return None

    def _search_json(self, query: str) -> List[Dict]:
        """Поиск в JSON когда SQLite недоступен"""
        results = []
        qlow = query.lower()
        if isinstance(self.formulas, list):
            for f in self.formulas:
                if (qlow in f.get('name','').lower() or 
                    qlow in f.get('description','').lower()):
                    results.append({
                        "title": f.get('name'),
                        "type": "formula",
                        "content_length": len(str(f))
                    })
        return results

    def get_all_practices(self) -> List[Dict]:
        """Список всех практик"""
        if isinstance(self.practices, list):
            return self.practices
        return []

    def get_db_stats(self) -> Dict:
        """Статистика базы знаний"""
        stats = {
            "formulas": len(self.formulas) if isinstance(self.formulas, list) else 0,
            "practices": len(self.practices) if isinstance(self.practices, list) else 0,
            "number_meanings": len(self.number_meanings),
            "db_connected": self.db_conn is not None,
        }
        if self.db_cursor:
            try:
                self.db_cursor.execute("SELECT COUNT(*) FROM documents")
                stats["documents"] = self.db_cursor.fetchone()[0]
            except Exception:
                stats["documents"] = 0
        return stats
