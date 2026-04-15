from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_PATH = DATABASE_DIR / "bus_booking.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}")

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

raw_cors_origins = os.getenv("CORS_ORIGINS")
CORS_ORIGINS = (
    [origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()]
    if raw_cors_origins
    else DEFAULT_CORS_ORIGINS
)
