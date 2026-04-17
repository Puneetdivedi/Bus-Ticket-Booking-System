# Bus Ticket Booking System

A modern, production-ready full-stack application for managing bus ticket bookings with an optimized conductor boarding workflow.

**Live Demo**: [View System Architecture](#architecture)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Booking Management
- ✅ Real-time seat availability checking
- ✅ Book up to 6 seats per mobile number per journey
- ✅ Edit and cancel bookings
- ✅ Journey-date specific bookings
- ✅ Mobile number validation

### Passenger Management
- ✅ Optimized boarding sequence (farthest-seat-first algorithm)
- ✅ Boarding status tracking
- ✅ CSV export for conductor workflow
- ✅ Mobile number-based search

### UI/UX
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Visual 2×4 seat layout (15 rows = 60 seats)
- ✅ Real-time seat state updates
- ✅ Intuitive booking confirmation

### Security & Performance
- ✅ API key authentication
- ✅ Request logging and monitoring
- ✅ Database-level seat collision prevention
- ✅ Pagination support
- ✅ Security headers (CORS, X-Frame-Options, etc.)
- ✅ Structured logging (JSON/Text)

## 🛠 Tech Stack

### Frontend
- **React 18.3** - UI library
- **Vite 6.0** - Build tool & dev server
- **Tailwind CSS 3.4** - Utility-first styling
- **Axios 1.7** - HTTP client

### Backend
- **FastAPI 0.115** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM
- **Pydantic 2.10** - Data validation
- **Uvicorn 0.32** - ASGI server

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **SQLite/PostgreSQL** - Database
- **GitHub** - Version control

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- Git
- Docker (optional, for containerized deployment)

### Option 1: Local Development

#### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate
# or (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (new terminal)
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start dev server
npm run dev
```

#### Access Application
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health

### Option 2: Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

## 📐 Architecture

### System Components

```
┌─────────────────────────────────────────┐
│           Frontend (React)              │
│  - Booking Interface                    │
│  - Seat Selection                       │
│  - Booking Management                   │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────┐
│         API Gateway (FastAPI)           │
│  - CORS Middleware                      │
│  - Request Logging                      │
│  - Authentication                       │
│  - Rate Limiting                        │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
    ┌────────────┐      ┌─────────────┐
    │  Services  │      │ Exceptions  │
    │  - Booking │      │  & Handlers │
    │  - Boarding│      └─────────────┘
    │  - Rules   │
    └────────────┘
        ▼
    ┌────────────────────────┐
    │  SQLAlchemy ORM        │
    │  - Models              │
    │  - Validation          │
    └───────────┬────────────┘
                ▼
    ┌────────────────────────┐
    │   SQLite Database      │
    │   (PostgreSQL ready)   │
    └────────────────────────┘
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
All endpoints support optional API key authentication:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/bookings
```

### Endpoints

#### 1. Get Available Seats
```http
GET /bookings/seat-map?travel_date=2024-12-25
```

**Response:**
```json
{
  "travel_date": "2024-12-25",
  "booked_seats": ["A1", "A2", "B3"]
}
```

#### 2. Get Boarding Sequence
```http
GET /bookings/boarding-sequence?travel_date=2024-12-25
```

**Response:**
```json
{
  "travel_date": "2024-12-25",
  "estimated_total_time_seconds": 300,
  "bookings": [
    {
      "sequence_number": 1,
      "booking_id": "uuid-1",
      "seats": ["D15", "D14"],
      "mobile_number": "9876543210",
      "is_boarded": false
    }
  ]
}
```

#### 3. Create Booking
```http
POST /bookings
Content-Type: application/json

{
  "travel_date": "2024-12-25",
  "mobile_number": "9876543210",
  "seats": ["A1", "A2"]
}
```

#### 4. List Bookings (with Pagination)
```http
GET /bookings?travel_date=2024-12-25&skip=0&limit=50&mobile_number=9876543210
```

#### 5. Get Single Booking
```http
GET /bookings/{booking_id}
```

#### 6. Update Booking
```http
PUT /bookings/{booking_id}
Content-Type: application/json

{
  "travel_date": "2024-12-25",
  "mobile_number": "9876543210",
  "seats": ["A1", "A2", "A3"]
}
```

#### 7. Update Boarding Status
```http
PATCH /bookings/{booking_id}/boarding
Content-Type: application/json

{
  "is_boarded": true
}
```

#### 8. Export Bookings to CSV
```http
GET /bookings/export/csv?travel_date=2024-12-25
```

#### 9. Health Check
```http
GET /health
```

### Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "message": "Seat(s) already booked: A1, A2",
    "code": "CONFLICT",
    "details": {
      "conflicting_seats": ["A1", "A2"]
    }
  }
}
```

**Common Status Codes:**
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `409` - Conflict (seat already booked)
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## 🔧 Development

### Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── bookings.py          # API endpoints
│   ├── services/
│   │   ├── bookings.py              # Business logic
│   │   ├── boarding.py              # Boarding algorithm
│   │   └── booking_rules.py         # Validation rules
│   ├── database.py                  # Database setup
│   ├── main.py                      # FastAPI app
│   ├── models.py                    # SQLAlchemy models
│   ├── schemas.py                   # Pydantic schemas
│   ├── settings.py                  # Configuration
│   ├── logger.py                    # Logging setup
│   ├── security.py                  # Auth utilities
│   ├── middleware.py                # Custom middleware
│   └── exceptions.py                # Exception handlers
├── requirements.txt                 # Dependencies
└── .env.example                     # Environment template

frontend/
├── src/
│   ├── components/                  # React components
│   ├── api/
│   │   └── client.js               # Axios config
│   └── utils/                       # Helper functions
├── package.json
├── vite.config.js
└── tailwind.config.js

database/
└── schema.sql                       # Database schema
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend
cd backend
flake8 app/
black app/
mypy app/

# Frontend
cd frontend
npm run lint
npm run format
```

## 🐳 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment Variables

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:password@db:5432/bus_booking
LOG_LEVEL=WARNING
API_KEY=your-secure-api-key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Database Migration (SQLite → PostgreSQL)

```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost/bus_booking

# Recreate tables
python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"
```

## ⚙️ Configuration

### Environment Variables

See [backend/.env.example](backend/.env.example) and [frontend/.env.example](frontend/.env.example) for all available options.

**Key Settings:**
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed frontend origins
- `API_KEY_ENABLED` - Enable/disable API key validation
- `API_KEY` - Secret API key
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT` - Environment name (development, staging, production)

## 🆘 Troubleshooting

### Backend Issues

**Issue: "Database is locked"**
- Ensure only one process is accessing SQLite
- Switch to PostgreSQL for concurrent access

**Issue: "Connection refused" from frontend**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS_ORIGINS in .env

### Frontend Issues

**Issue: "API requests fail"**
- Verify `VITE_API_BASE_URL` points to correct backend
- Check browser console for CORS errors

## 📝 Versioning

- **API Version**: v1.0.0
- **Frontend Version**: v1.0.0
- **Backend Version**: v1.0.0

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For issues and questions:
- Open a GitHub Issue
- Check existing documentation
- Review API docs at `/api/docs`

---

**Last Updated:** 2024  
**Status**: ✅ Production Ready

- Node.js 18+
- Python 3.11+

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell maps `python` to a Windows Store stub, install Python and reopen the terminal. If your shell blocks `npm`, use `npm.cmd` instead of `npm`.

Backend runs on `http://localhost:8000`.

### Frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

If your PowerShell execution policy blocks `npm`, use:

```powershell
npm.cmd install
npm.cmd run dev
```

Frontend runs on `http://localhost:5173`.

## Environment

Create `frontend/.env` from `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The SQLite file is created automatically at `database/bus_booking.db`.

## API Endpoints

- `GET /api/health` - health check
- `GET /api/bookings/seat-map?travel_date=YYYY-MM-DD` - booked seats for a date
- `GET /api/bookings?travel_date=YYYY-MM-DD&mobile_number=9999` - booking list with optional mobile search
- `POST /api/bookings` - create booking
- `GET /api/bookings/{booking_id}` - fetch one booking
- `PUT /api/bookings/{booking_id}` - update booking before travel date
- `PATCH /api/bookings/{booking_id}/boarding` - mark passenger group as boarded or not boarded
- `GET /api/bookings/boarding-sequence?travel_date=YYYY-MM-DD` - optimal boarding order
- `GET /api/bookings/export/csv?travel_date=YYYY-MM-DD` - export daily list

## Database Schema

The ORM models live in `backend/app/models.py` and the SQL reference schema is in `database/schema.sql`.

Core tables:

- `bookings`
  - `booking_id`
  - `travel_date`
  - `mobile_number`
  - `is_boarded`
  - `created_at`
  - `updated_at`
- `booking_seats`
  - `booking_id`
  - `travel_date`
  - `seat_number`
  - unique constraint on `(travel_date, seat_number)`

## Boarding Algorithm

Required function behavior:

1. Convert each seat to its row number.
2. For each booking, compute the maximum row number from its booked seats.
3. Sort bookings in descending order of that maximum row.
4. Board from farthest row to nearest row.

Example:

- Booking A -> `A1` -> row `1`
- Booking B -> `A7` -> row `7`
- Booking C -> `A15` -> row `15`

Optimal order:

- Booking C
- Booking B
- Booking A

Implementation lives in:

- `backend/app/services/boarding.py`

## Assumptions

- Same-day booking is allowed, but past dates are rejected.
- Editing is allowed only before the booking's current travel date.
- Boarding time follows the assessment assumption that far-to-near ordering avoids blocking and gives the minimum theoretical completion time.

## Submission Notes

- Frontend and backend are intentionally separated for clean deployment boundaries.
- Business rules are enforced in both the UI and the API, with the database acting as the final guard against duplicate seat allocation.
- The seat map uses hash/set lookups for efficient availability checks and minimal render work.
#   U p d a t e d :   0 4 / 1 7 / 2 0 2 6   1 5 : 0 3 : 5 5  
 