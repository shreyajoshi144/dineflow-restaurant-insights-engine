from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from database import engine, get_db
import models
import schemas
import crud
import auth
from seed import run_seed

# ── Create all tables on startup ──────────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dineflow API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Dineflow API is running 🍽️"}


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/signup", response_model=schemas.UserOut, status_code=201)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "role": user.role}


# ── Booking ───────────────────────────────────────────────────────────────────

@app.post("/book", response_model=schemas.BookingOut, status_code=201)
def book_table(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_booking(db, current_user.id, booking)


@app.get("/bookings", response_model=List[schemas.BookingOut])
def get_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.get_user_bookings(db, current_user.id)


# ── Availability ──────────────────────────────────────────────────────────────

@app.get("/availability")
def check_availability(
    time: datetime = Query(..., description="ISO datetime, e.g. 2024-07-15T19:00:00"),
    db: Session = Depends(get_db),
):
    tables = crud.get_available_tables(db, time)
    return {
        "time":             time.isoformat(),
        "available_tables": [{"id": t.id, "capacity": t.capacity} for t in tables],
        "total_available":  len(tables),
    }


# ── Smart Suggestions ─────────────────────────────────────────────────────────

@app.get("/suggestions")
def get_suggestions(
    time: datetime = Query(..., description="ISO datetime to check"),
    db: Session = Depends(get_db),
):
    return crud.get_suggestions(db, time)


# ── Public Analytics ──────────────────────────────────────────────────────────

@app.get("/analytics/peak-hours")
def peak_hours(db: Session = Depends(get_db)):
    return {"peak_hours": crud.get_peak_hours(db)}


@app.get("/analytics/distribution")
def booking_distribution(db: Session = Depends(get_db)):
    return {"distribution": crud.get_booking_distribution(db)}


# ── Seed ──────────────────────────────────────────────────────────────────────

@app.post("/seed-data")
def seed_data(db: Session = Depends(get_db)):
    result = run_seed(db)
    return {"message": "Database seeded successfully", **result}


# ════════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES  (all protected by require_admin dependency)
# ════════════════════════════════════════════════════════════════════════════

# ── User management ───────────────────────────────────────────────────────────

@app.get("/admin/users")
def admin_list_users(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """List all users with their active booking counts."""
    return {"users": crud.admin_get_all_users(db)}


# ── Booking management ────────────────────────────────────────────────────────

@app.get("/admin/bookings")
def admin_list_bookings(
    date:    Optional[str] = Query(None, description="Filter by date YYYY-MM-DD"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    page:    int           = Query(1,  ge=1),
    limit:   int           = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Paginated list of all bookings with optional date / user_id filters."""
    return crud.admin_get_bookings(db, date=date, user_id=user_id, page=page, limit=limit)


@app.delete("/admin/booking/{booking_id}")
def admin_cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Soft-cancel a booking (sets status='cancelled', does NOT delete)."""
    return crud.admin_cancel_booking(db, booking_id)


# ── Admin analytics ───────────────────────────────────────────────────────────

@app.get("/admin/most-booked-tables")
def admin_most_booked_tables(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Tables ranked by active booking volume."""
    return {"most_booked_tables": crud.admin_most_booked_tables(db)}


@app.get("/admin/top-users")
def admin_top_users(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Users with the most active bookings."""
    return {"top_users": crud.admin_top_users(db, limit=limit)}


@app.get("/admin/cancellation-rate")
def admin_cancellation_rate(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Overall ratio of cancelled to total bookings."""
    return crud.admin_cancellation_rate(db)


@app.get("/admin/hourly-load")
def admin_hourly_load(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Active booking counts for every hour of the day (00–23)."""
    return {"hourly_load": crud.admin_hourly_load(db)}


@app.get("/admin/table-utilization")
def admin_table_utilization(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Per-table active booking count and seating capacity."""
    return {"table_utilization": crud.admin_table_utilization(db)}
