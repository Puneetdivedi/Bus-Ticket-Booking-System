from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.services.booking_rules import VALID_SEATS, is_past_date, sort_seats


class BookingPayload(BaseModel):
    travel_date: date
    mobile_number: str = Field(min_length=10, max_length=10)
    seats: list[str]

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Mobile number must contain exactly 10 digits.")
        return value

    @field_validator("travel_date")
    @classmethod
    def validate_travel_date(cls, value: date) -> date:
        if is_past_date(value):
            raise ValueError("Past travel dates are not allowed.")
        return value

    @field_validator("seats")
    @classmethod
    def validate_seats(cls, value: list[str]) -> list[str]:
        normalized = [seat.strip().upper() for seat in value]
        unique_seats = list(dict.fromkeys(normalized))

        if not unique_seats:
            raise ValueError("Select at least one seat.")
        if len(unique_seats) > 6:
            raise ValueError("A booking cannot contain more than 6 seats.")
        invalid_seats = [seat for seat in unique_seats if seat not in VALID_SEATS]
        if invalid_seats:
            raise ValueError(f"Invalid seat(s): {', '.join(invalid_seats)}.")
        if len(unique_seats) != len(normalized):
            raise ValueError("Duplicate seats are not allowed.")
        return sort_seats(unique_seats)


class BoardingStatusPayload(BaseModel):
    is_boarded: bool


class BookingResponse(BaseModel):
    booking_id: str
    travel_date: date
    mobile_number: str
    seats: list[str]
    passenger_count: int
    is_boarded: bool
    can_edit: bool
    max_row: int
    sequence_number: int | None = None
    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseModel):
    travel_date: date
    total_bookings: int
    total_passengers: int
    bookings: list[BookingResponse]


class SeatAvailabilityResponse(BaseModel):
    travel_date: date
    booked_seats: list[str]


class BoardingSequenceItem(BaseModel):
    sequence_number: int
    booking_id: str
    mobile_number: str
    seats: list[str]
    max_row: int
    is_boarded: bool


class BoardingSequenceResponse(BaseModel):
    travel_date: date
    estimated_total_time_seconds: int
    bookings: list[BoardingSequenceItem]
