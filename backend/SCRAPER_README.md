# Generic Major Scraper

A modular, configuration-driven scraper for extracting major requirements from UIC course catalog pages.

## Features

- **Configuration-driven**: Add new majors by updating configuration, not code
- **Modular design**: Easy to extend to other majors
- **Test mode**: Safely test scraping without affecting production database
- **Automatic categorization**: Intelligently categorizes courses by department
- **Elective detection**: Automatically identifies elective vs required courses

## Quick Start

### Test a major configuration
```bash
python3 generic_major_scraper.py --test --major=CS
```

### Scrape all configured majors
```bash
python3 generic_major_scraper.py
```

### Scrape specific majors
```bash
python3 generic_major_scraper.py --major=CS,MATH
```

## Adding a New Major

### Step 1: Add Configuration

Edit `generic_major_scraper.py` and add your major to `MAJOR_CONFIGS`:

```python
MAJOR_CONFIGS = {
    'CS': { ... },  # Existing
    'MATH': {       # New major
        'name': 'Mathematics',
        'core_courses': [
            'MATH 210', 'MATH 215', 'MATH 220',
            # List core required courses for fallback
        ],
        'department_categories': {
            'Required Math': ['MATH'],
            'Required CS': ['CS'],
            'Required Science': ['PHYS', 'CHEM'],
            'Required Other': ['ENGR']
        },
        'elective_categories': {
            'Math Electives': ['MATH', 'STAT'],
            'CS Electives': ['CS'],
            'Other Electives': []  # Catch-all
        },
        'concentrations': [
            {
                'name': None,  # General major (no concentration)
                'url': 'https://catalog.uic.edu/...'
            },
            {
                'name': 'Applied Mathematics',
                'url': 'https://catalog.uic.edu/...'
            }
        ]
    }
}
```

### Step 2: Test Configuration

```bash
python3 generic_major_scraper.py --test --major=MATH
```

This creates `uic_courses_test.db` without touching your production database.

### Step 3: Verify Results

Check the test database:
```bash
sqlite3 uic_courses_test.db "SELECT * FROM majors WHERE name = 'Mathematics'"
sqlite3 uic_courses_test.db "SELECT * FROM major_requirements WHERE major_id = 2"
```

### Step 4: Run Production Scrape

Once satisfied:
```bash
python3 generic_major_scraper.py --major=MATH
```

## Configuration Guide

### `core_courses`
List of core required courses used as fallback if table scraping fails.

### `department_categories`
Maps requirement types to department prefixes:
- **Key**: Display name for requirement type (e.g., "Required Math")
- **Value**: List of department codes (e.g., `['MATH', 'STAT']`)

Courses are categorized by matching their department code to these lists.

### `elective_categories`
Same format as `department_categories`, but for elective courses.

Use an empty list `[]` as "Other Electives" to catch any uncategorized courses.

### `concentrations`
List of concentration objects:
- **`name`**: Concentration name (use `None` for general major)
- **`url`**: UIC catalog page URL

## How It Works

1. **Table Detection**: Looks for `<table class="sc_courselist">` elements
2. **Context Analysis**: Checks heading text for keywords like "elective", "select", "choose"
3. **Course Extraction**: Extracts course codes using regex pattern `([A-Z]{2,4})\s+(\d{3})`
4. **Categorization**: Matches department codes to configuration categories
5. **Database Insert**: Stores courses with appropriate requirement/elective types

## Fallback Mechanism

If table scraping finds no courses:
1. Searches page text for `core_courses` list
2. Adds found courses to appropriate categories
3. Useful for pages with non-standard formatting

## Database Schema

The scraper populates three tables:

### `majors`
- `id`: Primary key
- `name`: Major name (e.g., "Computer Science")
- `concentration`: Concentration name or NULL

### `major_requirements`
- `major_id`: Foreign key to majors
- `course_code`: Course code (e.g., "CS 141")
- `requirement_type`: Category from configuration (e.g., "Required CS")

### `major_electives`
- `major_id`: Foreign key to majors
- `course_code`: Course code
- `elective_type`: Category from configuration (e.g., "CS Electives")

## Testing Results

The generic scraper was tested against the existing CS major scraper:

| Major | Required Courses | Electives | Match |
|-------|------------------|-----------|-------|
| CS (General) | 33 | 58 | 100% |
| CS - Computer Systems | 33 | 60 | 100% |
| CS - Design | 32 | 0 | 100% |
| CS - HCC | 36 | 50 | 100% |
| CS - Software Engineering | 33 | 53 | 100% |

## Troubleshooting

### No courses found
- Check if the URL is correct
- Verify the page has `<table class="sc_courselist">` elements
- Inspect the HTML structure - may need custom parsing

### Courses in wrong category
- Review `department_categories` mapping
- Check if department code is listed correctly
- Verify course code format matches regex pattern

### Duplicate courses
- Normal behavior - scraper uses `INSERT OR IGNORE`
- Check if course appears in multiple sections

## Next Steps

After scraping:
1. Run the Flask API: `python api.py`
2. Frontend automatically picks up new majors
3. All prerequisite logic, filtering, and planning work immediately

## Migration from Old Scraper

The old `cs_major_requirements_scraper.py` can be retired. The generic scraper:
- Produces identical results
- Is more maintainable
- Is easier to extend
- Has better error handling
- Includes test mode

Keep the old scraper for reference or remove it once confident.
