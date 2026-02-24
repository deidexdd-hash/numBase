"""
AI КОНСУЛЬТАНТ — бесплатный AI через Gemini Flash (primary) и Groq (fallback)
RAG: контекст из базы знаний SQLite + JSON

Бесплатные API:
  - Google Gemini Flash: 15 RPM, 1M токенов/день (бесплатно)
    Получить ключ: https://aistudio.google.com/app/apikey
  - Groq (Llama 3.1): 30 RPM, 14400 запросов/день (бесплатно)
    Получить ключ: https://console.groq.com/

Установка:
  pip install google-generativeai groq
"""

import json
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATA_DIR = Path(__file__).parent / "data"

# ── Проверка доступных AI провайдеров ──────────────────────────────
def get_ai_provider():
    """Определить доступный AI провайдер (приоритет: Gemini → Groq → Local)"""
    
    # 1. Google Gemini (бесплатный tier: 15 RPM)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            return "gemini", genai
        except ImportError:
            pass
    
    # 2. Groq (бесплатный tier: Llama 3.1 8B)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            return "groq", client
        except ImportError:
            pass
    
    return "local", None


class AIConsultant:
    """AI Консультант на основе базы знаний — без платных API"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = DATA_DIR
        else:
            self.data_dir = Path(data_dir)
        
        # SQLite для полнотекстового поиска
        db_path = self.data_dir / "knowledge_base.db"
        self.conn = None
        if db_path.exists():
            self.conn = sqlite3.connect(str(db_path))
            self.conn.row_factory = sqlite3.Row
        
        # JSON данные
        self._load_knowledge()
        
        # AI провайдер
        self.provider_name, self.provider = get_ai_provider()

    def _load_knowledge(self):
        """Загрузить знания из JSON"""
        def load(name):
            p = self.data_dir / name
            if not p.exists():
                return {}
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        self.formulas = load("formulas.json")
        self.practices = load("practices.json")
        self.number_meanings = load("number_meanings.json")
        # Если number_meanings — список, конвертируем в dict
        if isinstance(self.number_meanings, list):
            self.number_meanings = {str(item.get('value','')): item for item in self.number_meanings}

    # ── Поиск в базе ────────────────────────────────────────────────
    def search_docs(self, query: str, limit: int = 5) -> List[Dict]:
        """Поиск по SQLite (FTS5 если есть, иначе LIKE)"""
        if not self.conn:
            return []
        try:
            cur = self.conn.cursor()
            # Попытка FTS5
            try:
                cur.execute("""
                    SELECT d.title, d.content
                    FROM documents_fts f
                    JOIN documents d ON f.rowid = d.id
                    WHERE f MATCH ? ORDER BY rank LIMIT ?
                """, (query, limit))
            except Exception:
                # Fallback LIKE
                cur.execute("""
                    SELECT title, content FROM documents
                    WHERE content LIKE ? OR title LIKE ? LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
            rows = cur.fetchall()
            return [{"title": r[0], "content": (r[1] or "")[:600]} for r in rows]
        except Exception as e:
            return []

    def build_context(self, query: str, user_data: dict = None) -> str:
        """Собрать контекст из базы знаний для ответа AI"""
        parts = []
        
        # 1. Релевантные документы
        docs = self.search_docs(query)
        if docs:
            parts.append("📚 МАТЕРИАЛЫ ИЗ БАЗЫ ЗНАНИЙ:")
            for i, doc in enumerate(docs, 1):
                parts.append(f"{i}. {doc['title']}: {doc['content'][:400]}...")
        
        # 2. Данные пользователя (числа расчётов)
        if user_data:
            parts.append("\n🔢 НУМЕРОЛОГИЧЕСКИЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:")
            for key, val in user_data.items():
                if isinstance(val, dict) and 'value' in val:
                    n = str(val['value'])
                    meaning = self.number_meanings.get(n, {})
                    if meaning:
                        parts.append(f"  {key}: {val['value']} — {meaning.get('title','')}")
                        desc = meaning.get('description', '')
                        if desc:
                            parts.append(f"    {desc[:200]}")
        
        # 3. Релевантные формулы
        if isinstance(self.formulas, list):
            qlow = query.lower()
            for f in self.formulas:
                if qlow in f.get('name','').lower() or qlow in f.get('description','').lower():
                    parts.append(f"\n⚙ Формула: {f['name']} — {f.get('description','')}")
        
        return "\n".join(parts) if parts else "База знаний по запросу не вернула результатов."

    # ── Вызов AI ────────────────────────────────────────────────────
    def ask(self, question: str, user_data: dict = None) -> dict:
        """Получить ответ AI на основе базы знаний"""
        context = self.build_context(question, user_data)
        
        system = """Ты — AI-консультант по нумерологии и ансестологии (работа с родом).
Отвечай на русском языке. Используй предоставленный контекст из базы знаний.
Давай глубокие, содержательные ответы с практическими рекомендациями.
Если информации недостаточно — скажи об этом честно."""
        
        user_msg = f"""Контекст из базы знаний:
{context}

Вопрос: {question}"""

        # Gemini
        if self.provider_name == "gemini":
            return self._ask_gemini(system, user_msg)
        
        # Groq
        if self.provider_name == "groq":
            return self._ask_groq(system, user_msg)
        
        # Local fallback
        return self._local_answer(question, context)

    def _ask_gemini(self, system: str, user_msg: str) -> dict:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=system
            )
            resp = model.generate_content(user_msg)
            return {
                "answer": resp.text,
                "provider": "gemini-1.5-flash",
                "status": "ok"
            }
        except Exception as e:
            return {"answer": f"Ошибка Gemini: {e}", "provider": "gemini", "status": "error"}

    def _ask_groq(self, system: str, user_msg: str) -> dict:
        try:
            resp = self.provider.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return {
                "answer": resp.choices[0].message.content,
                "provider": "groq-llama-3.1-8b",
                "status": "ok"
            }
        except Exception as e:
            return {"answer": f"Ошибка Groq: {e}", "provider": "groq", "status": "error"}

    def _local_answer(self, question: str, context: str) -> dict:
        """Локальный ответ без AI — на основе контекста из базы"""
        if context and "База знаний по запросу не вернула" not in context:
            answer = (
                "На основе базы знаний:\n\n" + context[:1200] + 
                "\n\n💡 Для развёрнутых AI-ответов добавьте GEMINI_API_KEY или GROQ_API_KEY в .env файл (оба бесплатны)."
            )
        else:
            answer = (
                "По вашему запросу информация в базе не найдена. "
                "Попробуйте уточнить запрос.\n\n"
                "💡 Для AI-ответов: получите бесплатный ключ на https://aistudio.google.com/app/apikey "
                "и добавьте GEMINI_API_KEY в .env"
            )
        return {"answer": answer, "provider": "local-kb", "status": "ok"}
