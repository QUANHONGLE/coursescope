from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from _db import (get_db_connection, get_prerequisites_grouped,
                 get_difficulty_from_grades, estimate_difficulty, parse_credits)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse course_code from query parameters
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)

            if 'code' not in params:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing course code parameter'}).encode())
                return

            course_code = params['code'][0].upper()

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, course_code, course_number, title, credits, credits_undergrad, credits_grad, description, level
                FROM courses
                WHERE course_code = ?
            ''', (course_code,))

            course = cursor.fetchone()

            if course is None:
                conn.close()
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Course not found'}).encode())
                return

            prereq_data = get_prerequisites_grouped(course['id'])
            difficulty = get_difficulty_from_grades(course['course_code'])
            if difficulty is None:
                difficulty = estimate_difficulty(course['level'])

            credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
            credits_grad = course['credits_grad'] or parse_credits(course['credits'])

            result = {
                'id': course['course_code'].lower().replace(' ', ''),
                'code': course['course_code'],
                'title': course['title'],
                'credits': credits_undergrad,
                'creditsUndergrad': credits_undergrad,
                'creditsGrad': credits_grad,
                'level': course['level'],
                'difficulty': difficulty,
                'description': course['description'],
                'prerequisiteGroups': prereq_data['groups'],
                'prerequisitesFormatted': prereq_data['formatted']
            }

            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
