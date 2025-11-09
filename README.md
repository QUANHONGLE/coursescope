# CourseScope - Course Planning Tool for UIC

A modern course planning application for UIC students with prerequisite tracking, grade distributions, and major requirements visualization.

**Live Demo:** https://coursescope-8aec-git-main-quanhongles-projects.vercel.app/?_vercel_share=wap0W56A8zG6q4dCnieN55jkNbQ5h8ND

## 🚀 Features

- **Smart Prerequisite Tracking** - Automatically calculates eligible courses based on completed requirements
- **Major Planning** - Track progress toward CS degree with different concentrations
- **Grade Distributions** - View historical grade data by instructor and semester
- **Course Search & Filtering** - Filter by level, difficulty, credits, and prerequisites
- **Real-time Updates** - Instant feedback as you plan your course schedule

## 🏗️ Tech Stack

**Frontend:**
- React 18 + Vite
- TailwindCSS
- Framer Motion (animations)
- Deployed on Vercel

**Backend:**
- Python Serverless Functions (Vercel)
- SQLite database with 1,500+ courses
- Grade distribution data from UIC Registrar

## 📦 Deployment

This app is deployed on Vercel with automatic serverless backend.

### Production URL Structure
- **Frontend**: `https://your-app.vercel.app`
- **API Endpoints**: `https://your-app.vercel.app/api/*`

### Automatic Deployments
Every push to `main` branch automatically deploys to production via Vercel.

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/QUANHONGLE/coursescope.git
   cd coursescope
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install flask flask-cors flask-caching
   cd ..
   ```

4. **Run development servers**

   **Terminal 1 - Start Flask Backend:**
   ```bash
   npm run backend
   ```
   Backend runs on `http://localhost:5001`

   **Terminal 2 - Start Frontend:**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173` with API proxy to Flask

### How It Works

- **Local Development**: Vite proxies `/api/*` requests to Flask backend (`localhost:5001`)
- **Production (Vercel)**: Uses serverless functions in `api/` folder
- **No conflicts**: Vite proxy only active during `npm run dev`, production uses Vercel functions

## 📁 Project Structure

```
coursescope/
├── api/                          # Vercel serverless functions (production)
│   ├── _db.py                   # Database utilities
│   ├── majors.py                # GET /api/majors
│   ├── majors/[id]/requirements.py  # GET /api/majors/<id>/requirements
│   ├── courses.py               # GET /api/courses
│   ├── course.py                # GET /api/course?code=CS101
│   ├── eligible.py              # POST /api/eligible
│   ├── grades.py                # GET /api/grades?code=CS101
│   └── uic_courses.db          # SQLite database
├── backend/                     # Flask API (local development)
│   ├── api.py                  # Flask server
│   ├── generic_major_scraper.py # Major requirements scraper
│   ├── generic_course_scraper.py # Course catalog scraper
│   ├── grade_distribution_importer.py # Grade data importer
│   └── uic_courses.db          # Local database
├── src/                         # React frontend
│   ├── components/
│   ├── App.jsx
│   └── main.jsx
├── vite.config.js               # Vite config with proxy for local dev
├── start-backend.sh             # Script to start Flask backend
└── package.json
```

## 🔌 API Endpoints

All endpoints are available at `/api/*`:

### Majors
- `GET /api/majors` - List all majors and concentrations
- `GET /api/majors/<id>/requirements` - Get requirements for a specific major

### Courses
- `GET /api/courses` - Get all courses with prerequisites and difficulty
- `GET /api/course?code=<code>` - Get single course details
- `POST /api/eligible` - Get eligible courses based on completed courses
  ```json
  { "completed": ["CS 111", "CS 141"] }
  ```

### Grades
- `GET /api/grades?code=<code>` - Get grade distribution data for a course

## 📊 Database

The SQLite database (`uic_courses.db`) contains:
- **courses** - 1,500+ UIC courses
- **prerequisites** - Grouped AND/OR prerequisite logic
- **majors** - CS major and concentrations
- **major_requirements** - Required courses per major
- **major_electives** - Elective courses per major
- **grade_distributions** - Historical grade data
- **semesters** - Semester information

## 🔧 Data Management

### Scraping Fresh Course Data

```bash
cd backend

# Scrape course catalog
python3 generic_course_scraper.py

# Scrape major requirements
python3 generic_major_scraper.py --major=CS

# Import grade distributions
python3 grade_distribution_importer.py grade_distribution_csv/
```

After updating the database:
1. Copy `backend/uic_courses.db` to `api/uic_courses.db`
2. Commit and push to GitHub
3. Vercel will automatically redeploy with new data

## ⚡ Performance

Optimized for 1,500+ courses:
- Database indexing on all query columns
- Bulk queries with O(1) dictionary lookups
- 10-minute API response caching
- 300ms debounced search
- Serverless functions scale automatically

## 🚢 Deployment Guide

### Vercel Setup (Already Configured)

1. **Connect GitHub repo to Vercel**
2. **Vercel auto-detects:**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Serverless Functions: `api/` folder

3. **Every push to main** triggers automatic deployment

### Manual Deployment

```bash
# Build frontend locally
npm run build

# Deploy to Vercel
npm install -g vercel
vercel --prod
```

## 🐛 Troubleshooting

**API not connecting:**
- Check Vercel function logs in dashboard
- Verify database file exists in `api/` folder
- Check CORS headers in serverless functions

**Port already in use (local dev):**
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**Database locked:**
```bash
lsof uic_courses.db
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Push to your fork
6. Create a Pull Request

## 📄 License

MIT License - feel free to use this for your own university!

## 🔗 Resources

- [UIC Course Catalog](https://catalog.uic.edu/)
- [UIC CS Department](https://catalog.uic.edu/ucat/colleges-depts/engineering/cs/)
- [Vercel Documentation](https://vercel.com/docs)
