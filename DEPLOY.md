# 🍽️ Dineflow — Deployment Guide

Deploy the FastAPI backend to **Render** (free) and the Streamlit frontend to **Streamlit Cloud** (free).

---

## 📁 Folder Structure After This Setup

```
dineflow-deploy/
├── backend/                  ← Deploy to Render
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   ├── seed.py
│   └── requirements.txt
│
├── frontend/                 ← Deploy to Streamlit Cloud
│   ├── app.py
│   ├── requirements.txt
│   └── .streamlit/
│       ├── config.toml
│       └── secrets.toml.example
│
├── render.yaml               ← Render auto-deploy config
├── .gitignore
└── DEPLOY.md                 ← This file
```

---

## 🚀 Step-by-Step Deployment

### STEP 1 — Push to GitHub

Create **one GitHub repo** (e.g. `dineflow`) and push everything:

```bash
git init
git add .
git commit -m "initial deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dineflow.git
git push -u origin main
```

---

### STEP 2 — Deploy Backend on Render

1. Go to [https://render.com](https://render.com) → Sign up / Log in
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Fill in:

| Field | Value |
|-------|-------|
| **Name** | `dineflow-api` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

5. Under **Environment Variables**, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Any random string, e.g. `dineflow-prod-secret-2026` |
| `DB_PATH` | `/tmp/dineflow.db` |

6. Click **Create Web Service**
7. Wait ~3 minutes for build. Once green, copy your URL:
   ```
   https://dineflow-api.onrender.com
   ```
8. Test it: `https://dineflow-api.onrender.com/` should return:
   ```json
   {"message": "Dineflow API is running 🍽️"}
   ```

> ⚠️ **Important:** Render free tier spins down after 15 min of inactivity.
> First request after sleep takes ~30 seconds. This is normal on free tier.

> ⚠️ **Database note:** Render free tier has an **ephemeral filesystem** — the SQLite
> database resets on every deploy/restart. This is fine for demo purposes.
> For persistence, upgrade to Render's paid tier or use a hosted DB like
> [Turso](https://turso.tech) (free SQLite in the cloud).

---

### STEP 3 — Seed the database after deploy

After the backend is live, seed it once via the API:

```bash
curl -X POST https://dineflow-api.onrender.com/seed-data
```

Or just use the **Seed Demo Data** button in the Streamlit UI after deploying the frontend.

---

### STEP 4 — Deploy Frontend on Streamlit Cloud

1. Go to [https://share.streamlit.io](https://share.streamlit.io) → Sign up / Log in with GitHub
2. Click **New app**
3. Fill in:

| Field | Value |
|-------|-------|
| **Repository** | `YOUR_USERNAME/dineflow` |
| **Branch** | `main` |
| **Main file path** | `frontend/app.py` |
| **App URL** | `dineflow` (or any name you like) |

4. Click **Advanced settings → Secrets** and paste:

```toml
BACKEND_URL = "https://dineflow-api.onrender.com"
```

   *(Replace with your actual Render URL from Step 2)*

5. Click **Deploy!** — takes ~2 minutes
6. Your app will be live at:
   ```
   https://dineflow.streamlit.app
   ```

---

## ✅ Verify Everything Works

After both are deployed, test this flow:

```
1. Open your Streamlit URL
2. Sign Up with a new email
3. Log in
4. Sidebar → Seed Demo Data → Run Seed  (populates DB)
5. Book Table → pick a date → Check Availability
6. Book a table → confirm balloons 🎈
7. Analytics → verify peak hours + distribution chart appear
```

---

## 🔧 Local Development (no change)

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 — Frontend
cd frontend
pip install -r requirements.txt
streamlit run app.py
# app.py automatically uses localhost:8000 when BACKEND_URL is not set
```

---

## 🌐 Environment Variables Summary

### Backend (Render)
| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ Yes | JWT signing secret — set any long random string |
| `DB_PATH` | ✅ Yes | Set to `/tmp/dineflow.db` on Render free tier |

### Frontend (Streamlit Cloud Secrets)
| Variable | Required | Description |
|----------|----------|-------------|
| `BACKEND_URL` | ✅ Yes | Full URL of your Render backend, no trailing slash |

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Backend returns 500 on first request | Wait 30s — Render free tier cold start |
| "Cannot connect to backend" in UI | Check `BACKEND_URL` in Streamlit secrets, no trailing slash |
| Bookings disappear after a while | Expected on Render free — ephemeral SQLite. Re-seed via button |
| Login fails after re-deploy | DB reset on deploy — sign up again or re-seed |
| CORS error in browser console | Already handled in `main.py` via `CORSMiddleware` |
| `bcrypt` version error | Fixed — `requirements.txt` pins `bcrypt==4.0.1` |

---

## 📌 Quick Links After Deploy

| Service | URL |
|---------|-----|
| Streamlit App | `https://YOUR_APP.streamlit.app` |
| Backend API | `https://dineflow-api.onrender.com` |
| Swagger Docs | `https://dineflow-api.onrender.com/docs` |
| Seed Data | `POST https://dineflow-api.onrender.com/seed-data` |

---

*Built with FastAPI · SQLite · SQLAlchemy · JWT · Streamlit*
