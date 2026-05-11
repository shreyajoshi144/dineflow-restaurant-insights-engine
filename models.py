from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # "user" | "admin"
    role            = Column(String, nullable=False, default="user", server_default="user")

    bookings = relationship("Booking", back_populates="user")


class Table(Base):
    __tablename__ = "tables"

    id       = Column(Integer, primary_key=True, index=True)
    capacity = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="table")


class Booking(Base):
    __tablename__ = "bookings"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    table_id     = Column(Integer, ForeignKey("tables.id"), nullable=False)
    booking_time = Column(DateTime, nullable=False)
    # "active" | "cancelled"
    status       = Column(String, nullable=False, default="active", server_default="active")

    user  = relationship("User", back_populates="bookings")
    table = relationship("Table", back_populates="bookings")
