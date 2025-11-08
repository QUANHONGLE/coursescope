from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from _db import get_db_connection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, concentration
                FROM majors
                ORDER BY name, concentration
            ''')

            majors = cursor.fetchall()
            result = []

            for major in majors:
                result.append({
                    'id': major['id'],
                    'name': major['name'],
                    'concentration': major['concentration']
                })

            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
