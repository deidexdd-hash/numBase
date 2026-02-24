#!/usr/bin/env python3
"""
API Server for Numerology Knowledge Base
Simple HTTP server with SQLite search endpoint
"""

import json
import sqlite3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Paths
DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "knowledge_base.db"

class APIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler"""
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if path == '/api/search':
                self.handle_search(params)
            elif path == '/api/documents':
                self.handle_documents(params)
            elif path == '/api/stats':
                self.handle_stats()
            elif path == '/api/categories':
                self.handle_categories()
            else:
                self.send_error(404, json.dumps({"error": "Not found"}))
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_search(self, params):
        """Handle search request"""
        query = params.get('q', [''])[0]
        limit = int(params.get('limit', ['10'])[0])
        
        if not query:
            self.wfile.write(json.dumps({"results": [], "total": 0}).encode())
            return
        
        if not DB_PATH.exists():
            self.wfile.write(json.dumps({"results": [], "error": "Database not found"}).encode())
            return
        
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Search in content and title
            search_term = f"%{query}%"
            cursor.execute('''
                SELECT id, filename, title, doc_type, categories, content, content_length
                FROM documents
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY 
                    CASE 
                        WHEN title LIKE ? THEN 1
                        WHEN content LIKE ? THEN 2
                        ELSE 3
                    END,
                    content_length DESC
                LIMIT ?
            ''', (search_term, search_term, search_term, search_term, limit))
            
            results = []
            for row in cursor.fetchall():
                # Get snippet around match
                content = row['content'] or ''
                snippet = self.get_snippet(content, query, 150)
                
                results.append({
                    "id": row['id'],
                    "filename": row['filename'],
                    "title": row['title'],
                    "type": row['doc_type'],
                    "categories": json.loads(row['categories']) if row['categories'] else [],
                    "snippet": snippet,
                    "content_length": row['content_length']
                })
            
            response = {
                "query": query,
                "results": results,
                "total": len(results)
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        finally:
            conn.close()
    
    def handle_documents(self, params):
        """Get single document by ID"""
        doc_id = params.get('id', [''])[0]
        
        if not doc_id:
            self.wfile.write(json.dumps({"error": "ID required"}).encode())
            return
        
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, filename, title, doc_type, categories, content, content_length
                FROM documents
                WHERE id = ?
            ''', (doc_id,))
            
            row = cursor.fetchone()
            if row:
                document = {
                    "id": row['id'],
                    "filename": row['filename'],
                    "title": row['title'],
                    "type": row['doc_type'],
                    "categories": json.loads(row['categories']) if row['categories'] else [],
                    "content": row['content'],
                    "content_length": row['content_length']
                }
                self.wfile.write(json.dumps(document, ensure_ascii=False).encode())
            else:
                self.wfile.write(json.dumps({"error": "Document not found"}).encode())
                
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        finally:
            conn.close()
    
    def handle_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*), SUM(content_length) FROM documents')
            row = cursor.fetchone()
            
            stats = {
                "documents": row[0],
                "total_chars": row[1],
                "size_mb": round(row[1] / (1024 * 1024), 2) if row[1] else 0
            }
            
            self.wfile.write(json.dumps(stats).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        finally:
            conn.close()
    
    def handle_categories(self):
        """Get all categories"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT DISTINCT category 
                FROM category_index 
                ORDER BY category
            ''')
            
            categories = [row[0] for row in cursor.fetchall()]
            self.wfile.write(json.dumps({"categories": categories}).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        finally:
            conn.close()
    
    def get_snippet(self, text, query, context=150):
        """Extract snippet around query match"""
        lower_text = text.lower()
        lower_query = query.lower()
        
        pos = lower_text.find(lower_query)
        if pos == -1:
            return text[:context * 2] + "..."
        
        start = max(0, pos - context)
        end = min(len(text), pos + len(query) + context)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet

def run_server(port=8000):
    """Start HTTP server"""
    server = HTTPServer(('localhost', port), APIHandler)
    print(f"=" * 60)
    print(f"API Server started at http://localhost:{port}")
    print(f"=" * 60)
    print(f"\nAvailable endpoints:")
    print(f"  GET /api/search?q=query&limit=10")
    print(f"  GET /api/documents?id=1")
    print(f"  GET /api/stats")
    print(f"  GET /api/categories")
    print(f"\nPress Ctrl+C to stop")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
