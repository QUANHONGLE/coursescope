from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from _db import (get_db_connection, format_prerequisites_from_list,
                 estimate_difficulty, parse_credits)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get all courses
            cursor.execute('''
                SELECT id, course_code, course_number, title, credits, credits_undergrad, credits_grad, description, level, difficulty
                FROM courses
                ORDER BY course_number
            ''')
            courses = cursor.fetchall()

            # Fetch ALL prerequisites in one query
            cursor.execute('''
                SELECT course_id, prerequisite_code, group_id
                FROM prerequisites
                ORDER BY course_id, group_id, prerequisite_code
            ''')
            all_prereqs = cursor.fetchall()

            # Fetch ALL grade distributions in one query
            cursor.execute('''
                SELECT
                    course_code,
                    SUM(grade_a) as total_a,
                    SUM(grade_b) as total_b,
                    SUM(grade_c) as total_c,
                    SUM(grade_d) as total_d,
                    SUM(grade_f) as total_f
                FROM grade_distributions
                GROUP BY course_code
            ''')
            all_grades = cursor.fetchall()

            # Build lookup dictionaries for O(1) access
            prereqs_by_course = {}
            for prereq in all_prereqs:
                course_id = prereq['course_id']
                if course_id not in prereqs_by_course:
                    prereqs_by_course[course_id] = []
                prereqs_by_course[course_id].append({
                    'code': prereq['prerequisite_code'],
                    'group': prereq['group_id']
                })

            grades_by_course = {}
            for grade_row in all_grades:
                total_a = grade_row['total_a'] or 0
                total_b = grade_row['total_b'] or 0
                total_c = grade_row['total_c'] or 0
                total_d = grade_row['total_d'] or 0
                total_f = grade_row['total_f'] or 0
                total_letter = total_a + total_b + total_c + total_d + total_f

                if total_letter > 0:
                    ab_pct = ((total_a + total_b) / total_letter) * 100
                    if ab_pct >= 70:
                        grades_by_course[grade_row['course_code']] = "Light"
                    elif ab_pct >= 50:
                        grades_by_course[grade_row['course_code']] = "Moderate"
                    else:
                        grades_by_course[grade_row['course_code']] = "Challenging"

            # Build result with O(1) lookups instead of N queries
            result = []
            for course in courses:
                # Get prerequisites from lookup
                prereq_list = prereqs_by_course.get(course['id'], [])
                prereq_data = format_prerequisites_from_list(prereq_list)

                # Get difficulty from lookup
                difficulty = grades_by_course.get(course['course_code'])
                if difficulty is None:
                    difficulty = course['difficulty'] or estimate_difficulty(course['level'])

                credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
                credits_grad = course['credits_grad'] or parse_credits(course['credits'])

                result.append({
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
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
