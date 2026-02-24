#!/usr/bin/env python3
"""
AI KONSULTANT - Module dlya integrecii s OpenAI
Otvety na osnove bazy znanij ispolzuja RAG (Retrieval Augmented Generation)
"""

import json
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional

# Zagruzka peremennyh iz .env fajla (esli est)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# OpenAI API key iz peremennyh sredy
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def check_openai_available() -> bool:
    """Proverit dostupnost OpenAI"""
    try:
        import openai
        return OPENAI_API_KEY is not None
    except ImportError:
        return False

class AIConsultant:
    """AI Konsultant na osnove bazy znanij"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.db_path = self.data_dir / "knowledge_base.db"
        self.conn = None
        
        if self.db_path.exists():
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        
        # Zagruzka formul i praktik
        self._load_knowledge()
        
        # Inicializaciya OpenAI
        self.openai_available = check_openai_available()
        if self.openai_available:
            import openai
            openai.api_key = OPENAI_API_KEY
    
    def _load_knowledge(self):
        """Zagruzit znanija iz JSON"""
        try:
            with open(self.data_dir / "formulas.json", 'r', encoding='utf-8') as f:
                self.formulas = json.load(f)
            
            with open(self.data_dir / "practices.json", 'r', encoding='utf-8') as f:
                self.practices = json.load(f)
                
            with open(self.data_dir / "number_meanings.json", 'r', encoding='utf-8') as f:
                self.number_meanings = {item['value']: item for item in json.load(f)}
        except Exception as e:
            print(f"Oshibka zagruzki znanij: {e}")
            self.formulas = []
            self.practices = []
            self.number_meanings = {}
    
    def search_relevant_docs(self, query: str, limit: int = 5) -> List[Dict]:
        """Najti relevantnye dokumenty iz SQLite"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            search_term = f"%{query}%"
            
            cursor.execute('''
                SELECT id, filename, title, content, content_length
                FROM documents
                WHERE content LIKE ? OR title LIKE ?
                LIMIT ?
            ''', (search_term, search_term, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'title': row['title'],
                    'content': row['content'][:1000],  # Pervaia 1000 simvolov
                    'filename': row['filename']
                })
            
            return results
        except Exception as e:
            print(f"Oshibka poiska: {e}")
            return []
    
    def get_context_for_query(self, query: str, user_data: Dict = None) -> str:
        """Sobrat kontekst dlja OpenAI zaprosa"""
        context_parts = []
        
        # 1. Najti relevantnye dokumenty
        docs = self.search_relevant_docs(query)
        if docs:
            context_parts.append("RELEVANTNYE DOKUMENTY IZ BAZY:")
            for i, doc in enumerate(docs, 1):
                context_parts.append(f"{i}. {doc['title']}: {doc['content'][:500]}...")
            context_parts.append("")
        
        # 2. Najti podhodyashhie formuly
        relevant_formulas = []
        query_lower = query.lower()
        for formula in self.formulas:
            if (query_lower in formula.get('name', '').lower() or 
                query_lower in formula.get('description', '').lower() or
                query_lower in formula.get('category', '').lower()):
                relevant_formulas.append(formula)
        
        if relevant_formulas:
            context_parts.append("RELEVANTNYE FORMULY:")
            for f in relevant_formulas[:3]:
                context_parts.append(f"- {f['name']}: {f['description']}")
            context_parts.append("")
        
        # 3. Najti praktiki
        relevant_practices = []
        for practice in self.practices:
            if (query_lower in practice.get('name', '').lower() or
                query_lower in practice.get('description', '').lower()):
                relevant_practices.append(practice)
        
        if relevant_practices:
            context_parts.append("REKOMENDUEMYE PRAKTIKI:")
            for p in relevant_practices[:3]:
                context_parts.append(f"- {p['name']}: {p.get('description', '')[:200]}")
            context_parts.append("")
        
        # 4. Dobavit dannye polzovatelja esli est
        if user_data:
            context_parts.append("DANNYE POLZOVATELJA:")
            if 'life_path' in user_data:
                lp = user_data['life_path']
                meaning = self.number_meanings.get(lp, {})
                context_parts.append(f"- Put zhizni: {lp} ({meaning.get('title', '')})")
            if 'birth_number' in user_data:
                bn = user_data['birth_number']
                meaning = self.number_meanings.get(bn, {})
                context_parts.append(f"- Chislo rozhdenija: {bn} ({meaning.get('title', '')})")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def ask(self, question: str, user_data: Dict = None) -> Dict:
        """Zadat vopros AI konsultantu"""
        if not self.openai_available:
            return {
                'success': False,
                'error': 'OpenAI ne dostupen. Ustanovite: pip install openai i zadajte OPENAI_API_KEY',
                'local_answer': self.generate_local_answer(question)
            }
        
        try:
            import openai
            
            # Poluchit kontekst
            context = self.get_context_for_query(question, user_data)
            
            # Sozdat prompt
            system_prompt = """Ty ekspert po numerologii i ansestologii. 
Ispolzuj predostavlennyj kontekst iz bazy znanij dlja otveta na vopros.
Bud dostoveren, empatichen i predlaga konkretnye rekomendacii.
Esli ne znaesh otveta tochno, skazhi ob etom otverenno."""
            
            user_prompt = f"""KONTEKST IZ BAZY ZNANIJ:
{context}

VOPROS POLZOVATELJA:
{question}

Daj razvernutyj, empatichnyj otvet s konkretnymi rekomendacijami."""
            
            # Zapros k OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            return {
                'success': True,
                'answer': answer,
                'context_used': len(context) > 0,
                'sources': [doc['title'] for doc in self.search_relevant_docs(question, 3)]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'local_answer': self.generate_local_answer(question)
            }
    
    def generate_local_answer(self, question: str) -> str:
        """Generirovat otvet bez OpenAI (lokalno)"""
        # Najti relevantnye formuly i praktiki
        query_lower = question.lower()
        
        answer_parts = ["LOKALNYJ OTVET (bez AI):\n"]
        
        # Najti formuly
        matching_formulas = [f for f in self.formulas 
                           if query_lower in f.get('name', '').lower() or 
                           query_lower in f.get('description', '').lower()]
        
        if matching_formulas:
            answer_parts.append("Naidennye formuly:")
            for f in matching_formulas[:3]:
                answer_parts.append(f"• {f['name']}: {f['description']}")
            answer_parts.append("")
        
        # Najti praktiki
        matching_practices = [p for p in self.practices
                            if query_lower in p.get('name', '').lower() or
                            query_lower in p.get('description', '').lower()]
        
        if matching_practices:
            answer_parts.append("Rekomenduemye praktiki:")
            for p in matching_practices[:3]:
                answer_parts.append(f"• {p['name']}: {p.get('description', '')[:150]}...")
            answer_parts.append("")
        
        if not matching_formulas and not matching_practices:
            answer_parts.append("Po vashemu zaprosu nichego ne najdeno v baze.")
            answer_parts.append("Poprobujte drugie kluchevye slova ili zadajte bolee obschij vopros.")
        
        return "\n".join(answer_parts)
    
    def analyze_life_path(self, life_path_number: int) -> Dict:
        """Analiz puti zhizni s AI"""
        meaning = self.number_meanings.get(life_path_number, {})
        
        question = f"Kakovy osobennosti cheloveka s putem zhizni {life_path_number} - {meaning.get('title', '')}? Kakie zadachi i prednaznachenie?"
        
        return self.ask(question, {'life_path': life_path_number})
    
    def get_practice_recommendation(self, life_path: int, issue: str) -> Dict:
        """Poluchit rekomendacii po praktikam"""
        question = f"Kakie praktiki rekomendujutsja dlja cheloveka s putem zhizni {life_path} po voprosu: {issue}?"
        return self.ask(question, {'life_path': life_path})
    
    def close(self):
        """Zakryt soedinenija"""
        if self.conn:
            self.conn.close()


def demo():
    """Demonstracija raboty AI konsultanta"""
    print("=" * 70)
    print("DEMO: AI KONSULTANT")
    print("=" * 70)
    
    consultant = AIConsultant()
    
    if not consultant.openai_available:
        print("\n[!] OpenAI API kluch ne najden.")
        print("Zadajte: export OPENAI_API_KEY='vash-kluch'")
        print("Libo zagruzite iz .env fajla")
        print("\nBudet ispolzovatsja lokalnyj poisk.")
    
    # Testovye voprosy
    test_questions = [
        "Chto znachit put zhizni 7?",
        "Kak uluchshit finansovoe polozhenie?",
        "Kakie praktiki pomogut s rodovymi programmami?",
    ]
    
    for question in test_questions:
        print(f"\n{'='*70}")
        print(f"Vopros: {question}")
        print('='*70)
        
        result = consultant.ask(question)
        
        if result['success']:
            print(f"\n[AI Otvet]:")
            print(result['answer'])
            if result['sources']:
                print(f"\n[Istochniki]: {', '.join(result['sources'])}")
        else:
            print(f"\n[Oshibka]: {result['error']}")
            print(f"\n[Lokalnyj otvet]:")
            print(result['local_answer'])
    
    consultant.close()
    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo()
