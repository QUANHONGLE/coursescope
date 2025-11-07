# CourseScope - Setup & Development Guide

A course planning tool for UIC students with prerequisite tracking, grade distributions, and major requirements.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Initial Setup

1. **Clone and Navigate**
   ```bash
   cd coursescope
   ```

2. **Set Up Backend**
   ```bash
   cd backend

   # Install Python dependencies
   pip install -r requirements.txt

   # Database should already exist with data
   # If you need to scrape fresh data, see "Data Setup" below

   # IMPORTANT: Add performance indexes to database (one-time setup)
   python add_indexes.py
   ```

3. **Set Up Frontend**
   ```bash
   cd ..  # Back to project root
   npm install
   ```

4. **Start Development Servers**

   **Terminal 1 - Backend:**
   ```bash
   cd backend
   python3 api.py
   ```
   Backend runs on `http://localhost:5001`

   **Terminal 2 - Frontend:**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

5. **Open Browser**
   Navigate to `http://localhost:5173`

## Data Setup

### Database Structure
The system uses SQLite (`uic_courses.db`) with the following tables:
- `courses` - Course information
- `prerequisites` - Course prerequisites with grouped AND/OR logic
- `majors` - Major programs and concentrations
- `major_requirements` - Required courses for each major
- `major_electives` - Elective courses for each major
- `grade_distributions` - Historical grade data
- `semesters` - Semester information

### Scraping Course Data

**Scrape course catalog:**
```bash
cd backend
python3 uic_course_scraper.py
```

This scrapes:
- Course codes, titles, descriptions
- Credit hours
- Prerequisite information

### Scraping Major Requirements

**Use the generic scraper (recommended):**
```bash
cd backend

# Test first (creates uic_courses_test.db)
python3 generic_major_scraper.py --test --major=CS

# If test looks good, run for real
python3 generic_major_scraper.py --major=CS

# Or scrape all configured majors
python3 generic_major_scraper.py
```

**Current configured majors:**
- CS (Computer Science)
  - General
  - Computer Systems
  - Design
  - Human-Centered Computing
  - Software Engineering

**To add a new major:** See [backend/SCRAPER_README.md](backend/SCRAPER_README.md)

### Importing Grade Distributions

```bash
cd backend

# Place CSV files in grade_distribution_csv/ folder
# Expected format: "Spring 2025.csv", "Fall 2024.csv", etc.

python3 grade_distribution_importer.py grade_distribution_csv/
```

CSV files should have columns:
- `CRS SUBJ CD` - Department code (e.g., "CS")
- `CRS NBR` - Course number (e.g., "141")
- `Primary Instructor` - Instructor name
- `A`, `B`, `C`, `D`, `F`, `W`, `S`, `U` - Grade counts

### Updating Prerequisites Logic

If you need to manually update prerequisite groups:
```bash
cd backend
python3 update_prerequisite_logic.py
```

This script helps convert simple AND/OR logic to grouped prerequisites.

## Architecture

### Backend (`/backend`)
- **Framework:** Flask
- **Database:** SQLite
- **Port:** 5001

**Key Files:**
- `api.py` - Main API server
- `generic_major_scraper.py` - Modular major requirements scraper
- `uic_course_scraper.py` - Course catalog scraper
- `grade_distribution_importer.py` - Grade data importer
- `uic_courses.db` - SQLite database

### Frontend (`/src`)
- **Framework:** React 18 + Vite
- **Styling:** TailwindCSS
- **Animations:** Framer Motion
- **Port:** 5173

**Key Components:**
- `App.jsx` - Main app with state management
- `OnboardingSection.jsx` - Major selection and completed courses
- `EligibleCourses.jsx` - Filtered course list
- `RequiredCoursesChecklist.jsx` - Sidebar with major requirements
- `Modals.jsx` - Course details and grade distributions

## 🔧 API Endpoints

### Majors
- `GET /api/majors` - List all majors
- `GET /api/majors/<id>/requirements` - Get major requirements and electives

### Courses
- `GET /api/courses` - List all courses
- `GET /api/courses/<code>` - Get specific course details
- `POST /api/courses/eligible` - Get eligible courses based on completed courses
  ```json
  {
    "completedCourses": ["CS 111", "CS 141", "CS 151"]
  }
  ```

### Grades
- `GET /api/courses/<code>/grades` - Get grade distribution data

## ⚡ Performance

CourseScope is optimized to handle 1,500+ courses efficiently:

- **Database Indexing**: All frequently queried columns are indexed
- **Query Optimization**: Eliminated N+1 queries, using bulk fetches with dictionary lookups
- **Response Caching**: API responses cached for 10 minutes (Flask-Caching)
- **Debounced Search**: 300ms debounce prevents excessive filtering during typing
- **Progressive Rendering**: Large lists limited to 50 items initially with "Show more" option

**Performance Metrics:**
- Initial API load: ~300ms (uncached), ~11ms (cached)
- Search/Filter: Smooth, no lag
- Supports 1,500+ courses without slowdown

For detailed performance documentation, see [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)

## Features

### Prerequisite System
- **Grouped Logic:** Supports complex prerequisites like "(CS 141 OR CS 107) AND CS 151 AND CS 211"
- **Visual Display:** Pills with AND/OR indicators in sidebar and modals
- **Smart Eligibility:** Automatically calculates eligible courses based on completed courses

### Major Planning
- **Multiple Majors:** Support for any UIC major (currently CS)
- **Concentrations:** Different tracks within a major
- **Progress Tracking:** Visual indicators for completed, in-progress, and pending courses
- **Electives:** Separate tracking for required vs elective courses

### Grade Distributions
- **Historical Data:** View grade distributions by semester or instructor
- **Instructor Comparison:** Compare different instructors' grading patterns
- **Visual Charts:** Animated grade bars with percentages
- **Statistics:** A/B rate, pass rate, withdrawal rate

### Course Filtering
- **Level:** Filter by 100/200/300/400 level
- **Difficulty:** Easy, Moderate, Challenging
- **Credits:** Filter by credit hours
- **Search:** Search by code or title
- **Eligibility:** Only show courses you can take based on prerequisites

## Testing

### Backend API Testing
```bash
# Test majors endpoint
curl http://localhost:5001/api/majors

# Test major requirements
curl http://localhost:5001/api/majors/1/requirements

# Test courses endpoint
curl http://localhost:5001/api/courses

# Test course details
curl http://localhost:5001/api/courses/CS%20141

# Test grade data
curl http://localhost:5001/api/courses/CS%20141/grades
```

### Frontend Testing
1. Start both servers
2. Open `http://localhost:5173`
3. Test the flow:
   - Select major
   - Mark courses as completed
   - Verify eligible courses update
   - Check sidebar shows correct requirements
   - Test course details modal
   - Test grade distribution modal

### Scraper Testing
Always test scrapers before running on production database:
```bash
# Generic scraper with test flag
python3 generic_major_scraper.py --test --major=CS

# Compare results
sqlite3 uic_courses_test.db "SELECT * FROM majors"
sqlite3 uic_courses_test.db "SELECT * FROM major_requirements"

# Clean up test database
rm uic_courses_test.db
```

## Development Notes

### Adding a New Major

1. **Configure scraper** in `generic_major_scraper.py`:
   ```python
   MAJOR_CONFIGS = {
       'MATH': {
           'name': 'Mathematics',
           'core_courses': [...],
           'department_categories': {...},
           'elective_categories': {...},
           'concentrations': [...]
       }
   }
   ```

2. **Test scraper:**
   ```bash
   python3 generic_major_scraper.py --test --major=MATH
   ```

3. **Scrape data:**
   ```bash
   python3 generic_major_scraper.py --major=MATH
   ```

4. **Frontend automatically picks up new major** - no code changes needed!

### Database Migrations

The database schema supports:
- Multiple majors and concentrations
- Complex prerequisite logic (grouped AND/OR)
- Grade distributions for any course
- Extensible requirement types

No migrations needed when adding new majors or courses.

### Common Issues

**Port already in use:**
```bash
# Kill process on port 5001 (backend)
lsof -ti:5001 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

**Database locked:**
```bash
# Make sure no other processes are accessing the database
lsof uic_courses.db
```

**Empty instructor names:**
- CSV import script handles empty instructor names
- Frontend displays "Instructor Not Specified"
- Multiple unspecified grouped as "X instructors unspecified"

**Prerequisites not showing:**
- Make sure `prerequisiteGroups` field exists in API response
- Check prerequisite `group_id` in database
- Run `update_prerequisite_logic.py` if needed

## 🚢 Production Deployment

1. **Build frontend:**
   ```bash
   npm run build
   ```

2. **Serve static files** from `dist/` folder

3. **Configure backend** for production:
   - Set proper CORS origins
   - Use production database
   - Configure logging
   - Use production WSGI server (gunicorn, waitress)

4. **Environment variables:**
   ```bash
   FLASK_ENV=production
   DATABASE_PATH=/path/to/uic_courses.db
   ```

## Documentation

- [Backend Scraper Guide](backend/SCRAPER_README.md) - Detailed scraper documentation
- [API Documentation](backend/api.py) - View source for API details
- [Database Schema](backend/) - Check create_*_tables() functions

## Contributing

When adding features:
1. Maintain modular architecture
2. Keep frontend major-agnostic
3. Test with multiple majors
4. Document configuration changes
5. Test scrapers in test mode first

## Dependencies

### Backend
- Flask - Web framework
- Flask-CORS - Cross-origin resource sharing
- Flask-Caching - Response caching for performance
- BeautifulSoup4 - HTML parsing
- Requests - HTTP requests
- SQLite3 - Database (built-in)

### Frontend
- React - UI framework
- Vite - Build tool
- TailwindCSS - Styling
- Framer Motion - Animations
- Lucide React - Icons

## 🔗 Resources

- [UIC Course Catalog](https://catalog.uic.edu/)
- [UIC CS Department](https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/)
- [UIC Grade Distributions](https://registrar.uic.edu/ucat/grade-distributions/)
