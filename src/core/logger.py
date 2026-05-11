"""
logger.py — Структуроване логування у JSON-форматі.

Забезпечує єдиний формат логів для всієї системи.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Форматтер логів у JSON-формат."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(
    name: str = "library_system",
    level: str = "INFO",
    log_file: str | None = "logs/library.log",
) -> logging.Logger:
    """Налаштувати структурований логер.

    Args:
        name: Ім'я логера.
        level: Рівень логування (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Шлях до файлу логів (None — тільки консоль).

    Returns:
        Налаштований логер.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    json_formatter = JSONFormatter()

    # Консольний handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # Файловий handler
    if log_file:
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "library_system") -> logging.Logger:
    """Отримати існуючий логер або створити новий."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
