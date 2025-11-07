# -*- coding: utf-8 -*-
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'uic_courses.db')

def add_indexes():
    """Add indexes to improve query performance"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("Adding database indexes...")

    # Index for course lookups by code
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_courses_code
        ON courses(course_code)
    ''')
    print("Created index on courses.course_code")

    # Index for prerequisite lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_prerequisites_course_id
        ON prerequisites(course_id)
    ''')
    print("Created index on prerequisites.course_id")

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_prerequisites_code
        ON prerequisites(prerequisite_code)
    ''')
    print("Created index on prerequisites.prerequisite_code")

    # Index for grade distribution lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_grade_distributions_course_code
        ON grade_distributions(course_code)
    ''')
    print("Created index on grade_distributions.course_code")

    # Index for semester lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_grade_distributions_semester_id
        ON grade_distributions(semester_id)
    ''')
    print("Created index on grade_distributions.semester_id")

    # Index for major requirements
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_major_requirements_major_id
        ON major_requirements(major_id)
    ''')
    print("Created index on major_requirements.major_id")

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_major_requirements_course_code
        ON major_requirements(course_code)
    ''')
    print("Created index on major_requirements.course_code")

    # Index for major electives
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_major_electives_major_id
        ON major_electives(major_id)
    ''')
    print("Created index on major_electives.major_id")

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_major_electives_course_code
        ON major_electives(course_code)
    ''')
    print("Created index on major_electives.course_code")

    conn.commit()
    conn.close()

    print("\nAll indexes created successfully!")

if __name__ == '__main__':
    add_indexes()
