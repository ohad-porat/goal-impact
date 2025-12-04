# FBRef Scraper Scrapers Package

from .competitions_scraper import CompetitionsScraper
from .events_scraper import EventsScraper
from .matches_scraper import MatchesScraper
from .nations_scraper import NationsScraper
from .players_scraper import PlayersScraper
from .seasons_scraper import SeasonsScraper
from .team_stats_scraper import TeamStatsScraper
from .teams_scraper import TeamsScraper

__all__ = [
    "CompetitionsScraper",
    "EventsScraper",
    "MatchesScraper",
    "NationsScraper",
    "PlayersScraper",
    "SeasonsScraper",
    "TeamsScraper",
    "TeamStatsScraper",
]
