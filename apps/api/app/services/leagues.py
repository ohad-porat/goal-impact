"""League-related business logic services."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload

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
from app.services.common import format_season_display_name, normalize_season_years


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
    competitions = (
        db.query(Competition)
        .join(Nation)
        .options(joinedload(Competition.seasons))
        .all()
    )
    
    leagues_data = []
    for competition in competitions:
        available_seasons = format_season_range(competition.seasons)
        
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


def get_all_unique_seasons(db: Session) -> List[SeasonDisplay]:
    """Get all unique seasons grouped by logical period."""
    all_seasons = db.query(Season).all()
    season_groups = {}
    
    for season in all_seasons:
        normalized_start, normalized_end = normalize_season_years(season.start_year, season.end_year)
        key = (normalized_start, normalized_end)
        if key not in season_groups:
            season_groups[key] = []
        season_groups[key].append(season)
    
    seasons_data = []
    seen_display_names = set()
    
    for (normalized_start, normalized_end), seasons in season_groups.items():
        representative = None
        for season in seasons:
            if season.start_year != season.end_year:
                representative = season
                break
        
        if not representative:
            representative = seasons[0]
        
        display_name = format_season_display_name(normalized_start, normalized_end)
        
        if display_name not in seen_display_names:
            seen_display_names.add(display_name)
            seasons_data.append(
                SeasonDisplay(
                    id=representative.id,
                    start_year=normalized_start,
                    end_year=normalized_end,
                    display_name=display_name
                )
            )
    
    seasons_data.sort(key=lambda x: x.start_year, reverse=True)
    
    return seasons_data


def get_league_table_for_season(
    db: Session,
    league_id: int,
    season_id: int
) -> Tuple[Optional[LeagueInfo], Optional[SeasonDisplay], List[LeagueTableEntry]]:
    """Get league table for a specific league and season."""
    competition = (
        db.query(Competition)
        .options(joinedload(Competition.nation))
        .filter(Competition.id == league_id)
        .first()
    )
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
        .options(joinedload(TeamStats.team))
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
