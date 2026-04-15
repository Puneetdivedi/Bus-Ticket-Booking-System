from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.bookings import router as bookings_router
from app.config import CORS_ORIGINS
from app.database import Base, engine

WEBAPP_DIR = Path(__file__).resolve().parents[2] / "webapp"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Bus Ticket Booking System API",
    version="1.0.0",
    summary="Booking and boarding APIs for the bus conductor workflow.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings_router)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


if WEBAPP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
