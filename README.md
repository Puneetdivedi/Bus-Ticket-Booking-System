# Bus Ticket Booking System

Full-stack bus conductor console built with React, Tailwind CSS, FastAPI, SQLAlchemy, and SQLite.

## Tech Stack

- Frontend: React with hooks, Vite, Tailwind CSS, Axios
- Backend: FastAPI, REST APIs, SQLAlchemy ORM
- Database: SQLite

## Project Structure

```text
.
|-- backend
|   |-- app
|   |   |-- api/routes
|   |   |-- services
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- main.py
|   |   |-- models.py
|   |   `-- schemas.py
|   `-- requirements.txt
|-- database
|   `-- schema.sql
|-- frontend
|   |-- src
|   |   |-- api
|   |   |-- components
|   |   `-- utils
|   |-- package.json
|   `-- tailwind.config.js
`-- README.md
```

## Features

- Screen 1: book and edit bookings with a visual 2 x 2 seat layout for 15 rows
- Screen 2: travel-date-wise booking list with call links, boarding status toggle, and edit entry point
- Seat states: available, selected, and booked
- Validations for past dates, mobile number format, empty seat selection, duplicate seats, max 6 seats per mobile per day, and double booking
- Backend conflict checks plus database-level unique seat protection
- Boarding sequence calculated and displayed using the required farthest-seat-first algorithm
- Bonus support for mobile search and CSV export

## Setup

### Prerequisites

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
