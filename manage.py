#!/usr/bin/env python3
"""
KNOWLEDGE BASE MANAGER v2.1
Centralizovannyj skript upravlenija vsemi komponentami
Proverka, nastrojka, diagnostika i zapusk
"""

import sys
import os
import json
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Zagruzka .env esli est
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("[OK] .env fajl zagruzhen")
except ImportError:
    pass

class ProjectManager:
    """Upravlenie proektom Knowledge Base"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Zagruzit ili sozdat konfiguraciju"""
        config_file = self.base_dir / "config.json"
        
        default_config = {
            "version": "2.1",
            "data_sources": {
                "pdf_folder": "C:/Users/New/Desktop/пдф",
                "auto_load_html": True
            },
            "features": {
                "ai_enabled": bool(os.getenv('OPENAI_API_KEY')),
                "telegram_enabled": bool(os.getenv('TELEGRAM_BOT_TOKEN')),
                "web_enabled": True,
                "cli_enabled": True
            },
            "database": {
                "sqlite_path": "data/knowledge_base.db",
                "history_path": "data/history.db"
            },
            "api": {
                "host": "localhost",
                "port": 8000,
                "web_port": 3000
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Objedinit s defoltami
                    default_config.update(loaded)
            except Exception as e:
                print(f"[WARN] Oshibka zagruzki config: {e}")
        
        return default_config
    
    def save_config(self):
        """Sohranit konfiguraciju"""
        config_file = self.base_dir / "config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("[OK] Konfiguracija sohranena")
        except Exception as e:
            print(f"[ERROR] Oshibka sohranenija config: {e}")
    
    def check_structure(self) -> Tuple[bool, List[str]]:
        """Proverit strukturu proekta"""
        print("\n" + "="*60)
        print("PROVERKA STRUKTURY PROEKTA")
        print("="*60)
        
        required = {
            'Core': [
                'knowledge_base.py',
                'ai_consultant.py', 
                'history_manager.py',
                'api_server.py'
            ],
            'Interfaces': [
                'calculator_cli.py',
                'telegram_bot.py',
                'launch_web.py'
            ],
            'Data': [
                'data/formulas.json',
                'data/practices.json',
                'data/number_meanings.json',
                'data/knowledge_base.db'
            ]
        }
        
        errors = []
        all_ok = True
        
        for category, files in required.items():
            print(f"\n{category}:")
            for file in files:
                path = self.base_dir / file
                if path.exists():
                    size = path.stat().st_size
                    print(f"  [OK] {file} ({size} bytes)")
                else:
                    print(f"  [ERR] {file} (OTSTVETVET)")
                    errors.append(file)
                    all_ok = False
        
        # Proverka zavisimostej
        print("\nZavisimosti:")
        deps = ['openai', 'python-telegram-bot', 'beautifulsoup4', 'python-dotenv']
        for dep in deps:
            try:
                __import__(dep.replace('-', '_'))
                print(f"  [OK] {dep}")
            except ImportError:
                print(f"  [ERR] {dep} (ne ustanovlen)")
                errors.append(f"pip install {dep}")
        
        return all_ok, errors
    
    def check_data_consistency(self) -> bool:
        """Proverit soglasovannost dannyh"""
        print("\n" + "="*60)
        print("PROVERKA SOGLASOVANNOSTI DANNYH")
        print("="*60)
        
        try:
            # JSON fajly
            with open(self.data_dir / 'formulas.json', 'r', encoding='utf-8') as f:
                formulas = json.load(f)
            print(f"  Formulas: {len(formulas)} zapisiej")
            
            with open(self.data_dir / 'practices.json', 'r', encoding='utf-8') as f:
                practices = json.load(f)
            print(f"  Praktiki: {len(practices)} zapisiej")
            
            # SQLite
            db_path = self.data_dir / 'knowledge_base.db'
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*), SUM(content_length) FROM documents')
                count, chars = cursor.fetchone()
                print(f"  SQLite: {count} dokumentov, {chars:,} simvolov")
                
                # Proverka HTML dokumentov
                cursor.execute("SELECT COUNT(*) FROM documents WHERE doc_type='html'")
                html_count = cursor.fetchone()[0]
                print(f"  HTML dokumentov: {html_count}")
                
                conn.close()
            
            return True
            
        except Exception as e:
            print(f"  [ERR] Oshibka: {e}")
            return False
    
    def setup_environment(self):
        """Nastrojka okruzhenija"""
        print("\n" + "="*60)
        print("NASTROJKA OKRUZhENIJa")
        print("="*60)
        
        # Proverka .env
        env_file = self.base_dir / '.env'
        if not env_file.exists():
            print("\n.env fajl ne najden. Sozdat?")
            choice = input("(y/n): ").strip().lower()
            if choice in ['y', 'yes', 'д', 'да']:
                self._create_env_file()
        else:
            print("[OK] .env fajl suschestvuet")
            # Proverka kljuchei
            openai_key = os.getenv('OPENAI_API_KEY')
            tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
            
            if openai_key:
                print(f"  [OK] OpenAI API kljuch: {openai_key[:20]}...")
                self.config['features']['ai_enabled'] = True
            else:
                print("  [WARN] OpenAI API kljuch ne najden")
                print("         AI-konsultant budet rabotat v offline rezhime")
            
            if tg_token:
                print(f"  [OK] Telegram token: {tg_token[:20]}...")
                self.config['features']['telegram_enabled'] = True
            else:
                print("  [WARN] Telegram token ne najden")
        
        # Nastrojka papki s PDF
        print(f"\nTekushhaja papka s PDF: {self.config['data_sources']['pdf_folder']}")
        print("Izmenit? (y/n): ", end='')
        if input().strip().lower() in ['y', 'yes', 'д', 'да']:
            new_path = input("Novyj put: ").strip()
            if new_path:
                self.config['data_sources']['pdf_folder'] = new_path
                print(f"[OK] Put obnovlen: {new_path}")
        
        self.save_config()
    
    def _create_env_file(self):
        """Sozdat .env fajl"""
        env_file = self.base_dir / '.env'
        
        print("\nNastrojka API kljuchei:")
        print("  (Mozhno propustit, nastroit potom)")
        
        openai_key = input("OpenAI API kljuch (Enter - propustit): ").strip()
        tg_token = input("Telegram Bot token (Enter - propustit): ").strip()
        
        content = f"""# Knowledge Base API Keys
# Sozdano: {datetime.now().isoformat()}

# OpenAI (dlja AI-konsultanta)
# Poluchenie: https://platform.openai.com/api-keys
OPENAI_API_KEY={openai_key}

# Telegram Bot (dlja bota)
# Poluchenie: @BotFather v Telegram
TELEGRAM_BOT_TOKEN={tg_token}
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] .env fajl sozdan: {env_file}")
        
        # Perezagruzit
        if openai_key or tg_token:
            load_dotenv(env_file)
            print("[OK] Kljuchi zagruzheny")
    
    def run_diagnostics(self):
        """Zapustit diagnostiku"""
        print("\n" + "="*60)
        print("DIAGNOSTIKA SISTEMY")
        print("="*60)
        
        all_ok = True
        
        # 1. Proverka struktury
        ok, errors = self.check_structure()
        if not ok:
            all_ok = False
            print("\n[!] Najdeny problemy v strukture:")
            for err in errors:
                print(f"    - {err}")
        
        # 2. Proverka dannyh
        if not self.check_data_consistency():
            all_ok = False
        
        # 3. Test bazovyh modulej
        print("\nTest bazovyh modulej:")
        try:
            sys.path.insert(0, str(self.base_dir))
            
            from knowledge_base import HybridKnowledgeBase
            kb = HybridKnowledgeBase()
            result = kb.calculate_life_path(15, 6, 1990)
            assert result['value'] == 4
            print("  ✓ KnowledgeBase (raschety)")
            kb.close()
            
            from history_manager import CalculationHistory
            hist = CalculationHistory()
            print("  ✓ History Manager")
            
            from ai_consultant import AIConsultant
            ai = AIConsultant()
            print(f"  ✓ AI Consultant (OpenAI: {ai.openai_available})")
            ai.close()
            
        except Exception as e:
            print(f"  ✗ Oshibka modulej: {e}")
            all_ok = False
        
        if all_ok:
            print("\n" + "="*60)
            print("✅ VSE TESTY PROJDENY!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠️  NAJDENY PROBLEMY")
            print("="*60)
        
        return all_ok
    
    def run_cli(self):
        """Zapustit CLI kalkulyator"""
        print("\n[Zapusk CLI kalkulyatora...]")
        subprocess.run([sys.executable, "calculator_cli.py"], cwd=self.base_dir)
    
    def run_web(self):
        """Zapustit Web + API"""
        print("\n[Zapusk Web + API...]")
        print("  Web: http://localhost:3000")
        print("  API: http://localhost:8000")
        print("  Nazhmite Ctrl+C dlja ostanovki\n")
        try:
            subprocess.run([sys.executable, "launch_web.py"], cwd=self.base_dir)
        except KeyboardInterrupt:
            print("\n[Ostanovka...]")
    
    def run_telegram(self):
        """Zapustit Telegram bot"""
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            print("\n[!] Telegram token ne nastrojen!")
            print("    Zapustite nastrojku (punkt 5)")
            return
        
        print("\n[Zapusk Telegram bota...]")
        print("  Nazhmite Ctrl+C dlja ostanovki\n")
        try:
            subprocess.run([sys.executable, "telegram_bot.py"], cwd=self.base_dir)
        except KeyboardInterrupt:
            print("\n[Ostanovka...]")
    
    def show_menu(self):
        """Pokazat glavnoe menju"""
        print("\n" + "="*60)
        print("KNOWLEDGE BASE MANAGER v2.1")
        print("="*60)
        print("\n1. [NASTROJKA] Okruzhenija (.env, config)")
        print("2. [TEST] Diagnostika sistemy")
        print("3. [CLI] Kalkulyator")
        print("4. [WEB] Web + API (localhost:3000)")
        print("5. [BOT] Telegram Bot")
        print("6. [INFO] Informacija o proekte")
        print("7. [EXIT] Vyhod")
        print("-"*60)
    
    def show_info(self):
        """Pokazat informaciju o proekte"""
        print("\n" + "="*60)
        print("INFORMACIJa O PROEKTE")
        print("="*60)
        
        print(f"\nVersija: {self.config['version']}")
        print(f"Papka proekta: {self.base_dir}")
        print(f"Papka dannyh: {self.data_dir}")
        
        print("\nFunkcii:")
        for feature, enabled in self.config['features'].items():
            status = "[ON]" if enabled else "[OFF]"
            print(f"  {status} {feature}")
        
        print("\nDostupnye interfejsy:")
        print("  • CLI kalkulyator (calculator_cli.py)")
        print("  • Web prilozhenie (app/index.html)")
        print("  • API server (api_server.py)")
        print("  • Telegram bot (telegram_bot.py)")
        
        print("\nBaza dannyh:")
        db_path = self.data_dir / 'knowledge_base.db'
        if db_path.exists():
            size = db_path.stat().st_size / (1024*1024)
            print(f"  • SQLite: {size:.2f} MB")
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM documents')
            count = cursor.fetchone()[0]
            print(f"  • Dokumentov: {count}")
            conn.close()
    
    def main(self):
        """Glavnyj cikl"""
        os.chdir(self.base_dir)
        
        while True:
            self.show_menu()
            choice = input("\nVash vybor (1-7): ").strip()
            
            try:
                if choice == '1':
                    self.setup_environment()
                elif choice == '2':
                    self.run_diagnostics()
                elif choice == '3':
                    self.run_cli()
                elif choice == '4':
                    self.run_web()
                elif choice == '5':
                    self.run_telegram()
                elif choice == '6':
                    self.show_info()
                elif choice == '7':
                    print("\nDo svidanija! 👋")
                    break
                else:
                    print("\nNеверный выбор!")
                
                if choice not in ['3', '4', '5']:
                    input("\nNazhmite Enter...")
                    
            except KeyboardInterrupt:
                print("\n\nDo svidanija! 👋")
                break
            except Exception as e:
                print(f"\nOshibka: {e}")
                input("\nNazhmite Enter...")


def main():
    """Tochka vhoda"""
    manager = ProjectManager()
    manager.main()


if __name__ == "__main__":
    main()
