#!/usr/bin/env python3
"""
Istorija raschetov - modul dlja sohranenija i upravlenija raschetami
Podderzhka profilej polzovatelej i istorii
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

class UserProfile:
    """Profil polzovatelja"""
    
    def __init__(self, user_id: str, name: str = "", email: str = ""):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = datetime.now().isoformat()
        self.calculations = []
    
    def to_dict(self) -> Dict:
        """Konvertirovat v slovar"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at,
            'calculations_count': len(self.calculations)
        }


class CalculationHistory:
    """Upravlenie istoriej raschetov"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = Path(__file__).parent / "data" / "history.db"
        else:
            self.db_path = Path(db_path)
        
        self._init_database()
        self.current_user = None
    
    def _init_database(self):
        """Inicializirovat bazu dannyh"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tablica polzovatelej
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                created_at TEXT,
                birth_date TEXT,
                life_path INTEGER,
                birth_number INTEGER
            )
        ''')
        
        # Tablica raschetov
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                calc_type TEXT,
                input_data TEXT,
                result TEXT,
                result_value INTEGER,
                created_at TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Indeksy
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_calc_user ON calculations(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_calc_type ON calculations(calc_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_calc_date ON calculations(created_at)')
        
        conn.commit()
        conn.close()
    
    def create_user(self, name: str, email: str = "", birth_date: str = None) -> UserProfile:
        """Sozdat novogo polzovatelja"""
        # Generirovat ID iz email ili imeni
        user_id = hashlib.md5(f"{email or name}{datetime.now()}".encode()).hexdigest()[:12]
        
        user = UserProfile(user_id, name, email)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (user_id, name, email, created_at, birth_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, email, user.created_at, birth_date))
        
        conn.commit()
        conn.close()
        
        self.current_user = user
        return user
    
    def login_user(self, user_id: str) -> Optional[UserProfile]:
        """Vojti kak polzovatel"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = UserProfile(row[0], row[1], row[2])
            user.created_at = row[3]
            self.current_user = user
            return user
        return None
    
    def save_calculation(self, calc_type: str, input_data: Dict, result: Dict, 
                        notes: str = "") -> int:
        """Sohranit raschet"""
        if not self.current_user:
            raise ValueError("Neobhodimo vojti kak polzovatel")
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        calc_data = {
            'user_id': self.current_user.user_id,
            'calc_type': calc_type,
            'input_data': json.dumps(input_data, ensure_ascii=False),
            'result': json.dumps(result, ensure_ascii=False),
            'result_value': result.get('value'),
            'created_at': datetime.now().isoformat(),
            'notes': notes
        }
        
        cursor.execute('''
            INSERT INTO calculations (user_id, calc_type, input_data, result, 
                                    result_value, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (calc_data['user_id'], calc_data['calc_type'], calc_data['input_data'],
              calc_data['result'], calc_data['result_value'], calc_data['created_at'],
              calc_data['notes']))
        
        calc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return calc_id
    
    def get_user_history(self, user_id: str = None, calc_type: str = None, 
                        limit: int = 50) -> List[Dict]:
        """Poluchit istoriju raschetov polzovatelja"""
        if user_id is None and self.current_user:
            user_id = self.current_user.user_id
        
        if not user_id:
            return []
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if calc_type:
            cursor.execute('''
                SELECT * FROM calculations 
                WHERE user_id = ? AND calc_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, calc_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM calculations 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'calc_type': row['calc_type'],
                'input_data': json.loads(row['input_data']),
                'result': json.loads(row['result']),
                'result_value': row['result_value'],
                'created_at': row['created_at'],
                'notes': row['notes']
            })
        
        conn.close()
        return results
    
    def get_calculation(self, calc_id: int) -> Optional[Dict]:
        """Poluchit konkretnyj raschet po ID"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM calculations WHERE id = ?', (calc_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'calc_type': row['calc_type'],
                'input_data': json.loads(row['input_data']),
                'result': json.loads(row['result']),
                'created_at': row['created_at'],
                'notes': row['notes']
            }
        return None
    
    def delete_calculation(self, calc_id: int) -> bool:
        """Udalit raschet"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM calculations WHERE id = ?', (calc_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return deleted
    
    def get_statistics(self, user_id: str = None) -> Dict:
        """Poluchit statistiku polzovatelja"""
        if user_id is None and self.current_user:
            user_id = self.current_user.user_id
        
        if not user_id:
            return {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Obshhee kolichestvo
        cursor.execute('SELECT COUNT(*) FROM calculations WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()[0]
        
        # Po tipam
        cursor.execute('''
            SELECT calc_type, COUNT(*), AVG(result_value)
            FROM calculations 
            WHERE user_id = ?
            GROUP BY calc_type
        ''', (user_id,))
        
        by_type = {}
        for row in cursor.fetchall():
            by_type[row[0]] = {
                'count': row[1],
                'avg_value': round(row[2], 2) if row[2] else None
            }
        
        # Poslednie raschety
        cursor.execute('''
            SELECT created_at FROM calculations 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id,))
        
        last_calc = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_calculations': total,
            'by_type': by_type,
            'last_calculation': last_calc[0] if last_calc else None
        }
    
    def list_all_users(self) -> List[Dict]:
        """Spisok vseh polzovatelej"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, COUNT(c.id) as calc_count
            FROM users u
            LEFT JOIN calculations c ON u.user_id = c.user_id
            GROUP BY u.user_id
            ORDER BY u.created_at DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'created_at': row['created_at'],
                'calculations': row['calc_count']
            })
        
        conn.close()
        return results
    
    def export_history(self, user_id: str = None, format: str = 'json') -> str:
        """Jeksportirovat istoriju"""
        if user_id is None and self.current_user:
            user_id = self.current_user.user_id
        
        history = self.get_user_history(user_id, limit=1000)
        
        if format == 'json':
            return json.dumps(history, ensure_ascii=False, indent=2)
        elif format == 'html':
            # Prostoj HTML
            html = ["<html><head><meta charset='utf-8'><title>Istorija raschetov</title></head><body>"]
            html.append("<h1>Istorija raschetov</h1>")
            html.append("<table border='1'><tr><th>Data</th><th>Tip</th><th>Rezultat</th><th>Zametki</th></tr>")
            
            for calc in history:
                html.append(f"<tr>")
                html.append(f"<td>{calc['created_at'][:10]}</td>")
                html.append(f"<td>{calc['calc_type']}</td>")
                html.append(f"<td>{calc['result_value']}</td>")
                html.append(f"<td>{calc['notes']}</td>")
                html.append(f"</tr>")
            
            html.append("</table></body></html>")
            return "\n".join(html)
        
        return ""


def demo():
    """Demonstracija raboty s istoriej"""
    print("=" * 70)
    print("DEMO: ISTORIJa RASChETOV")
    print("=" * 70)
    
    history = CalculationHistory()
    
    # 1. Sozdat polzovatelja
    print("\n[1] Sozdanie polzovatelja...")
    user = history.create_user("Ivan Ivanov", "ivan@example.com", "15.06.1990")
    print(f"    Sozdan polzovatel: {user.name} (ID: {user.user_id})")
    
    # 2. Sohranit neskolko raschetov
    print("\n[2] Sohranenie raschetov...")
    
    calcs = [
        ('life_path', {'day': 15, 'month': 6, 'year': 1990}, {'value': 4, 'title': 'Chetverka'}, 'Glavnyj raschet'),
        ('birth_number', {'day': 15}, {'value': 6, 'title': 'Shestorka'}, ''),
        ('finance', {'day': 15, 'month': 6, 'year': 1990}, {'value': 7, 'title': 'Semerka'}, 'Finansovyj analiz'),
    ]
    
    for calc_type, input_data, result, notes in calcs:
        calc_id = history.save_calculation(calc_type, input_data, result, notes)
        print(f"    Sohranen raschet #{calc_id}: {calc_type} = {result['value']}")
    
    # 3. Pokazat istoriju
    print("\n[3] Istorija raschetov:")
    user_history = history.get_user_history(limit=10)
    for calc in user_history:
        print(f"    {calc['created_at'][:10]} | {calc['calc_type']:15} | {calc['result_value']} | {calc['notes'][:30]}")
    
    # 4. Statistika
    print("\n[4] Statistika:")
    stats = history.get_statistics()
    print(f"    Vsego raschetov: {stats['total_calculations']}")
    print(f"    Po tipam:")
    for calc_type, data in stats['by_type'].items():
        print(f"      - {calc_type}: {data['count']} raschetov")
    
    # 5. Jeksport
    print("\n[5] Jeksport v JSON:")
    export = history.export_history(format='json')
    print(f"    Jeksportirovano {len(json.loads(export))} zapisiej")
    
    print("\n" + "=" * 70)
    print("Demo zaversheno!")
    print("=" * 70)


if __name__ == "__main__":
    demo()
