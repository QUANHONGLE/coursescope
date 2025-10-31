import requests
from bs4 import BeautifulSoup
import sqlite3
import re

def create_major_tables():
    """Create tables for major requirements"""
    conn = sqlite3.connect('uic_courses.db')
    cursor = conn.cursor()
    
    # Table for majors/concentrations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS majors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            concentration TEXT,
            UNIQUE(name, concentration)
        )
    ''')
    
    # Table for major requirements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS major_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            major_id INTEGER NOT NULL,
            course_code TEXT NOT NULL,
            requirement_type TEXT NOT NULL,
            FOREIGN KEY (major_id) REFERENCES majors(id),
            UNIQUE(major_id, course_code)
        )
    ''')
    
    conn.commit()
    return conn

def scrape_cs_software_requirements():
    """Scrape CS Software Engineering concentration requirements"""
    url = "https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/bs-cs-se-conc/"
    
    print(f"Fetching {url}...")
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    requirements = {
        'Core CS': [],
        'Software Concentration': [],
        'Math': [],
        'Science': []
    }
    
    # Find all course links and text
    course_pattern = re.compile(r'\b([A-Z]{2,4})\s+(\d{3})\b')
    
    # Get all text content
    text_content = soup.get_text()
    
    # Find all course codes
    all_courses = course_pattern.findall(text_content)
    
    for dept, number in all_courses:
        course_code = f"{dept} {number}"
        
        # Categorize courses
        if dept == 'CS':
            # Check if it's a software-specific course or core
            course_num = int(number)
            
            # Software Engineering specific courses (typically 440s, 470s)
            if course_num in [440, 441, 442, 443, 474, 476, 477]:
                if course_code not in requirements['Software Concentration']:
                    requirements['Software Concentration'].append(course_code)
                    print(f"✓ Found Software Concentration: {course_code}")
            # Core CS courses
            elif course_num < 500:  # Exclude grad courses
                if course_code not in requirements['Core CS']:
                    requirements['Core CS'].append(course_code)
                    print(f"✓ Found Core CS: {course_code}")
        
        elif dept == 'MATH' or dept == 'IE' or dept == 'STAT':
            if course_code not in requirements['Math']:
                requirements['Math'].append(course_code)
                print(f"✓ Found Math: {course_code}")
        
        elif dept in ['PHYS', 'CHEM', 'BIOS']:
            if course_code not in requirements['Science']:
                requirements['Science'].append(course_code)
                print(f"✓ Found Science: {course_code}")
    
    return requirements

def insert_major_requirements(conn, requirements):
    """Insert major and requirements into database"""
    cursor = conn.cursor()
    
    # Insert major
    cursor.execute('''
        INSERT OR IGNORE INTO majors (name, concentration)
        VALUES (?, ?)
    ''', ('Computer Science', 'Software Engineering'))
    
    cursor.execute('''
        SELECT id FROM majors WHERE name = ? AND concentration = ?
    ''', ('Computer Science', 'Software Engineering'))
    major_id = cursor.fetchone()[0]
    
    # Insert requirements
    total_courses = 0
    for req_type, courses in requirements.items():
        for course_code in courses:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO major_requirements 
                    (major_id, course_code, requirement_type)
                    VALUES (?, ?, ?)
                ''', (major_id, course_code, req_type))
                total_courses += 1
            except sqlite3.IntegrityError:
                print(f"Duplicate: {course_code}")
    
    conn.commit()
    print(f"\n✓ Successfully inserted {total_courses} required courses!")

def display_requirements(conn):
    """Display the major requirements"""
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.name, m.concentration, COUNT(mr.course_code) as total_courses
        FROM majors m
        LEFT JOIN major_requirements mr ON m.id = mr.major_id
        WHERE m.name = 'Computer Science' AND m.concentration = 'Software Engineering'
        GROUP BY m.id
    ''')
    
    result = cursor.fetchone()
    if result:
        print(f"\n--- {result[0]} ({result[1]}) ---")
        print(f"Total Required Courses: {result[2]}\n")
        
        # Show breakdown by requirement type
        cursor.execute('''
            SELECT mr.requirement_type, COUNT(*) as count
            FROM major_requirements mr
            JOIN majors m ON mr.major_id = m.id
            WHERE m.name = 'Computer Science' AND m.concentration = 'Software Engineering'
            GROUP BY mr.requirement_type
        ''')
        
        print("Breakdown:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} courses")
        
        # Show sample courses
        print("\nSample Required Courses:")
        cursor.execute('''
            SELECT mr.course_code, mr.requirement_type
            FROM major_requirements mr
            JOIN majors m ON mr.major_id = m.id
            WHERE m.name = 'Computer Science' AND m.concentration = 'Software Engineering'
            ORDER BY mr.requirement_type, mr.course_code
            LIMIT 10
        ''')
        
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]})")

if __name__ == "__main__":
    print("UIC CS Software Engineering Requirements Scraper\n" + "="*50)
    
    # Create database tables
    conn = create_major_tables()
    print("✓ Database tables created/connected\n")
    
    # Scrape requirements
    requirements = scrape_cs_software_requirements()
    
    # Insert into database
    if any(requirements.values()):
        insert_major_requirements(conn, requirements)
        display_requirements(conn)
    else:
        print("No requirements found!")
    
    # Close connection
    conn.close()
    print("\n✓ Database connection closed")
    print("\nQuery examples:")
    print("  sqlite3 uic_courses.db")
    print("  SELECT * FROM majors;")
    print("  SELECT * FROM major_requirements;")