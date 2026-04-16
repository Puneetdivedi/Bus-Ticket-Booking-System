"""Tests for booking endpoints."""
import pytest
from datetime import date, timedelta


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_seat_map(client):
    """Test get seat map endpoint."""
    tomorrow = date.today() + timedelta(days=1)
    response = client.get(f"/api/bookings/seat-map?travel_date={tomorrow}")
    assert response.status_code == 200
    data = response.json()
    assert "travel_date" in data
    assert "booked_seats" in data
    assert isinstance(data["booked_seats"], list)


def test_create_booking(client):
    """Test create booking endpoint."""
    tomorrow = date.today() + timedelta(days=1)
    payload = {
        "travel_date": str(tomorrow),
        "mobile_number": "9876543210",
        "seats": ["A1", "A2"],
    }
    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "booking_id" in data
    assert data["mobile_number"] == "9876543210"
    assert len(data["seats"]) == 2


def test_get_booking(client):
    """Test get booking endpoint."""
    tomorrow = date.today() + timedelta(days=1)
    # Create booking
    payload = {
        "travel_date": str(tomorrow),
        "mobile_number": "9876543210",
        "seats": ["A1"],
    }
    create_response = client.post("/api/bookings", json=payload)
    booking_id = create_response.json()["booking_id"]

    # Get booking
    response = client.get(f"/api/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json()["booking_id"] == booking_id


def test_list_bookings(client):
    """Test list bookings endpoint."""
    tomorrow = date.today() + timedelta(days=1)
    response = client.get(f"/api/bookings?travel_date={tomorrow}&limit=50")
    assert response.status_code == 200
    data = response.json()
    assert "travel_date" in data
    assert "bookings" in data


def test_invalid_mobile_number(client):
    """Test validation for invalid mobile number."""
    tomorrow = date.today() + timedelta(days=1)
    payload = {
        "travel_date": str(tomorrow),
        "mobile_number": "invalid",
        "seats": ["A1"],
    }
    response = client.post("/api/bookings", json=payload)
    assert response.status_code == 422  # Validation error


def test_past_date_validation(client):
    """Test validation for past dates."""
    past_date = date.today() - timedelta(days=1)
    payload = {
        "travel_date": str(past_date),
        "mobile_number": "9876543210",
        "seats": ["A1"],
    }
    response = client.post("/api/bookings", json=payload)
    assert response.status_code in [400, 422]  # Validation error


def test_pagination(client):
    """Test pagination parameters."""
    tomorrow = date.today() + timedelta(days=1)
    response = client.get(f"/api/bookings?travel_date={tomorrow}&skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "bookings" in data


def test_invalid_pagination_limit(client):
    """Test invalid pagination limit."""
    tomorrow = date.today() + timedelta(days=1)
    response = client.get(f"/api/bookings?travel_date={tomorrow}&skip=0&limit=1000")
    assert response.status_code in [400, 422]  # Validation error - limit > 500
