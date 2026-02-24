# NASTROJKA API KLJuChEJ

## OpenAI API Key (dlja AI-konsultanta)

### Shag 1: Registracija na OpenAI

1. Perejdite na https://platform.openai.com/
2. Najmite "Sign up" i zaregistrirujtes
3. Podtverdite email
4. Vojdite v akkaunt

### Shag 2: Poluchenie API kljucha

1. Vojdite v https://platform.openai.com/api-keys
2. Najmite "+ Create new secret key"
3. Dajte nazvanie (naprimer: "Numerology Bot")
4. Skopirujte kljuch (on pokazyvaetsja tolko raz!)
   
   **Vazhno:** Kljuch vygliadit tak:
   ```
   sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Shag 3: Nastrojka v projekte

**Variant A: .env fajl (rekomenduetsja)**

1. Otkrojte fajl `.env` v papke projekta
2. Zamenite znachenie:
   ```
   OPENAI_API_KEY=sk-proj-vash-kljuch-zdes
   ```
3. Sohranite fajl

**Variant B: Peremennaja okruzhenija**

Windows (CMD):
```cmd
set OPENAI_API_KEY=sk-proj-vash-kljuch-zdes
```

Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="sk-proj-vash-kljuch-zdes"
```

Linux/Mac:
```bash
export OPENAI_API_KEY="sk-proj-vash-kljuch-zdes"
```

### Shag 4: Proverka

Zapustite AI-konsultanta:
```bash
python ai_consultant.py
```

Esli vse nastoreno verno, uvidite:
```
DEMO: AI KONSULTANT
====================
Vopros: Chto znachit put zhizni 7?
...
[AI Otvet]: ... (razvernutyj otvet)
```

---

## Telegram Bot Token (dlja bota)

### Shag 1: Sozdanie bota

1. Otkrojte Telegram i najdite @BotFather
2. Otpravte `/start`, zatem `/newbot`
3. Pridumajte nazvanie (naprimer: "Moj Numerolog")
4. Pridumajte username (okanchivaetsja na 'bot', naprimer: moj_numerolog_bot)
5. BotFather otpravit token:
   ```
   123456789:ABCdefGHIjklMNOpqrSTUvwxyz
   ```

### Shag 2: Nastrojka

**V .env fajle:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
```

**Ili v terminale:**
```bash
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
python telegram_bot.py
```

---

## BEZOPASNOST

**Vazhnye pravila:**

1. **Nikogda ne publikujte kljuchi v:**
   - GitHub/GitLab (publichnye repozitorii)
   - Skrinshotah
   - Messengerah
   - Dokumentacii

2. **Fajl .env dolzhen byt v .gitignore:**
   ```
   .env
   *.env
   ```

3. **Esli kljuch utek:**
   - OpenAI: udalite na https://platform.openai.com/api-keys
   - Telegram: otpravte `/revoke` @BotFather
   - Sozdaite novyj kljuch

4. **Limitacii OpenAI (besplatnyj tarif):**
   - 5 zaprosov v minutu
   - $5 kreditov na nachalo
   - Posle izrashodovanija - nuzhno popolnit

---

## PROVERKA RABOTY

### Test AI-konsultanta:
```bash
python ai_consultant.py
```

Ozhidaemyj rezultat:
- Esli kljuch est: poluchite AI-otvet
- Esli kljucha net: lokalnyj poisk s bazy

### Test Telegram bota:
```bash
python telegram_bot.py
```

Ozhidaemyj rezultat:
```
Zapusk bota...
Bot zapushen. Nazhmite Ctrl+C dlja ostanovki.
```

---

## REShENIE PROBLEM

### "OpenAI API kluch ne najden"

**Prichiny:**
1. Ne ustanovlena peremennaja OPENAI_API_KEY
2. Fajl .env ne najden ili nepravilnyj format
3. Oshibka v nazvanii peremennoj

**Reshenie:**
```bash
# Proverte ustanovku
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Dolzhno vyvesti vash kljuch
# Esli None - peremennaja ne ustanovlena
```

### "Rate limit exceeded"

**Prichina:** Slishkom mnogo zaprosov

**Reshenie:**
- Podozhdite neskolko minut
- Uvelichte zaderzhku mezhdu zaprosami
- Perejdjite na platnyj tarif OpenAI

### "Invalid API key"

**Prichina:** Nevernyj kljuch

**Reshenie:**
1. Proverte kljuch na https://platform.openai.com/api-keys
2. Skopirujte zanovo
3. Obnovite v .env fajle ili peremennyh

---

## POLEZNYE KOMANDY

### Windows:
```cmd
# Ustanovka (dlja tekushhej sessii)
set OPENAI_API_KEY=sk-xxx

# Proverte
set OPENAI_API_KEY

# Udalenie
set OPENAI_API_KEY=
```

### Linux/Mac:
```bash
# Ustanovka
export OPENAI_API_KEY="sk-xxx"

# Proverte
echo $OPENAI_API_KEY

# Udalenie
unset OPENAI_API_KEY
```

### Postojannaja nastrojka (Linux/Mac ~/.bashrc):
```bash
echo 'export OPENAI_API_KEY="sk-xxx"' >> ~/.bashrc
source ~/.bashrc
```

### Postojannaja nastrojka (Windows - sistemnye peremennye):
1. Panel upravlenija → Sistema → Dopolnitelnye parametry
2. Peremennye sredy
3. Novaja → Imja: OPENAI_API_KEY, Znachenie: sk-xxx

---

## STIMULY REKOMENDACII

Dla lichnogo ispolzovanija:
- Besplatnyj tarif OpenAI: $5 kreditov (hvataet na ~500 zaprosov)
- Stoimost GPT-3.5: ~$0.002 za 1000 tokenov (ochen deshevo)

Dla kommercheskogo ispolzovanija:
- Plata tolko za ispolzovanie (pay-as-you-go)
- Limitacii vyshe na platnyh tarifah

---

**GOTOVO K ISPOLZOVANIJu!** 🚀
