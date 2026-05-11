# Dineflow — Pre-Deployment Checklist

## ✅ All tests passed — 4 bugs fixed before this checklist was written

---

## 🐛 Bugs Fixed (apply before deploying)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `render.yaml` | `rootDir: backend` — your files are flat, Render would 404 | Removed `rootDir` |
| 2 | `database.py` | `from sqlalchemy.ext.declarative import declarative_base` — deprecated/broken in SQLAlchemy 2.0 | Changed to `from sqlalchemy.orm import declarative_base` |
| 3 | `requirements.txt` | `bcrypt==4.1.3` — passlib 1.7.4 cannot introspect 4.x versions, logs stderr noise on every request | Pinned to `bcrypt==4.0.1` |
| 4 | `render.yaml` | `PYTHON_VERSION: 3.11.0` mismatched `runtime.txt: python-3.11.9` | Aligned both to `3.11.9` |

---

## 🚀 Step-by-Step Deployment

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dineflow.git
git push -u origin main
```

> ⚠️ Verify `.gitignore` is committed — it excludes `*.db` so your SQLite file never goes to GitHub.

---

### Step 2 — Deploy Backend on Render

1. Go to https://render.com → New → Web Service
2. Connect your GitHub repo
3. Settings:

| Field | Value |
|-------|-------|
| **Root Directory** | *(leave blank)* |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

4. Environment Variables (already in `render.yaml` — auto-applied):

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Auto-generated ✅ |
| `DB_PATH` | `/tmp/dineflow.db` |
| `PYTHON_VERSION` | `3.11.9` |

5. Click **Create Web Service** → wait ~3 min for green

6. Test: `https://YOUR-APP.onrender.com/` → `{"message":"Dineflow API is running 🍽️"}`

> ⚠️ Render free tier **cold-starts** after 15 min idle — first request takes ~30s.  
> ⚠️ `/tmp/dineflow.db` is **ephemeral** — resets on every restart. Seed after each deploy.

---

### Step 3 — Seed the Database

After backend is live, run once:

```bash
curl -X POST https://YOUR-APP.onrender.com/seed-data
```

This creates: 5 users (alice=admin), 10 tables, 100 bookings.

---

### Step 4 — Deploy Frontend on Streamlit Cloud

1. Go to https://share.streamlit.io → New app
2. Settings:

| Field | Value |
|-------|-------|
| **Repository** | `YOUR_USERNAME/dineflow` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

3. Advanced → Secrets → paste:

```toml
BACKEND_URL = "https://YOUR-APP.onrender.com"
```

4. Click **Deploy** → live at `https://YOUR-APP.streamlit.app`

---

## ✅ Smoke Test Checklist

After both are deployed, run through this sequence:

```
1. Open Streamlit URL
2. Sign Up with a fresh email
3. Log In — sidebar should show role tag
4. Sidebar → Seed Demo Data → Run Seed
5. Book Table → pick date → Check Availability → Book a table → 🎈 balloons
6. Log out, log in as alice@dineflow.com / password123
7. Sidebar → 🛡️ Admin Panel should appear
8. Admin Panel → All Bookings → Cancel a booking
9. Admin Panel → Analytics tab → charts load
10. Analytics page → peak hours + distribution chart appear
```

---

## 🔑 Demo Credentials

| Email | Password | Role |
|-------|----------|------|
| `alice@dineflow.com` | `password123` | **admin** |
| `bob@dineflow.com` | `password123` | user |
| `carol@dineflow.com` | `password123` | user |

---

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Backend 502 on first request | Render cold start | Wait 30s, retry |
| "Cannot connect to backend" in UI | Wrong `BACKEND_URL` | Remove trailing slash, check Streamlit secrets |
| Bookings disappeared | Render restarted `/tmp` | POST `/seed-data` again |
| Login fails after re-deploy | DB wiped with restart | Seed again |
| Admin Panel not in sidebar | Not logged in as admin | Use alice@dineflow.com |
| `bcrypt` error in logs | Wrong bcrypt version | Ensure `bcrypt==4.0.1` in requirements.txt |

---

## 📌 Quick Links After Deploy

| | URL |
|--|-----|
| Streamlit App | `https://YOUR-APP.streamlit.app` |
| Backend API | `https://YOUR-APP.onrender.com` |
| Swagger Docs | `https://YOUR-APP.onrender.com/docs` |
| Seed Endpoint | `POST https://YOUR-APP.onrender.com/seed-data` |
