"""
seed.py — Populate Dineflow DB with realistic demo data.

5 users · 10 tables · 100 bookings (evening-biased)
alice@dineflow.com is seeded as admin.
"""

import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models
from auth import hash_password

USERS = [
    {"email": "alice@dineflow.com",  "password": "password123", "role": "admin"},
    {"email": "bob@dineflow.com",    "password": "password123", "role": "user"},
    {"email": "carol@dineflow.com",  "password": "password123", "role": "user"},
    {"email": "dave@dineflow.com",   "password": "password123", "role": "user"},
    {"email": "eve@dineflow.com",    "password": "password123", "role": "user"},
]

TABLE_CAPACITIES = [2, 2, 4, 4, 4, 6, 6, 8, 8, 10]

# Hours weighted toward evening (18-22)
HOUR_WEIGHTS = {
    10: 2, 11: 3, 12: 6, 13: 5, 14: 3,
    15: 2, 16: 3, 17: 5, 18: 10, 19: 15,
    20: 15, 21: 12, 22: 8, 23: 4,
}
HOURS   = list(HOUR_WEIGHTS.keys())
WEIGHTS = list(HOUR_WEIGHTS.values())


def run_seed(db: Session) -> dict:
    # ── Clear existing data ───────────────────────────────────────────────────
    db.query(models.Booking).delete()
    db.query(models.Table).delete()
    db.query(models.User).delete()
    db.commit()

    # ── Create users ──────────────────────────────────────────────────────────
    user_objs = []
    for u in USERS:
        obj = models.User(
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(obj)
        user_objs.append(obj)
    db.commit()
    for obj in user_objs:
        db.refresh(obj)

    # ── Create tables ─────────────────────────────────────────────────────────
    table_objs = []
    for cap in TABLE_CAPACITIES:
        obj = models.Table(capacity=cap)
        db.add(obj)
        table_objs.append(obj)
    db.commit()
    for obj in table_objs:
        db.refresh(obj)

    # ── Create bookings (2-hour slot aware, no overlaps) ─────────────────────
    today      = datetime.now().replace(minute=0, second=0, microsecond=0)
    used_slots: set = set()   # (table_id, booking_time) — unique per 2-hour block
    bookings_created = 0
    attempts = 0

    while bookings_created < 100 and attempts < 3000:
        attempts += 1
        day_offset = random.randint(-7, 7)
        hour       = random.choices(HOURS, weights=WEIGHTS, k=1)[0]
        btime      = (today + timedelta(days=day_offset)).replace(hour=hour)
        table      = random.choice(table_objs)
        user       = random.choice(user_objs)

        # Enforce the 2-hour slot model: skip if the same table is booked
        # within 2 hours of btime
        conflict = any(
            table.id == t_id
            and abs((btime - bt).total_seconds()) < 7200   # < 2 hours
            for (t_id, bt) in used_slots
        )
        if conflict:
            continue

        used_slots.add((table.id, btime))
        booking = models.Booking(
            user_id      = user.id,
            table_id     = table.id,
            booking_time = btime,
            status       = "active",
        )
        db.add(booking)
        bookings_created += 1

    db.commit()

    return {
        "users":    len(user_objs),
        "tables":   len(table_objs),
        "bookings": bookings_created,
    }


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = run_seed(db)
        print(f"✅ Seed complete: {result}")
        print("   Admin credentials: alice@dineflow.com / password123")
    finally:
        db.close()
