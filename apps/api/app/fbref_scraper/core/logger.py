"""Logging configuration for FBRef scrapers."""

import logging
from typing import Optional, Dict
from .scraper_config import get_log_level, get_log_format, get_log_date_format


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    def __init__(self, fmt: Optional[str] = None) -> None:
        """Initialize the colored formatter."""
        super().__init__(fmt)
        self.colors: Dict[str, str] = {
            'WARNING': '\033[33m',
            'ERROR': '\033[31m',
            'RESET': '\033[0m'
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with colors."""
        log_color = self.colors.get(record.levelname, '')
        reset_color = self.colors['RESET'] if log_color else ''
        
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        return super().format(record)


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Set up a logger with colored console output."""
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)
    log_level = get_log_level().upper()
    logger.setLevel(getattr(logging, log_level))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    formatter = ColoredFormatter(get_log_format())
    formatter.datefmt = get_log_date_format()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance."""
    return setup_logger(name)
