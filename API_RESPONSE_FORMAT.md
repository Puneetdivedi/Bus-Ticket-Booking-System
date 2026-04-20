# API Response Format Specification

## Overview

All API responses follow a consistent JSON structure for predictability and easier client integration.

## Success Response Format

### Standard Response
```json
{
  "status": "success",
  "data": {
    "booking_id": "123e4567-e89b-12d3-a456-426614174000",
    "travel_date": "2024-12-25",
    "mobile_number": "9876543210",
    "seats": ["A1", "A2"],
    "is_boarded": false,
    "created_at": "2024-12-20T10:30:00Z"
  },
  "meta": {
    "request_id": "req-123456",
    "timestamp": "2024-12-20T10:35:00Z",
    "version": "1.1.5"
  }
}
```

### List Response with Pagination
```json
{
  "status": "success",
  "data": {
    "items": [...],
    "total": 100,
    "skip": 0,
    "limit": 50,
    "has_more": true
  },
  "meta": {
    "request_id": "req-123456",
    "timestamp": "2024-12-20T10:35:00Z"
  }
}
```

## Error Response Format

### Standard Error
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Seat(s) already booked: A1, A2",
    "details": {
      "conflicting_seats": ["A1", "A2"]
    }
  },
  "meta": {
    "request_id": "req-123456",
    "timestamp": "2024-12-20T10:35:00Z"
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (e.g., double booking) |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Permission denied |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Headers

All responses include:
- `X-Request-ID`: Unique request identifier for tracing
- `X-Process-Time`: Response time in milliseconds
- `Content-Type`: application/json
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block

## Examples

### Create Booking
**Request:**
```bash
POST /api/bookings
Content-Type: application/json

{
  "travel_date": "2024-12-25",
  "mobile_number": "9876543210",
  "seats": ["A1", "A2"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "booking_id": "uuid-here",
    "travel_date": "2024-12-25",
    "mobile_number": "9876543210",
    "seats": ["A1", "A2"],
    "is_boarded": false
  }
}
```

### Booking Conflict Error
**Request:**
```bash
POST /api/bookings
{
  "travel_date": "2024-12-25",
  "mobile_number": "9876543210",
  "seats": ["A1"]  # Already booked
}
```

**Response:**
```json
{
  "status": "error",
  "error": {
    "code": "CONFLICT",
    "message": "Seat(s) already booked: A1",
    "details": {
      "conflicting_seats": ["A1"]
    }
  }
}
```

## Versioning

API versioning is handled through the base URL and version header:
- Current API Version: 1.1.0
- All responses include the API version in metadata

## Backward Compatibility

- Existing endpoints remain unchanged
- New fields are added with backward compatibility
- Deprecated fields are marked and supported for 2+ versions
