#!/usr/bin/env python3
"""
main.py — единая точка входа для приложения Нумерология и Ансестология

Запуск:
    python main.py
    # или
    uvicorn main:app --reload --port 8000

Адрес после запуска:
    http://localhost:8000        → Web-приложение
    http://localhost:8000/api/  → REST API
    http://localhost:8000/docs  → Swagger документация
"""

import json
import logging
import os
import sqlite3
import sys
import webbrowser
from pathlib import Path
from typing import List, Optional

# Загружаем .env если есть
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
except ImportError:
    print("❌ FastAPI не установлен. Выполните:")
    print("   pip install fastapi uvicorn[standard] aiofiles")
    sys.exit(1)

# ── Конфигурация ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
APP_DIR  = BASE_DIR / "app"
DB_PATH  = DATA_DIR / "knowledge_base.db"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("main")

# ── FastAPI приложение ────────────────────────────────────────────
app = FastAPI(
    title="Нумерология и Ансестология API",
    description="База знаний: 83 PDF, 15 формул, 8 практик. Phase 9: PWA offline support.",
    version="4.1.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# ── PWA middleware: Service-Worker-Allowed header (Phase 9) ──────────
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

class PWAHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        # Allow SW to control the whole origin
        if request.url.path.endswith('sw.js'):
            response.headers['Service-Worker-Allowed'] = '/'
            response.headers['Cache-Control'] = 'no-cache'
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

app.add_middleware(PWAHeadersMiddleware)

# ── Подключение к БД ─────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    """Создать соединение с БД (row_factory = dict)"""
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail=f"База данных не найдена: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_fts(conn: sqlite3.Connection):
    """Создать FTS5-индекс если его нет."""
    cur = conn.cursor()
    # Проверяем наличие таблицы
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts'")
    if cur.fetchone() is None:
        log.info("Создаём FTS5-индекс...")
        cur.execute("""
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                title,
                content,
                content='documents',
                content_rowid='id',
                tokenize='unicode61'
            )
        """)
        cur.execute("""
            INSERT INTO documents_fts(rowid, title, content)
            SELECT id, title, content FROM documents
        """)
        conn.commit()
        log.info("FTS5-индекс создан.")


# ── Хелперы ───────────────────────────────────────────────────────
def get_snippet(text: str, query: str, context: int = 150) -> str:
    """Вернуть фрагмент текста вокруг вхождения запроса."""
    lower = text.lower()
    pos = lower.find(query.lower())
    if pos == -1:
        return text[:context * 2] + "..."
    start = max(0, pos - context)
    end = min(len(text), pos + len(query) + context)
    snippet = text[start:end]
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def load_json(filename: str):
    """Загрузить JSON-файл из data/."""
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def reduce_to_single(n: int) -> int:
    """Свести число к однозначному (нумерологически)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


# ══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════════

# ── Поиск ─────────────────────────────────────────────────────────
@app.get("/api/search", summary="Полнотекстовый поиск по базе знаний")
def search(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
):
    """FTS5-поиск по всем 105 документам с ранжированием по релевантности."""
    try:
        conn = get_db()
        ensure_fts(conn)
        cur = conn.cursor()

        # FTS5-запрос с BM25-ранжированием
        fts_query = q.replace('"', '""')  # экранируем кавычки
        try:
            cur.execute("""
                SELECT d.id, d.filename, d.title, d.doc_type, d.categories,
                       d.content, d.content_length,
                       rank AS score
                FROM documents_fts
                JOIN documents d ON documents_fts.rowid = d.id
                WHERE documents_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, limit))
        except sqlite3.OperationalError:
            # Fallback: LIKE если FTS таблица повреждена
            like = f"%{q}%"
            cur.execute("""
                SELECT id, filename, title, doc_type, categories,
                       content, content_length, 0 AS score
                FROM documents
                WHERE content LIKE ? OR title LIKE ?
                LIMIT ?
            """, (like, like, limit))

        rows = cur.fetchall()
        conn.close()

        results = []
        for row in rows:
            cats = []
            try:
                cats = json.loads(row["categories"]) if row["categories"] else []
            except Exception:
                pass

            # Фильтр по категории если задан
            if category and category not in cats:
                continue

            results.append({
                "id": row["id"],
                "filename": row["filename"],
                "title": row["title"],
                "type": row["doc_type"],
                "categories": cats,
                "snippet": get_snippet(row["content"] or "", q),
                "content_length": row["content_length"],
            })

        return {"query": q, "results": results, "total": len(results)}

    except HTTPException:
        raise
    except Exception as e:
        log.exception("Ошибка поиска")
        raise HTTPException(status_code=500, detail=str(e))


# ── Документы ─────────────────────────────────────────────────────
@app.get("/api/documents/{doc_id}", summary="Получить документ по ID")
def get_document(doc_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, filename, title, doc_type, categories, content, content_length FROM documents WHERE id=?",
            (doc_id,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Документ не найден")

        return {
            "id": row["id"],
            "filename": row["filename"],
            "title": row["title"],
            "type": row["doc_type"],
            "categories": json.loads(row["categories"]) if row["categories"] else [],
            "content": row["content"],
            "content_length": row["content_length"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Статистика ────────────────────────────────────────────────────
@app.get("/api/stats", summary="Статистика базы данных")
def get_stats():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), SUM(content_length) FROM documents")
        count, chars = cur.fetchone()
        conn.close()

        formulas  = load_json("formulas.json") or []
        practices = load_json("practices.json") or []

        return {
            "documents":  count or 0,
            "total_chars": chars or 0,
            "size_mb":    round((chars or 0) / (1024 * 1024), 2),
            "formulas":   len(formulas),
            "practices":  len(practices),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Категории ─────────────────────────────────────────────────────
@app.get("/api/categories", summary="Список категорий")
def get_categories():
    try:
        conn = get_db()
        cur = conn.cursor()
        # Пробуем category_index, fallback на парсинг JSON-поля
        try:
            cur.execute("SELECT DISTINCT category FROM category_index ORDER BY category")
            cats = [r[0] for r in cur.fetchall()]
        except sqlite3.OperationalError:
            cur.execute("SELECT DISTINCT categories FROM documents WHERE categories != '[]'")
            cats_set = set()
            for (raw,) in cur.fetchall():
                try:
                    for c in json.loads(raw or "[]"):
                        cats_set.add(c)
                except Exception:
                    pass
            cats = sorted(cats_set)
        conn.close()
        return {"categories": cats}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Расчёты ───────────────────────────────────────────────────────
@app.get("/api/calculate", summary="Нумерологические расчёты по дате рождения")
def calculate_all(
    day:   int = Query(..., ge=1, le=31),
    month: int = Query(..., ge=1, le=12),
    year:  int = Query(..., ge=1900, le=2100),
    name:  Optional[str] = Query(None, description="ФИО для числа судьбы"),
):
    """
    Возвращает все основные расчёты за один запрос.
    Используется главным экраном приложения.
    """
    try:
        sys.path.insert(0, str(BASE_DIR))
        from knowledge_base import HybridKnowledgeBase
        kb = HybridKnowledgeBase()

        result = {
            "input": {"day": day, "month": month, "year": year, "name": name},
            "life_path":        kb.calculate_life_path(day, month, year),
            "birth_number":     kb.calculate_birth_number(day),
            "financial_channel": kb.calculate_financial_channel(day, month, year),
            "chakras":          kb.calculate_chakras(day, month, year),
        }

        # Число судьбы по ФИО — только если передано имя
        if name and name.strip():
            result["destiny"] = kb.calculate_destiny_number(name.strip())
        else:
            result["destiny"] = None

        return result

    except Exception as e:
        log.exception("Ошибка расчёта")
        raise HTTPException(status_code=500, detail=str(e))


# ── Формулы и практики ────────────────────────────────────────────
@app.get("/api/formulas", summary="Список нумерологических формул")
def get_formulas():
    data = load_json("formulas.json")
    if data is None:
        raise HTTPException(status_code=404, detail="formulas.json не найден")
    return {"formulas": data, "total": len(data)}


@app.get("/api/practices", summary="Список практик")
def get_practices():
    data = load_json("practices.json")
    if data is None:
        raise HTTPException(status_code=404, detail="practices.json не найден")
    return {"practices": data, "total": len(data)}


@app.get("/api/number-meanings", summary="Значения чисел")
def get_number_meanings():
    data = load_json("number_meanings.json")
    if data is None:
        raise HTTPException(status_code=404, detail="number_meanings.json не найден")
    return data


# ── AI-консультант ────────────────────────────────────────────────
from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str
    user_data: Optional[dict] = None   # результаты расчётов, если есть

@app.post("/api/ask", summary="AI-консультант (RAG + OpenAI)")
def ask_ai(req: AskRequest):
    """Ответ на вопрос на основе базы знаний."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустым")
    try:
        sys.path.insert(0, str(BASE_DIR))
        from ai_consultant import AIConsultant
        consultant = AIConsultant()
        result = consultant.ask(req.question, user_data=req.user_data)
        return result
    except Exception as e:
        log.exception("Ошибка AI-консультанта")
        raise HTTPException(status_code=500, detail=str(e))


# ── Health-check ──────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "db": DB_PATH.exists(), "app": APP_DIR.exists()}


# ── Bulk Calculate (Phase 8.3) ───────────────────────────────────
class BulkClientItem(BaseModel):
    day: int
    month: int
    year: int
    name: Optional[str] = None

class BulkRequest(BaseModel):
    clients: List[BulkClientItem]

@app.post("/api/bulk-calculate", summary="Пакетный расчёт для кабинета практика (max 50)")
def bulk_calculate(req: BulkRequest):
    """Принимает список клиентов, возвращает нумерологические профили для каждого."""
    if len(req.clients) > 50:
        raise HTTPException(status_code=400, detail="Максимум 50 клиентов за запрос")
    try:
        sys.path.insert(0, str(BASE_DIR))
        from knowledge_base import HybridKnowledgeBase
        kb = HybridKnowledgeBase()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"База знаний недоступна: {e}")

    results = []
    for idx, client in enumerate(req.clients):
        try:
            r: dict = {}
            r["birth_number"]     = kb.calculate_birth_number(client.day)
            r["life_path"]        = kb.calculate_life_path(client.day, client.month, client.year)
            r["financial_channel"]= kb.calculate_financial_channel(client.day, client.month, client.year)
            if client.name:
                r["destiny"]      = kb.calculate_destiny_number(client.name.strip())
            else:
                r["destiny"]      = None
            results.append({"index": idx, "name": client.name, "success": True, **r})
        except Exception as e:
            results.append({"index": idx, "name": client.name, "success": False, "error": str(e)})

    return {"results": results, "total": len(results)}


# ── Export Text Report (Phase 8.3) ──────────────────────────────
@app.get("/api/export", summary="Экспорт нумерологического отчёта (text/plain)")
def export_report(
    day: int   = Query(..., ge=1, le=31),
    month: int = Query(..., ge=1, le=12),
    year: int  = Query(..., ge=1900, le=2100),
    name: Optional[str] = Query(None)
):
    """Возвращает текстовый отчёт по нумерологическому профилю."""
    try:
        sys.path.insert(0, str(BASE_DIR))
        from knowledge_base import HybridKnowledgeBase
        kb = HybridKnowledgeBase()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"База знаний недоступна: {e}")

    try:
        dob = f"{day:02d}.{month:02d}.{year}"
        lines = [
            "═" * 52,
            "   🔮  НУМЕРОЛОГИЧЕСКИЙ ПРОФИЛЬ",
            "═" * 52,
            f"   Дата рождения : {dob}",
        ]
        if name:
            lines.append(f"   Имя           : {name}")
        lines += ["═" * 52, ""]

        calcs = [
            ("Число рождения",   kb.calculate_birth_number(day)),
            ("Путь жизни",       kb.calculate_life_path(day, month, year)),
            ("Финансовый канал", kb.calculate_financial_channel(day, month, year)),
        ]
        if name:
            calcs.append(("Число судьбы", kb.calculate_destiny_number(name.strip())))

        for label, result in calcs:
            if result is None:
                continue
            val  = result.get("value", "—")
            title = result.get("meaning", {}).get("title", "")
            kws   = ", ".join(result.get("meaning", {}).get("keywords", [])[:5])
            desc  = result.get("meaning", {}).get("description", "")[:200]
            lines += [
                f"  {label}: {val}",
                f"  {title}",
            ]
            if kws:
                lines.append(f"  Ключевые слова: {kws}")
            if desc:
                lines.append(f"  {desc}")
            lines.append("")

        lines += [
            "─" * 52,
            "  Создано: Нумерология и Ансестология v3.0",
            "═" * 52,
        ]
        text = "\n".join(lines)

        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=text,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="numerology_{dob}.txt"'}
        )
    except Exception as e:
        log.exception("Ошибка экспорта")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════
# Статика (Web UI) — монтируем последней, чтобы не перекрыть /api/
# ══════════════════════════════════════════════════════════════════
if APP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(APP_DIR), html=True), name="static")
else:
    log.warning(f"Папка с веб-приложением не найдена: {APP_DIR}")


# ══════════════════════════════════════════════════════════════════
# Запуск
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print("\n" + "═" * 55)
    print("  🔮  Нумерология и Ансестология  v4.1  (PWA)")
    print("═" * 55)
    print(f"  Web:  {url}")
    print(f"  API:  {url}/docs")
    print(f"  БД:   {DB_PATH}  ({'✓' if DB_PATH.exists() else '✗ не найдена'})")
    print("  Ctrl+C для остановки")
    print("═" * 55 + "\n")

    # Открываем браузер через секунду после старта сервера
    import threading
    def open_browser():
        import time
        time.sleep(1.2)
        webbrowser.open(url)
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("main:app", host=HOST, port=PORT, reload=False, log_level="warning")
