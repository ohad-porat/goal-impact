"""Configuration management for FBRef scrapers."""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass
class ScraperConfig:
    """Configuration class for FBRef scrapers."""
    SELECTED_NATIONS: Optional[List[str]] = None
    YEAR_RANGE: Tuple[int, int] = (1992, 2024)
    RATE_LIMITS: Optional[Dict[str, int]] = None
    DEBUG: bool = True
    REQUEST_TIMEOUT: int = 60
    FBREF_BASE_URL: str = 'https://fbref.com'
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'
    
    def __post_init__(self) -> None:
        """Initialize default values after dataclass creation."""
        if self.SELECTED_NATIONS is None:
            self.SELECTED_NATIONS = ['Brazil', 'England', 'France', 'Germany', 'Italy', 'Netherlands', 'Portugal', 'Spain']
        
        if self.RATE_LIMITS is None:
            self.RATE_LIMITS = {
                'default': 7,
                'heavy': 10,
                'light': 6
            }


config = ScraperConfig()


def get_config() -> ScraperConfig:
    """Get the current scraper configuration."""
    return config


def update_config(**kwargs) -> None:
    """Update configuration values."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")


def get_selected_nations() -> List[str]:
    """Get the list of selected nations for scraping."""
    return config.SELECTED_NATIONS


def get_year_range() -> Tuple[int, int]:
    """Get the year range for data scraping."""
    return config.YEAR_RANGE


def get_rate_limit(operation_type: str = 'default') -> int:
    """Get the rate limit for a specific operation type."""
    return config.RATE_LIMITS.get(operation_type, config.RATE_LIMITS['default'])


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return config.DEBUG


def get_log_level() -> str:
    """Get the current log level."""
    return config.LOG_LEVEL


def get_log_format() -> str:
    """Get the log message format string."""
    return config.LOG_FORMAT


def get_log_date_format() -> str:
    """Get the log date format string."""
    return config.LOG_DATE_FORMAT
