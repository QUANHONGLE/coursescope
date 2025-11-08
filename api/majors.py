from http.server import BaseHTTPRequestHandler
import json
from _db import get_db_connection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
        return
