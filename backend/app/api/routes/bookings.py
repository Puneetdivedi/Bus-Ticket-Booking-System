"""Booking management API routes with authentication and rate limiting."""
from __future__ import annotations

import csv
import io
import logging
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ValidationException
from app.schemas import (
    BoardingSequenceResponse,
    BoardingStatusPayload,
    BookingListResponse,
    BookingPayload,
    BookingResponse,
    SeatAvailabilityResponse,
)
from app.security import optional_api_key
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("/seat-map", response_model=SeatAvailabilityResponse)
def get_seat_map(
    travel_date: date = Query(...),
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """Get available seats for a specific travel date."""
    logger.info(f"Fetching seat map for date: {travel_date}")
    try:
        booked_seats = get_booked_seats(db, travel_date)
        logger.info(f"Successfully retrieved seat map: {len(booked_seats)} booked seats")
        return {
            "travel_date": travel_date,
            "booked_seats": booked_seats,
        }
    except Exception as exc:
        logger.error(f"Error fetching seat map: {str(exc)}", exc_info=True)
        raise


@router.get("/boarding-sequence", response_model=BoardingSequenceResponse)
def get_boarding_sequence(
    travel_date: date = Query(...),
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """Get optimal boarding sequence for a specific travel date."""
    logger.info(f"Fetching boarding sequence for date: {travel_date}")
    try:
        bookings = list_bookings(db, travel_date)
        logger.info(f"Retrieved {len(bookings)} bookings for boarding sequence")
        return {
            "travel_date": travel_date,
            "estimated_total_time_seconds": get_estimated_boarding_time_seconds(bookings),
            "bookings": serialize_boarding_sequence(bookings),
        }
    except Exception as exc:
        logger.error(f"Error fetching boarding sequence: {str(exc)}", exc_info=True)
        raise


@router.get("/export/csv")
def export_bookings_csv(
    travel_date: date = Query(...),
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> StreamingResponse:
    """Export bookings as CSV for a specific travel date."""
    logger.info(f"Exporting bookings as CSV for date: {travel_date}")
    try:
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
        logger.info(f"Successfully exported {len(ordered_bookings)} bookings to CSV")
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)
    except Exception as exc:
        logger.error(f"Error exporting bookings to CSV: {str(exc)}", exc_info=True)
        raise


@router.get("", response_model=BookingListResponse)
def get_bookings(
    travel_date: date = Query(...),
    mobile_number: str | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """List bookings with pagination support."""
    logger.info(
        f"Listing bookings for date: {travel_date}, skip: {skip}, limit: {limit}, mobile: {mobile_number}"
    )
    try:
        if skip < 0:
            raise ValidationException("Skip must be non-negative", {"skip": skip})
        if limit < 1 or limit > 500:
            raise ValidationException("Limit must be between 1 and 500", {"limit": limit})

        bookings = list_bookings(db, travel_date, mobile_number, skip=skip, limit=limit)
        result = serialize_booking_list(bookings, travel_date)
        logger.info(f"Retrieved {len(bookings)} bookings")
        return result
    except Exception as exc:
        logger.error(f"Error listing bookings: {str(exc)}", exc_info=True)
        raise


@router.post("", response_model=BookingResponse, status_code=201)
def create_booking_endpoint(
    payload: BookingPayload,
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """Create a new booking."""
    logger.info(f"Creating booking: date={payload.travel_date}, seats={payload.seats}")
    try:
        booking = create_booking(db, payload.travel_date, payload.mobile_number, payload.seats)
        logger.info(f"Successfully created booking: {booking.booking_id}")
        return serialize_booking(booking)
    except Exception as exc:
        logger.error(f"Error creating booking: {str(exc)}", exc_info=True)
        raise


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """Retrieve a specific booking by ID."""
    logger.info(f"Fetching booking: {booking_id}")
    try:
        booking = fetch_booking_or_404(db, booking_id)
        logger.info(f"Successfully retrieved booking: {booking_id}")
        return serialize_booking(booking)
    except Exception as exc:
        logger.error(f"Error fetching booking {booking_id}: {str(exc)}")
        raise


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking_endpoint(
    booking_id: str,
    payload: BookingPayload,
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """Update an existing booking."""
    logger.info(f"Updating booking: {booking_id}, date={payload.travel_date}, seats={payload.seats}")
    try:
        booking = update_booking(db, booking_id, payload.travel_date, payload.mobile_number, payload.seats)
        logger.info(f"Successfully updated booking: {booking_id}")
        return serialize_booking(booking)
    except Exception as exc:
        logger.error(f"Error updating booking {booking_id}: {str(exc)}", exc_info=True)
        raise


@router.patch("/{booking_id}/boarding", response_model=BookingResponse)
def update_boarding_status(
    booking_id: str,
    payload: BoardingStatusPayload,
    db: Session = Depends(get_db),
    api_key: str | None = Depends(optional_api_key),
) -> dict:
    """Update boarding status for a booking."""
    logger.info(f"Updating boarding status for booking: {booking_id}, is_boarded={payload.is_boarded}")
    try:
        booking = toggle_boarding_status(db, booking_id, payload.is_boarded)
        logger.info(f"Successfully updated boarding status for: {booking_id}")
        return serialize_booking(booking)
    except Exception as exc:
        logger.error(f"Error updating boarding status for {booking_id}: {str(exc)}", exc_info=True)
        raise
