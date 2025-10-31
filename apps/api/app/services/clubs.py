"""Club-related business logic services."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.nations import Nation
from app.models.teams import Team
from app.models.team_stats import TeamStats
from app.models.competitions import Competition
from app.models.seasons import Season
from app.models.players import Player
from app.models.player_stats import PlayerStats
from app.schemas.clubs import (
    ClubSummary,
    ClubByNation,
    NationBasic,
    ClubInfo,
    NationDetailed,
    SeasonStats,
    CompetitionInfo,
    TeamStatsInfo,
    SquadPlayer,
    PlayerBasic,
    CompetitionDisplay,
)
from app.schemas.players import SeasonDisplay
from app.services.common import format_season_display_name
from app.services.players import transform_player_stats


def _build_club_info(team: Team) -> ClubInfo:
    """Build ClubInfo from Team model."""
    return ClubInfo(
        id=team.id,
        name=team.name,
        nation=NationDetailed(
            id=team.nation.id if team.nation else None,
            name=team.nation.name if team.nation else "Unknown",
            country_code=team.nation.country_code if team.nation else None
        )
    )


def get_top_clubs_for_nation_core(
    db: Session,
    nation_id: int,
    limit: int = 10,
    tier: str = "1st"
) -> List[ClubSummary]:
    """Get top clubs for a nation by average position."""
    teams_with_avg_position = (
        db.query(
            Team.id,
            Team.name,
            func.avg(TeamStats.ranking).label('avg_position')
        )
        .join(TeamStats)
        .join(Season)
        .join(Competition)
        .filter(
            Team.nation_id == nation_id,
            Competition.tier == tier,
            TeamStats.ranking.isnot(None)
        )
        .group_by(Team.id, Team.name)
        .order_by('avg_position', Team.name)
        .limit(limit)
        .all()
    )
    
    return [
        ClubSummary(
            id=team.id,
            name=team.name,
            avg_position=round(float(team.avg_position), 1)
        )
        for team in teams_with_avg_position
    ]


def get_clubs_by_nation(db: Session, limit_per_nation: int = 5) -> List[ClubByNation]:
    """Get top clubs per nation based on average finishing position in tier 1 leagues."""
    nations_with_competitions = db.query(Nation).join(Competition).distinct().all()
    
    result = []
    for nation in nations_with_competitions:
        clubs = get_top_clubs_for_nation_core(db, nation.id, limit=limit_per_nation)
        
        if clubs:
            result.append(
                ClubByNation(
                    nation=NationBasic(
                        id=nation.id,
                        name=nation.name,
                        country_code=nation.country_code
                    ),
                    clubs=clubs
                )
            )
    
    return result


def get_club_with_seasons(db: Session, club_id: int) -> tuple[Optional[ClubInfo], List[SeasonStats]]:
    """Get club information with all season statistics."""
    team = db.query(Team).options(joinedload(Team.nation)).filter(Team.id == club_id).first()
    
    if not team:
        return None, []
    
    team_stats_query = (
        db.query(TeamStats, Season, Competition)
        .select_from(TeamStats)
        .join(Season)
        .join(Competition)
        .filter(TeamStats.team_id == club_id)
        .order_by(Season.start_year.desc(), Competition.name)
        .all()
    )
    
    seasons_data = [
        SeasonStats(
            season=SeasonDisplay(
                id=season.id,
                start_year=season.start_year,
                end_year=season.end_year,
                display_name=format_season_display_name(season.start_year, season.end_year)
            ),
            competition=CompetitionInfo(
                id=competition.id,
                name=competition.name,
                tier=competition.tier
            ),
            stats=TeamStatsInfo(
                ranking=team_stat.ranking,
                matches_played=team_stat.matches_played,
                wins=team_stat.wins,
                draws=team_stat.draws,
                losses=team_stat.losses,
                goals_for=team_stat.goals_for,
                goals_against=team_stat.goals_against,
                goal_difference=team_stat.goal_difference,
                points=team_stat.points,
                attendance=team_stat.attendance,
                notes=team_stat.notes
            )
        )
        for team_stat, season, competition in team_stats_query
    ]
    
    return _build_club_info(team), seasons_data


def get_team_season_squad_stats(
    db: Session,
    team_id: int,
    season_id: int
) -> tuple[Optional[ClubInfo], Optional[SeasonDisplay], Optional[CompetitionDisplay], List[SquadPlayer]]:
    """Get team squad with player statistics for a specific season."""
    team = db.query(Team).options(joinedload(Team.nation)).filter(Team.id == team_id).first()
    if not team:
        return None, None, None, []
    
    season = db.query(Season).options(joinedload(Season.competition)).filter(Season.id == season_id).first()
    if not season:
        return None, None, None, []
    
    player_stats_query = (
        db.query(PlayerStats, Player)
        .select_from(PlayerStats)
        .join(Player)
        .filter(
            PlayerStats.team_id == team_id,
            PlayerStats.season_id == season_id
        )
        .order_by(PlayerStats.goal_value.desc())
        .all()
    )
    
    players_data = [
        SquadPlayer(
            player=PlayerBasic(
                id=player.id,
                name=player.name
            ),
            stats=transform_player_stats(player_stats)
        )
        for player_stats, player in player_stats_query
    ]
    
    season_display = SeasonDisplay(
        id=season.id,
        start_year=season.start_year,
        end_year=season.end_year,
        display_name=format_season_display_name(season.start_year, season.end_year)
    )
    
    competition_display = CompetitionDisplay(
        id=season.competition.id if season.competition else None,
        name=season.competition.name if season.competition else "Unknown"
    )
    
    return _build_club_info(team), season_display, competition_display, players_data
