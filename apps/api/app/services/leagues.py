"""League-related business logic services."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.competitions import Competition
from app.models.nations import Nation
from app.models.seasons import Season
from app.models.team_stats import TeamStats
from app.models.teams import Team
from app.schemas.leagues import (
    LeagueSummary,
    LeagueInfo,
    LeagueTableEntry,
)
from app.schemas.players import SeasonDisplay
from app.services.common import format_season_display_name


def format_season_range(seasons: List[Season]) -> str:
    """Format available season range string for leagues."""
    if not seasons:
        return "No seasons available"
    
    sorted_seasons = sorted(seasons, key=lambda season: season.start_year)
    first_season = sorted_seasons[0]
    last_season = sorted_seasons[-1]
    
    if first_season.start_year == first_season.end_year and last_season.start_year == last_season.end_year:
        return f"{first_season.start_year} - {last_season.start_year}"
    else:
        first_range = format_season_display_name(first_season.start_year, first_season.end_year)
        last_range = format_season_display_name(last_season.start_year, last_season.end_year)
        return f"{first_range} - {last_range}"


def get_all_leagues_with_season_ranges(db: Session) -> List[LeagueSummary]:
    """Get all available leagues with their season ranges formatted."""
    competitions = db.query(Competition).join(Nation).all()
    
    leagues_data = []
    for competition in competitions:
        seasons = db.query(Season).filter(Season.competition_id == competition.id).all()
        available_seasons = format_season_range(seasons)
        
        leagues_data.append(
            LeagueSummary(
                id=competition.id,
                name=competition.name,
                country=competition.nation.name if competition.nation else "Unknown",
                gender=competition.gender,
                tier=competition.tier,
                available_seasons=available_seasons
            )
        )
    
    return leagues_data


def get_league_seasons(db: Session, league_id: int) -> List[SeasonDisplay]:
    """Get all available seasons for a league, sorted by start_year descending."""
    seasons = db.query(Season).filter(Season.competition_id == league_id).all()
    
    seasons_data = [
        SeasonDisplay(
            id=season.id,
            start_year=season.start_year,
            end_year=season.end_year,
            display_name=format_season_display_name(season.start_year, season.end_year)
        )
        for season in seasons
    ]
    
    seasons_data.sort(key=lambda x: x.start_year, reverse=True)
    return seasons_data


def get_league_table_for_season(
    db: Session,
    league_id: int,
    season_id: int
) -> Tuple[Optional[LeagueInfo], Optional[SeasonDisplay], List[LeagueTableEntry]]:
    """Get league table for a specific league and season."""
    competition = db.query(Competition).filter(Competition.id == league_id).first()
    if not competition:
        return None, None, []
    
    season = (
        db.query(Season)
        .filter(Season.id == season_id, Season.competition_id == league_id)
        .first()
    )
    if not season:
        return None, None, []
    
    team_stats = (
        db.query(TeamStats)
        .join(Team)
        .filter(TeamStats.season_id == season_id)
        .order_by(TeamStats.ranking)
        .all()
    )
    
    table_data = [
        LeagueTableEntry(
            position=team_stat.ranking,
            team_id=team_stat.team.id,
            team_name=team_stat.team.name,
            matches_played=team_stat.matches_played,
            wins=team_stat.wins,
            draws=team_stat.draws,
            losses=team_stat.losses,
            goals_for=team_stat.goals_for,
            goals_against=team_stat.goals_against,
            goal_difference=team_stat.goal_difference,
            points=team_stat.points
        )
        for team_stat in team_stats
    ]
    
    league_info = LeagueInfo(
        id=competition.id,
        name=competition.name,
        country=competition.nation.name if competition.nation else "Unknown"
    )
    
    season_info = SeasonDisplay(
        id=season.id,
        start_year=season.start_year,
        end_year=season.end_year,
        display_name=format_season_display_name(season.start_year, season.end_year)
    )
    
    return league_info, season_info, table_data
