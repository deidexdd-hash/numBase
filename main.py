#!/usr/bin/env python3
"""
main.py — единая точка входа
Нумерология и Ансестология Knowledge Base v3.0

Запуск:
    python main.py
    uvicorn main:app --reload --port 8000

После запуска:
    http://localhost:8000        → Web SPA
    http://localhost:8000/api/  → REST API
    http://localhost:8000/docs  → Swagger
"""

import json
import logging
import os
import sys
import webbrowser
from pathlib import Path
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import JSONResponse, PlainTextResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request as StarletteRequest
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ Установите зависимости: pip install fastapi uvicorn[standard] aiofiles")
    sys.exit(1)

# ── Конфигурация ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
APP_DIR  = BASE_DIR / "app"
DB_PATH  = DATA_DIR / "knowledge_base.db"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

# ── FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Нумерология и Ансестология",
    description="База знаний: 83+ PDF, формулы, практики с родом, AI-консультант (Gemini/Groq бесплатно)",
    version="3.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["GET","POST","OPTIONS"],
                   allow_headers=["Content-Type","Authorization"])

class PWAHeaders(BaseHTTPMiddleware):
    async def dispatch(self, req: StarletteRequest, call_next):
        resp = await call_next(req)
        if req.url.path.endswith("sw.js"):
            resp.headers["Service-Worker-Allowed"] = "/"
            resp.headers["Cache-Control"] = "no-cache"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp

app.add_middleware(PWAHeaders)

# ── Хелперы ───────────────────────────────────────────────────────
def load_json(name: str):
    p = DATA_DIR / name
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def get_kb():
    sys.path.insert(0, str(BASE_DIR))
    from knowledge_base import HybridKnowledgeBase
    return HybridKnowledgeBase()

# ── HEALTH ────────────────────────────────────────────────────────
@app.get("/api/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "db": DB_PATH.exists(),
        "app": APP_DIR.exists(),
        "version": "3.0.0"
    }

# ── STATS ─────────────────────────────────────────────────────────
@app.get("/api/stats", tags=["system"])
def stats():
    try:
        kb = get_kb()
        return kb.get_db_stats()
    except Exception as e:
        raise HTTPException(500, str(e))

# ── CALCULATE ─────────────────────────────────────────────────────
@app.get("/api/calculate", summary="Нумерологический расчёт по дате рождения", tags=["calculator"])
def calculate(
    day:   int = Query(..., ge=1, le=31, description="День рождения"),
    month: int = Query(..., ge=1, le=12, description="Месяц рождения"),
    year:  int = Query(..., ge=1900, le=2100, description="Год рождения"),
    name:  Optional[str] = Query(None, description="ФИО для числа судьбы"),
):
    """Возвращает: число рождения, путь жизни, финансовый канал, чакры, личный год, число судьбы."""
    try:
        kb = get_kb()
        return kb.calculate_all(day, month, year, name)
    except Exception as e:
        log.exception("Ошибка расчёта")
        raise HTTPException(500, str(e))

# ── BULK CALCULATE ────────────────────────────────────────────────
class BulkItem(BaseModel):
    day: int
    month: int
    year: int
    name: Optional[str] = None

class BulkRequest(BaseModel):
    clients: List[BulkItem]

@app.post("/api/bulk-calculate", tags=["calculator"])
def bulk_calculate(req: BulkRequest):
    """Пакетный расчёт (max 50 клиентов)"""
    if len(req.clients) > 50:
        raise HTTPException(400, "Максимум 50 клиентов")
    try:
        kb = get_kb()
        results = []
        for i, c in enumerate(req.clients):
            try:
                r = kb.calculate_all(c.day, c.month, c.year, c.name)
                results.append({"index": i, "name": c.name, "success": True, **r})
            except Exception as e:
                results.append({"index": i, "name": c.name, "success": False, "error": str(e)})
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(503, str(e))

# ── SEARCH ────────────────────────────────────────────────────────
@app.get("/api/search", summary="Поиск по базе знаний (FTS5 + LIKE fallback)", tags=["knowledge"])
def search(
    q:     str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None, description="Категория фильтрации"),
):
    try:
        kb = get_kb()
        results = kb.search_documents(q, limit=limit, category=category)
        return {"query": q, "results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(500, str(e))

# ── DOCUMENT CONTENT ──────────────────────────────────────────────
@app.get("/api/document/{doc_id}", tags=["knowledge"])
def get_document(doc_id: int):
    try:
        kb = get_kb()
        content = kb.get_document_content(doc_id)
        if content is None:
            raise HTTPException(404, "Документ не найден")
        return {"id": doc_id, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

# ── FORMULAS ──────────────────────────────────────────────────────
@app.get("/api/formulas", tags=["knowledge"])
def get_formulas():
    data = load_json("formulas.json")
    if data is None:
        raise HTTPException(404, "formulas.json не найден")
    return {"formulas": data, "total": len(data) if isinstance(data, list) else 0}

# ── NUMBER MEANINGS ───────────────────────────────────────────────
@app.get("/api/number-meanings", tags=["knowledge"])
def get_number_meanings():
    data = load_json("number_meanings.json")
    if data is None:
        raise HTTPException(404, "number_meanings.json не найден")
    return data

@app.get("/api/number-meanings/{number}", tags=["knowledge"])
def get_number_meaning(number: int):
    data = load_json("number_meanings.json")
    if data is None:
        raise HTTPException(404, "Файл не найден")
    m = data.get(str(number)) if isinstance(data, dict) else None
    if m is None:
        raise HTTPException(404, f"Число {number} не найдено")
    return m

# ── PRACTICES ─────────────────────────────────────────────────────
@app.get("/api/practices", tags=["knowledge"])
def get_practices():
    data = load_json("practices.json")
    if data is None:
        raise HTTPException(404, "practices.json не найден")
    return {"practices": data, "total": len(data) if isinstance(data, list) else 0}

# ── AI CONSULTANT ─────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str
    user_data: Optional[dict] = None

@app.post("/api/ask", summary="AI-консультант (Gemini/Groq — бесплатно)", tags=["ai"])
def ask_ai(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(400, "Вопрос не может быть пустым")
    try:
        from ai_consultant import AIConsultant
        consultant = AIConsultant()
        return consultant.ask(req.question, user_data=req.user_data)
    except Exception as e:
        log.exception("Ошибка AI")
        raise HTTPException(500, str(e))

# ── AI STATUS ─────────────────────────────────────────────────────
@app.get("/api/ai-status", tags=["ai"])
def ai_status():
    """Проверить доступность AI провайдера"""
    from ai_consultant import get_ai_provider
    provider_name, _ = get_ai_provider()
    status_map = {
        "gemini": "✅ Google Gemini Flash (бесплатно)",
        "groq":   "✅ Groq Llama 3.1 (бесплатно)",
        "local":  "⚠️ Локальный режим (без AI) — добавьте GEMINI_API_KEY или GROQ_API_KEY"
    }
    return {
        "provider": provider_name,
        "status": status_map.get(provider_name, "unknown"),
        "gemini_key_set": bool(os.getenv("GEMINI_API_KEY")),
        "groq_key_set":   bool(os.getenv("GROQ_API_KEY")),
    }

# ── EXPORT TEXT REPORT ────────────────────────────────────────────
@app.get("/api/export", tags=["calculator"])
def export_report(
    day: int = Query(...), month: int = Query(...), year: int = Query(...),
    name: Optional[str] = Query(None)
):
    """Экспорт нумерологического отчёта в текст"""
    try:
        kb = get_kb()
        data = kb.calculate_all(day, month, year, name)
        lines = [
            "=" * 50,
            "НУМЕРОЛОГИЧЕСКИЙ ОТЧЁТ",
            "=" * 50,
            f"Дата рождения: {day:02d}.{month:02d}.{year}",
        ]
        if name:
            lines.append(f"Имя: {name}")
        lines.append("")
        
        sections = [
            ("birth_number",      "✦ ЧИСЛО РОЖДЕНИЯ"),
            ("life_path",         "◉ ПУТЬ ЖИЗНИ"),
            ("financial_channel", "◈ ФИНАНСОВЫЙ КАНАЛ"),
            ("personal_year",     "⟐ ЛИЧНЫЙ ГОД"),
            ("destiny",           "∞ ЧИСЛО СУДЬБЫ"),
        ]
        for key, label in sections:
            d = data.get(key)
            if d and isinstance(d, dict) and d.get("value"):
                lines.append(label)
                lines.append(f"Значение: {d['value']}")
                if d.get("formula_text"):
                    lines.append(f"Формула: {d['formula_text']}")
                m = d.get("meaning", {})
                if m.get("title"):
                    lines.append(f"Архетип: {m['title']}")
                if m.get("description"):
                    lines.append(f"Описание: {m['description'][:300]}")
                lines.append("")
        
        return PlainTextResponse("\n".join(lines), headers={
            "Content-Disposition": f'attachment; filename="numerology_{day}{month}{year}.txt"'
        })
    except Exception as e:
        raise HTTPException(500, str(e))

# ── KNOWLEDGE BASE ADD ─────────────────────────────────────────────
class KBAddRequest(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = []

@app.post("/api/knowledge/add", tags=["knowledge"], summary="Добавить запись в базу знаний")
def add_knowledge(req: KBAddRequest):
    """Пополнение базы знаний через API"""
    import sqlite3 as sq
    if not DB_PATH.exists():
        raise HTTPException(503, "База данных недоступна")
    try:
        conn = sq.connect(str(DB_PATH))
        cur = conn.cursor()
        # Добавляем в documents
        cur.execute("""
            INSERT INTO documents (filename, title, content, doc_type, categories, content_length)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"manual_{req.title[:30].replace(' ','_')}.txt",
            req.title,
            req.content,
            req.category,
            json.dumps(req.tags, ensure_ascii=False),
            len(req.content)
        ))
        doc_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {"status": "ok", "doc_id": doc_id, "title": req.title}
    except Exception as e:
        raise HTTPException(500, str(e))

# ── Статика (Web SPA) ────────────────────────────────────────────
if APP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(APP_DIR), html=True), name="app")
else:
    @app.get("/")
    def root():
        return {"message": "API работает. Папка app/ не найдена — откройте /docs"}

# ── Запуск ────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info(f"🚀 Сервер: http://localhost:{PORT}")
    log.info(f"📚 Документация: http://localhost:{PORT}/docs")
    
    import threading, time
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{PORT}")
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
