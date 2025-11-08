import sqlite3
import os
from collections import defaultdict
import re

# Database path - Vercel serverless functions need absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'uic_courses.db')

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def parse_credits(credits_str):
    """Parse credits string and extract numeric value"""
    if not credits_str:
        return 3
    match = re.search(r'(\d+)', credits_str)
    return int(match.group(1)) if match else 3

def estimate_difficulty(level):
    """Estimate difficulty based on course level"""
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

    groups_dict = defaultdict(list)
    for prereq in prereq_list:
        groups_dict[prereq['group']].append(prereq['code'])

    groups = [groups_dict[gid] for gid in sorted(groups_dict.keys())]

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
        'groups': [[course1, course2], [course3], ...],
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

    groups_dict = defaultdict(list)
    for row in prereq_rows:
        groups_dict[row['group_id']].append(row['prerequisite_code'])

    groups = [groups_dict[gid] for gid in sorted(groups_dict.keys())]

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
    """
    conn = get_db_connection()
    cursor = conn.cursor()

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

    total_letter_grades = total_a + total_b + total_c + total_d + total_f

    if total_letter_grades == 0:
        return None

    ab_percentage = ((total_a + total_b) / total_letter_grades) * 100

    if ab_percentage >= 70:
        return "Light"
    elif ab_percentage >= 50:
        return "Moderate"
    else:
        return "Challenging"
