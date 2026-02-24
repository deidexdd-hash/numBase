# VZAIMODEJSTVIE MODULEJ I POTOKI DANNYH

## Arhitektura vzaimodejstvija

```
┌─────────────────────────────────────────────────────────────┐
│                    SLOJ PREDSTAVLENIJa                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   CLI        │  │    Web       │  │   Telegram     │  │
│  │calculator_cli│  │  index.html  │  │    Bot         │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                 │                  │            │
│         └─────────────────┼──────────────────┘            │
│                           │                               │
└───────────────────────────┼───────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 SLOJ PRILOZhENIJa                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              manage.py (Central Controller)          │  │
│  │  • Upravlenie • Diagnostika • Nastrojka • Zapusk   │  │
│  └─────────────────────────┬────────────────────────────┘  │
│                            │                               │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │            │
│         ▼                  ▼                  ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │KnowledgeBase │  │ AI Consultant│  │History Manager │  │
│  │knowledge_base│  │ ai_consultant│  │history_manager │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                 │                  │            │
└─────────┼─────────────────┼──────────────────┼────────────┘
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SLOJ DANNYH                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   JSON       │  │   SQLite     │  │    SQLite      │  │
│  │  formulas    │  │ knowledge_   │  │   history      │  │
│  │  practices   │  │    base      │  │                │  │
│  └──────────────┘  └──────────────┘  └────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Detalnye potoki dannyh

### 1. Potok: CLI Kalkulyator

```
Polzovatel vvodit datu
        │
        ▼
calculator_cli.py
        │
        ├──► KnowledgeBase.calculate_life_path()
        │         │
        │         ├──► Chitaet formulas.json
        │         ├──► Chitaet number_meanings.json
        │         └──► Vozvrashhaet rezultat
        │
        └──► Pokazyvaet rezultat polzovatelju
```

### 2. Potok: AI Konsultant

```
Vopros polzovatelja
        │
        ▼
ai_consultant.py
        │
        ├──► 1. search_relevant_docs()
        │         │
        │         └──► SQLite (LIKE poisk)
        │               SELECT * FROM documents
        │               WHERE content LIKE '%vopros%'
        │
        ├──► 2. Poisk formul i praktik
        │         │
        │         ├──► Chitaet formulas.json
        │         └──► Chitaet practices.json
        │
        ├──► 3. Formirovanie prompta
        │         │
        │         └──► Sobiraet kontekst:
        │               - Dokumenty (top-5)
        │               - Formuly (relevantnye)
        │               - Praktiki (relevantnye)
        │               - Dannye polzovatelja
        │
        ├──► 4. OpenAI API
        │         │
        │         └──► POST /v1/chat/completions
        │               Model: gpt-3.5-turbo
        │               Prompt: system + user s kontekstom
        │
        └──► 5. Vozvrat otveta
                  │
                  └──► Esli OpenAI ne dostupen:
                        └──► Fallback: local_answer()
```

### 3. Potok: History Manager

```
Sohranenie rascheta
        │
        ▼
history_manager.py
        │
        ├──► 1. create_user()
        │         │
        │         └──► INSERT INTO users
        │               SQLite: data/history.db
        │
        ├──► 2. save_calculation()
        │         │
        │         └──► INSERT INTO calculations
        │               Polja: user_id, calc_type, 
        │                      input_data, result, 
        │                      created_at
        │
        └──► 3. Poluchenie istorii
                  │
                  ├──► get_user_history()
                  │     SELECT * FROM calculations
                  │     WHERE user_id = ?
                  │
                  └──► get_statistics()
                        SELECT COUNT(*), AVG(...)
                        GROUP BY calc_type
```

### 4. Potok: API Server

```
HTTP Zapros
        │
        ▼
api_server.py
        │
        ├──► GET /api/search?q=...&limit=...
        │         │
        │         ├──► Razbor parametrov
        │         ├──► SQLite poisk:
        │         │     SELECT ... FROM documents
        │         │     WHERE content LIKE ?
        │         ├──► Formirovanie snippets
        │         └──► JSON response
        │
        ├──► GET /api/documents?id=...
        │         │
        │         └──► Polnyj tekst dokumenta
        │
        ├──► GET /api/stats
        │         │
        │         └──► Obshhaja statistika
        │
        └──► GET /api/categories
                  │
                  └──► Spisok kategorij

        │
        └──► CORS zagolovki (dlja Web)
```

### 5. Potok: Telegram Bot

```
Sooobshhenie v Telegram
        │
        ▼
telegram_bot.py
        │
        ├──► Komanda /life 15 6 1990
        │         │
        │         ├──► Razbor argumentov
        │         ├──► KnowledgeBase.calculate_life_path()
        │         └──► Otvet v Telegram
        │
        ├──► Komanda /ask vopros
        │         │
        │         ├──► AIConsultant.ask(vopros)
        │         ├──► Poluchenie AI-otveta
        │         └──► Otvet v Telegram
        │
        └──► Tekst "15.06.1990"
                  │
                  ├──► Avtoraspoznavanie daty
                  ├──► Raschet vseh pokazatelej
                  └──► Svodnyj otvet v Telegram
```

### 6. Potok: Agregacija Dannyh

```
PDF i HTML fajly
        │
        ▼
aggregate_json.py
        │
        ├──► load_from_txt()
        │         │
        │         └──► Ctenie .txt fajlov
        │               (rezultat OCR)
        │
        ├──► load_from_html()
        │         │
        │         ├──► BeautifulSoup parsing
        │         └──► Izvlechenie teksta
        │
        ├──► load_json()
        │         │
        │         └──► Ctenie formulas.json
        │               practices.json
        │
        └──► save_to_sqlite()
                  │
                  ├──► INSERT INTO documents
                  └──► Sohranenie v knowledge_base.db
```

## Formaty dannyh

### 1. JSON Formula
```json
{
  "id": "life_path",
  "name": "Put zhizni",
  "category": "numerology",
  "formula": "DD + MM + GGGG → svodim k odnomu",
  "inputs": [...],
  "source_files": ["Life_Path.pdf"]
}
```

### 2. JSON Practice
```json
{
  "id": "genogram",
  "name": "Praktika genogrammy",
  "duration": "30-60 minut",
  "steps": ["Shag 1...", "Shag 2..."],
  "materials": ["bumaga", "ruchki"]
}
```

### 3. SQLite Documents
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    title TEXT,
    doc_type TEXT,  -- 'pdf', 'html', 'txt'
    categories TEXT, -- JSON array
    content TEXT,    -- Polnyj tekst
    content_length INTEGER
);
```

### 4. SQLite History
```sql
CREATE TABLE calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    calc_type TEXT,    -- 'life_path', 'birth_number', ...
    input_data TEXT,   -- JSON
    result TEXT,       -- JSON
    result_value INTEGER,
    created_at TEXT,
    notes TEXT
);
```

## Tablica vzaimodejstvija modulej

| Modul | Zavisit ot | Ispolzuetsja | Funkcija |
|-------|------------|--------------|----------|
| **manage.py** | vse | Centralnoe upravlenie | Diagnostika, nastrojka, zapusk |
| **knowledge_base.py** | JSON, SQLite | CLI, Web, Telegram, AI | Bazovye raschety i poisk |
| **ai_consultant.py** | KB, SQLite, OpenAI | Telegram, CLI (opcjonalno) | AI-otvety s kontekstom |
| **history_manager.py** | SQLite | CLI, Web (opcjonalno) | Hranenie istorii |
| **api_server.py** | KB, SQLite | Web (frontend) | HTTP API dlja poiska |
| **telegram_bot.py** | KB, AI, TelegramAPI | Polzovateli Telegram | Bot interface |
| **calculator_cli.py** | KB | Polzovateli CLI | CLI interface |
| **aggregate_json.py** | SQLite, BS4 | Inicializacija | Agregacija dannyh |

## Peredacha dannyh mezhdu slojami

### SLOJ PREDSTAVLENIJa → SLOJ PRILOZhENIJa
- **Vhod:** Komandy polzovatelja, zaprosy
- **Formata:** Tekst, komandy, HTTP zaprosy
- **Protokol:** STDIN/STDOUT, HTTP, Telegram API

### SLOJ PRILOZhENIJa → SLOJ DANNYH
- **Vhod:** Zaprosy na ctenie/zapis
- **Formata:** SQL zaprosy, JSON obekty
- **Protokol:** SQLite3, file I/O

### SLOJ DANNYH → VNEShNIE SERVISY
- **Vhod:** AI zaprosy
- **Formata:** JSON (HTTP POST)
- **Protokol:** HTTPS (OpenAI API)

## Zhiznennyj cikl zaprosa

### Primer: Polzovatel sprashivaet "Chto znachit put zhizni 7?"

1. **Vvod** (CLI/Web/Telegram)
   - Polzovatel vvodit vopros

2. **Marshrutizacija** (manage.py ili naprjamuju)
   - Zapros napravljaetsja v AIConsultant

3. **Sbor konteksta** (ai_consultant.py)
   - Poisk v SQLite (top-5 dokumentov)
   - Poisk formul s "put zhizni"
   - Poisk znachenija chisla 7
   - Sborka prompta

4. **Obrabotka** (OpenAI ili lokalno)
   - Generacija otveta na osnove konteksta

5. **Vyvodata** (SLOJ PREDSTAVLENIJa)
   - Otobrazhenie rezultata polzovatelju
   - Ukazanie istochnikov

6. **Sohranenie** (opcjonalno)
   - Zapros v history.db (esli vkliuchena istorija)

## Bezopasnost dannyh

### Lokalnoe hranenie:
- ✅ Vse dannye v lokalnyh fajlah
- ✅ Net oblachnoj sinhronizacii
- ✅ API kljuchi v .env (ne v kode)

### Zashhita:
- ✅ SQL-injekcii - zashhishheny parametrizaciej
- ✅ XSS - vhodnye dannye filtrujutsja (BeautifulSoup)
- ✅ Tokeny - hranjatsja v peremennyh okruzhenija

## Monitoring i diagnostika

### Chto proverjaet manage.py:

1. **Struktura:**
   - Vse fajly na meste
   - Pravilnye puti
   - Dostup k papkam

2. **Zavisimosti:**
   - openai
   - python-telegram-bot
   - beautifulsoup4
   - python-dotenv

3. **Bazy dannyh:**
   - Dostup k SQLite
   - Celostnost dannyh
   - Kolichestvo dokumentov

4. **Integracija:**
   - Testovye raschety
   - Testovye zaprosy k AI
   - Test sohranenija istorii

---

**Konec dokumentacii**
