from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from typing import Optional, List


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


# ── Table ─────────────────────────────────────────────────────────────────────

class TableOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    capacity: int


# ── Booking ───────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    table_id: int
    booking_time: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    table_id: int
    booking_time: datetime
    user_id: int
    status: str


# ── Analytics ─────────────────────────────────────────────────────────────────

class PeakHour(BaseModel):
    hour: int
    count: int


class DayDistribution(BaseModel):
    date: str
    count: int


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminBookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    table_id: int
    booking_time: datetime
    user_id: int
    status: str
    user_email: Optional[str] = None


class PaginatedBookings(BaseModel):
    total: int
    page: int
    limit: int
    bookings: List[AdminBookingOut]
