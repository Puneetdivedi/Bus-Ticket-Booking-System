# Development Guide

## Local Development Setup

### Prerequisites
- Python 3.10+ with pip
- Node.js 18+ with npm
- Git
- Virtual environment tool (venv, conda, or pipenv)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```

5. **Run development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access API documentation**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Access application**
   - http://localhost:5173

## Code Structure

### Backend

```
backend/app/
├── api/
│   └── routes/
│       └── bookings.py           # API endpoint definitions
├── services/
│   ├── bookings.py               # Booking business logic
│   ├── boarding.py               # Boarding sequence algorithm
│   └── booking_rules.py          # Validation rules
├── database.py                   # Database configuration
├── main.py                       # FastAPI application
├── models.py                     # SQLAlchemy ORM models
├── schemas.py                    # Pydantic validation schemas
├── settings.py                   # Configuration management
├── logger.py                     # Logging setup
├── security.py                   # Authentication helpers
├── middleware.py                 # Custom middleware
└── exceptions.py                 # Exception classes
```

### Frontend

```
frontend/src/
├── api/
│   └── client.js                 # Axios HTTP client
├── components/
│   ├── BookingForm.jsx           # Booking creation form
│   ├── BookingTable.jsx          # Booking list table
│   ├── SeatLayout.jsx            # Seat grid visualization
│   ├── BoardingSequencePanel.jsx # Boarding info display
│   ├── ConfirmationModal.jsx     # Confirmation dialog
│   ├── SeatLegend.jsx            # Seat status legend
│   └── SeatLegend.jsx            # Boarding sequen panel
└── utils/
    ├── seats.js                  # Seat utilities
    └── format.js                 # Formatting utilities
```

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Pydantic schema** in `backend/app/schemas.py`
   ```python
   class MyRequestSchema(BaseModel):
       field: str
   ```

2. **Add SQLAlchemy model** in `backend/app/models.py` (if needed)

3. **Create business logic** in `backend/app/services/`

4. **Define route** in `backend/app/api/routes/bookings.py`
   ```python
   @router.get("/my-endpoint")
   def my_endpoint(db: Session = Depends(get_db)):
       return {"result": "success"}
   ```

### Modifying Database Schema

1. **Update** `backend/app/models.py`
2. **Update** `database/schema.sql`
3. **Delete** old database files
4. **Restart** backend to recreate tables

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality Checks

```bash
# Backend
cd backend

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/

# Frontend
cd frontend

# Lint code
npm run lint

# Format code
npm run format
```

## Debugging

### Backend Debug Logging

Set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

Or in .env:
```
LOG_LEVEL=DEBUG
```

### Frontend React DevTools

1. Install React DevTools browser extension
2. Open DevTools (F12)
3. Use React tab to inspect components

### Database Inspection

```bash
# SQLite
sqlite3 database/bus_booking.db

# PostgreSQL
psql -U user -d bus_booking -h localhost
```

## Deployment

### Docker Build

```bash
# Backend
docker build -f Dockerfile.backend -t bus-booking-api:latest .

# Frontend
docker build -f Dockerfile.frontend -t bus-booking-web:latest .
```

### Environment Configuration for Production

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@db:5432/bus_booking
LOG_LEVEL=WARNING
API_KEY_ENABLED=true
API_KEY=secure-api-key-here
CORS_ORIGINS=https://yourdomain.com
```

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.10+

# Check port availability
lsof -i :8000  # (macOS/Linux)
netstat -ano | findstr :8000  # (Windows)

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend compilation errors

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
npm run dev
```

### Database errors

```bash
# Reset database (SQLite)
rm database/bus_booking.db

# Recreate tables
cd backend && python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"
```

## Best Practices

### Code Style
- Use type hints in Python
- Follow PEP 8 conventions
- Use Prettier for JavaScript formatting

### Commits
- Write meaningful commit messages
- Reference issues when applicable
- Keep commits focused

### Documentation
- Add docstrings to functions
- Update README for significant changes
- Document API changes in API docs

## Performance Optimization

### Backend
- Use database indexes for frequent queries
- Implement caching for read-heavy operations
- Use connection pooling for databases

### Frontend
- Lazy load components
- Optimize images
- Use React.memo for expensive components

## Security Checklist

- [ ] API keys are not committed to repository
- [ ] Environment variables are properly configured
- [ ] CORS origins are restricted
- [ ] Input validation is implemented
- [ ] SQL injection prevention (SQLAlchemy parameterized queries)
- [ ] XSS protection enabled
- [ ] CSRF tokens for state-changing operations
- [ ] Rate limiting configured
- [ ] Logging sensitive data is avoided

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
