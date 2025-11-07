import sqlite3
import re

def update_prerequisite_logic():
    """
    Parse course descriptions to determine if prerequisites are OR or AND logic.

    Heuristic:
    - If description contains multiple "or" between prerequisites -> OR logic
    - If description contains "and" between prerequisites -> AND logic
    - If 4+ prerequisites for a course -> likely OR logic (multiple entry paths)
    - If 2-3 prerequisites -> check description for "and"
    """

    conn = sqlite3.connect('uic_courses.db')
    cursor = conn.cursor()

    # Get all courses with prerequisites
    cursor.execute('''
        SELECT
            c.id,
            c.course_code,
            c.description,
            COUNT(p.prerequisite_code) as prereq_count,
            GROUP_CONCAT(p.prerequisite_code, '|') as prereqs
        FROM courses c
        JOIN prerequisites p ON c.id = p.course_id
        GROUP BY c.id
    ''')

    courses = cursor.fetchall()

    or_count = 0
    and_count = 0

    for course_id, course_code, description, prereq_count, prereqs_str in courses:
        prereqs = prereqs_str.split('|')

        # Default to OR if we can't determine
        logic_type = 'OR'

        if description:
            desc_lower = description.lower()

            # Count occurrences of " or " and " and " in prerequisite section
            prereq_match = re.search(r'prerequisite\(s\):([^.]+)', desc_lower)
            if prereq_match:
                prereq_text = prereq_match.group(1)

                # Check for prerequisite course codes in the text
                prereq_mentions = sum(1 for p in prereqs if p.lower() in prereq_text)

                # Count logical operators
                or_count_text = prereq_text.count(' or ')
                and_count_text = prereq_text.count(' and ')

                # Determine logic type
                if prereq_count >= 4:
                    # Likely OR - multiple entry paths
                    logic_type = 'OR'
                elif and_count_text >= prereq_count - 1:
                    # If we see "and" connecting prerequisites, it's AND logic
                    # Example: "CS 251 and CS 211 and CS 261"
                    logic_type = 'AND'
                elif or_count_text >= prereq_count - 1:
                    # If we see "or" connecting prerequisites, it's OR logic
                    logic_type = 'OR'
                else:
                    # Check for patterns like "one of" or "either"
                    if 'one of' in prereq_text or 'either' in prereq_text:
                        logic_type = 'OR'
                    elif prereq_count <= 3 and and_count_text > 0:
                        logic_type = 'AND'

        # Update all prerequisites for this course
        cursor.execute('''
            UPDATE prerequisites
            SET logic_type = ?
            WHERE course_id = ?
        ''', (logic_type, course_id))

        if logic_type == 'OR':
            or_count += 1
        else:
            and_count += 1

        print(f"{course_code}: {logic_type} ({prereq_count} prerequisites: {', '.join(prereqs)})")

    conn.commit()
    conn.close()

    print(f"\n✓ Updated prerequisite logic types")
    print(f"  OR courses: {or_count}")
    print(f"  AND courses: {and_count}")

if __name__ == "__main__":
    update_prerequisite_logic()
