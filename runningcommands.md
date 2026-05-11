python -m venv venv
source venv/bin/activate        # macOS/Linux
# OR
venv\Scripts\activate           # Windows

pip install -r requirements.txt
uvicorn main:app --reload
# In another terminal:
streamlit run app.py
# Seed demo data:
curl -X POST http://localhost:8000/seed-data

🔑 Admin Credentials
Email: alice@dineflow.com
Password: password123