from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import Booking, BookingSeat
from app.services.boarding import get_optimal_boarding_sequence
from app.services.booking_rules import get_row_number, is_past_date, sort_seats


def _booking_query():
    return select(Booking).options(selectinload(Booking.seat_assignments))


def fetch_booking_or_404(db: Session, booking_id: str) -> Booking:
    booking = db.scalar(_booking_query().where(Booking.booking_id == booking_id))
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return booking


def list_bookings(
    db: Session,
    travel_date: date,
    mobile_number: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Booking]:
    """List bookings with pagination support."""
    statement = _booking_query().where(Booking.travel_date == travel_date).order_by(Booking.created_at.asc())
    if mobile_number:
        statement = statement.where(Booking.mobile_number.contains(mobile_number))
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    return list(db.scalars(statement).unique().all())


def get_booked_seats(db: Session, travel_date: date) -> list[str]:
    statement = select(BookingSeat.seat_number).where(BookingSeat.travel_date == travel_date)
    return sort_seats(list(db.scalars(statement).all()))


def _validate_seat_conflicts(
    db: Session,
    travel_date: date,
    seats: list[str],
    exclude_booking_id: str | None = None,
) -> None:
    statement = select(BookingSeat.seat_number).where(
        BookingSeat.travel_date == travel_date,
        BookingSeat.seat_number.in_(seats),
    )
    if exclude_booking_id:
        statement = statement.where(BookingSeat.booking_id != exclude_booking_id)

    conflicting_seats = list(db.scalars(statement).all())
    if conflicting_seats:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Seat(s) already booked: {', '.join(sort_seats(conflicting_seats))}.",
        )


def _validate_mobile_quota(
    db: Session,
    travel_date: date,
    mobile_number: str,
    incoming_seat_count: int,
    exclude_booking_id: str | None = None,
) -> None:
    statement = (
        select(func.count(BookingSeat.id))
        .join(Booking, Booking.booking_id == BookingSeat.booking_id)
        .where(
            Booking.travel_date == travel_date,
            Booking.mobile_number == mobile_number,
        )
    )

    if exclude_booking_id:
        statement = statement.where(Booking.booking_id != exclude_booking_id)

    existing_seat_count = db.scalar(statement) or 0

    if existing_seat_count + incoming_seat_count > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mobile number can hold a maximum of 6 seats for the same travel date.",
        )


def _upsert_seat_assignments(booking: Booking, travel_date: date, seats: list[str]) -> None:
    booking.seat_assignments.clear()
    for seat_number in seats:
        booking.seat_assignments.append(
            BookingSeat(
                booking_id=booking.booking_id,
                travel_date=travel_date,
                seat_number=seat_number,
            )
        )


def create_booking(db: Session, travel_date: date, mobile_number: str, seats: list[str]) -> Booking:
    if is_past_date(travel_date):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Past travel dates are not allowed.")

    _validate_seat_conflicts(db, travel_date, seats)
    _validate_mobile_quota(db, travel_date, mobile_number, len(seats))

    booking = Booking(
        booking_id=str(uuid4()),
        travel_date=travel_date,
        mobile_number=mobile_number,
    )
    _upsert_seat_assignments(booking, travel_date, seats)
    db.add(booking)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more seats were booked by another request. Please refresh and try again.",
        ) from error

    db.refresh(booking)
    return booking


def update_booking(
    db: Session,
    booking_id: str,
    travel_date: date,
    mobile_number: str,
    seats: list[str],
) -> Booking:
    booking = fetch_booking_or_404(db, booking_id)

    if booking.travel_date <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bookings can only be edited before the travel date.",
        )

    if is_past_date(travel_date):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Past travel dates are not allowed.")

    _validate_seat_conflicts(db, travel_date, seats, exclude_booking_id=booking.booking_id)
    _validate_mobile_quota(
        db,
        travel_date,
        mobile_number,
        len(seats),
        exclude_booking_id=booking.booking_id,
    )

    booking.travel_date = travel_date
    booking.mobile_number = mobile_number
    booking.is_boarded = False

    booking.seat_assignments.clear()
    db.flush()
    _upsert_seat_assignments(booking, travel_date, seats)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update booking because one or more seats are no longer available.",
        ) from error

    db.refresh(booking)
    return booking


def toggle_boarding_status(db: Session, booking_id: str, is_boarded: bool) -> Booking:
    booking = fetch_booking_or_404(db, booking_id)
    booking.is_boarded = is_boarded
    db.commit()
    db.refresh(booking)
    return booking


def serialize_booking(booking: Booking, sequence_number: int | None = None) -> dict:
    seats = sort_seats([seat.seat_number for seat in booking.seat_assignments])
    return {
        "booking_id": booking.booking_id,
        "travel_date": booking.travel_date,
        "mobile_number": booking.mobile_number,
        "seats": seats,
        "passenger_count": len(seats),
        "is_boarded": booking.is_boarded,
        "can_edit": booking.travel_date > date.today(),
        "max_row": max(get_row_number(seat) for seat in seats),
        "sequence_number": sequence_number,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
    }


def serialize_booking_list(bookings: list[Booking], travel_date: date) -> dict:
    ordered_bookings = get_optimal_boarding_sequence(bookings)
    sequence_lookup = {booking.booking_id: index for index, booking in enumerate(ordered_bookings, start=1)}

    return {
        "travel_date": travel_date,
        "total_bookings": len(bookings),
        "total_passengers": sum(len(booking.seat_assignments) for booking in bookings),
        "bookings": [
            serialize_booking(booking, sequence_number=sequence_lookup[booking.booking_id])
            for booking in ordered_bookings
        ],
    }
