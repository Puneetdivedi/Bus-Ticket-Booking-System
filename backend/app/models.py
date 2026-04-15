from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    travel_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    mobile_number: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    is_boarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    seat_assignments: Mapped[list["BookingSeat"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="BookingSeat.seat_number",
    )


class BookingSeat(Base):
    __tablename__ = "booking_seats"
    __table_args__ = (
        UniqueConstraint("travel_date", "seat_number", name="uq_booking_seat_per_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    travel_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    seat_number: Mapped[str] = mapped_column(String(4), nullable=False)

    booking: Mapped[Booking] = relationship(back_populates="seat_assignments")
