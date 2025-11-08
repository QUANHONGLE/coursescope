from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from _db import (get_db_connection, get_prerequisites_grouped,
                 get_difficulty_from_grades, estimate_difficulty, parse_credits)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read POST body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            completed_codes = data.get('completed', [])

            conn = get_db_connection()
            cursor = conn.cursor()

            # Get all courses
            cursor.execute('''
                SELECT id, course_code, course_number, title, credits, credits_undergrad, credits_grad, description, level
                FROM courses
                ORDER BY course_number
            ''')
            courses = cursor.fetchall()

            eligible = []

            for course in courses:
                # Skip if already completed
                if course['course_code'] in completed_codes:
                    continue

                prereq_data = get_prerequisites_grouped(course['id'])

                # Check if prerequisites are met
                prereqs_met = True
                if prereq_data['groups']:
                    for group in prereq_data['groups']:
                        group_met = any(prereq in completed_codes for prereq in group)
                        if not group_met:
                            prereqs_met = False
                            break

                if prereqs_met:
                    difficulty = get_difficulty_from_grades(course['course_code'])
                    if difficulty is None:
                        difficulty = estimate_difficulty(course['level'])

                    credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
                    credits_grad = course['credits_grad'] or parse_credits(course['credits'])

                    eligible.append({
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
                    })

            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(eligible).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
