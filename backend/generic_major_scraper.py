import requests
from bs4 import BeautifulSoup
import sqlite3
import re

# Configuration for different majors
MAJOR_CONFIGS = {
    'CS': {
        'name': 'Computer Science',
        'core_courses': [
            'CS 111', 'CS 112', 'CS 113',  # One of these is required
            'CS 141', 'CS 151', 'CS 211', 'CS 251', 'CS 261',
            'CS 277', 'CS 301', 'CS 341', 'CS 342', 'CS 361',
            'CS 362', 'CS 377', 'CS 401', 'CS 499'
        ],
        'department_categories': {
            'Required CS': ['CS'],
            'Required Math': ['MATH', 'IE', 'STAT'],
            'Required Science': ['PHYS', 'CHEM', 'BIOS'],
            'Required English': ['ENGL'],
            'Required Other': ['ENGR']
        },
        'elective_categories': {
            'CS Electives': ['CS'],
            'Math Electives': ['MATH', 'IE', 'STAT'],
            'Science Electives': ['PHYS', 'CHEM', 'BIOS'],
            'Other Electives': []  # Catch-all
        },
        'concentrations': [
            {
                'name': None,
                'url': 'https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/bs-cs/'
            },
            {
                'name': 'Computer Systems',
                'url': 'https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/bs-cs-com-syst-conc/'
            },
            {
                'name': 'Human-Centered Computing',
                'url': 'https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/bs-cs-hcc-conc/'
            },
            {
                'name': 'Software Engineering',
                'url': 'https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/bs-cs-se-conc/'
            },
            {
                'name': 'Design',
                'url': 'https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/bs-cs-design/'
            }
        ]
    }
    # Add more majors here:
    # 'MATH': { ... },
    # 'PHYS': { ... },
}

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

    # Table for major electives
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS major_electives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            major_id INTEGER NOT NULL,
            course_code TEXT NOT NULL,
            elective_type TEXT NOT NULL,
            FOREIGN KEY (major_id) REFERENCES majors(id),
            UNIQUE(major_id, course_code)
        )
    ''')

    conn.commit()
    return conn

def scrape_major_requirements(url, config):
    """Generic scraper for major requirements using configuration"""

    print(f"Fetching {url}...")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize requirement dictionaries based on config
    requirements = {cat: [] for cat in config['department_categories'].keys()}
    electives = {cat: [] for cat in config['elective_categories'].keys()}

    # Course pattern regex
    course_pattern = re.compile(r'\b([A-Z]{2,4})\s+(\d{3})\b')

    # Find all tables with courselist class
    tables = soup.find_all('table', class_='sc_courselist')

    for table in tables:
        # Get the heading before this table to determine context
        prev_heading = table.find_previous(['h2', 'h3', 'h4'])
        context = prev_heading.get_text().lower() if prev_heading else ""

        # Check if this is an elective section
        is_elective = any(keyword in context for keyword in ['elective', 'select', 'choose', 'option'])

        # Extract course codes from this table
        rows = table.find_all('tr')
        for row in rows:
            # Look for course code in the first column
            code_cell = row.find('td', class_='codecol')
            if code_cell:
                code_link = code_cell.find('a')
                if code_link:
                    course_text = code_link.get_text(strip=True)
                    match = course_pattern.match(course_text)
                    if match:
                        course_code = f"{match.group(1)} {match.group(2)}"
                        dept = match.group(1)

                        if is_elective:
                            # Categorize elective
                            categorized = False
                            for elective_type, depts in config['elective_categories'].items():
                                if dept in depts:
                                    if course_code not in electives[elective_type]:
                                        electives[elective_type].append(course_code)
                                        print(f"✓ Found {elective_type}: {course_code}")
                                    categorized = True
                                    break

                            # If not categorized, add to "Other Electives"
                            if not categorized and 'Other Electives' in electives:
                                if course_code not in electives['Other Electives']:
                                    electives['Other Electives'].append(course_code)
                                    print(f"✓ Found Other Elective: {course_code}")
                        else:
                            # Categorize required course
                            categorized = False
                            for req_type, depts in config['department_categories'].items():
                                if dept in depts:
                                    if course_code not in requirements[req_type]:
                                        requirements[req_type].append(course_code)
                                        print(f"✓ Found {req_type}: {course_code}")
                                    categorized = True
                                    break

    # Fallback: if we didn't find courses in tables, look for core courses
    if not any(requirements.values()) and 'core_courses' in config:
        print("⚠ No courses found in tables, using fallback method...")
        # Try to find courses mentioned in the page
        all_text = soup.get_text()
        for core_course in config['core_courses']:
            if core_course in all_text:
                dept = core_course.split()[0]
                for req_type, depts in config['department_categories'].items():
                    if dept in depts:
                        if core_course not in requirements[req_type]:
                            requirements[req_type].append(core_course)
                            print(f"✓ Found {req_type} (fallback): {core_course}")
                        break

    return requirements, electives

def insert_major_requirements(conn, requirements, electives, major_name, concentration):
    """Insert major, requirements, and electives into database"""
    cursor = conn.cursor()

    # Insert major
    cursor.execute('''
        INSERT OR IGNORE INTO majors (name, concentration)
        VALUES (?, ?)
    ''', (major_name, concentration))

    # Handle None concentration in query
    if concentration is None:
        cursor.execute('''
            SELECT id FROM majors WHERE name = ? AND concentration IS NULL
        ''', (major_name,))
    else:
        cursor.execute('''
            SELECT id FROM majors WHERE name = ? AND concentration = ?
        ''', (major_name, concentration))

    result = cursor.fetchone()
    if result is None:
        print(f"Error: Could not find major {major_name} - {concentration}")
        return
    major_id = result[0]

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

    # Insert electives
    total_electives = 0
    for elective_type, courses in electives.items():
        for course_code in courses:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO major_electives
                    (major_id, course_code, elective_type)
                    VALUES (?, ?, ?)
                ''', (major_id, course_code, elective_type))
                total_electives += 1
            except sqlite3.IntegrityError:
                print(f"Duplicate elective: {course_code}")

    conn.commit()
    print(f"\n✓ Successfully inserted {total_courses} required courses and {total_electives} electives!")

def scrape_all_majors(major_keys=None, test_mode=False):
    """
    Scrape requirements for all configured majors

    Args:
        major_keys: List of major keys to scrape (e.g., ['CS', 'MATH']). If None, scrape all.
        test_mode: If True, creates a separate test database
    """
    # Create database tables
    if test_mode:
        db_name = 'uic_courses_test.db'
        print(f"⚠️  TEST MODE: Using {db_name}")
    else:
        db_name = 'uic_courses.db'

    # Temporarily modify connection
    global create_major_tables
    original_create = create_major_tables

    def create_test_tables():
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS majors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                concentration TEXT,
                UNIQUE(name, concentration)
            )
        ''')

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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS major_electives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                major_id INTEGER NOT NULL,
                course_code TEXT NOT NULL,
                elective_type TEXT NOT NULL,
                FOREIGN KEY (major_id) REFERENCES majors(id),
                UNIQUE(major_id, course_code)
            )
        ''')

        conn.commit()
        return conn

    if test_mode:
        conn = create_test_tables()
    else:
        conn = create_major_tables()

    print("✓ Database tables created/connected\n")

    # Determine which majors to scrape
    if major_keys is None:
        major_keys = list(MAJOR_CONFIGS.keys())

    # Scrape each major
    for major_key in major_keys:
        if major_key not in MAJOR_CONFIGS:
            print(f"⚠️  Warning: '{major_key}' not found in MAJOR_CONFIGS")
            continue

        config = MAJOR_CONFIGS[major_key]
        major_name = config['name']
        concentrations = config['concentrations']

        print(f"\n{'='*60}")
        print(f"Scraping {major_name}")
        print('='*60)

        for idx, conc_config in enumerate(concentrations, 1):
            concentration = conc_config['name']
            url = conc_config['url']

            display_name = f"{major_name}" + (f" - {concentration}" if concentration else "")
            print(f"\n[{idx}/{len(concentrations)}] {display_name}")
            print("-" * 50)

            try:
                requirements, electives = scrape_major_requirements(url, config)

                if any(requirements.values()) or any(electives.values()):
                    insert_major_requirements(conn, requirements, electives, major_name, concentration)
                    print(f"✓ Successfully processed {display_name}")
                else:
                    print(f"⚠ No requirements or electives found for {display_name}")
            except Exception as e:
                print(f"✗ Error processing {display_name}: {str(e)}")
                import traceback
                traceback.print_exc()

    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.name, m.concentration, COUNT(mr.course_code) as req_count
        FROM majors m
        LEFT JOIN major_requirements mr ON m.id = mr.major_id
        GROUP BY m.id
        ORDER BY m.name, m.concentration
    ''')

    for row in cursor.fetchall():
        concentration_text = f" - {row[1]}" if row[1] else ""
        print(f"  {row[0]}{concentration_text}: {row[2]} required courses")

    # Close connection
    conn.close()
    print(f"\n✓ Database connection closed")

    if test_mode:
        print(f"\n📊 Test results saved to: {db_name}")
        print("\nCompare with original:")
        print(f"  diff <(sqlite3 uic_courses.db 'SELECT * FROM major_requirements ORDER BY major_id, course_code') <(sqlite3 {db_name} 'SELECT * FROM major_requirements ORDER BY major_id, course_code')")

if __name__ == "__main__":
    import sys

    print("="*60)
    print("Generic Major Requirements Scraper")
    print("="*60)

    # Parse command line arguments
    test_mode = '--test' in sys.argv
    major_filter = None

    # Check for major filter argument
    for arg in sys.argv[1:]:
        if arg.startswith('--major='):
            major_filter = arg.split('=')[1].split(',')

    if test_mode:
        print("\n🧪 Running in TEST MODE")
        print("Results will be saved to uic_courses_test.db")

    if major_filter:
        print(f"\n🎯 Scraping only: {', '.join(major_filter)}")

    print()

    # Run scraper
    scrape_all_majors(major_keys=major_filter, test_mode=test_mode)

    print("\n" + "="*60)
    print("Next steps:")
    if test_mode:
        print("  1. Compare test results with original database")
        print("  2. If results match, run without --test flag")
    else:
        print("  1. Run the Flask API: python api.py")
        print("  2. View majors: curl http://localhost:5001/api/majors")
    print("="*60)
