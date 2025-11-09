# Deployment Guide

## Vercel Deployment

Your CourseScope application consists of two parts:
1. **Frontend** (React + Vite)
2. **Backend** (Python Flask API)

### Option 1: Deploy Both to Vercel (Recommended for this project)

#### Step 1: Deploy the Backend API

1. Create a new Vercel project for the backend:
   ```bash
   cd backend
   ```

2. Create a `vercel.json` in the `backend` folder:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "api.py"
       }
     ]
   }
   ```

3. Deploy to Vercel:
   ```bash
   vercel
   ```

4. Note the deployed URL (e.g., `https://your-backend.vercel.app`)

#### Step 2: Deploy the Frontend

1. In your Vercel project settings for the frontend, add an environment variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-backend.vercel.app/api`

2. Deploy the frontend:
   ```bash
   vercel
   ```

### Option 2: Frontend on Vercel, Backend Elsewhere

If you deploy the backend to Railway, Render, or another platform:

1. Deploy your backend to your chosen platform
2. Get the backend URL (e.g., `https://your-api.railway.app`)
3. In Vercel frontend settings, set:
   - `VITE_API_URL` = `https://your-api.railway.app/api`

### Local Development

For local development, the code will work as-is:
- Frontend runs on `http://localhost:5174` (Vite dev server)
- Backend runs on `http://localhost:5001` (Flask)
- Vite proxy configuration handles API requests

No environment variables needed locally - just run:
```bash
# Terminal 1 - Backend
cd backend
python api.py

# Terminal 2 - Frontend
npm run dev
```

### Environment Variables Summary

| Environment | VITE_API_URL | Behavior |
|-------------|--------------|----------|
| Local Dev | (not set) | Uses `/api` which Vite proxies to `localhost:5001` |
| Production | `https://your-backend.vercel.app/api` | Frontend makes requests directly to backend URL |

### Database Considerations

Your SQLite database (`uic_courses.db`) needs to be accessible to the backend. For Vercel:
- SQLite works but is read-only after deployment
- Consider migrating to PostgreSQL/MySQL for production if you need write access
- Or use Vercel's blob storage for the SQLite file

### CORS Configuration

Make sure your backend `api.py` has CORS enabled for your frontend domain:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://your-frontend.vercel.app", "http://localhost:5174"])
```
