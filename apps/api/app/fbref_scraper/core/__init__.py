# FBRef Scraper Core Package

from .base_scraper import BaseScraper, WebScraper
from .cli_parser import parse_arguments, parse_date, parse_nations
from .logger import ColoredFormatter, get_logger, setup_logger
from .progress_manager import (
    clear_scraping_progress,
    get_scrapers_to_run,
    load_scraping_progress,
    save_scraping_progress,
)
from .scraper_config import (
    ScraperConfig,
    get_config,
    get_log_date_format,
    get_log_format,
    get_log_level,
    get_rate_limit,
    get_selected_nations,
    get_year_range,
    is_debug_mode,
    update_config,
)

__all__ = [
    "BaseScraper",
    "WebScraper",
    "ScraperConfig",
    "get_config",
    "update_config",
    "get_selected_nations",
    "get_year_range",
    "get_rate_limit",
    "is_debug_mode",
    "get_log_level",
    "get_log_format",
    "get_log_date_format",
    "save_scraping_progress",
    "load_scraping_progress",
    "clear_scraping_progress",
    "get_scrapers_to_run",
    "ColoredFormatter",
    "setup_logger",
    "get_logger",
    "parse_arguments",
    "parse_date",
    "parse_nations",
]
