# NASTROJKA TELEGRAM BOTA

## Bystryj start (3 shaga)

### Shag 1: Poluchenie tokena (2 minuty)

1. Otkrojte **Telegram** na telefone ili kompjutere
2. Najdite bot **@BotFather** (oficialnyj bot dlja sozdanija botov)
3. Najmite **START** ili otpravte `/start`
4. Otpravte komandu `/newbot`
5. BotFather poprosit nazvanie:
   - Otpravte: `Moj Numerolog` (ili ljuboe drugoe)
6. BotFather poprosit username (dolzhen okanchivatjsja na 'bot'):
   - Otpravte: `moj_numerolog_bot` (primer)
7. **GOTovo!** BotFather prishet token:
   ```
   123456789:ABCdefGHIjklMNOpqrSTUvwxyz1234567890
   ```

**Vazhno:** Sohranite etot token - on nuzhen dlja zapuska!

---

### Shag 2: Ustanovka zavisimostej (1 minuta)

V terminale/cmd v papke projekta:

```bash
pip install python-telegram-bot
```

Esli u vas est OpenAI kljuch (opcjonalno):
```bash
pip install openai
```

---

### Shag 3: Nastrojka tokena i zapusk (1 minuta)

**Variant A: Cherez peremennuju okruzhenija (rekomenduetsja)**

**Windows:**
```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
python telegram_bot.py
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
python telegram_bot.py
```

**Variant B: Cherez .env fajl**

1. Sozdaem fajl `.env` v papke `knowledge_base_v2/`:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz1234567890
```

2. Izmenite `telegram_bot.py`:
```python
# V nachale fajla dobavte:
from dotenv import load_dotenv
load_dotenv()  # Zagruzka iz .env fajla
```

3. Zapuskajte:
```bash
python telegram_bot.py
```

**Variant C: Naprjamuju v kode** (ne rekomenduetsja dlja produkcii)

Otkrojte `telegram_bot.py` i najdite stroku:
```python
self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
```

Zamenite na:
```python
self.token = token or "123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
```

---

## Proverka raboty

Posle zapuska vy uvidite:
```
Zapusk bota...
Bot zapushen. Nazhmite Ctrl+C dlja ostanovki.
```

1. Otkrojte Telegram
2. Najdite vashego bota (po username, naprimer @moj_numerolog_bot)
3. Najmite **START**
4. Bot privetstvuet vas!

---

## Dostupnye komandy

| Komanda | Opisanie | Primer |
|---------|----------|--------|
| `/start` | Privetstvie i instrukcija | - |
| `/help` | Spisok vseh komand | - |
| `/menu` | Glavnoe menju s knopkami | - |
| `/life DD MM YYYY` | Put zhizni | `/life 15 6 1990` |
| `/birth DD` | Chislo rozhdenija | `/birth 15` |
| `/destiny FIO` | Chislo sudby | `/destiny Ivanov Ivan` |
| `/finance DD MM YYYY` | Finansovyj kanal | `/finance 15 6 1990` |
| `/chakras DD MM YYYY` | Balans chakr | `/chakras 15 6 1990` |
| `/search [zapros]` | Poisk po baze | `/search finansovyj kanal` |
| `/practices` | Spisok praktik | - |
| `/ask [vopros]` | AI-konsultant | `/ask chto znachit 7?` |

**Ficha:** Prosto napishite datu (naprimer `15.06.1990`) - bot sam rasschitaet vse vozmozhnye pokazateli!

---

## Dopolnitelnye nastrojki

### 1. Dobavlenie opisanija bota

V @BotFather:
1. Otpravte `/mybots`
2. Najdite vashego bota
3. Najmite **Edit Bot**
4. Nastrojte:
   - **Edit Name** - imja bota
   - **Edit Description** - opisanie v profile
   - **Edit About** - tekst v razdele "O bote"
   - **Edit Commands** - podskazki pri vvode /
   - **Edit Botpic** - avatar bota

### 2. Komandy dlja menju

V @BotFather otpravte:
```
/setcommands
```

Zatem spisok:
```
start - Nachat rabotu
help - Pomoshh
menu - Glavnoe menju
life - Put zhizni
birth - Chislo rozhdenija
destiny - Chislo sudby
finance - Finansovyj kanal
chakras - Balans chakr
search - Poisk po baze
practices - Praktiki
ask - Zadat vopros AI
```

### 3. Privedenie bota v "production"

**Dlja krupnyh proektov:**
1. Ispolzujte webhook vmesto polling:
```python
# Vmesto updater.start_polling()
updater.start_webhook(listen="0.0.0.0",
                      port=int(os.environ.get('PORT', '8443')),
                      url_path=TOKEN,
                      webhook_url=f"https://vash-server.com/{TOKEN}")
```

2. Ustanovite supervisor/dlja avtozapuska
3. Ispolzujte bazy dannyh (uzhe est SQLite)

---

## Reshenie problem

### Problem: "Neobhodim TELEGRAM_BOT_TOKEN"
**Reshenie:** Token ne najden. Proverte:
- Pravilno li zadan token?
- Isplzuetes li export/set pered zapuskom?
- Est li fajl .env s tokenom?

### Problem: "python-telegram-bot ne najden"
**Reshenie:**
```bash
pip install python-telegram-bot
```

### Problem: Bot ne otvet
**Reshenie:**
1. Proverte token (vozmozhno vy peresozdali bota)
2. Ubedites chto bota ne blokirovali v Telegram
3. Perezapustite skript

### Problem: Oshibki kodirovki
**Reshenie:**
- Windows: Zapuskajte v PowerShell vmesto cmd
- Linux/Mac: Vse dolzhno rabotat
- Ispolzujte UTF-8 kodirovku v terminale

---

## Struktura bota

```
telegram_bot.py
  ├── NumerologyBot (klass)
  │   ├── cmd_start()        # /start
  │   ├── cmd_help()         # /help
  │   ├── cmd_menu()         # /menu
  │   ├── cmd_life_path()    # /life
  │   ├── cmd_birth_number() # /birth
  │   ├── cmd_destiny()      # /destiny
  │   ├── cmd_finance()      # /finance
  │   ├── cmd_chakras()      # /chakras
  │   ├── cmd_search()       # /search
  │   ├── cmd_practices()    # /practices
  │   ├── cmd_ask()          # /ask
  │   └── handle_text()      # Obrabotka teksta
  └──
```

---

## Bezopasnost

**Vazhno:** Nikogda ne publikujte token v:
- GitHub/GitLab (publichnye repozitorii)
- Skrinshotah
- Dokumentacii
- Messengerah

Esli token utechet:
1. Srochno otpravte `/revoke` BotFather
2. Poluchite novyj token
3. Zametite vo vseh mestah ispolzovanija

---

## Podderzhka

Po voprosam raboty bota:
1. Proverte logi v terminale
2. Proverte dostupnost internet
3. Ubedites chto bota ne blokirovali
4. Perezapustite skript

---

**GOTovo k ispolzovaniju!** 🚀
