"""Logging configuration for Atlas Cursor Studio."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggerService:
    """Configures a rotating log file for the application."""

    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.log_path = log_dir / "atlas_cursor_studio.log"
        self._configured = False

    def configure(self) -> None:
        """Configure the root logger once for the application session."""
        if self._configured:
            return

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        self._configured = True

    def get_logger(self, name: str) -> logging.Logger:
        """Return a named logger instance."""
        return logging.getLogger(name)
