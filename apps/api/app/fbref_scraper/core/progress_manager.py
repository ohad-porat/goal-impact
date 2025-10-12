"""Progress management utilities for FBRef scraper."""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
from .logger import get_logger

logger = get_logger('progress_manager')

SCRAPING_PROGRESS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "scraping_progress.json")

def save_scraping_progress(scraper_name: str, completed: bool = True) -> None:
    """Save overall scraping progress."""
    try:
        if os.path.exists(SCRAPING_PROGRESS_FILE):
            with open(SCRAPING_PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
        else:
            progress = {}
        
        progress[scraper_name] = {
            'completed': completed,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(SCRAPING_PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save scraping progress: {e}")


def load_scraping_progress() -> Dict:
    """Load overall scraping progress."""
    try:
        if os.path.exists(SCRAPING_PROGRESS_FILE):
            with open(SCRAPING_PROGRESS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load scraping progress: {e}")
    return {}


def clear_scraping_progress() -> None:
    """Clear overall scraping progress after successful completion."""
    try:
        if os.path.exists(SCRAPING_PROGRESS_FILE):
            os.remove(SCRAPING_PROGRESS_FILE)
    except Exception as e:
        logger.warning(f"Could not clear scraping progress: {e}")


def get_scrapers_to_run(resume: bool = False) -> List[Tuple[str, type]]:
    """Get list of scrapers to run based on resume status."""
    from ..scrapers import (
        NationsScraper,
        CompetitionsScraper,
        SeasonsScraper,
        TeamsScraper,
        TeamStatsScraper,
        PlayersScraper,
        MatchesScraper,
        EventsScraper
    )
    
    scrapers = [
        ('nations', NationsScraper),
        ('competitions', CompetitionsScraper),
        ('teams', TeamsScraper),
        ('seasons', SeasonsScraper),
        ('team_stats', TeamStatsScraper),
        ('players', PlayersScraper),
        ('matches', MatchesScraper),
        ('events', EventsScraper)
    ]
    
    if not resume:
        return scrapers
    
    progress = load_scraping_progress()
    start_index = 0
    
    for i, (name, _) in enumerate(scrapers):
        if name not in progress or not progress[name].get('completed', False):
            start_index = i
            break
    else:
        start_index = 0
    
    logger.info(f"Resuming from scraper: {scrapers[start_index][0]}")
    return scrapers[start_index:]
