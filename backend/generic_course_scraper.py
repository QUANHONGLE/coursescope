import requests
from bs4 import BeautifulSoup
import sqlite3
import re

def estimate_difficulty(level, prereq_count, credits_num, description):
    """
    Estimate difficulty based on multiple factors:
    - Course level (100-500)
    - Number of prerequisites
    - Credit hours
    - Keywords in description
    """
    difficulty_score = 0

    # Factor 1: Course level (0-3 points)
    if level >= 400:
        difficulty_score += 3
    elif level >= 300:
        difficulty_score += 2
    elif level >= 200:
        difficulty_score += 1

    # Factor 2: Prerequisites (0-2 points)
    if prereq_count >= 3:
        difficulty_score += 2
    elif prereq_count >= 1:
        difficulty_score += 1

    # Factor 3: Credit hours (0-1 point)
    if credits_num >= 4:
        difficulty_score += 1

    # Factor 4: Keywords in description (0-2 points)
    challenging_keywords = ['advanced', 'intensive', 'rigorous', 'complex', 'theoretical']
    light_keywords = ['introduction', 'survey', 'overview', 'fundamentals', 'basics']

    desc_lower = description.lower()
    if any(word in desc_lower for word in challenging_keywords):
        difficulty_score += 1
    if any(word in desc_lower for word in light_keywords):
        difficulty_score -= 1

    # Map score to difficulty (0-9 scale)
    if difficulty_score <= 2:
        return "Light"
    elif difficulty_score <= 5:
        return "Moderate"
    else:
        return "Challenging"

def create_database():
    """Create SQLite database with courses and prerequisites tables"""
    conn = sqlite3.connect('uic_courses.db')
    cursor = conn.cursor()

    # Main courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_number TEXT NOT NULL,
            title TEXT NOT NULL,
            credits TEXT,
            credits_undergrad INTEGER,
            credits_grad INTEGER,
            description TEXT,
            level INTEGER,
            difficulty TEXT,
            raw_text TEXT
        )
    ''')

    # Prerequisites table with group_id for complex logic
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            prerequisite_code TEXT NOT NULL,
            logic_type TEXT DEFAULT 'OR',
            group_id INTEGER DEFAULT 0,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(course_id, prerequisite_code)
        )
    ''')

    conn.commit()
    return conn

def parse_prerequisites(prereq_text, department):
    """
    Extract prerequisite course codes from text.
    Supports any department code (CS, MATH, PHYS, etc.)
    """
    if not prereq_text:
        return []

    # Find all course codes (e.g., CS 100, MATH 180, PHYS 141, etc.)
    # Pattern matches: 2-4 letter department code + space(s) + 3 digits
    prereq_codes = re.findall(r'[A-Z]{2,4}\s*\d{3}', prereq_text, re.IGNORECASE)

    # Normalize format (e.g., "CS141" -> "CS 141", "MATH180" -> "MATH 180")
    normalized = []
    for code in prereq_codes:
        # Extract department and number
        match = re.match(r'([A-Z]{2,4})\s*(\d{3})', code, re.IGNORECASE)
        if match:
            dept = match.group(1).upper()
            num = match.group(2)
            normalized_code = f"{dept} {num}"
            normalized.append(normalized_code)

    return list(set(normalized))  # Remove duplicates

def scrape_department_courses(department, url):
    """
    Scrape courses for a specific department

    Args:
        department: Department code (e.g., 'CS', 'MATH', 'PHYS')
        url: URL to the department's course catalog page
    """
    print(f"\nFetching {department} courses from {url}...")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all course blocks
    course_blocks = soup.find_all('div', class_='courseblock')

    courses = []

    for block in course_blocks:
        try:
            # Extract course code and title
            title_elem = block.find('p', class_='courseblocktitle')
            if not title_elem:
                continue

            title_text = title_elem.get_text(strip=True)

            # Parse course code (e.g., "MATH 180. Calculus I. 5 hours.")
            # Pattern: DEPT NUM. Title. Credits hours.
            code_pattern = rf'^({department}\s+\d+)\.\s+(.+?)\.?\s*(\d+(?:-\d+)?\s+hours?\.?)?$'
            code_match = re.match(code_pattern, title_text, re.IGNORECASE)

            if not code_match:
                print(f"Could not parse: {title_text}")
                continue

            course_code = code_match.group(1).strip().upper()
            # Normalize spaces
            course_code = course_code.replace('\xa0', ' ').replace('\u00a0', ' ')

            course_title = code_match.group(2).strip()
            # Clean up title
            if '.' in course_title:
                course_title = course_title.split('.')[0].strip()
            course_title = re.sub(r'\s+or\s*$', '', course_title).strip()

            credits = code_match.group(3).strip() if code_match.group(3) else None

            # Extract course number
            course_number = course_code.split()[-1]

            # Determine level (100, 200, 300, 400, 500)
            level = int(course_number[0]) * 100

            # Extract description
            desc_elem = block.find('p', class_='courseblockdesc')
            description = desc_elem.get_text(separator=' ', strip=True) if desc_elem else ""

            # Clean up multiple spaces
            description = re.sub(r'\s+', ' ', description)

            # Extract prerequisites text
            prereq_match = re.search(r'Prerequisite\s*\(s\):(.+?)(?:\.|Class Schedule|Course Information|$)', description, re.IGNORECASE)
            prereq_text = prereq_match.group(1).strip() if prereq_match else None

            # Parse individual prerequisite courses
            prerequisites = parse_prerequisites(prereq_text, department)

            # Extract numeric credits
            credits_num = 3  # default
            if credits:
                match = re.search(r'(\d+)', credits)
                if match:
                    credits_num = int(match.group(1))

            # Estimate difficulty
            difficulty = estimate_difficulty(level, len(prerequisites), credits_num, description)

            # Store raw HTML for reference
            raw_text = block.get_text(separator=' ', strip=True)
            raw_text = re.sub(r'\s+', ' ', raw_text)

            courses.append({
                'course_code': course_code,
                'course_number': course_number,
                'title': course_title,
                'credits': credits,
                'credits_undergrad': credits_num,
                'credits_grad': credits_num,
                'description': description,
                'prerequisites': prerequisites,
                'level': level,
                'difficulty': difficulty,
                'raw_text': raw_text
            })

            prereq_str = ", ".join(prerequisites) if prerequisites else "None"
            print(f"✓ {course_code} - {course_title} ({difficulty}) (Prereqs: {prereq_str})")

        except Exception as e:
            print(f"Error parsing course block: {e}")
            import traceback
            traceback.print_exc()
            continue

    return courses

def insert_courses(conn, courses):
    """Insert courses and prerequisites into database"""
    cursor = conn.cursor()

    inserted_count = 0
    updated_count = 0

    for course in courses:
        try:
            # Check if course exists
            cursor.execute('SELECT id FROM courses WHERE course_code = ?', (course['course_code'],))
            existing = cursor.fetchone()

            if existing:
                # Update existing course
                cursor.execute('''
                    UPDATE courses
                    SET course_number = ?, title = ?, credits = ?, credits_undergrad = ?,
                        credits_grad = ?, description = ?, level = ?, difficulty = ?, raw_text = ?
                    WHERE course_code = ?
                ''', (
                    course['course_number'],
                    course['title'],
                    course['credits'],
                    course['credits_undergrad'],
                    course['credits_grad'],
                    course['description'],
                    course['level'],
                    course['difficulty'],
                    course['raw_text'],
                    course['course_code']
                ))
                course_id = existing[0]
                updated_count += 1
            else:
                # Insert new course
                cursor.execute('''
                    INSERT INTO courses
                    (course_code, course_number, title, credits, credits_undergrad, credits_grad,
                     description, level, difficulty, raw_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    course['course_code'],
                    course['course_number'],
                    course['title'],
                    course['credits'],
                    course['credits_undergrad'],
                    course['credits_grad'],
                    course['description'],
                    course['level'],
                    course['difficulty'],
                    course['raw_text']
                ))
                course_id = cursor.lastrowid
                inserted_count += 1

            # Delete old prerequisites for this course
            cursor.execute('DELETE FROM prerequisites WHERE course_id = ?', (course_id,))

            # Insert prerequisites (all in group 0 with OR logic by default)
            for prereq_code in course['prerequisites']:
                cursor.execute('''
                    INSERT OR IGNORE INTO prerequisites (course_id, prerequisite_code, logic_type, group_id)
                    VALUES (?, ?, 'OR', 0)
                ''', (course_id, prereq_code))

        except sqlite3.IntegrityError as e:
            print(f"Error inserting course: {course['course_code']} - {e}")

    conn.commit()
    print(f"\n✓ Inserted {inserted_count} new courses, updated {updated_count} existing courses!")

def display_sample_data(conn, department):
    """Query and display sample data"""
    cursor = conn.cursor()

    print(f"\n--- Sample {department} Courses ---")
    cursor.execute('''
        SELECT c.course_code, c.title, c.credits, c.level, c.difficulty
        FROM courses c
        WHERE c.course_code LIKE ?
        ORDER BY c.course_number
        LIMIT 10
    ''', (f'{department}%',))

    for row in cursor.fetchall():
        course_code, title, credits, level, difficulty = row

        # Get prerequisites
        cursor.execute('''
            SELECT p.prerequisite_code
            FROM prerequisites p
            JOIN courses c ON p.course_id = c.id
            WHERE c.course_code = ?
        ''', (course_code,))

        prereqs = [p[0] for p in cursor.fetchall()]
        prereq_str = ", ".join(prereqs) if prereqs else "None"

        print(f"{course_code}: {title} ({credits}) - Level {level} - {difficulty}")
        print(f"  Prerequisites: {prereq_str}\n")

# Department configurations
DEPARTMENTS = {
    'CS': {
        'name': 'Computer Science',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/cs/'
    },
    'MATH': {
        'name': 'Mathematics',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/math/'
    },
    'PHYS': {
        'name': 'Physics',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/phys/'
    },
    'CHEM': {
        'name': 'Chemistry',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/chem/'
    },
    'ENGL': {
        'name': 'English',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/engl/'
    },
    'ENGR': {
        'name': 'Engineering',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/engr/'
    },
    'ACTG': {
        'name': 'Accounting',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/actg/'
    },
    'AH': {
        'name': 'Art History',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ah/'
    },
    'AHS': {
        'name': 'Applied Health Sciences',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ahs/'
    },
    'ANTH': {
        'name': 'Anthropology',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/anth/'
    },
    'ARCH': {
        'name': 'Architecture',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/arch/'
    },
    'BA': {
        'name': 'Business Administration',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ba/'
    },
    'BIOE': {
        'name': 'Bioengineering',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/bioe/'
    },
    'BIOS': {
        'name': 'Biological Sciences',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/bios/'
    },
    'BHIS': {
        'name': 'Biomedical & Health Information Sciences',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/bhis/'
    },
    'BLST': {
        'name': 'Black Studies',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/blst/'
    },
    'BSTT': {
        'name': 'Biostatistics',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/bstt/'
    },
    'BVIS': {
        'name': 'Biomedical Visualization',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/bvis/'
    },
    'CHE': {
        'name': 'Chemical Engineering',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/che/'
    },
    'CI': {
        'name': 'Curriculum and Instruction',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ci/'
    },
    'CLJ': {
        'name': 'Criminology, Law, and Justice',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/clj/'
    },
    'CME': {
        'name': 'Civil, Materials & Environmental Engineering',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/cme/'
    },
    'COMM': {
        'name': 'Communication',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/comm/'
    },
    'DES': {
        'name': 'Design',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/des/'
    },
    'ECE': {
        'name': 'Electrical & Computer Engineering',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ece/'
    },
    'EAES': {
        'name': 'Earth and Environmental Sciences',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/eaes/'
    },
    'IE': {
        'name': 'Industrial Engineering',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ie/'
    },
    'STAT': {
        'name': 'Statistics',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/stat/'
    },
    'MCS': {
        'name': 'Mathematical Computer Science',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/mcs/'
    },
    'PSCH': {
        'name': 'Psychology',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/psch/'
    },
    'ART': {
        'name': 'Art',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/art/'
    },
    'IDS': {
        'name': 'Information and Decision Sciences',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ids/'
    },
    'HIM': {
        'name': 'Health Information Management',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/him/'
    },
    'PPOL': {
        'name': 'Public Policy',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/ppol/'
    },
    'UPP': {
        'name': 'Urban Planning and Policy',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/upp/'
    },
    'US': {
        'name': 'Urban Studies',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/us/'
    },
    'PA': {
        'name': 'Public Administration',
        'url': 'https://catalog.uic.edu/ucat/course-descriptions/pa/'
    }
}

def main(departments=None):
    """
    Main scraper function

    Args:
        departments: List of department codes to scrape (e.g., ['CS', 'MATH'])
                    If None, scrape all configured departments
    """
    print("="*60)
    print("UIC Generic Course Scraper")
    print("="*60)

    # Create database
    conn = create_database()
    print("✓ Database created/connected: uic_courses.db")

    # Determine which departments to scrape
    if departments is None:
        departments = list(DEPARTMENTS.keys())

    total_courses = 0

    # Scrape each department
    for dept_code in departments:
        if dept_code not in DEPARTMENTS:
            print(f"\n⚠️  Department '{dept_code}' not configured. Skipping...")
            continue

        config = DEPARTMENTS[dept_code]
        print(f"\n{'='*60}")
        print(f"Scraping {config['name']} ({dept_code})")
        print('='*60)

        try:
            courses = scrape_department_courses(dept_code, config['url'])
            print(f"\n✓ Scraped {len(courses)} {dept_code} courses")

            if courses:
                insert_courses(conn, courses)
                display_sample_data(conn, dept_code)
                total_courses += len(courses)
            else:
                print(f"No {dept_code} courses found!")
        except Exception as e:
            print(f"\n✗ Error scraping {dept_code}: {e}")
            import traceback
            traceback.print_exc()

    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    cursor = conn.cursor()

    for dept_code in departments:
        if dept_code in DEPARTMENTS:
            cursor.execute('SELECT COUNT(*) FROM courses WHERE course_code LIKE ?', (f'{dept_code}%',))
            count = cursor.fetchone()[0]
            print(f"  {dept_code}: {count} courses in database")

    # Close connection
    conn.close()
    print("\n✓ Database connection closed")
    print("\nQuery examples:")
    print("  sqlite3 uic_courses.db")
    print("  SELECT * FROM courses WHERE course_code LIKE 'MATH%' LIMIT 5;")
    print("  SELECT * FROM prerequisites LIMIT 10;")

if __name__ == "__main__":
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        # Scrape specific departments
        depts = sys.argv[1].split(',')
        main(departments=depts)
    else:
        # Scrape all configured departments
        main()
