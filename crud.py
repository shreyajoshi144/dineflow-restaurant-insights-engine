from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status

import models
import schemas
from auth import hash_password, verify_password

# Each booking occupies a table for this many hours
SLOT_DURATION_HOURS = 2
# Max bookings a single user may make on one calendar day
MAX_BOOKINGS_PER_DAY = 3


# ── User ──────────────────────────────────────────────────────────────────────

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ── Table ─────────────────────────────────────────────────────────────────────

def get_all_tables(db: Session) -> List[models.Table]:
    return db.query(models.Table).all()


def get_available_tables(db: Session, booking_time: datetime) -> List[models.Table]:
    """
    Return tables not occupied at *booking_time*.

    A booking blocks its table for SLOT_DURATION_HOURS hours, so a new booking
    at T conflicts with any active booking whose time B satisfies:
        B <= T < B + SLOT_DURATION_HOURS
    Equivalently: T - SLOT_DURATION_HOURS < B <= T
    """
    window_start = booking_time - timedelta(hours=SLOT_DURATION_HOURS)

    booked_ids = select(models.Booking.table_id).where(
        models.Booking.status       == "active",
        models.Booking.booking_time >  window_start,
        models.Booking.booking_time <= booking_time,
    )
    return db.query(models.Table).filter(models.Table.id.notin_(booked_ids)).all()


# ── Booking ───────────────────────────────────────────────────────────────────

def _count_active_bookings_today(db: Session, user_id: int, booking_time: datetime) -> int:
    """Count active bookings the user already has on the same calendar day."""
    day_start = booking_time.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end   = day_start + timedelta(days=1)
    return (
        db.query(func.count(models.Booking.id))
        .filter(
            models.Booking.user_id == user_id,
            models.Booking.status  == "active",
            models.Booking.booking_time >= day_start,
            models.Booking.booking_time <  day_end,
        )
        .scalar()
    )


def create_booking(db: Session, user_id: int, booking: schemas.BookingCreate) -> models.Booking:
    # ── Rate limit: max 3 active bookings per user per day ────────────────────
    daily_count = _count_active_bookings_today(db, user_id, booking.booking_time)
    if daily_count >= MAX_BOOKINGS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit reached: you may only make {MAX_BOOKINGS_PER_DAY} "
                f"active bookings per day. Cancel an existing booking to proceed."
            ),
        )

    # ── Verify table exists ───────────────────────────────────────────────────
    table = db.query(models.Table).filter(models.Table.id == booking.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail=f"Table {booking.table_id} does not exist")

    # ── 2-hour slot conflict check ────────────────────────────────────────────
    # Conflict if any active booking B on the same table satisfies:
    #   B <= new_time < B + 2h  →  new_time - 2h < B <= new_time
    window_start = booking.booking_time - timedelta(hours=SLOT_DURATION_HOURS)
    conflict = (
        db.query(models.Booking)
        .filter(
            models.Booking.table_id     == booking.table_id,
            models.Booking.status       == "active",
            models.Booking.booking_time >  window_start,
            models.Booking.booking_time <= booking.booking_time,
        )
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Table {booking.table_id} is occupied at {booking.booking_time} "
                f"(slots last {SLOT_DURATION_HOURS}h). "
                "Check /suggestions for the next free slot."
            ),
        )

    db_booking = models.Booking(
        user_id      = user_id,
        table_id     = booking.table_id,
        booking_time = booking.booking_time,
        status       = "active",
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def get_user_bookings(db: Session, user_id: int) -> List[models.Booking]:
    """Return all bookings (active + cancelled) for a user, newest first."""
    return (
        db.query(models.Booking)
        .filter(models.Booking.user_id == user_id)
        .order_by(models.Booking.booking_time.desc())
        .all()
    )


# ── Smart Slot Suggestions ────────────────────────────────────────────────────

def get_suggestions(db: Session, booking_time: datetime) -> dict:
    available_now = get_available_tables(db, booking_time)

    if available_now:
        return {
            "status": "available",
            "available_tables": [t.id for t in available_now],
            "suggestions": [],
        }

    # Slot is full — find up to 3 nearby slots with availability
    suggestions: List[dict] = []
    for delta_hours in [1, -1, 2, -2, 3, -3, 4]:
        candidate = booking_time + timedelta(hours=delta_hours)
        available = get_available_tables(db, candidate)
        if available:
            suggestions.append({
                "time": candidate.isoformat(),
                "available_tables": [t.id for t in available],
            })
        if len(suggestions) >= 3:
            break

    return {
        "status": "full",
        "message": f"No tables available at {booking_time.isoformat()}",
        "suggestions": suggestions,
    }


# ── Public Analytics ──────────────────────────────────────────────────────────

def get_peak_hours(db: Session) -> List[dict]:
    """Top 3 busiest hours across all *active* bookings."""
    results = (
        db.query(
            func.strftime("%H", models.Booking.booking_time).label("hour"),
            func.count(models.Booking.id).label("count"),
        )
        .filter(models.Booking.status == "active")
        .group_by("hour")
        .order_by(func.count(models.Booking.id).desc())
        .limit(3)
        .all()
    )
    return [{"hour": int(r.hour), "count": r.count} for r in results]


def get_booking_distribution(db: Session) -> List[dict]:
    """Active booking count grouped by date."""
    results = (
        db.query(
            func.strftime("%Y-%m-%d", models.Booking.booking_time).label("date"),
            func.count(models.Booking.id).label("count"),
        )
        .filter(models.Booking.status == "active")
        .group_by("date")
        .order_by("date")
        .all()
    )
    return [{"date": r.date, "count": r.count} for r in results]


# ── Admin — User / Booking Management ────────────────────────────────────────

def admin_get_all_users(db: Session) -> List[dict]:
    """All users with their active booking count."""
    results = (
        db.query(
            models.User.id,
            models.User.email,
            models.User.role,
            func.count(models.Booking.id).label("booking_count"),
        )
        .outerjoin(
            models.Booking,
            (models.Booking.user_id == models.User.id)
            & (models.Booking.status == "active"),
        )
        .group_by(models.User.id)
        .order_by(models.User.id)
        .all()
    )
    return [
        {"id": r.id, "email": r.email, "role": r.role, "active_bookings": r.booking_count}
        for r in results
    ]


def admin_get_bookings(
    db: Session,
    date: Optional[str] = None,
    user_id: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """All bookings with optional filters and pagination. Returns enriched rows."""
    q = (
        db.query(
            models.Booking.id,
            models.Booking.table_id,
            models.Booking.booking_time,
            models.Booking.user_id,
            models.Booking.status,
            models.User.email.label("user_email"),
        )
        .join(models.User, models.User.id == models.Booking.user_id)
    )
    if date:
        q = q.filter(
            func.strftime("%Y-%m-%d", models.Booking.booking_time) == date
        )
    if user_id is not None:
        q = q.filter(models.Booking.user_id == user_id)

    total = q.count()
    rows  = (
        q.order_by(models.Booking.booking_time.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    bookings = [
        {
            "id":           r.id,
            "table_id":     r.table_id,
            "booking_time": r.booking_time.isoformat(),
            "user_id":      r.user_id,
            "status":       r.status,
            "user_email":   r.user_email,
        }
        for r in rows
    ]
    return {"total": total, "page": page, "limit": limit, "bookings": bookings}


def admin_cancel_booking(db: Session, booking_id: int) -> dict:
    """Set booking status to 'cancelled' (soft delete)."""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return {"message": f"Booking {booking_id} has been cancelled", "booking_id": booking_id}


# ── Admin Analytics ───────────────────────────────────────────────────────────

def admin_most_booked_tables(db: Session) -> List[dict]:
    """Tables ranked by number of active bookings."""
    results = (
        db.query(
            models.Booking.table_id,
            models.Table.capacity,
            func.count(models.Booking.id).label("count"),
        )
        .join(models.Table, models.Table.id == models.Booking.table_id)
        .filter(models.Booking.status == "active")
        .group_by(models.Booking.table_id)
        .order_by(func.count(models.Booking.id).desc())
        .all()
    )
    return [{"table_id": r.table_id, "capacity": r.capacity, "count": r.count} for r in results]


def admin_top_users(db: Session, limit: int = 10) -> List[dict]:
    """Users ranked by active booking count."""
    results = (
        db.query(
            models.User.id,
            models.User.email,
            func.count(models.Booking.id).label("count"),
        )
        .join(models.Booking, models.Booking.user_id == models.User.id)
        .filter(models.Booking.status == "active")
        .group_by(models.User.id)
        .order_by(func.count(models.Booking.id).desc())
        .limit(limit)
        .all()
    )
    return [{"user_id": r.id, "email": r.email, "count": r.count} for r in results]


def admin_cancellation_rate(db: Session) -> dict:
    """Overall cancellation rate as a percentage."""
    total     = db.query(func.count(models.Booking.id)).scalar() or 0
    cancelled = (
        db.query(func.count(models.Booking.id))
        .filter(models.Booking.status == "cancelled")
        .scalar()
        or 0
    )
    rate = round(cancelled / total * 100, 2) if total else 0.0
    return {
        "total_bookings":      total,
        "cancelled_bookings":  cancelled,
        "active_bookings":     total - cancelled,
        "cancellation_rate_pct": rate,
    }


def admin_hourly_load(db: Session) -> List[dict]:
    """Active booking count grouped by hour of day (00–23)."""
    results = (
        db.query(
            func.strftime("%H", models.Booking.booking_time).label("hour"),
            func.count(models.Booking.id).label("count"),
        )
        .filter(models.Booking.status == "active")
        .group_by("hour")
        .order_by("hour")
        .all()
    )
    return [{"hour": int(r.hour), "count": r.count} for r in results]


def admin_table_utilization(db: Session) -> List[dict]:
    """Each table's active booking count and capacity (sorted by utilisation desc)."""
    results = (
        db.query(
            models.Table.id.label("table_id"),
            models.Table.capacity,
            func.count(models.Booking.id).label("booking_count"),
        )
        .outerjoin(
            models.Booking,
            (models.Booking.table_id == models.Table.id)
            & (models.Booking.status == "active"),
        )
        .group_by(models.Table.id)
        .order_by(func.count(models.Booking.id).desc())
        .all()
    )
    return [
        {"table_id": r.table_id, "capacity": r.capacity, "booking_count": r.booking_count}
        for r in results
    ]
