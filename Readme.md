# Dineflow — Production-Grade Restaurant Reservation & Analytics Platform

A production-grade full-stack reservation system built with FastAPI, SQLAlchemy, SQLite, and Streamlit. The project is designed to showcase backend engineering and data-focused skills, including secure authentication, role-based access control, booking conflict resolution, rate limiting, and SQL-powered analytics.

---

## 🚀 Overview

Dineflow simulates a real-world restaurant reservation platform where users can register, authenticate, check table availability, and create reservations. Administrators can manage users and bookings, cancel reservations via soft deletion, and analyze booking behavior through operational analytics dashboards.

The system emphasizes production-level backend design and data modeling:

* JWT-based authentication and authorization
* Role-Based Access Control (Admin/User)
* 2-hour time-window conflict detection
* Rate limiting (maximum 3 bookings per user per day)
* Soft deletion using booking status
* SQLAlchemy ORM with relational schema design
* Aggregation analytics with efficient SQL queries
* Filtering and pagination for large datasets
* Interactive Streamlit admin dashboard

---

## 
![img.png](img.png)

---

## ✨ Core Features

### 🔐 Authentication & Authorization

* User signup and login
* JWT token generation and validation
* Protected API endpoints
* Admin-only route dependency
* Role included in login response

### 📅 Reservation Engine

* Real-time table availability
* 2-hour reservation blocking window
* Conflict prevention across overlapping bookings
* Smart alternative time suggestions
* Personal booking history

### 🛡️ Admin Management

* View all users
* View all bookings
* Cancel bookings without deleting records
* Filter by date and user
* Paginated results

### 📊 Analytics

* Peak booking hours
* Booking distribution by date
* Most booked tables
* Top users
* Cancellation rate
* Hourly load
* Table utilization

### ⚙️ Production Patterns

* Soft deletes via status field
* HTTP 429 rate limiting
* SQL aggregation queries
* Modular code organization
* Session-based frontend authentication

---

## 🧠 Backend & Data Engineering Highlights

This project demonstrates:

* REST API design with FastAPI
* Relational schema modeling with SQLAlchemy
* Authentication using JWT
* Role-based access control (RBAC)
* Business rule enforcement
* Query optimization through aggregation
* Pagination and filtering strategies
* ETL-style seed generation with synthetic data
* Data visualization with Streamlit

---

## 🗂️ Project Structure

```text
dineflow/
├── app.py          # Streamlit frontend and admin dashboard
├── main.py         # FastAPI routes
├── auth.py         # JWT auth and admin dependency
├── crud.py         # Business logic and analytics queries
├── models.py       # SQLAlchemy models
├── schemas.py      # Pydantic request/response schemas
├── database.py     # Database configuration
├── seed.py         # Demo data generator
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

### User

* id
* email
* hashed_password
* role (`user`, `admin`)

### Table

* id
* capacity

### Booking

* id
* user_id
* table_id
* booking_time
* status (`active`, `cancelled`)

---

## 📈 Analytics Endpoints

### Public Analytics

* `GET /analytics/peak-hours`
* `GET /analytics/distribution`

### Admin Analytics

* `GET /admin/most-booked-tables`
* `GET /admin/top-users`
* `GET /admin/cancellation-rate`
* `GET /admin/hourly-load`
* `GET /admin/table-utilization`

---

## 🔌 API Endpoints

### Authentication

* `POST /signup`
* `POST /login`

### Reservations

* `GET /availability`
* `POST /book`
* `GET /suggestions`
* `GET /bookings`

### Administration

* `GET /admin/users`
* `GET /admin/bookings`
* `DELETE /admin/booking/{id}`

### Utilities

* `POST /seed-data`

---

## ⚡ Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run FastAPI Backend

```bash
uvicorn main:app --reload
```

### 5. Run Streamlit Frontend

```bash
streamlit run app.py
```

### 6. Seed Demo Data

```bash
curl -X POST http://localhost:8000/seed-data
```

---

## 🔑 Demo Admin Credentials

```text
Email: alice@dineflow.com
Password: password123
```

---

## 🧪 Example Test Scenarios

* Create a new user account
* Book a table and verify availability updates
* Attempt overlapping bookings to trigger conflict detection
* Make more than 3 bookings in one day to test rate limiting
* Log in as admin and cancel bookings
* Review analytics dashboards

---

## 📌 Resume Description

Built a production-grade restaurant reservation and analytics platform using FastAPI, SQLAlchemy, SQLite, and Streamlit. Implemented JWT authentication, role-based access control, 2-hour conflict detection, rate limiting, soft deletion, and SQL-based analytics with filtering and pagination.

---

## 🎯 Skills Demonstrated

* Python Backend Development
* FastAPI REST APIs
* SQLAlchemy ORM
* Database Design
* Authentication & Security
* Role-Based Access Control
* Data Aggregation & Analytics
* Pagination & Filtering
* Streamlit Dashboards
* Software Architecture

---

## 🚀 Future Enhancements

* PostgreSQL deployment
* Docker containerization
* CI/CD pipeline
* Unit and integration testing
* Redis caching
* Background jobs with Celery
* Cloud deployment (AWS/GCP)

---
