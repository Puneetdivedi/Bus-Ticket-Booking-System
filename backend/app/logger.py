"""Structured logging configuration."""
import json
import logging
import sys
from datetime import datetime
from typing import Any

from app.settings import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Text formatter for human-readable logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        return (
            f"[{self.formatTime(record, self.datefmt)}] "
            f"{record.levelname} - {record.name}:{record.funcName}:{record.lineno} - "
            f"{record.getMessage()}"
        )


def setup_logging() -> None:
    """Configure structured logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Select formatter based on configuration
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if configured)
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class RequestLogger:
    """Helper class for adding extra data to log records."""

    @staticmethod
    def add_extra(logger: logging.Logger, message: str, **kwargs: Any) -> None:
        """Log with extra context data."""
        extra = {"extra_data": kwargs}
        logger.info(message, extra=extra)
