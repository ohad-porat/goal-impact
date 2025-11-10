"""Base scraper classes for FBRef data extraction."""

import json
import os
import pdb
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Type, TypeVar, Union

import pandas as pd
import requests
import cloudscraper
from bs4 import BeautifulSoup
from io import StringIO
from sqlalchemy.orm import Session

from app.core.database import Session as DBSession
from .logger import get_logger
from .scraper_config import ScraperConfig, get_config, get_rate_limit, is_debug_mode

T = TypeVar('T')
FAILED_RECORDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "failed_records.txt")


class BaseScraper(ABC):
    """Abstract base class for all FBRef scrapers."""
    
    def __init__(self) -> None:
        """Initialize the base scraper."""
        self.config: ScraperConfig = get_config()
        self.session: Optional[Session] = None
        self.logger = get_logger(self.__class__.__name__)
        self.http_session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            }
        )
        self.http_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
    
    @contextmanager
    def database_session(self) -> Iterator[Session]:
        """Context manager for database session handling."""
        self.session = DBSession()
        try:
            yield self.session
        except Exception as e:
            self.logger.error(f"Database Error: {e}")
            self.session.rollback()
            if is_debug_mode():
                pdb.set_trace()
            raise
        finally:
            self.session.close()
    
    def fetch_page(self, url: str, sleep_time: Optional[int] = None, max_retries: int = 3) -> BeautifulSoup:
        """Fetch and parse a web page with retry logic."""
        if sleep_time is None:
            sleep_time = get_rate_limit('default')
        
        self.logger.debug(f"Fetching page: {url}")
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.http_session.headers['Referer'] = self.config.FBREF_BASE_URL
                
                response = self.http_session.get(url, timeout=self.config.REQUEST_TIMEOUT)
                
                if response.status_code == 403:
                    wait_time = sleep_time * (2 ** attempt)
                    self.logger.warning(f"Forbidden (403) on attempt {attempt + 1}/{max_retries + 1} for {url}")
                    
                    self.logger.info(f"Response status: {response.status_code}")
                    self.logger.info(f"Response headers: {dict(response.headers)}")
                    self.logger.info(f"Request headers sent: {dict(self.http_session.headers)}")
                    if response.text:
                        preview = response.text[:500].replace('\n', ' ')
                        self.logger.info(f"Response body preview: {preview}")
                    
                    if attempt < max_retries:
                        self.logger.warning(f"Waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.error(f"Failed after {max_retries + 1} attempts with 403 Forbidden")
                        raise requests.HTTPError(f"403 Forbidden after {max_retries + 1} attempts")
                
                if response.status_code == 429:
                    wait_time = sleep_time * (2 ** attempt)
                    self.logger.warning(f"Rate limited (429). Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code >= 500:
                    wait_time = sleep_time * (2 ** attempt)
                    self.logger.warning(f"Server error ({response.status_code}). Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                time.sleep(sleep_time)
                
                return BeautifulSoup(response.text, 'html.parser')
                
            except requests.RequestException as e:
                if attempt == max_retries:
                    self.logger.error(f"HTTP Error fetching {url} after {max_retries + 1} attempts: {e}")
                    if is_debug_mode():
                        pdb.set_trace()
                    raise
                
                wait_time = sleep_time * (2 ** attempt)
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}). Waiting {wait_time}s: {e}")
                time.sleep(wait_time)
        
        raise Exception(f"Failed to fetch {url} after {max_retries + 1} attempts")
    
    def fetch_html_table(self, url: str, sleep_time: Optional[int] = None, max_retries: int = 3) -> List[pd.DataFrame]:
        """Fetch and parse HTML tables from a URL with retry logic."""
        if sleep_time is None:
            sleep_time = get_rate_limit('default')
        
        self.logger.debug(f"Fetching HTML table: {url}")
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.http_session.headers['Referer'] = self.config.FBREF_BASE_URL
                
                response = self.http_session.get(url, timeout=self.config.REQUEST_TIMEOUT)
                
                if response.status_code == 403:
                    wait_time = sleep_time * (2 ** attempt)
                    self.logger.warning(f"Forbidden (403) fetching HTML table on attempt {attempt + 1}/{max_retries + 1}")
                    if attempt < max_retries:
                        self.logger.warning(f"Waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise requests.HTTPError(f"403 Forbidden after {max_retries + 1} attempts")
                
                response.raise_for_status()
                time.sleep(sleep_time)
                
                return pd.read_html(StringIO(response.text))
                
            except Exception as e:
                if attempt == max_retries:
                    self.logger.error(f"Error fetching HTML table from {url} after {max_retries + 1} attempts: {e}")
                    if is_debug_mode():
                        pdb.set_trace()
                    raise
                
                wait_time = sleep_time * (2 ** attempt)
                self.logger.warning(f"HTML table fetch failed (attempt {attempt + 1}/{max_retries + 1}). Waiting {wait_time}s: {e}")
                time.sleep(wait_time)
        
        raise Exception(f"Failed to fetch HTML table from {url} after {max_retries + 1} attempts")
    
    def extract_fbref_id(self, url: str) -> str:
        """Extract FBRef ID from a URL."""
        parts = url.split("/")
        result = parts[3]
        return result
    
    def log_skip(self, entity_type: str, entity_name: str, reason: str = "Already exists") -> None:
        """Log a skip message for an entity."""
        self.logger.warning(f"Skipping {entity_type} '{entity_name}'. {reason}.")
    
    def log_error(self, operation: str, error: Exception) -> None:
        """Log an error that occurred during an operation."""
        self.logger.error(f"Error in {operation}: {error}")
        if is_debug_mode():
            pdb.set_trace()
    
    def log_error_and_continue(self, operation: str, error: Exception, entity_name: str = "") -> None:
        """Log an error but continue processing instead of stopping."""
        self.logger.error(f"Error in {operation} for {entity_name}: {error}. Continuing with next item.")
        self.log_failed_record(operation, entity_name, str(error))
    
    def log_progress(self, message: str) -> None:
        """Log a progress message."""
        self.logger.info(message)
    
    def _get_progress_file(self) -> str:
        """Get the progress file path for this scraper."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", f"progress_{self.__class__.__name__.lower()}.json")
    
    def save_progress(self, progress_data: Dict) -> None:
        """Save progress data to a file for resume capability."""
        try:
            with open(self._get_progress_file(), 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save progress: {e}")
    
    def load_progress(self) -> Optional[Dict]:
        """Load progress data from file for resume capability."""
        try:
            progress_file = self._get_progress_file()
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load progress: {e}")
        return None
    
    def clear_progress(self) -> None:
        """Clear progress file after successful completion."""
        try:
            progress_file = self._get_progress_file()
            if os.path.exists(progress_file):
                os.remove(progress_file)
        except Exception as e:
            self.logger.warning(f"Could not clear progress file: {e}")
    
    def log_failed_record(self, record_type: str, record_identifier: str, error: str) -> None:
        """Log a failed record to the failed records file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            scraper_name = self.__class__.__name__
            with open(FAILED_RECORDS_FILE, 'a') as f:
                f.write(f"[{timestamp}] {scraper_name} - {record_type}: {record_identifier} - Error: {error}\n")
        except Exception as e:
            self.logger.warning(f"Could not log failed record: {e}")
    
    def get_failed_records(self) -> List[str]:
        """Get list of failed records from the failed records file."""
        try:
            if os.path.exists(FAILED_RECORDS_FILE):
                with open(FAILED_RECORDS_FILE, 'r') as f:
                    return f.readlines()
        except Exception as e:
            self.logger.warning(f"Could not read failed records: {e}")
        return []
    
    def _clean_integer_value(self, value):
        """Clean value for integer fields: convert nan to None, float to int."""
        if value is None:
            return None
        if pd.isna(value):
            return None
        try:
            int_value = int(float(value))
            if int_value > 2147483647:
                self.logger.warning(f"Integer value {int_value} exceeds PostgreSQL integer max, setting to None")
                return None
            return int_value
        except (ValueError, TypeError, OverflowError):
            return None
    
    def _clean_float_value(self, value):
        """Clean value for float fields: convert nan to None."""
        if value is None:
            return None
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _clean_string_value(self, value) -> Optional[str]:
        """Clean value for string fields: convert nan to None, empty strings to None."""
        if value is None:
            return None
        if pd.isna(value):
            return None
        value_str = str(value).strip()
        return value_str if value_str else None
    
    @abstractmethod
    def scrape(self, **kwargs) -> None:
        """Abstract method to be implemented by subclasses."""
        pass
    
    def run(self, **kwargs) -> None:
        """Run the scraper with proper session management."""
        with self.database_session():
            self.scrape(**kwargs)


class WebScraper(BaseScraper):
    """Web scraper with BeautifulSoup integration for HTML parsing."""
    
    def __init__(self) -> None:
        """Initialize the web scraper."""
        super().__init__()
        self.soup: Optional[BeautifulSoup] = None
    
    def load_page(self, url: str, sleep_time: Optional[int] = None) -> BeautifulSoup:
        """Load a web page and store it in the soup attribute."""
        self.soup = self.fetch_page(url, sleep_time)
        return self.soup
    
    def find_element(self, tag: str, **attributes) -> Optional[BeautifulSoup]:
        """Find the first element matching the given tag and attributes."""
        if self.soup is None:
            raise ValueError("No page loaded. Call load_page() first.")
        return self.soup.find(tag, **attributes)
    
    def find_elements(self, tag: str, attributes=None, **kwargs) -> List[BeautifulSoup]:
        """Find all elements matching the given tag and attributes."""
        if self.soup is None:
            raise ValueError("No page loaded. Call load_page() first.")
        
        if attributes is not None:
            return self.soup.find_all(tag, attributes)
        else:
            return self.soup.find_all(tag, **kwargs)

    def get_fbref_competition_name(self, db_competition_name: str, season_start_year: int = None) -> str:
        """Map database competition names to FBRef dropdown text."""
        mapping = {
            'Fußball-Bundesliga': 'Bundesliga',
            'Campeonato Brasileiro Série A': 'Série A',
        }
        
        # Handle French league name change
        if db_competition_name == 'Ligue 1' and season_start_year is not None:
            if season_start_year <= 2001:
                return 'Division 1'
            else:
                return 'Ligue 1'
        
        return mapping.get(db_competition_name, db_competition_name)

    def find_or_create_record(self, model_class: Type[T], filters: Dict[str, Union[str, int]], data_dict: Dict[str, Union[str, int, float]], description: str) -> T:
        """Find an existing record or create a new one in the database."""
        existing = self.session.query(model_class).filter_by(**filters).first()
        if existing:
            self.log_skip(description.split()[0], description)
            return existing
        
        record = model_class(**data_dict)
        self.session.add(record)
        self.session.commit()
        self.logger.info(f"Added {description}")
        return record