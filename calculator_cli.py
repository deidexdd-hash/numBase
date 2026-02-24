#!/usr/bin/env python3
"""
KALKULYATOR NUMEROLOGII - CLI
Interaktivnyj kalkulyator dlya raboty s bazoj znanij
"""

import sys
from pathlib import Path

# Dobavlyaem put k knowledge_base
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_base import HybridKnowledgeBase

class CalculatorApp:
    """Interaktivnyj kalkulyator"""
    
    def __init__(self):
        self.kb = HybridKnowledgeBase()
        self.running = True
    
    def show_banner(self):
        """Pokazat privetstvie"""
        print("\n" + "=" * 60)
        print("  [KALKULYATOR NUMEROLOGII I ANSESTOLOGII]")
        print("=" * 60)
        print("\nDostupnye raschety:")
        print("  1. Put zhizni (Life Path)")
        print("  2. Chislo rozhdeniya (Birth Number)")
        print("  3. Chislo sudby po FIO (Destiny Number)")
        print("  4. Finansovyj kanal")
        print("  5. Balans chakr")
        print("  6. Poisk po baze znanij")
        print("  7. Spisok vseh formul")
        print("  8. Praktiki")
        print("  9. Statistika bazy")
        print("  0. Vyhod")
        print("-" * 60)
    
    def get_date_input(self):
        """Poluchit datu ot polzovatelya"""
        print("\nVvedite datu rozhdeniya:")
        while True:
            try:
                date_str = input("  Data (DD.MM.YYYY): ").strip()
                day, month, year = map(int, date_str.split('.'))
                
                if not (1 <= day <= 31):
                    print("  [OSHIbKA] Den dolzhen byt 1-31")
                    continue
                if not (1 <= month <= 12):
                    print("  [OSHIbKA] Mesyac dolzhen byt 1-12")
                    continue
                if not (1900 <= year <= 2100):
                    print("  [OSHIbKA] God dolzhen byt 1900-2100")
                    continue
                
                return day, month, year
            except ValueError:
                print("  [OSHIbKA] Nevernyj format. Ispolzujte: DD.MM.YYYY")
    
    def calculate_life_path(self):
        """Raschet puti zhizni"""
        print("\n" + "=" * 60)
        print("  [PUT ZHIZNI]")
        print("=" * 60)
        
        day, month, year = self.get_date_input()
        
        try:
            result = self.kb.calculate_life_path(day, month, year)
            
            print(f"\n[REZULTAT]:")
            print(f"  Chislo: {result['value']}")
            print(f"  Raschet: {day} + {month} + {year} = {result['details']['total']} -> {result['value']}")
            
            if result['meaning']:
                print(f"\n[ZNACHENIE]:")
                print(f"  {result['meaning'].get('title', '')}")
                desc = result['meaning'].get('description', '')
                if desc:
                    print(f"\n  {desc[:300]}...")
            
        except Exception as e:
            print(f"  [OSHIbKA]: {e}")
    
    def calculate_birth_number(self):
        """Raschet chisla rozhdeniya"""
        print("\n" + "=" * 60)
        print("  [CHISLO ROZHDENIYa]")
        print("=" * 60)
        
        print("\nVvedite den rozhdeniya:")
        while True:
            try:
                day = int(input("  Den (1-31): ").strip())
                if 1 <= day <= 31:
                    break
                print("  [OSHIbKA] Den dolzhen byt 1-31")
            except ValueError:
                print("  [OSHIbKA] Vvedite chislo")
        
        try:
            result = self.kb.calculate_birth_number(day)
            
            print(f"\n[REZULTAT]:")
            print(f"  Chislo: {result['value']}")
            print(f"  Raschet: {day} -> {result['value']}")
            
            if result['meaning']:
                print(f"\n[ZNACHENIE]:")
                print(f"  {result['meaning'].get('title', '')}")
                desc = result['meaning'].get('description', '')
                if desc:
                    print(f"\n  {desc[:300]}...")
            
        except Exception as e:
            print(f"  [OSHIbKA]: {e}")
    
    def calculate_destiny_number(self):
        """Raschet chisla sudby po FIO"""
        print("\n" + "=" * 60)
        print("  [CHISLO SUDBY (po FIO)]")
        print("=" * 60)
        
        fullname = input("\nVvedite FIO: ").strip()
        
        if not fullname:
            print("  [OSHIbKA] FIO ne mozhet byt pustym")
            return
        
        try:
            result = self.kb.calculate_destiny_number(fullname)
            
            print(f"\n[REZULTAT]:")
            print(f"  Chislo: {result['value']}")
            print(f"  FIO: {result['fullname']}")
            
            if result['meaning']:
                print(f"\n[ZNACHENIE]:")
                print(f"  {result['meaning'].get('title', '')}")
                desc = result['meaning'].get('description', '')
                if desc:
                    print(f"\n  {desc[:300]}...")
            
        except Exception as e:
            print(f"  [OSHIbKA]: {e}")
    
    def calculate_financial_channel(self):
        """Raschet finansovogo kanala"""
        print("\n" + "=" * 60)
        print("  [FINANSOVYJ KANAL]")
        print("=" * 60)
        
        day, month, year = self.get_date_input()
        
        try:
            result = self.kb.calculate_financial_channel(day, month, year)
            
            print(f"\n[RASChET]:")
            print(f"  A (Den) = {result['A']}")
            print(f"  B (Mesyac) = {result['B']}")
            print(f"  C (Summa cifr goda) = {result['C']}")
            print(f"  D (Itog) = {result['D']}")
            
            print(f"\n[*] Finansovyj kanal: {result['D']}")
            
        except Exception as e:
            print(f"  [OSHIbKA]: {e}")
    
    def calculate_chakras(self):
        """Raschet balansa chakr"""
        print("\n" + "=" * 60)
        print("  [BALANS CHAKR]")
        print("=" * 60)
        
        day, month, year = self.get_date_input()
        
        try:
            result = self.kb.calculate_chakras(day, month, year)
            
            chakras_names = {
                1: "Muladhara (kornevaya)",
                2: "Svadhistana (krestcovaya)",
                3: "Manipura (pupochnaya)",
                4: "Anahata (serdechnaya)",
                5: "Vishuddha (gorlovaya)",
                6: "Adzhna (tretij glaz)",
                7: "Sahasrara (koronnaya)"
            }
            
            print(f"\n[REZULTATY po chakram]:")
            for chakra_num, value in result['chakras'].items():
                name = chakras_names.get(chakra_num, f"Chakra {chakra_num}")
                print(f"  {chakra_num}. {name}: {value}")
            
            # Analiz
            print(f"\n[*] Analiz:")
            values = list(result['chakras'].values())
            avg = sum(values) / len(values)
            max_chakra = max(result['chakras'].items(), key=lambda x: x[1])
            min_chakra = min(result['chakras'].items(), key=lambda x: x[1])
            
            print(f"  Srednee znachenie: {avg:.1f}")
            print(f"  Samaya silnaya: {chakras_names[max_chakra[0]]} ({max_chakra[1]})")
            print(f"  Trebuet vnimaniya: {chakras_names[min_chakra[0]]} ({min_chakra[1]})")
            
        except Exception as e:
            print(f"  [OSHIbKA]: {e}")
    
    def search_knowledge(self):
        """Poisk po baze znanij"""
        print("\n" + "=" * 60)
        print("  [POISK PO BAZE ZNANIJ]")
        print("=" * 60)
        
        if not self.kb.db_cursor:
            print("\n[!] Baza SQLite ne dostupna.")
            print("  Zapustite snachala agregaciyu dannyh")
            return
        
        query = input("\nVvedite poiskovyj zapros: ").strip()
        
        if not query:
            print("  [OSHIbKA] Zaprosm ne mozhet byt pustym")
            return
        
        try:
            results = self.kb.search_documents(query, limit=10)
            
            print(f"\n[Najdeno dokumentov: {len(results)}]")
            
            if results:
                for i, doc in enumerate(results, 1):
                    print(f"\n{i}. [DOK] {doc['title']}")
                    print(f"   Tip: {doc['type']}")
                    if doc['categories']:
                        print(f"   Kategorii: {', '.join(doc['categories'])}")
            else:
                print("\n  Nichego ne najdeno.")
            
        except Exception as e:
            print(f"  [OSHIbKA] Poiska: {e}")
    
    def list_all_formulas(self):
        """Pokazat vse formuly"""
        print("\n" + "=" * 60)
        print("  [VSE FORMULY]")
        print("=" * 60)
        
        formulas = self.kb.formulas
        
        print(f"\nVsego formul: {len(formulas)}\n")
        
        # Gruppiruem po kategoriyam
        by_category = {}
        for f in formulas:
            cat = f.get('category', 'drugoe')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f)
        
        for category, items in by_category.items():
            print(f"\n{category.upper()}:")
            for f in items:
                print(f"  - {f.get('name', 'Bez nazvaniya')}")
                print(f"    {f.get('description', '')[:60]}...")
    
    def show_practices(self):
        """Pokazat praktiki"""
        print("\n" + "=" * 60)
        print("  [PRAKTIKI]")
        print("=" * 60)
        
        practices = self.kb.practices
        
        print(f"\nVsego praktik: {len(practices)}\n")
        
        for i, p in enumerate(practices, 1):
            print(f"{i}. {p.get('name', 'Bez nazvaniya')}")
            if p.get('duration'):
                print(f"   Dlitelnost: {p['duration']}")
            if p.get('description'):
                print(f"   Opisanie: {p['description'][:80]}...")
            print()
        
        # Predlagaem vybrat praktiku
        choice = input("Vyberite nomer praktiki dlya detalej (Enter - propustit): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(practices):
                self.show_practice_details(practices[idx])
    
    def show_practice_details(self, practice):
        """Pokazat detali praktiki"""
        print("\n" + "=" * 60)
        print(f"  [PRAKTIKA: {practice.get('name', '').upper()}]")
        print("=" * 60)
        
        if practice.get('description'):
            print(f"\n[Opisanie]:")
            print(f"  {practice['description']}")
        
        if practice.get('duration'):
            print(f"\n[Dlitelnost]: {practice['duration']}")
        
        if practice.get('materials'):
            print(f"\n[Materialy]:")
            for m in practice['materials']:
                print(f"  - {m}")
        
        if practice.get('steps'):
            print(f"\n[Shagi]:")
            for i, step in enumerate(practice['steps'], 1):
                print(f"  {i}. {step}")
    
    def show_stats(self):
        """Pokazat statistiku"""
        print("\n" + "=" * 60)
        print("  [STATISTIKA BAZY ZNANIJ]")
        print("=" * 60)
        
        stats = self.kb.get_stats()
        
        print(f"\n[JSON dannye (Lightweight)]:")
        print(f"  - Formul: {stats['lightweight']['formulas']}")
        print(f"  - Praktik: {stats['lightweight']['practices']}")
        print(f"  - Algoritmov: {stats['lightweight']['algorithms']}")
        print(f"  - Znachenij chisel: {stats['lightweight']['number_meanings']}")
        print(f"  - Razmer: {stats['lightweight']['size_kb']} KB")
        
        if stats['fulltext']:
            print(f"\n[SQLite baza (Full-text)]:")
            print(f"  - Dokumentov: {stats['fulltext']['documents']}")
            print(f"  - Obshchij obem teksta: {stats['fulltext']['total_chars']:,} simvolov")
            print(f"  - Razmer: ~{stats['fulltext']['size_mb']} MB")
        else:
            print(f"\n[SQLite baza]: ne dostupna")
    
    def run(self):
        """Glavnyj cikl"""
        while self.running:
            self.show_banner()
            
            choice = input("\nVyberite dejstvie (0-9): ").strip()
            
            if choice == '1':
                self.calculate_life_path()
            elif choice == '2':
                self.calculate_birth_number()
            elif choice == '3':
                self.calculate_destiny_number()
            elif choice == '4':
                self.calculate_financial_channel()
            elif choice == '5':
                self.calculate_chakras()
            elif choice == '6':
                self.search_knowledge()
            elif choice == '7':
                self.list_all_formulas()
            elif choice == '8':
                self.show_practices()
            elif choice == '9':
                self.show_stats()
            elif choice == '0':
                self.running = False
                print("\nDo svidaniya!")
            else:
                print("\n  [OSHIbKA] Nevernyj vybor.")
            
            if self.running:
                input("\nNazhmite Enter dlya prodolzheniya...")
        
        self.kb.close()


def main():
    """Tochka vhoda"""
    try:
        app = CalculatorApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nPrervano polzovatelem")
    except Exception as e:
        print(f"\n[KRITICHESKAYA OSHIbKA]: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
