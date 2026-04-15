from __future__ import annotations

from datetime import date

SEAT_COLUMNS = ("A", "B", "C", "D")
SEAT_ROWS = tuple(range(1, 16))
VALID_SEATS = {f"{column}{row}" for column in SEAT_COLUMNS for row in SEAT_ROWS}


def sort_seats(seats: list[str]) -> list[str]:
    return sorted(seats, key=lambda seat: (get_row_number(seat), seat[0]))


def get_row_number(seat: str) -> int:
    return int(seat[1:])


def is_past_date(travel_date: date) -> bool:
    return travel_date < date.today()
