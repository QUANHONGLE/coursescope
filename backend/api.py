from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for development

DATABASE = 'uic_courses.db'

# Check if database exists
if not os.path.exists(DATABASE):
    print(f"ERROR: Database file '{DATABASE}' not found!")
    print("Please run uic_course_scraper.py first to create the database.")
    exit(1)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Get all majors
@app.route('/api/majors', methods=['GET'])
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
    
    # Get full course details for each requirement
    required_courses = []
    for req in requirements:
        cursor.execute('''
            SELECT id, course_code, course_number, title, credits, description, level, difficulty
            FROM courses
            WHERE course_code = ?
        ''', (req['course_code'],))
        
        course = cursor.fetchone()
        if course:
            # Get prerequisites
            cursor.execute('''
                SELECT prerequisite_code
                FROM prerequisites
                WHERE course_id = ?
            ''', (course['id'],))
            
            prereqs = [row['prerequisite_code'] for row in cursor.fetchall()]
            
            required_courses.append({
                'id': course['course_code'].lower().replace(' ', ''),
                'code': course['course_code'],
                'title': course['title'],
                'credits': parse_credits(course['credits']),
                'level': course['level'],
                'difficulty': course['difficulty'] or estimate_difficulty(course['level']),
                'description': course['description'],
                'prerequisites': prereqs,
                'prereqChain': ' → '.join(prereqs) if prereqs else 'None',
                'requirementType': req['requirement_type']
            })
    
    result = {
        'major': {
            'id': major_id,
            'name': major['name'],
            'concentration': major['concentration']
        },
        'requiredCourses': required_courses
    }
    
    conn.close()
    return jsonify(result)

# Get all courses with their prerequisites
@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all courses
    cursor.execute('''
        SELECT id, course_code, course_number, title, credits, description, level, difficulty
        FROM courses
        ORDER BY course_number
    ''')
    courses = cursor.fetchall()
    
    result = []
    for course in courses:
        # Get prerequisites for this course
        cursor.execute('''
            SELECT prerequisite_code
            FROM prerequisites
            WHERE course_id = ?
        ''', (course['id'],))
        
        prereqs = [row['prerequisite_code'] for row in cursor.fetchall()]
        
        result.append({
            'id': course['course_code'].lower().replace(' ', ''),
            'code': course['course_code'],
            'title': course['title'],
            'credits': parse_credits(course['credits']),
            'level': course['level'],
            'difficulty': course['difficulty'] or estimate_difficulty(course['level']),
            'description': course['description'],
            'prerequisites': prereqs,
            'prereqChain': ' → '.join(prereqs) if prereqs else 'None'
        })
    
    conn.close()
    return jsonify(result)

# Get a single course by code
@app.route('/api/courses/<course_code>', methods=['GET'])
def get_course(course_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, course_code, course_number, title, credits, description, level
        FROM courses
        WHERE course_code = ?
    ''', (course_code.upper(),))
    
    course = cursor.fetchone()
    
    if course is None:
        conn.close()
        return jsonify({'error': 'Course not found'}), 404
    
    # Get prerequisites
    cursor.execute('''
        SELECT prerequisite_code
        FROM prerequisites
        WHERE course_id = ?
    ''', (course['id'],))
    
    prereqs = [row['prerequisite_code'] for row in cursor.fetchall()]
    
    result = {
        'id': course['course_code'].lower().replace(' ', ''),
        'code': course['course_code'],
        'title': course['title'],
        'credits': parse_credits(course['credits']),
        'level': course['level'],
        'difficulty': estimate_difficulty(course['level']),
        'description': course['description'],
        'prerequisites': prereqs,
        'prereqChain': ' → '.join(prereqs) if prereqs else 'None'
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
        SELECT id, course_code, course_number, title, credits, description, level
        FROM courses
        ORDER BY course_number
    ''')
    courses = cursor.fetchall()
    
    eligible = []
    
    for course in courses:
        # Skip if already completed
        if course['course_code'] in completed_codes:
            continue
        
        # Get prerequisites
        cursor.execute('''
            SELECT prerequisite_code
            FROM prerequisites
            WHERE course_id = ?
        ''', (course['id'],))
        
        prereqs = [row['prerequisite_code'] for row in cursor.fetchall()]
        
        # Check if all prerequisites are completed
        if all(prereq in completed_codes for prereq in prereqs):
            eligible.append({
                'id': course['course_code'].lower().replace(' ', ''),
                'code': course['course_code'],
                'title': course['title'],
                'credits': parse_credits(course['credits']),
                'level': course['level'],
                'difficulty': estimate_difficulty(course['level']),
                'description': course['description'],
                'prerequisites': prereqs,
                'prereqChain': ' → '.join(prereqs) if prereqs else 'None'
            })
    
    conn.close()
    return jsonify(eligible)

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
        return "Easy"
    elif level <= 300:
        return "Moderate"
    else:
        return "Challenging"

if __name__ == '__main__':
    print("="*50)
    print("Starting Flask API server...")
    print("API will be available at: http://localhost:5000")
    print("="*50)
    print("\nEndpoints:")
    print("  GET  /api/courses - Get all courses")
    print("  GET  /api/courses/<code> - Get single course")
    print("  POST /api/courses/eligible - Get eligible courses")
    print("\nPress CTRL+C to quit\n")
    print("="*50)
    app.run(debug=True, port=5001, host='0.0.0.0')