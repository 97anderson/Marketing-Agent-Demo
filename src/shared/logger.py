"""Logging Configuration.

This module sets up structured logging for the application.
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from src.shared.config import get_settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields.

    Adds application-specific fields to log records.
    """

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any]
    ) -> None:
        """Add custom fields to the log record.

        Args:
            log_record: The log record dictionary to modify.
            record: The original log record.
            message_dict: The message dictionary.
        """
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName

        # Add application context
        settings = get_settings()
        log_record["environment"] = settings.environment


def setup_logging() -> None:
    """Configure application logging.

    Sets up structured JSON logging for production and human-readable
    logging for development.
    """
    settings = get_settings()

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)

    # Use JSON formatter for production, simple formatter for development
    if settings.is_production:
        formatter = CustomJsonFormatter(
            "%(asctime)s %(level)s %(logger)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    logging.info(f"Logging configured with level: {settings.log_level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: The name of the logger (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
