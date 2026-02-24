#!/usr/bin/env python3
"""
processor/rebuild_fts.py — Пересоздание FTS5-индекса для полнотекстового поиска

Запуск: python processor/rebuild_fts.py

Зачем: SQLite FTS5 в 10-50 раз быстрее LIKE-поиска,
       поддерживает ранжирование по релевантности (BM25),
       находит все формы слова (unicode61 токенизер).
"""

import sqlite3
import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH  = DATA_DIR / "knowledge_base.db"


def rebuild_fts(db_path: Path = DB_PATH):
    if not db_path.exists():
        print(f"❌ База данных не найдена: {db_path}")
        sys.exit(1)

    print(f"📂 База данных: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cur  = conn.cursor()

    # Проверяем что таблица documents существует
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='documents'")
    if cur.fetchone()[0] == 0:
        print("❌ Таблица 'documents' не найдена в базе")
        conn.close()
        sys.exit(1)

    cur.execute("SELECT COUNT(*) FROM documents")
    doc_count = cur.fetchone()[0]
    print(f"📄 Документов в базе: {doc_count}")

    # Удаляем старый FTS-индекс если есть
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts'")
    if cur.fetchone():
        print("🗑  Удаляем старый FTS5-индекс...")
        cur.execute("DROP TABLE IF EXISTS documents_fts")

    # Создаём новый FTS5 с привязкой к основной таблице (content table)
    print("🔨 Создаём FTS5-индекс...")
    t0 = time.time()

    cur.execute("""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
            title,
            content,
            content='documents',
            content_rowid='id',
            tokenize='unicode61 remove_diacritics 1'
        )
    """)

    # Заполняем индекс
    cur.execute("""
        INSERT INTO documents_fts(rowid, title, content)
        SELECT id, COALESCE(title, ''), COALESCE(content, '')
        FROM documents
    """)

    # Оптимизируем (merge сегментов для ускорения поиска)
    cur.execute("INSERT INTO documents_fts(documents_fts) VALUES('optimize')")

    conn.commit()
    elapsed = time.time() - t0

    # Проверяем
    cur.execute("SELECT COUNT(*) FROM documents_fts")
    fts_count = cur.fetchone()[0]

    print(f"✅ FTS5-индекс создан за {elapsed:.2f}с")
    print(f"   Проиндексировано: {fts_count} документов")

    # Тест поиска
    print("\n🔍 Тест поиска...")
    tests = ["путь жизни", "финансовый", "генограмма", "число рождения"]
    for q in tests:
        q_esc = q.replace('"', '""')
        cur.execute("""
            SELECT d.title, rank
            FROM documents_fts
            JOIN documents d ON documents_fts.rowid = d.id
            WHERE documents_fts MATCH ?
            ORDER BY rank
            LIMIT 3
        """, (q_esc,))
        rows = cur.fetchall()
        print(f"   «{q}» → {len(rows)} результатов", end="")
        if rows:
            print(f"  (лучший: {rows[0][0][:50]})")
        else:
            print()

    conn.close()
    print("\n✅ FTS5-индекс готов к использованию")
    print("   Поиск в main.py теперь использует FTS5 автоматически")


if __name__ == "__main__":
    rebuild_fts()
