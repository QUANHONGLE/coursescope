from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from _db import get_db_connection

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

            # Check if course exists
            cursor.execute('''
                SELECT id, course_code, title
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

            # Get all grade distributions for this course
            cursor.execute('''
                SELECT
                    gd.instructor,
                    s.term,
                    s.year,
                    gd.grade_a,
                    gd.grade_b,
                    gd.grade_c,
                    gd.grade_d,
                    gd.grade_f,
                    gd.grade_w,
                    gd.grade_s,
                    gd.grade_u,
                    gd.total_students
                FROM grade_distributions gd
                JOIN semesters s ON gd.semester_id = s.id
                WHERE gd.course_code = ?
                ORDER BY s.year DESC, s.term, gd.instructor
            ''', (course_code,))

            distributions = cursor.fetchall()

            if not distributions:
                conn.close()
                result = {
                    'course_code': course['course_code'],
                    'course_title': course['title'],
                    'has_data': False,
                    'message': 'No grade distribution data available for this course',
                    'distributions': [],
                    'average': None
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return

            # Format distributions
            formatted_distributions = []
            total_a = total_b = total_c = total_d = total_f = total_w = total_s = total_u = 0
            total_students_all = 0

            for dist in distributions:
                instructor, term, year, a, b, c, d, f, w, s, u, total = dist

                # Calculate percentages for this distribution
                letter_grade_total = a + b + c + d + f

                formatted_distributions.append({
                    'instructor': instructor,
                    'semester': f"{term} {year}",
                    'term': term,
                    'year': year,
                    'grades': {
                        'A': a,
                        'B': b,
                        'C': c,
                        'D': d,
                        'F': f,
                        'W': w,
                        'S': s,
                        'U': u
                    },
                    'percentages': {
                        'A': round((a / letter_grade_total * 100), 1) if letter_grade_total > 0 else 0,
                        'B': round((b / letter_grade_total * 100), 1) if letter_grade_total > 0 else 0,
                        'C': round((c / letter_grade_total * 100), 1) if letter_grade_total > 0 else 0,
                        'D': round((d / letter_grade_total * 100), 1) if letter_grade_total > 0 else 0,
                        'F': round((f / letter_grade_total * 100), 1) if letter_grade_total > 0 else 0,
                        'W': round((w / total * 100), 1) if total > 0 else 0,
                    },
                    'total_students': total
                })

                # Accumulate for average
                total_a += a
                total_b += b
                total_c += c
                total_d += d
                total_f += f
                total_w += w
                total_s += s
                total_u += u
                total_students_all += total

            # Calculate overall averages
            letter_grade_total_all = total_a + total_b + total_c + total_d + total_f

            average = {
                'grades': {
                    'A': total_a,
                    'B': total_b,
                    'C': total_c,
                    'D': total_d,
                    'F': total_f,
                    'W': total_w,
                    'S': total_s,
                    'U': total_u
                },
                'percentages': {
                    'A': round((total_a / letter_grade_total_all * 100), 1) if letter_grade_total_all > 0 else 0,
                    'B': round((total_b / letter_grade_total_all * 100), 1) if letter_grade_total_all > 0 else 0,
                    'C': round((total_c / letter_grade_total_all * 100), 1) if letter_grade_total_all > 0 else 0,
                    'D': round((total_d / letter_grade_total_all * 100), 1) if letter_grade_total_all > 0 else 0,
                    'F': round((total_f / letter_grade_total_all * 100), 1) if letter_grade_total_all > 0 else 0,
                    'W': round((total_w / total_students_all * 100), 1) if total_students_all > 0 else 0,
                },
                'total_students': total_students_all,
                'semesters_count': len(distributions)
            }

            result = {
                'course_code': course['course_code'],
                'course_title': course['title'],
                'has_data': True,
                'distributions': formatted_distributions,
                'average': average
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
