#!/usr/bin/env python3
"""
main.py — единая точка входа
Нумерология и Ансестология Knowledge Base v3.0

На Render запускается один процесс. Telegram-бот встроен через webhook
прямо в FastAPI — отдельный процесс не нужен.

Переменные окружения (Render → Environment):
    TELEGRAM_BOT_TOKEN  — токен от @BotFather
    WEBHOOK_URL         — https://ВАШ-СЕРВИС.onrender.com  (без слэша в конце)
    GEMINI_API_KEY      — ключ Google Gemini (опционально)
    GROQ_API_KEY        — ключ Groq (опционально)
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
    from fastapi import FastAPI, HTTPException, Query, Request
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

WEBHOOK_URL    = os.getenv("WEBHOOK_URL", "").rstrip("/")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_PATH   = f"/webhook/{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else "/webhook/disabled"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

# ── FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Нумерология и Ансестология",
    description="База знаний: 83+ PDF, формулы, практики с родом, AI-консультант",
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

# ── Telegram Bot (webhook) ────────────────────────────────────────
_tg_app = None

def _build_telegram_app():
    global _tg_app
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        log.warning("TELEGRAM_BOT_TOKEN не задан — бот отключён")
        return None
    try:
        from telegram import Update
        from telegram.ext import (
            Application, CommandHandler, MessageHandler,
            ContextTypes, filters, ConversationHandler
        )
        from knowledge_base import HybridKnowledgeBase
        from ai_consultant import AIConsultant

        kb_i = HybridKnowledgeBase()
        ai_i = AIConsultant()
        WAITING_DATE = 1

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            stats = kb_i.get_db_stats()
            await update.message.reply_text(
                "🌟 *Нумерология и Ансестология*\n\n"
                f"База знаний: *{stats.get('documents', 0)}* документов • "
                f"*{stats.get('formulas', 0)}* формул\n\n"
                "Команды:\n/calc — Расчёт нумерологии\n/search <запрос> — Поиск\n"
                "/ask <вопрос> — AI-консультант\n/practices — Практики",
                parse_mode="Markdown"
            )

        async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "*Как использовать бота:*\n\n"
                "1️⃣ `/calc` — дата рождения ДД ММ ГГГГ\n"
                "2️⃣ `/search карма` — поиск по базе\n"
                "3️⃣ `/ask Что означает число 7?` — AI-ответ\n"
                "4️⃣ `/practices` — практики с родом",
                parse_mode="Markdown"
            )

        async def calc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "Введите дату рождения: *ДД ММ ГГГГ*\nПример: `15 06 1990`\n"
                "С именем: `15 06 1990 Мария Иванова`",
                parse_mode="Markdown"
            )
            return WAITING_DATE

        async def calc_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
            parts = update.message.text.strip().split(None, 3)
            if len(parts) < 3:
                await update.message.reply_text("❌ Формат: `15 06 1990`", parse_mode="Markdown")
                return WAITING_DATE
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                name = parts[3] if len(parts) > 3 else None
            except ValueError:
                await update.message.reply_text("❌ Введите числа: день месяц год")
                return WAITING_DATE
            await update.message.reply_text("⏳ Рассчитываю...")
            try:
                data = kb_i.calculate_all(day, month, year, name)
                lines = [f"📊 *Нумерология {day:02d}.{month:02d}.{year}*"]
                if name:
                    lines.append(f"👤 {name}")
                lines.append("")
                sections = [
                    ("birth_number", "✦ Число рождения"),
                    ("life_path", "◉ Путь жизни"),
                    ("financial_channel", "◈ Финансовый канал"),
                    ("personal_year", "⟐ Личный год"),
                ]
                if name:
                    sections.append(("destiny", "∞ Число судьбы"))
                for key, label in sections:
                    d = data.get(key)
                    if d and d.get("value"):
                        m = d.get("meaning", {})
                        lines.append(f"*{label}: {d['value']}*")
                        if m.get("title"):
                            lines.append(f"_{m['title']}_")
                        if m.get("description"):
                            lines.append(m["description"])
                        if m.get("keywords"):
                            lines.append(f"🔑 {', '.join(m['keywords'])}")
                        lines.append("")
                await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
            return ConversationHandler.END

        async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = " ".join(context.args)
            if not query:
                await update.message.reply_text("Использование: /search <запрос>")
                return
            results = kb_i.search_documents(query, limit=5)
            if not results:
                await update.message.reply_text("❌ Ничего не найдено")
                return
            lines = [f"🔍 Найдено по «{query}»:\n"]
            for r in results:
                lines.append(f"📄 *{r.get('title', 'Без названия')}*")
                if r.get("snippet"):
                    lines.append(f"_{r['snippet']}_")
                lines.append("")
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

        async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
            question = " ".join(context.args)
            if not question:
                await update.message.reply_text("Использование: /ask <вопрос>")
                return
            await update.message.reply_text("🤔 Думаю...")
            result = ai_i.ask(question)
            answer   = result.get("answer", "Не удалось получить ответ")
            provider = result.get("provider", "")
            text = f"💬 {answer[:3500]}"
            if provider:
                text += f"\n\n_Источник: {provider}_"
            await update.message.reply_text(text, parse_mode="Markdown")

        async def practices_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
            pp = kb_i.get_all_practices()
            if not pp:
                await update.message.reply_text("Практики не найдены")
                return
            lines = ["🌿 *Практики с Родом:*\n"]
            for p in pp[:8]:
                dur = p.get("duration", "")
                lines.append(f"• *{p.get('name','Без названия')}*" + (f" ({dur})" if dur else ""))
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

        async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("Отменено.")
            return ConversationHandler.END

        # .updater(None) — отключаем Updater, он нужен только для polling.
        # При webhook-режиме Updater не используется и вызывает ошибки совместимости.
        tg = Application.builder().token(TELEGRAM_TOKEN).updater(None).build()
        tg.add_handler(CommandHandler("start", start))
        tg.add_handler(CommandHandler("help",  help_cmd))
        tg.add_handler(ConversationHandler(
            entry_points=[CommandHandler("calc", calc_start)],
            states={WAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_process)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ))
        tg.add_handler(CommandHandler("search",    search))
        tg.add_handler(CommandHandler("ask",       ask_ai))
        tg.add_handler(CommandHandler("practices", practices_cmd))
        log.info("✅ Telegram Application инициализирован")
        return tg

    except ImportError as e:
        log.warning(f"Telegram недоступен: {e}")
        return None
    except Exception as e:
        log.warning(f"Ошибка инициализации бота: {e}")
        return None


@app.on_event("startup")
async def startup():
    global _tg_app
    _tg_app = _build_telegram_app()
    if _tg_app and WEBHOOK_URL:
        await _tg_app.initialize()
        await _tg_app.start()
        full = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await _tg_app.bot.set_webhook(full)
        log.info(f"🤖 Webhook установлен: {full}")
    elif _tg_app:
        log.warning("⚠️  WEBHOOK_URL не задан — добавьте в Render → Environment: WEBHOOK_URL=https://ВАШ-СЕРВИС.onrender.com")

@app.on_event("shutdown")
async def shutdown():
    if _tg_app:
        await _tg_app.stop()
        await _tg_app.shutdown()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    if not _tg_app:
        return JSONResponse({"ok": False, "error": "bot not initialized"}, status_code=503)
    try:
        from telegram import Update
        update = Update.de_json(await request.json(), _tg_app.bot)
        await _tg_app.process_update(update)
        return JSONResponse({"ok": True})
    except Exception as e:
        log.exception("Ошибка webhook")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ── Хелперы ───────────────────────────────────────────────────────
def load_json(name):
    p = DATA_DIR / name
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def get_kb():
    sys.path.insert(0, str(BASE_DIR))
    from knowledge_base import HybridKnowledgeBase
    return HybridKnowledgeBase()

# ── API endpoints (все те же, что были в оригинале) ───────────────

@app.get("/api/health", tags=["system"])
def health():
    return {
        "status": "ok", "db": DB_PATH.exists(), "app": APP_DIR.exists(),
        "version": "3.0.0",
        "telegram_bot": _tg_app is not None,
        "webhook_set": bool(WEBHOOK_URL and TELEGRAM_TOKEN),
    }

@app.get("/api/stats", tags=["system"])
def stats_ep():
    try:
        return get_kb().get_db_stats()
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/calculate", tags=["calculator"])
def calculate(
    day: int = Query(..., ge=1, le=31), month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=1900, le=2100), name: Optional[str] = Query(None),
):
    try:
        return get_kb().calculate_all(day, month, year, name)
    except Exception as e:
        raise HTTPException(500, str(e))

class BulkItem(BaseModel):
    day: int; month: int; year: int; name: Optional[str] = None

class BulkRequest(BaseModel):
    clients: List[BulkItem]

@app.post("/api/bulk-calculate", tags=["calculator"])
def bulk_calculate(req: BulkRequest):
    if len(req.clients) > 50:
        raise HTTPException(400, "Максимум 50 клиентов")
    kb = get_kb()
    results = []
    for i, c in enumerate(req.clients):
        try:
            r = kb.calculate_all(c.day, c.month, c.year, c.name)
            results.append({"index": i, "name": c.name, "success": True, **r})
        except Exception as e:
            results.append({"index": i, "name": c.name, "success": False, "error": str(e)})
    return {"results": results, "total": len(results)}

@app.get("/api/search", tags=["knowledge"])
def search_ep(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50),
              category: Optional[str] = Query(None)):
    try:
        results = get_kb().search_documents(q, limit=limit, category=category)
        return {"query": q, "results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/document/{doc_id}", tags=["knowledge"])
def get_document(doc_id: int):
    try:
        content = get_kb().get_document_content(doc_id)
        if content is None:
            raise HTTPException(404, "Документ не найден")
        return {"id": doc_id, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/formulas", tags=["knowledge"])
def get_formulas():
    data = load_json("formulas.json")
    if data is None:
        raise HTTPException(404, "formulas.json не найден")
    return {"formulas": data, "total": len(data) if isinstance(data, list) else 0}

@app.get("/api/number-meanings", tags=["knowledge"])
def get_number_meanings():
    data = load_json("number_meanings.json")
    if data is None:
        raise HTTPException(404, "number_meanings.json не найден")
    return data

@app.get("/api/number-meanings/{number}", tags=["knowledge"])
def get_number_meaning(number: int):
    data = load_json("number_meanings.json")
    if data is None or not isinstance(data, dict):
        raise HTTPException(404, "Файл не найден")
    m = data.get(str(number))
    if m is None:
        raise HTTPException(404, f"Число {number} не найдено")
    return m

@app.get("/api/practices", tags=["knowledge"])
def get_practices():
    data = load_json("practices.json")
    if data is None:
        raise HTTPException(404, "practices.json не найден")
    return {"practices": data, "total": len(data) if isinstance(data, list) else 0}

class AskRequest(BaseModel):
    question: str
    user_data: Optional[dict] = None

@app.post("/api/ask", tags=["ai"])
def ask_ai_ep(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(400, "Вопрос не может быть пустым")
    try:
        from ai_consultant import AIConsultant
        return AIConsultant().ask(req.question, user_data=req.user_data)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/ai-status", tags=["ai"])
def ai_status():
    from ai_consultant import get_ai_provider
    pname, _ = get_ai_provider()
    return {
        "provider": pname,
        "status": {"gemini":"✅ Google Gemini Flash","groq":"✅ Groq Llama 3.1",
                   "local":"⚠️ Локальный режим"}.get(pname, "unknown"),
        "gemini_key_set": bool(os.getenv("GEMINI_API_KEY")),
        "groq_key_set":   bool(os.getenv("GROQ_API_KEY")),
    }

@app.get("/api/export", tags=["calculator"])
def export_report(day: int = Query(...), month: int = Query(...),
                  year: int = Query(...), name: Optional[str] = Query(None)):
    try:
        data = get_kb().calculate_all(day, month, year, name)
        lines = ["="*50,"НУМЕРОЛОГИЧЕСКИЙ ОТЧЁТ","="*50,f"Дата: {day:02d}.{month:02d}.{year}"]
        if name:
            lines.append(f"Имя: {name}")
        lines.append("")
        for key, label in [("birth_number","✦ ЧИСЛО РОЖДЕНИЯ"),("life_path","◉ ПУТЬ ЖИЗНИ"),
                            ("financial_channel","◈ ФИНАНСОВЫЙ КАНАЛ"),("personal_year","⟐ ЛИЧНЫЙ ГОД"),
                            ("destiny","∞ ЧИСЛО СУДЬБЫ")]:
            d = data.get(key)
            if d and isinstance(d, dict) and d.get("value"):
                lines += [label, f"Значение: {d['value']}"]
                m = d.get("meaning", {})
                if m.get("title"):       lines.append(f"Архетип: {m['title']}")
                if m.get("description"): lines.append(f"Описание: {m['description']}")
                lines.append("")
        return PlainTextResponse("\n".join(lines), headers={
            "Content-Disposition": f'attachment; filename="numerology_{day}{month}{year}.txt"'
        })
    except Exception as e:
        raise HTTPException(500, str(e))

class KBAddRequest(BaseModel):
    title: str; content: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = []

@app.post("/api/knowledge/add", tags=["knowledge"])
def add_knowledge(req: KBAddRequest):
    import sqlite3 as sq
    if not DB_PATH.exists():
        raise HTTPException(503, "База данных недоступна")
    try:
        conn = sq.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (filename,title,content,doc_type,categories,content_length) VALUES (?,?,?,?,?,?)",
            (f"manual_{req.title[:30].replace(' ','_')}.txt", req.title, req.content,
             req.category, json.dumps(req.tags, ensure_ascii=False), len(req.content))
        )
        doc_id = cur.lastrowid
        conn.commit(); conn.close()
        return {"status": "ok", "doc_id": doc_id, "title": req.title}
    except Exception as e:
        raise HTTPException(500, str(e))

# ── Статика ───────────────────────────────────────────────────────
if APP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(APP_DIR), html=True), name="app")
else:
    @app.get("/")
    def root():
        return {"message": "API работает. Папка app/ не найдена."}

# ── Локальный запуск ──────────────────────────────────────────────
if __name__ == "__main__":
    log.info(f"🚀 http://localhost:{PORT}")
    log.info(f"📚 http://localhost:{PORT}/docs")
    log.info("💡 Для бота на Render задайте WEBHOOK_URL=https://ВАШ-СЕРВИС.onrender.com")
    import threading, time
    def _open():
        time.sleep(1.5); webbrowser.open(f"http://localhost:{PORT}")
    threading.Thread(target=_open, daemon=True).start()
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
