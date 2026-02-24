# KALKULYATOR NUMEROLOGII v2.0

## Fazy razrabotki

- [x] **Phase 1: MVP** - CLI kalkulyator (Zaversheno)
- [x] **Phase 2: Core** - Web prilozhenie + API (Zaversheno)
- [ ] **Phase 3: Advanced** - AI-konsultant (V processe)

## Varianty zapuska

### 1. CLI Kalkulyator (MVP)

```bash
cd knowledge_base_v2
python calculator_cli.py
```

**Dostupnye funkcii:**
1. Put zhizni (Life Path)
2. Chislo rozhdeniya
3. Chislo sudby po FIO
4. Finansovyj kanal
5. Balans chakr
6. Poisk po baze
7. Spisok formul (15 sht)
8. Praktiki (8 sht)
9. Statistika

### 2. Web Prilozhenie + API (Phase 2)

**Variant A: Avtozapusk vsego**
```bash
python launch_web.py
# Otkroetsya brauzer avtomaticheski
# Web: http://localhost:3000
# API: http://localhost:8000
```

**Variant B: Ruchnoj zapusk**
```bash
# Terminal 1: API server
python api_server.py

# Terminal 2: Web server
cd app
python -m http.server 3000

# Otkryt v brauzere
# http://localhost:3000
```

**Vozmozhnosti Web:**
- Adptivnyj dizajn (mobile-friendly)
- 9 razdelov s bokovym menu
- Polnotekstovyj poisk po 105 dokumentam
- Fallback na lokalnyj poisk esli API nedostupen
- Kрасивye karty rezultatov

### 3. API Ispolzovanie

```bash
# Poisk
curl "http://localhost:8000/api/search?q=finansovyj&limit=5"

# Statistika
curl "http://localhost:8000/api/stats"

# Kategorii
curl "http://localhost:8000/api/categories"

# Dokument
curl "http://localhost:8000/api/documents?id=1"
```

## Struktura proekta

```
knowledge_base_v2/
├── knowledge_base.py       # Python API
├── calculator_cli.py       # CLI interfejs
├── api_server.py           # HTTP API server [NEW]
├── launch_web.py           # Zapuskatel web+api [NEW]
├── app/
│   └── index.html          # Web prilozhenie [NEW]
└── data/
    ├── knowledge_base.db   # SQLite (105 docs)
    ├── formulas.json       # 15 formul
    └── practices.json      # 8 praktik
```

## Testirovanie

```bash
# Test CLI
echo "9" | python calculator_cli.py

# Test API
python api_server.py &
curl http://localhost:8000/api/stats

# Test Web
python launch_web.py
```

## Dannye

- **PDF dokumentov:** 83
- **HTML dokumentov:** 2
- **Vsego v baze:** 105 dokumentov
- **Obem teksta:** 898,830 simvolov
- **Formul:** 15
- **Praktik:** 8

## Sleduyushij shag (Phase 3)

- AI-konsultant (OpenAI integraciya)
- Istoriya raschetov
- Telegram bot
