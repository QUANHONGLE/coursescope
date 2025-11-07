import sqlite3
import csv
import os
import re
from pathlib import Path

def create_grade_tables():
    """Create tables for grade distributions"""
    conn = sqlite3.connect('uic_courses.db')
    cursor = conn.cursor()
    
    # Table for semesters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS semesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(term, year)
        )
    ''')
    
    # Table for grade distributions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grade_distributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            semester_id INTEGER NOT NULL,
            instructor TEXT,
            grade_a INTEGER DEFAULT 0,
            grade_b INTEGER DEFAULT 0,
            grade_c INTEGER DEFAULT 0,
            grade_d INTEGER DEFAULT 0,
            grade_f INTEGER DEFAULT 0,
            grade_w INTEGER DEFAULT 0,
            grade_s INTEGER DEFAULT 0,
            grade_u INTEGER DEFAULT 0,
            total_students INTEGER DEFAULT 0,
            FOREIGN KEY (semester_id) REFERENCES semesters(id),
            UNIQUE(course_code, semester_id, instructor)
        )
    ''')
    
    conn.commit()
    return conn

def parse_semester_from_filename(filename):
    """
    Parse semester and year from filename
    Expected format: Spring_2025.csv, Fall_2024.csv, etc.
    """
    basename = os.path.basename(filename)
    # Remove .csv extension
    name = basename.replace('.csv', '')
    
    # Split by underscore or space
    parts = re.split(r'[_\s]+', name)
    
    if len(parts) >= 2:
        term = parts[0].capitalize()  # Spring, Fall, Summer, Winter
        try:
            year = int(parts[1])
            return term, year
        except ValueError:
            pass
    
    # Default if parsing fails
    print(f"Warning: Could not parse semester from '{filename}', using default 'Unknown 2025'")
    return "Unknown", 2025

def insert_or_get_semester(cursor, term, year):
    """Insert semester if it doesn't exist and return its ID"""
    cursor.execute('''
        INSERT OR IGNORE INTO semesters (term, year)
        VALUES (?, ?)
    ''', (term, year))
    
    cursor.execute('''
        SELECT id FROM semesters WHERE term = ? AND year = ?
    ''', (term, year))
    
    return cursor.fetchone()[0]

def normalize_course_code(dept, number):
    """Normalize course code to match database format (e.g., 'CS 141')"""
    return f"{dept} {number}"

def import_grade_csv(conn, csv_path):
    """Import grades from a single CSV file"""
    cursor = conn.cursor()
    
    # Parse semester from filename
    term, year = parse_semester_from_filename(csv_path)
    semester_id = insert_or_get_semester(cursor, term, year)
    
    print(f"\nImporting {csv_path}")
    print(f"Semester: {term} {year} (ID: {semester_id})")
    
    imported_count = 0
    skipped_count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            dept = row.get('CRS SUBJ CD', '').strip()
            number = row.get('CRS NBR', '').strip()
            instructor = row.get('Primary Instructor', '').strip()

            # Clean up instructor field - handle cases like " ," or just ","
            if instructor in [',', '']:
                instructor = ''

            # Skip if missing essential data
            if not dept or not number:
                skipped_count += 1
                continue
            
            course_code = normalize_course_code(dept, number)
            
            # Extract grade counts
            try:
                grade_a = int(row.get('A', 0) or 0)
                grade_b = int(row.get('B', 0) or 0)
                grade_c = int(row.get('C', 0) or 0)
                grade_d = int(row.get('D', 0) or 0)
                grade_f = int(row.get('F', 0) or 0)
                grade_w = int(row.get('W', 0) or 0)
                grade_s = int(row.get('S', 0) or 0)
                grade_u = int(row.get('U', 0) or 0)
                
                # Calculate total students (letter grades + W)
                total_students = grade_a + grade_b + grade_c + grade_d + grade_f + grade_w + grade_s + grade_u
                
                # Skip entries with no students
                if total_students == 0:
                    skipped_count += 1
                    continue
                
                # Insert or replace grade distribution
                cursor.execute('''
                    INSERT OR REPLACE INTO grade_distributions
                    (course_code, semester_id, instructor, grade_a, grade_b, grade_c, 
                     grade_d, grade_f, grade_w, grade_s, grade_u, total_students)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (course_code, semester_id, instructor, grade_a, grade_b, grade_c,
                      grade_d, grade_f, grade_w, grade_s, grade_u, total_students))
                
                imported_count += 1
                
                if imported_count <= 5:  # Show first 5 for verification
                    print(f"  ✓ {course_code} - {instructor}: A={grade_a}, B={grade_b}, C={grade_c}, Total={total_students}")
                
            except (ValueError, TypeError) as e:
                print(f"  ✗ Error parsing grades for {course_code}: {e}")
                skipped_count += 1
                continue
    
    conn.commit()
    print(f"\n✓ Imported {imported_count} grade distributions")
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} entries (missing data or no students)")
    
    return imported_count

def import_all_csv_files(directory_path='.'):
    """Import all CSV files from a directory"""
    conn = create_grade_tables()
    print("✓ Database tables created/connected")
    
    # Find all CSV files
    csv_files = list(Path(directory_path).glob('*.csv'))
    
    if not csv_files:
        print(f"\n⚠️  No CSV files found in {directory_path}")
        print("Please place CSV files in the same directory as this script.")
        conn.close()
        return
    
    print(f"\nFound {len(csv_files)} CSV file(s):")
    for f in csv_files:
        print(f"  • {f.name}")
    
    total_imported = 0
    for csv_file in csv_files:
        try:
            count = import_grade_csv(conn, str(csv_file))
            total_imported += count
        except Exception as e:
            print(f"\n✗ Error importing {csv_file.name}: {e}")
            continue
    
    # Display summary statistics
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    
    cursor = conn.cursor()
    
    # Total semesters
    cursor.execute('SELECT COUNT(*) FROM semesters')
    semester_count = cursor.fetchone()[0]
    print(f"Total semesters: {semester_count}")
    
    # Total grade distributions
    cursor.execute('SELECT COUNT(*) FROM grade_distributions')
    total_distributions = cursor.fetchone()[0]
    print(f"Total grade distributions: {total_distributions}")
    
    # Courses with grade data
    cursor.execute('SELECT COUNT(DISTINCT course_code) FROM grade_distributions')
    courses_with_grades = cursor.fetchone()[0]
    print(f"Courses with grade data: {courses_with_grades}")
    
    # Sample semesters
    print("\nSemesters in database:")
    cursor.execute('SELECT term, year FROM semesters ORDER BY year DESC, term')
    for term, year in cursor.fetchall():
        cursor.execute('''
            SELECT COUNT(*) FROM grade_distributions 
            WHERE semester_id = (SELECT id FROM semesters WHERE term = ? AND year = ?)
        ''', (term, year))
        count = cursor.fetchone()[0]
        print(f"  • {term} {year}: {count} distributions")
    
    # Sample courses with most data
    print("\nCourses with most grade data:")
    cursor.execute('''
        SELECT course_code, COUNT(*) as distribution_count
        FROM grade_distributions
        GROUP BY course_code
        ORDER BY distribution_count DESC
        LIMIT 10
    ''')
    for course_code, count in cursor.fetchall():
        print(f"  • {course_code}: {count} semesters")
    
    conn.close()
    print("\n✓ Import complete!")
    print("\nTo view grade data in your API, the endpoint will be:")
    print("  GET /api/courses/<code>/grades")

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("UIC Grade Distribution Importer")
    print("="*60)
    
    # Allow passing directory as argument, otherwise use current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    import_all_csv_files(directory)
    
    print("\n" + "="*60)
    print("Next steps:")
    print("  1. Run the Flask API: python api.py")
    print("  2. Test the grade endpoint: curl http://localhost:5001/api/courses/CS%20141/grades")
    print("  3. Add more CSV files and re-run this script to update")
    print("="*60)