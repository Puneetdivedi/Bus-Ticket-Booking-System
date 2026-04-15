from __future__ import annotations

from app.models import Booking
from app.services.booking_rules import get_row_number, sort_seats


def get_booking_max_row(booking: Booking) -> int:
    seat_numbers = [seat.seat_number for seat in booking.seat_assignments]
    return max(get_row_number(seat_number) for seat_number in seat_numbers)


def get_optimal_boarding_sequence(bookings: list[Booking]) -> list[Booking]:
    return sorted(
        bookings,
        key=lambda booking: (
            -get_booking_max_row(booking),
            booking.created_at,
            booking.booking_id,
        ),
    )


def get_estimated_boarding_time_seconds(bookings: list[Booking]) -> int:
    return 60 if bookings else 0


def serialize_boarding_sequence(bookings: list[Booking]) -> list[dict]:
    sequence = []
    for index, booking in enumerate(get_optimal_boarding_sequence(bookings), start=1):
        seats = sort_seats([seat.seat_number for seat in booking.seat_assignments])
        sequence.append(
            {
                "sequence_number": index,
                "booking_id": booking.booking_id,
                "mobile_number": booking.mobile_number,
                "seats": seats,
                "max_row": max(get_row_number(seat) for seat in seats),
                "is_boarded": booking.is_boarded,
            }
        )
    return sequence
