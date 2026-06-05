"""Logging helpers for local development."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a standard library logger for the requested namespace."""
    return logging.getLogger(name)
