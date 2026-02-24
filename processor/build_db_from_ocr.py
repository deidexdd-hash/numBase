#!/usr/bin/env python3
"""
Загрузка OCR txt файлов в SQLite базу знаний.

Использование:
    python processor/build_db_from_ocr.py [путь к папке ocr_results]

По умолчанию ищет папку ../ocr_results/ рядом со скриптом.
"""

import sqlite3, json, re, sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH  = DATA_DIR / "knowledge_base.db"

OCR_DIR  = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR.parent / "ocr_results"

TITLE_OVERRIDES = {
    'да нет':       'Алгоритм подбора схемы проработки',
    'ВНИМАНИЕ':     'Алгоритм выбора техники проработки',
    'АЛФАВИТ':      'Алфавит и расшифровка значений',
}

def extract_title(text: str) -> str:
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
    if not lines:
        return 'Без заголовка'
    first = lines[0]
    for key, val in TITLE_OVERRIDES.items():
        if first.startswith(key):
            return val
    return first[:80]

def detect_category(title: str, content: str) -> str:
    t = title.lower(); c = content.lower()[:1000]
    if any(x in t for x in ['цифра','число рожд','жизни цифр']):
        return 'numerology'
    if any(x in t for x in ['практика','ритуал','благослов','поклон','алтар','пояс','молитв','медитац','сборник']):
        return 'practice'
    if any(x in t for x in ['расчёт','расчет','рсч','финансов','инвест','риски','имущ','бизнес','беременн','переезд','канал']):
        return 'calculation'
    if any(x in t for x in ['генограм','нерожденн','исключенн','программы поколен']):
        return 'ancestrology'
    if any(x in t for x in ['алгоритм','схема','выбор','диагностика','техника','методолог']):
        return 'methodology'
    if any(x in t for x in ['карма','трансгенер','эпигенет','проклят','самопрокл','болезн']):
        return 'karmic'
    if any(x in t for x in ['медитац','молитв','сборник']):
        return 'meditation'
    if 'ансестолог' in c[:500] or 'доверитель' in c[:500]:
        return 'ancestrology'
    if 'число рождения' in c[:500] or 'путь жизни' in c[:300]:
        return 'numerology'
    return 'general'

def clean_text(text: str) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return '\n'.join(l.rstrip() for l in text.split('\n')).strip()

def build_db(ocr_dir: Path, db_path: Path):
    txt_files = sorted(ocr_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ TXT файлы не найдены в {ocr_dir}")
        return

    print(f"Найдено txt файлов: {len(txt_files)}")
    print(f"База данных: {db_path}")
    print()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS documents_fts;
        DROP TABLE IF EXISTS category_index;
        DROP TABLE IF EXISTS documents;

        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT NOT NULL,
            doc_type TEXT DEFAULT 'txt',
            categories TEXT DEFAULT '[]',
            content TEXT NOT NULL,
            content_length INTEGER DEFAULT 0,
            extraction_method TEXT DEFAULT 'ocr_txt',
            extracted_at TEXT
        );

        CREATE TABLE category_index (
            category TEXT NOT NULL,
            doc_id INTEGER NOT NULL
        );

        CREATE VIRTUAL TABLE documents_fts USING fts5(
            filename, title, content,
            content='documents',
            content_rowid='id',
            tokenize='unicode61'
        );
    """)
    conn.commit()

    now = datetime.now().isoformat()
    loaded = 0
    from collections import Counter
    cats = Counter()

    for fpath in txt_files:
        try:
            raw = fpath.read_bytes()
            text = raw.decode('utf-8', errors='replace')
            text = clean_text(text)
            title = extract_title(text)
            cat = detect_category(title, text)
            cats[cat] += 1

            cur.execute("""
                INSERT INTO documents (filename, title, doc_type, categories, content, content_length, extraction_method, extracted_at)
                VALUES (?, ?, 'txt', ?, ?, ?, 'ocr_txt', ?)
            """, (fpath.name, title, json.dumps([cat]), text, len(text), now))
            
            cur.execute("INSERT INTO category_index VALUES (?, ?)", (cat, cur.lastrowid))
            loaded += 1
        except Exception as e:
            print(f"  ❌ {fpath.name}: {e}")

    conn.commit()
    cur.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()

    print(f"✅ Загружено: {loaded} документов")
    print(f"   Категории:")
    for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"     {cat}: {cnt}")

if __name__ == "__main__":
    if not OCR_DIR.exists():
        print(f"❌ Папка ocr_results не найдена: {OCR_DIR}")
        print(f"   Использование: python {__file__} /путь/к/ocr_results")
        sys.exit(1)
    build_db(OCR_DIR, DB_PATH)
