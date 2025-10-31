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
    easy_keywords = ['introduction', 'survey', 'overview', 'fundamentals', 'basics']
    
    desc_lower = description.lower()
    if any(word in desc_lower for word in challenging_keywords):
        difficulty_score += 1
    if any(word in desc_lower for word in easy_keywords):
        difficulty_score -= 1
    
    # Map score to difficulty (0-9 scale)
    if difficulty_score <= 2:
        return "Easy"
    elif difficulty_score <= 5:
        return "Moderate"
    else:
        return "Challenging"

# Create SQLite database with two tables
def create_database():
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
            description TEXT,
            level INTEGER,
            difficulty TEXT,
            raw_text TEXT
        )
    ''')
    
    # Prerequisites table (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            prerequisite_code TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(course_id, prerequisite_code)
        )
    ''')
    
    conn.commit()
    return conn

# Extract prerequisite course codes from text
def parse_prerequisites(prereq_text):
    if not prereq_text:
        return []
    
    # Find all CS course codes (e.g., CS 100, CS 141, etc.)
    prereq_codes = re.findall(r'CS\s*\d{3}', prereq_text, re.IGNORECASE)
    
    # Normalize format (e.g., "CS141" -> "CS 141")
    normalized = []
    for code in prereq_codes:
        normalized_code = re.sub(r'CS\s*(\d{3})', r'CS \1', code, flags=re.IGNORECASE)
        normalized.append(normalized_code.upper())
    
    return list(set(normalized))  # Remove duplicates

# Scrape UIC CS courses
def scrape_uic_courses():
    url = "https://catalog.uic.edu/ucat/course-descriptions/cs/"
    
    print(f"Fetching {url}...")
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
            
            # Parse course code (e.g., "CS 100")
            code_match = re.match(r'^(CS\s+\d+)\.\s+(.+?)\.?\s*(\d+(?:-\d+)?\s+hours?\.?)?$', title_text)
            if not code_match:
                print(f"Could not parse: {title_text}")
                continue
            
            course_code = code_match.group(1).strip()
            # Normalize spaces (replace non-breaking spaces with regular spaces)
            course_code = course_code.replace('\xa0', ' ').replace('\u00a0', ' ')
            
            course_title = code_match.group(2).strip()
            # Clean up title - remove trailing periods and extra text after periods
            if '.' in course_title:
                course_title = course_title.split('.')[0].strip()
            # Remove any text after "or" at the end
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
            prereq_match = re.search(r'Prerequisite\s*\(s\):(.+?)(?:\.|$)', description, re.IGNORECASE)
            prereq_text = prereq_match.group(1).strip() if prereq_match else None
            
            # Parse individual prerequisite courses
            prerequisites = parse_prerequisites(prereq_text)
            
            # Extract numeric credits for difficulty calculation
            credits_num = 3  # default
            if credits:
                match = re.search(r'(\d+)', credits)
                if match:
                    credits_num = int(match.group(1))
            
            # Estimate difficulty based on multiple factors
            difficulty = estimate_difficulty(level, len(prerequisites), credits_num, description)
            
            # Store raw HTML for reference
            raw_text = block.get_text(separator=' ', strip=True)
            raw_text = re.sub(r'\s+', ' ', raw_text)
            
            courses.append({
                'course_code': course_code,
                'course_number': course_number,
                'title': course_title,
                'credits': credits,
                'description': description,
                'prerequisites': prerequisites,
                'level': level,
                'difficulty': difficulty,
                'raw_text': raw_text
            })
            
            prereq_str = ", ".join(prerequisites) if prerequisites else "None"
            print(f"✓ Parsed: {course_code} - {course_title} ({difficulty}) (Prereqs: {prereq_str})")
            
        except Exception as e:
            print(f"Error parsing course block: {e}")
            continue
    
    return courses

# Insert courses and prerequisites into database
def insert_courses(conn, courses):
    cursor = conn.cursor()
    
    for course in courses:
        try:
            # Insert course
            cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (course_code, course_number, title, credits, description, level, difficulty, raw_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course['course_code'],
                course['course_number'],
                course['title'],
                course['credits'],
                course['description'],
                course['level'],
                course['difficulty'],
                course['raw_text']
            ))
            
            # Get the course_id
            cursor.execute('SELECT id FROM courses WHERE course_code = ?', (course['course_code'],))
            course_id = cursor.fetchone()[0]
            
            # Delete old prerequisites for this course
            cursor.execute('DELETE FROM prerequisites WHERE course_id = ?', (course_id,))
            
            # Insert prerequisites
            for prereq_code in course['prerequisites']:
                cursor.execute('''
                    INSERT OR IGNORE INTO prerequisites (course_id, prerequisite_code)
                    VALUES (?, ?)
                ''', (course_id, prereq_code))
            
        except sqlite3.IntegrityError as e:
            print(f"Error inserting course: {course['course_code']} - {e}")
    
    conn.commit()
    print(f"\n✓ Successfully inserted {len(courses)} courses into database!")

# Query and display sample data with prerequisites
def display_sample_data(conn):
    cursor = conn.cursor()
    
    print("\n--- Sample Courses with Prerequisites ---")
    cursor.execute('''
        SELECT c.course_code, c.title, c.credits, c.level, c.difficulty
        FROM courses c
        ORDER BY c.course_number
        LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        course_code, title, credits, level, difficulty = row
        
        # Get prerequisites for this course
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

# Main execution
if __name__ == "__main__":
    print("UIC CS Course Scraper\n" + "="*50)
    
    # Create database
    conn = create_database()
    print("✓ Database created/connected: uic_courses.db\n")
    
    # Scrape courses
    courses = scrape_uic_courses()
    print(f"\n✓ Scraped {len(courses)} courses")
    
    # Insert into database
    if courses:
        insert_courses(conn, courses)
        display_sample_data(conn)
    else:
        print("No courses found to insert!")
    
    # Close connection
    conn.close()
    print("\n✓ Database connection closed")
    print("\nQuery examples:")
    print("  sqlite3 uic_courses.db")
    print("  SELECT * FROM courses LIMIT 5;")
    print("  SELECT * FROM prerequisites LIMIT 10;")