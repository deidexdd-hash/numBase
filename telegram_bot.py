#!/usr/bin/env python3
"""
TELEGRAM BOT - Numerologija i Ansestologija
Bot dlja bystryh raschetov i konsultacij
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Zagruzka peremennyh iz .env fajla (esli est)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Nastrojka logirovanija
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Proverka nalichija python-telegram-bot
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, Filters, CallbackContext
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Oshibka: ustanovite python-telegram-bot: pip install python-telegram-bot")
    sys.exit(1)

# Import nashih modulej
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_base import HybridKnowledgeBase

# Sostojanija razgovora
WAITING_DATE = 1
WAITING_NAME = 2
WAITING_QUESTION = 3

class NumerologyBot:
    """Telegram bot dlja numerologii"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("Neobhodim TELEGRAM_BOT_TOKEN")
        
        self.kb = HybridKnowledgeBase()
        self.updater = Updater(self.token)
        self.dp = self.updater.dispatcher
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Nastrojka obrabotchikov komand"""
        # Osnovnye komandy
        self.dp.add_handler(CommandHandler("start", self.cmd_start))
        self.dp.add_handler(CommandHandler("help", self.cmd_help))
        self.dp.add_handler(CommandHandler("menu", self.cmd_menu))
        
        # Komandy raschetov
        self.dp.add_handler(CommandHandler("life", self.cmd_life_path))
        self.dp.add_handler(CommandHandler("birth", self.cmd_birth_number))
        self.dp.add_handler(CommandHandler("destiny", self.cmd_destiny))
        self.dp.add_handler(CommandHandler("finance", self.cmd_finance))
        self.dp.add_handler(CommandHandler("chakras", self.cmd_chakras))
        
        # Poisk i praktiki
        self.dp.add_handler(CommandHandler("search", self.cmd_search))
        self.dp.add_handler(CommandHandler("practices", self.cmd_practices))
        
        # Konsultant
        self.dp.add_handler(CommandHandler("ask", self.cmd_ask))
        
        # Obrabotka tekstovyh soobshhenij
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_text))
        
        # Obrabotka oshibok
        self.dp.add_error_handler(self.error_handler)
    
    def cmd_start(self, update: Update, context: CallbackContext):
        """Komanda /start"""
        user = update.effective_user
        welcome_text = f"""
Zdravstvujte, {user.first_name}! 👋

Ja bot-numerolog. Pomogu:
🔢 Rasschitat vashi chisla
📚 Najti informaciju v baze znanij
🧠 Dat rekomendacii po praktikam

Ispolzujte /help dlja spiska komand
ili /menu dlja bystrogo dostupa.

📊 V baze: {self.kb.get_stats()['lightweight']['formulas']} formul, 
{self.kb.get_stats()['lightweight']['practices']} praktik
        """
        update.message.reply_text(welcome_text)
    
    def cmd_help(self, update: Update, context: CallbackContext):
        """Komanda /help"""
        help_text = """
📋 DOSTUPNYE KOMANDY:

🔢 RASChETY:
/life - Put zhizni (data rozhdenija)
/birth - Chislo rozhdenija (den)
/destiny - Chislo sudby (FIO)
/finance - Finansovyj kanal
/chakras - Balans chakr

📚 BAZA ZNANIJ:
/search [zapros] - Poisk po dokumentam
/practices - Spisok praktik

🧠 KONSULTANT:
/ask [vopros] - Zadat vopros AI

⚙️ DRUGIE:
/menu - Glavnoe menju
/help - Jeta spravka
        """
        update.message.reply_text(help_text)
    
    def cmd_menu(self, update: Update, context: CallbackContext):
        """Glavnoe menju s knopkami"""
        keyboard = [
            [InlineKeyboardButton("🔢 Put zhizni", callback_data='calc_life'),
            InlineKeyboardButton("🎂 Chislo rozhdenija", callback_data='calc_birth')],
            [InlineKeyboardButton("✨ Chislo sudby", callback_data='calc_destiny'),
            InlineKeyboardButton("💰 Finansy", callback_data='calc_finance')],
            [InlineKeyboardButton("🧘 Praktiki", callback_data='show_practices'),
            InlineKeyboardButton("🔍 Poisk", callback_data='show_search')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Vyberite dejstvie:', reply_markup=reply_markup)
    
    def cmd_life_path(self, update: Update, context: CallbackContext):
        """Raschet puti zhizni"""
        args = context.args
        if len(args) >= 3:
            try:
                day, month, year = int(args[0]), int(args[1]), int(args[2])
                result = self.kb.calculate_life_path(day, month, year)
                
                response = f"""
🌟 PUT ZHIZNI: {result['value']}

Raschet: {day} + {month} + {year} = {result['details']['total']} → {result['value']}

{result['meaning'].get('title', '')}

{result['meaning'].get('description', '')[:300]}...
                """
                update.message.reply_text(response)
            except Exception as e:
                update.message.reply_text(f"Oshibka rascheta: {e}")
        else:
            update.message.reply_text(
                "Ispolzovanie: /life DD MM YYYY\n"
                "Primer: /life 15 6 1990"
            )
    
    def cmd_birth_number(self, update: Update, context: CallbackContext):
        """Raschet chisla rozhdenija"""
        args = context.args
        if args:
            try:
                day = int(args[0])
                result = self.kb.calculate_birth_number(day)
                
                response = f"""
🎂 ChISLO ROZhDENIJa: {result['value']}

Raschet: {day} → {result['value']}

{result['meaning'].get('title', '')}

{result['meaning'].get('description', '')[:300]}...
                """
                update.message.reply_text(response)
            except Exception as e:
                update.message.reply_text(f"Oshibka: {e}")
        else:
            update.message.reply_text("Ispolzovanie: /birth DD\nPrimer: /birth 15")
    
    def cmd_destiny(self, update: Update, context: CallbackContext):
        """Raschet chisla sudby"""
        if context.args:
            fullname = ' '.join(context.args)
            result = self.kb.calculate_destiny_number(fullname)
            
            response = f"""
✨ ChISLO SUDBY: {result['value']}

FIO: {fullname}

{result['meaning'].get('title', '')}

{result['meaning'].get('description', '')[:300]}...
            """
            update.message.reply_text(response)
        else:
            update.message.reply_text("Ispolzovanie: /destiny Ivanov Ivan Ivanovich")
    
    def cmd_finance(self, update: Update, context: CallbackContext):
        """Finansovyj kanal"""
        args = context.args
        if len(args) >= 3:
            try:
                day, month, year = int(args[0]), int(args[1]), int(args[2])
                result = self.kb.calculate_financial_channel(day, month, year)
                
                response = f"""
💰 FINANSOVYJ KANAL: {result['D']}

A (Den) = {result['A']}
B (Mesyac) = {result['B']}
C (Summa cifr goda) = {result['C']}
D (Itog) = {result['D']}

Vash finansovyj kod: {result['D']}
                """
                update.message.reply_text(response)
            except Exception as e:
                update.message.reply_text(f"Oshibka: {e}")
        else:
            update.message.reply_text("Ispolzovanie: /finance DD MM YYYY")
    
    def cmd_chakras(self, update: Update, context: CallbackContext):
        """Balans chakr"""
        args = context.args
        if len(args) >= 3:
            try:
                day, month, year = int(args[0]), int(args[1]), int(args[2])
                result = self.kb.calculate_chakras(day, month, year)
                
                chakras_text = "\n".join([
                    f"{name}: {value}"
                    for name, value in result['chakras'].items()
                ])
                
                response = f"""
🕉️ BALANS ChAKR:

{chakras_text}

Vsego centrov: 7
                """
                update.message.reply_text(response)
            except Exception as e:
                update.message.reply_text(f"Oshibka: {e}")
        else:
            update.message.reply_text("Ispolzovanie: /chakras DD MM YYYY")
    
    def cmd_search(self, update: Update, context: CallbackContext):
        """Poisk po baze"""
        if context.args:
            query = ' '.join(context.args)
            results = self.kb.search_documents(query, limit=5)
            
            if results:
                response = f"🔍 Rezultaty poiska '{query}':\n\n"
                for i, doc in enumerate(results, 1):
                    response += f"{i}. {doc['title']}\n"
                    response += f"   {doc['snippet'][:100]}...\n\n"
            else:
                response = f"Po zaprosu '{query}' nichego ne najdeno."
            
            update.message.reply_text(response)
        else:
            update.message.reply_text("Ispolzovanie: /search finansovyj kanal")
    
    def cmd_practices(self, update: Update, context: CallbackContext):
        """Spisok praktik"""
        practices = self.kb.practices
        
        response = "🧘 DOSTUPNYE PRAKTIKI:\n\n"
        for i, p in enumerate(practices[:10], 1):
            response += f"{i}. {p['name']}\n"
            if p.get('duration'):
                response += f"   Dlitelnost: {p['duration']}\n"
            response += "\n"
        
        response += "\nDlja podrobnostej o praktike napishite ee nazvanie."
        update.message.reply_text(response)
    
    def cmd_ask(self, update: Update, context: CallbackContext):
        """Zadat vopros AI"""
        if context.args:
            question = ' '.join(context.args)
            update.message.reply_text("Dumaju nad otvetom... 🤔")
            
            # Proverka dostupnosti AI
            try:
                from ai_consultant import AIConsultant
                consultant = AIConsultant()
                result = consultant.ask(question)
                
                if result['success']:
                    answer = result['answer']
                    if len(answer) > 4000:
                        answer = answer[:4000] + "..."
                    update.message.reply_text(answer)
                else:
                    update.message.reply_text(f"Lokalnyj otvet:\n{result['local_answer']}")
                
                consultant.close()
            except Exception as e:
                update.message.reply_text(f"Izvinite, proizoshla oshibka: {e}")
        else:
            update.message.reply_text("Ispolzovanie: /ask chto znachit put zhizni 7?")
    
    def handle_text(self, update: Update, context: CallbackContext):
        """Obrabotka obychnyh soobshhenij"""
        text = update.message.text
        
        # Proverka, mozhet eto data?
        if '.' in text and len(text.split('.')) == 3:
            try:
                parts = text.split('.')
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                
                # Avtomaticheski raschet vseh pokazatelej
                life = self.kb.calculate_life_path(day, month, year)
                birth = self.kb.calculate_birth_number(day)
                finance = self.kb.calculate_financial_channel(day, month, year)
                
                response = f"""
📊 VASHI ChISLA (data: {text}):

🌟 Put zhizni: {life['value']} ({life['meaning'].get('title', '')})
🎂 Chislo rozhdenija: {birth['value']} ({birth['meaning'].get('title', '')})
💰 Finansovyj kanal: {finance['D']}

Ispolzujte /help dlja vseh vozmozhnostej!
                """
                update.message.reply_text(response)
                return
            except:
                pass
        
        # Obychnyj otvet
        update.message.reply_text(
            f"Polucheno soobshhenie: {text}\n\n"
            "Ispolzujte /menu dlja dejstvij ili /help dlja spravki."
        )
    
    def error_handler(self, update: Update, context: CallbackContext):
        """Obrabotka oshibok"""
        logger.error(f"Oshibka: {context.error}")
        if update and update.effective_message:
            update.effective_message.reply_text("Proizoshla oshibka. Poprobujte pozzhe.")
    
    def run(self):
        """Zapustit bota"""
        logger.info("Zapusk bota...")
        self.updater.start_polling()
        logger.info("Bot zapushen. Nazhmite Ctrl+C dlja ostanovki.")
        self.updater.idle()


def main():
    """Tochka vhoda"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("=" * 60)
        print("Oshibka: ne zadan TELEGRAM_BOT_TOKEN")
        print("=" * 60)
        print("\nPoluchenie tokena:")
        print("1. Najdite @BotFather v Telegram")
        print("2. Otpravte /newbot")
        print("3. Sledujte instrukcijam")
        print("4. Skopirujte token")
        print("\nZapusk:")
        print("  export TELEGRAM_BOT_TOKEN='vash-token'")
        print("  python telegram_bot.py")
        print("=" * 60)
        return
    
    bot = NumerologyBot(token)
    bot.run()


if __name__ == "__main__":
    main()
