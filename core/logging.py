"""Centralised structured logging configuration for the application.

This module exposes `configure_logging` to initialise the root logger and
`get_logger` as a convenience wrapper.
"""

import logging
import os
from typing import Optional


def configure_logging(level: Optional[str] = None) -> None:
    """Configure application logging.

    Uses `LOG_LEVEL` env var as default (INFO).
    """
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    fmt = "%(asctime)s %(levelname)s [%(name)s:%(module)s] %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S%z"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    root = logging.getLogger()
    # avoid adding multiple handlers when called repeatedly
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
