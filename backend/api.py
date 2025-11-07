from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import sqlite3
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for development

# Configure caching
cache_config = {
    'CACHE_TYPE': 'SimpleCache',  # In-memory cache
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes default
}
app.config.from_mapping(cache_config)
cache = Cache(app)

@app.get("/")
def home():
    return {"ok": True, "service": "CourseScope API", "docs": "/api/majors"}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'uic_courses.db')

if not os.path.exists(DATABASE):
    print(f"ERROR: Database file '{DATABASE}' not found!")
    print("Please run generic_course_scraper.py and generic_major_scraper.py first to create the database.")
    exit(1)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Get all majors
@app.route('/api/majors', methods=['GET'])
@cache.cached(timeout=600)  # Cache for 10 minutes
def get_majors():
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
    return jsonify(result)

# Get required courses for a major
@app.route('/api/majors/<int:major_id>/requirements', methods=['GET'])
def get_major_requirements(major_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get major info
    cursor.execute('SELECT name, concentration FROM majors WHERE id = ?', (major_id,))
    major = cursor.fetchone()
    
    if not major:
        conn.close()
        return jsonify({'error': 'Major not found'}), 404
    
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
            # Get prerequisites with groups
            prereq_data = get_prerequisites_grouped(course['id'])

            # Determine difficulty: use grade data if available, otherwise use level-based estimate
            difficulty = get_difficulty_from_grades(course['course_code'])
            if difficulty is None:
                difficulty = course['difficulty'] or estimate_difficulty(course['level'])

            credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
            credits_grad = course['credits_grad'] or parse_credits(course['credits'])

            required_courses.append({
                'id': course['course_code'].lower().replace(' ', ''),
                'code': course['course_code'],
                'title': course['title'],
                'credits': credits_undergrad,  # Default to undergrad for backwards compatibility
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
            # Get prerequisites with groups
            prereq_data = get_prerequisites_grouped(course['id'])

            # Determine difficulty: use grade data if available, otherwise use level-based estimate
            difficulty = get_difficulty_from_grades(course['course_code'])
            if difficulty is None:
                difficulty = course['difficulty'] or estimate_difficulty(course['level'])

            credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
            credits_grad = course['credits_grad'] or parse_credits(course['credits'])

            elective_courses.append({
                'id': course['course_code'].lower().replace(' ', ''),
                'code': course['course_code'],
                'title': course['title'],
                'credits': credits_undergrad,  # Default to undergrad for backwards compatibility
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
    return jsonify(result)

# Get all courses with their prerequisites
@app.route('/api/courses', methods=['GET'])
@cache.cached(timeout=600)  # Cache for 10 minutes - this is the most expensive endpoint
def get_courses():
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
    return jsonify(result)

# Get a single course by code
@app.route('/api/courses/<course_code>', methods=['GET'])
def get_course(course_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, course_code, course_number, title, credits, credits_undergrad, credits_grad, description, level
        FROM courses
        WHERE course_code = ?
    ''', (course_code.upper(),))
    
    course = cursor.fetchone()
    
    if course is None:
        conn.close()
        return jsonify({'error': 'Course not found'}), 404

    # Get prerequisites with groups
    prereq_data = get_prerequisites_grouped(course['id'])

    # Determine difficulty: use grade data if available, otherwise use level-based estimate
    difficulty = get_difficulty_from_grades(course['course_code'])
    if difficulty is None:
        difficulty = estimate_difficulty(course['level'])

    credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
    credits_grad = course['credits_grad'] or parse_credits(course['credits'])

    result = {
        'id': course['course_code'].lower().replace(' ', ''),
        'code': course['course_code'],
        'title': course['title'],
        'credits': credits_undergrad,  # Default to undergrad for backwards compatibility
        'creditsUndergrad': credits_undergrad,
        'creditsGrad': credits_grad,
        'level': course['level'],
        'difficulty': difficulty,
        'description': course['description'],
        'prerequisiteGroups': prereq_data['groups'],
        'prerequisitesFormatted': prereq_data['formatted']
    }

    conn.close()
    return jsonify(result)

# Get eligible courses based on completed courses
@app.route('/api/courses/eligible', methods=['POST'])
def get_eligible_courses():
    data = request.get_json()
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

        # Get prerequisites with groups
        prereq_data = get_prerequisites_grouped(course['id'])

        # Check if prerequisites are met
        # Groups are AND'd together, items within a group are OR'd
        prereqs_met = True
        if prereq_data['groups']:
            for group in prereq_data['groups']:
                # For each group, at least ONE course must be completed (OR logic within group)
                group_met = any(prereq in completed_codes for prereq in group)
                if not group_met:
                    prereqs_met = False
                    break

        if prereqs_met:
            # Determine difficulty: use grade data if available, otherwise use level-based estimate
            difficulty = get_difficulty_from_grades(course['course_code'])
            if difficulty is None:
                difficulty = estimate_difficulty(course['level'])

            credits_undergrad = course['credits_undergrad'] or parse_credits(course['credits'])
            credits_grad = course['credits_grad'] or parse_credits(course['credits'])

            eligible.append({
                'id': course['course_code'].lower().replace(' ', ''),
                'code': course['course_code'],
                'title': course['title'],
                'credits': credits_undergrad,  # Default to undergrad for backwards compatibility
                'creditsUndergrad': credits_undergrad,
                'creditsGrad': credits_grad,
                'level': course['level'],
                'difficulty': difficulty,
                'description': course['description'],
                'prerequisiteGroups': prereq_data['groups'],
                'prerequisitesFormatted': prereq_data['formatted']
            })
    
    conn.close()
    return jsonify(eligible)

# Get grade distribution for a course
@app.route('/api/courses/<course_code>/grades', methods=['GET'])
def get_grade_distribution(course_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if course exists
    cursor.execute('''
        SELECT id, course_code, title
        FROM courses
        WHERE course_code = ?
    ''', (course_code.upper(),))
    
    course = cursor.fetchone()
    
    if course is None:
        conn.close()
        return jsonify({'error': 'Course not found'}), 404
    
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
    ''', (course_code.upper(),))
    
    distributions = cursor.fetchall()
    
    if not distributions:
        conn.close()
        return jsonify({
            'course_code': course['course_code'],
            'course_title': course['title'],
            'has_data': False,
            'message': 'No grade distribution data available for this course',
            'distributions': [],
            'average': None
        })
    
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
    return jsonify(result)

# Helper functions
def parse_credits(credits_str):
    if not credits_str:
        return 3
    # Extract first number from string like "3 hours" or "3-4 hours"
    import re
    match = re.search(r'(\d+)', credits_str)
    return int(match.group(1)) if match else 3

def estimate_difficulty(level):
    if level <= 200:
        return "Light"
    elif level <= 300:
        return "Moderate"
    else:
        return "Challenging"

def format_prerequisites_from_list(prereq_list):
    """
    Format prerequisites from a list of dicts with 'code' and 'group' keys.
    Returns: {
        'groups': [[course1, course2], [course3], ...],
        'formatted': 'string representation'
    }
    """
    if not prereq_list:
        return {'groups': [], 'formatted': 'None'}

    from collections import defaultdict
    groups_dict = defaultdict(list)
    for prereq in prereq_list:
        groups_dict[prereq['group']].append(prereq['code'])

    # Convert to list of lists
    groups = [groups_dict[gid] for gid in sorted(groups_dict.keys())]

    # Format as string: (A OR B) AND C AND (D OR E)
    formatted_parts = []
    for group in groups:
        if len(group) == 1:
            formatted_parts.append(group[0])
        else:
            formatted_parts.append('(' + ' or '.join(group) + ')')

    formatted = ' and '.join(formatted_parts) if formatted_parts else 'None'

    return {
        'groups': groups,
        'formatted': formatted
    }

def get_prerequisites_grouped(course_id):
    """
    Get prerequisites grouped by group_id.
    Returns: {
        'groups': [[course1, course2], [course3], ...],  # Each inner array is OR'd, groups are AND'd
        'formatted': 'string representation'
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT prerequisite_code, group_id
        FROM prerequisites
        WHERE course_id = ?
        ORDER BY group_id, prerequisite_code
    ''', (course_id,))

    prereq_rows = cursor.fetchall()
    conn.close()

    if not prereq_rows:
        return {'groups': [], 'formatted': 'None'}

    # Group prerequisites by group_id
    from collections import defaultdict
    groups_dict = defaultdict(list)
    for row in prereq_rows:
        groups_dict[row['group_id']].append(row['prerequisite_code'])

    # Convert to list of lists
    groups = [groups_dict[gid] for gid in sorted(groups_dict.keys())]

    # Format as string: (A OR B) AND C AND (D OR E)
    formatted_parts = []
    for group in groups:
        if len(group) == 1:
            formatted_parts.append(group[0])
        else:
            formatted_parts.append('(' + ' or '.join(group) + ')')

    formatted = ' and '.join(formatted_parts) if formatted_parts else 'None'

    return {
        'groups': groups,
        'formatted': formatted
    }

def get_difficulty_from_grades(course_code):
    """
    Calculate difficulty based on grade distribution data.
    Returns difficulty string or None if no data available.

    Criteria:
    - Light: A+B >= 70%
    - Moderate: 50% <= A+B < 70%
    - Challenging: A+B < 50%
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get grade distribution for this course
    cursor.execute('''
        SELECT
            SUM(gd.grade_a) as total_a,
            SUM(gd.grade_b) as total_b,
            SUM(gd.grade_c) as total_c,
            SUM(gd.grade_d) as total_d,
            SUM(gd.grade_f) as total_f
        FROM grade_distributions gd
        WHERE gd.course_code = ?
    ''', (course_code,))

    result = cursor.fetchone()
    conn.close()

    if not result or result['total_a'] is None:
        return None

    total_a = result['total_a'] or 0
    total_b = result['total_b'] or 0
    total_c = result['total_c'] or 0
    total_d = result['total_d'] or 0
    total_f = result['total_f'] or 0

    # Calculate total letter grades (excluding W, S, U)
    total_letter_grades = total_a + total_b + total_c + total_d + total_f

    if total_letter_grades == 0:
        return None

    # Calculate A+B percentage
    ab_percentage = ((total_a + total_b) / total_letter_grades) * 100

    if ab_percentage >= 70:
        return "Light"
    elif ab_percentage >= 50:
        return "Moderate"
    else:
        return "Challenging"

if __name__ == '__main__':
    print("="*50)
    print("Starting Flask API server...")
    print("API will be available at: http://localhost:5001 (local)")
    print("="*50)
    print("\nEndpoints:")
    print("  GET  /api/courses - Get all courses")
    print("  GET  /api/courses/<code> - Get single course")
    print("  GET  /api/courses/<code>/grades - Get grade distribution")
    print("  POST /api/courses/eligible - Get eligible courses")
    print("  GET  /api/majors - Get all majors")
    print("  GET  /api/majors/<id>/requirements - Get major requirements")
    print("\nPress CTRL+C to quit\n")
    print("="*50)

    import os
    port = int(os.environ.get("PORT", 5001))  # Render sets PORT
    # Debug True locally, False on Render (if PORT is present)
    debug = (os.environ.get("PORT") is None)
    app.run(host='0.0.0.0', port=port, debug=debug)
