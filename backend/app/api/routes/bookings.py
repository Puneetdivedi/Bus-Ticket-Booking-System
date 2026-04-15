from __future__ import annotations

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    BoardingSequenceResponse,
    BoardingStatusPayload,
    BookingListResponse,
    BookingPayload,
    BookingResponse,
    SeatAvailabilityResponse,
)
from app.services.boarding import get_estimated_boarding_time_seconds, serialize_boarding_sequence
from app.services.bookings import (
    create_booking,
    fetch_booking_or_404,
    get_booked_seats,
    list_bookings,
    serialize_booking,
    serialize_booking_list,
    toggle_boarding_status,
    update_booking,
)

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("/seat-map", response_model=SeatAvailabilityResponse)
def get_seat_map(travel_date: date = Query(...), db: Session = Depends(get_db)) -> dict:
    return {
        "travel_date": travel_date,
        "booked_seats": get_booked_seats(db, travel_date),
    }


@router.get("/boarding-sequence", response_model=BoardingSequenceResponse)
def get_boarding_sequence(travel_date: date = Query(...), db: Session = Depends(get_db)) -> dict:
    bookings = list_bookings(db, travel_date)
    return {
        "travel_date": travel_date,
        "estimated_total_time_seconds": get_estimated_boarding_time_seconds(bookings),
        "bookings": serialize_boarding_sequence(bookings),
    }


@router.get("/export/csv")
def export_bookings_csv(travel_date: date = Query(...), db: Session = Depends(get_db)) -> StreamingResponse:
    bookings = list_bookings(db, travel_date)
    ordered_bookings = serialize_boarding_sequence(bookings)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sequence", "Booking ID", "Seats", "Mobile Number", "Boarding Status"])

    for booking in ordered_bookings:
        writer.writerow(
            [
                booking["sequence_number"],
                booking["booking_id"],
                ", ".join(booking["seats"]),
                booking["mobile_number"],
                "Boarded" if booking["is_boarded"] else "Not Boarded",
            ]
        )

    output.seek(0)
    filename = f"bookings-{travel_date.isoformat()}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)


@router.get("", response_model=BookingListResponse)
def get_bookings(
    travel_date: date = Query(...),
    mobile_number: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    bookings = list_bookings(db, travel_date, mobile_number)
    return serialize_booking_list(bookings, travel_date)


@router.post("", response_model=BookingResponse, status_code=201)
def create_booking_endpoint(payload: BookingPayload, db: Session = Depends(get_db)) -> dict:
    booking = create_booking(db, payload.travel_date, payload.mobile_number, payload.seats)
    return serialize_booking(booking)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str, db: Session = Depends(get_db)) -> dict:
    booking = fetch_booking_or_404(db, booking_id)
    return serialize_booking(booking)


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking_endpoint(booking_id: str, payload: BookingPayload, db: Session = Depends(get_db)) -> dict:
    booking = update_booking(db, booking_id, payload.travel_date, payload.mobile_number, payload.seats)
    return serialize_booking(booking)


@router.patch("/{booking_id}/boarding", response_model=BookingResponse)
def update_boarding_status(
    booking_id: str,
    payload: BoardingStatusPayload,
    db: Session = Depends(get_db),
) -> dict:
    booking = toggle_boarding_status(db, booking_id, payload.is_boarded)
    return serialize_booking(booking)
