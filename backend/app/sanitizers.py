"""Input sanitization and validation utilities."""
import re
from typing import Any


class Sanitizer:
    """Utilities for sanitizing user input."""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            raise ValueError("Expected string")
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Truncate to max length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove any null characters
        value = value.replace("\x00", "")
        
        return value

    @staticmethod
    def sanitize_mobile_number(mobile: str) -> str:
        """Sanitize and validate mobile number."""
        # Remove non-digit characters
        mobile = re.sub(r"\D", "", mobile)
        
        # Check length
        if len(mobile) != 10:
            raise ValueError("Mobile number must be 10 digits")
        
        return mobile

    @staticmethod
    def sanitize_seat_number(seat: str) -> str:
        """Sanitize and validate seat number."""
        seat = seat.strip().upper()
        
        # Validate seat format (e.g., A1, B2, D15)
        if not re.match(r"^[A-D]\d{1,2}$", seat):
            raise ValueError(f"Invalid seat format: {seat}")
        
        return seat

    @staticmethod
    def escape_csv_field(field: Any) -> str:
        """Escape CSV field for safe export."""
        field = str(field)
        
        # Escape quotes
        if '"' in field:
            field = field.replace('"', '""')
        
        # Quote if contains special characters
        if any(c in field for c in [",", '"', "\n", "\r"]):
            field = f'"{field}"'
        
        return field

    @staticmethod
    def sanitize_date_string(date_str: str) -> str:
        """Sanitize date string input."""
        date_str = date_str.strip()
        
        # Simple validation - should be YYYY-MM-DD format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            raise ValueError("Invalid date format. Expected YYYY-MM-DD")
        
        return date_str


class InputValidator:
    """Advanced input validation."""

    @staticmethod
    def validate_seat_list(seats: list[str], max_seats: int = 6) -> list[str]:
        """Validate and sanitize seat list."""
        if not isinstance(seats, list):
            raise ValueError("Seats must be a list")
        
        if len(seats) == 0:
            raise ValueError("At least one seat must be selected")
        
        if len(seats) > max_seats:
            raise ValueError(f"Maximum {max_seats} seats allowed per booking")
        
        # Check for duplicates
        unique_seats = set()
        sanitized = []
        
        for seat in seats:
            try:
                sanitized_seat = Sanitizer.sanitize_seat_number(seat)
                if sanitized_seat in unique_seats:
                    raise ValueError(f"Duplicate seat: {sanitized_seat}")
                unique_seats.add(sanitized_seat)
                sanitized.append(sanitized_seat)
            except ValueError as e:
                raise ValueError(f"Invalid seat {seat}: {str(e)}")
        
        return sanitized

    @staticmethod
    def validate_mobile_number(mobile: str) -> str:
        """Validate mobile number."""
        try:
            return Sanitizer.sanitize_mobile_number(mobile)
        except ValueError as e:
            raise ValueError(f"Invalid mobile number: {str(e)}")

    @staticmethod
    def validate_travel_date(travel_date: str) -> str:
        """Validate travel date."""
        try:
            return Sanitizer.sanitize_date_string(travel_date)
        except ValueError as e:
            raise ValueError(f"Invalid travel date: {str(e)}")
