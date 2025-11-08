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
            # Parse major_id from query parameters
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)

            if 'id' not in params:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing major id parameter'}).encode())
                return

            major_id = int(params['id'][0])

            conn = get_db_connection()
            cursor = conn.cursor()

            # Get major info
            cursor.execute('SELECT name, concentration FROM majors WHERE id = ?', (major_id,))
            major = cursor.fetchone()

            if not major:
                conn.close()
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Major not found'}).encode())
                return

            # Get required course codes
            cursor.execute('''
                SELECT course_code, requirement_type
                FROM major_requirements
                WHERE major_id = ?
                ORDER BY requirement_type, course_code
            ''', (major_id,))

            requirements = cursor.fetchall()

            # Get elective course codes
            cursor.execute('''
                SELECT course_code, elective_type
                FROM major_electives
                WHERE major_id = ?
                ORDER BY elective_type, course_code
            ''', (major_id,))

            electives_data = cursor.fetchall()

            # Get full course details for each requirement
            required_courses = []
            for req in requirements:
                cursor.execute('''
                    SELECT id, course_code, course_number, title, credits, credits_undergrad, credits_grad, description, level, difficulty
                    FROM courses
                    WHERE course_code = ?
                ''', (req['course_code'],))

                course = cursor.fetchone()
                if course:
                    prereq_data = get_prerequisites_grouped(course['id'])
                    difficulty = get_difficulty_from_grades(course['course_code'])
                    if difficulty is None:
                        difficulty = course['difficulty'] or estimate_difficulty(course['level'])

                    credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
                    credits_grad = course['credits_grad'] or parse_credits(course['credits'])

                    required_courses.append({
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
                        'prerequisitesFormatted': prereq_data['formatted'],
                        'requirementType': req['requirement_type']
                    })

            # Get full course details for each elective
            elective_courses = []
            for elective in electives_data:
                cursor.execute('''
                    SELECT id, course_code, course_number, title, credits, credits_undergrad, credits_grad, description, level, difficulty
                    FROM courses
                    WHERE course_code = ?
                ''', (elective['course_code'],))

                course = cursor.fetchone()
                if course:
                    prereq_data = get_prerequisites_grouped(course['id'])
                    difficulty = get_difficulty_from_grades(course['course_code'])
                    if difficulty is None:
                        difficulty = course['difficulty'] or estimate_difficulty(course['level'])

                    credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
                    credits_grad = course['credits_grad'] or parse_credits(course['credits'])

                    elective_courses.append({
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
                        'prerequisitesFormatted': prereq_data['formatted'],
                        'electiveType': elective['elective_type']
                    })

            result = {
                'major': {
                    'id': major_id,
                    'name': major['name'],
                    'concentration': major['concentration']
                },
                'requiredCourses': required_courses,
                'electiveCourses': elective_courses
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
