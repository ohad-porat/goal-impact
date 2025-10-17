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
from bs4 import BeautifulSoup
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
                response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
                
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
                time.sleep(sleep_time)
                return pd.read_html(url)
                
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

    def get_fbref_competition_name(self, db_competition_name: str) -> str:
        """Map database competition names to FBRef dropdown text."""
        mapping = {
            'Fußball-Bundesliga': 'Bundesliga',
            'Campeonato Brasileiro Série A': 'Série A',
        }
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