#!/usr/bin/env python3
"""
TELEGRAM BOT — Нумерология и Ансестология
Токен: добавить TELEGRAM_BOT_TOKEN в .env когда будет готов

Команды:
    /start    — Приветствие
    /calc     — Нумерологический расчёт
    /search   — Поиск по базе знаний
    /ask      — AI-консультант
    /practices — Список практик

Запуск:
    python telegram_bot.py
"""

import os
import logging
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("⚠️ TELEGRAM_BOT_TOKEN не установлен")
    print("   1. Создайте бота у @BotFather: https://t.me/BotFather → /newbot")
    print("   2. Добавьте токен в .env: TELEGRAM_BOT_TOKEN=ваш_токен")
    print("   3. Запустите: python telegram_bot.py")
    sys.exit(0)

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        ContextTypes, filters, ConversationHandler
    )
except ImportError:
    print("❌ Установите: pip install python-telegram-bot==20.7")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from knowledge_base import HybridKnowledgeBase
from ai_consultant import AIConsultant

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")

kb = HybridKnowledgeBase()
ai = AIConsultant()

# Состояния ConversationHandler
WAITING_DATE = 1
WAITING_NAME = 2

# ── Хелпер форматирования ──────────────────────────────────────────
def format_meaning(meaning: dict, max_items: int = 4) -> str:
    """Форматировать интерпретацию числа для Telegram"""
    if not meaning:
        return ""
    lines = []
    if meaning.get("title"):
        lines.append(f"*{meaning['title']}*")
    if meaning.get("description"):
        lines.append(f"\n_{meaning['description'][:200]}_")
    if meaning.get("keywords"):
        lines.append(f"\n🔑 {', '.join(meaning['keywords'][:5])}")
    if meaning.get("positive"):
        lines.append(f"\n✦ {', '.join(meaning['positive'][:4])}")
    if meaning.get("chakra"):
        lines.append(f"\n🔮 {meaning['chakra']}")
    return "\n".join(lines)

# ── Обработчики команд ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = kb.get_db_stats()
    text = (
        "🌟 *Нумерология и Ансестология*\n\n"
        f"База знаний: *{stats.get('documents', 0)}* документов • "
        f"*{stats.get('formulas', 0)}* формул • "
        f"*{stats.get('practices', 0)}* практик\n\n"
        "Команды:\n"
        "/calc — Рассчитать нумерологию\n"
        "/search <запрос> — Поиск по базе\n"
        "/ask <вопрос> — AI-консультант\n"
        "/practices — Список практик\n"
        "/help — Помощь"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Как использовать бота:*\n\n"
        "1️⃣ `/calc` — введите дату рождения (ДД ММ ГГГГ)\n"
        "   Бот рассчитает: число рождения, путь жизни,\n"
        "   финансовый канал, личный год\n\n"
        "2️⃣ `/search карма` — поиск по базе знаний\n\n"
        "3️⃣ `/ask Что означает число 7 в нумерологии?`\n"
        "   AI-консультант отвечает на основе базы знаний\n\n"
        "4️⃣ `/practices` — список практик с родом"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def calc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите дату рождения в формате *ДД ММ ГГГГ*\n"
        "Например: `15 06 1990`\n\n"
        "Или сразу с именем:\n`15 06 1990 Мария Иванова`",
        parse_mode="Markdown"
    )
    return WAITING_DATE

async def calc_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split(None, 3)
    
    if len(parts) < 3:
        await update.message.reply_text(
            "❌ Формат: `15 06 1990` или `15 06 1990 Мария Иванова`",
            parse_mode="Markdown"
        )
        return WAITING_DATE
    
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        name = parts[3] if len(parts) > 3 else None
    except ValueError:
        await update.message.reply_text("❌ Введите числа: день месяц год")
        return WAITING_DATE
    
    await update.message.reply_text("⏳ Рассчитываю...")
    
    try:
        data = kb.calculate_all(day, month, year, name)
        lines = [f"📊 *Нумерология {day:02d}.{month:02d}.{year}*"]
        if name:
            lines.append(f"👤 {name}")
        lines.append("")
        
        sections = [
            ("birth_number",      "✦ Число рождения"),
            ("life_path",         "◉ Путь жизни"),
            ("financial_channel", "◈ Финансовый канал"),
            ("personal_year",     "⟐ Личный год"),
        ]
        if name:
            sections.append(("destiny", "∞ Число судьбы"))
        
        for key, label in sections:
            d = data.get(key)
            if d and d.get("value"):
                n = d["value"]
                m = d.get("meaning", {})
                title = m.get("title", "")
                desc = m.get("description", "")[:120]
                lines.append(f"*{label}: {n}*")
                if title:
                    lines.append(f"_{title}_")
                if desc:
                    lines.append(desc)
                if m.get("keywords"):
                    lines.append(f"🔑 {', '.join(m['keywords'][:4])}")
                lines.append("")
        
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    
    return ConversationHandler.END

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Использование: /search <ваш запрос>")
        return
    
    results = kb.search_documents(query, limit=5)
    if not results:
        await update.message.reply_text("❌ По вашему запросу ничего не найдено")
        return
    
    lines = [f"🔍 Найдено по «{query}»:\n"]
    for r in results:
        title = r.get("title", "Без названия")
        size = r.get("content_length", 0)
        lines.append(f"📄 *{title}*")
        if size:
            lines.append(f"   {size} символов")
        lines.append("")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Использование: /ask <ваш вопрос>")
        return
    
    await update.message.reply_text("🤔 Думаю...")
    result = ai.ask(question)
    answer = result.get("answer", "Не удалось получить ответ")
    provider = result.get("provider", "")
    
    text = f"💬 {answer[:3000]}"
    if provider:
        text += f"\n\n_Источник: {provider}_"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def practices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_practices = kb.get_all_practices()
    if not all_practices:
        await update.message.reply_text("Практики не найдены в базе")
        return
    
    lines = ["🌿 *Практики с Родом:*\n"]
    for p in all_practices[:8]:
        name = p.get("name", "Без названия")
        dur = p.get("duration", "")
        lines.append(f"• *{name}*" + (f" ({dur})" if dur else ""))
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

# ── Главная функция ──────────────────────────────────────────────
def main():
    log.info(f"🤖 Бот запускается с токеном: {TOKEN[:10]}...")
    
    app_bot = Application.builder().token(TOKEN).build()
    
    calc_handler = ConversationHandler(
        entry_points=[CommandHandler("calc", calc_start)],
        states={WAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("help", help_cmd))
    app_bot.add_handler(calc_handler)
    app_bot.add_handler(CommandHandler("search", search))
    app_bot.add_handler(CommandHandler("ask", ask_ai))
    app_bot.add_handler(CommandHandler("practices", practices))
    
    log.info("✅ Бот запущен. Ctrl+C для остановки.")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
