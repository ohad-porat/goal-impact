"""Player-related business logic services."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Player, PlayerStats as PlayerStatsModel, Season, Team, Competition, TeamStats
from app.schemas.players import (
    PlayerInfo,
    SeasonData,
    SeasonDisplay,
    TeamInfo,
    CompetitionInfo,
    PlayerStats,
)
from app.services.common import format_season_display_name, build_nation_info


def transform_player_stats(stats: PlayerStatsModel) -> PlayerStats:
    """Transform PlayerStats model to PlayerStats schema with rounding."""
    return PlayerStats(
        matches_played=stats.matches_played,
        matches_started=stats.matches_started,
        total_minutes=stats.total_minutes,
        minutes_divided_90=round(stats.minutes_divided_90, 2) if stats.minutes_divided_90 else None,
        goals_scored=stats.goals_scored,
        assists=stats.assists,
        total_goal_assists=stats.total_goal_assists,
        non_pk_goals=stats.non_pk_goals,
        pk_made=stats.pk_made,
        pk_attempted=stats.pk_attempted,
        yellow_cards=stats.yellow_cards,
        red_cards=stats.red_cards,
        goal_value=round(stats.goal_value, 2) if stats.goal_value is not None else None,
        gv_avg=round(stats.gv_avg, 2) if stats.gv_avg is not None else None,
        goal_per_90=round(stats.goal_per_90, 2) if stats.goal_per_90 is not None else None,
        assists_per_90=round(stats.assists_per_90, 2) if stats.assists_per_90 is not None else None,
        total_goals_assists_per_90=round(stats.total_goals_assists_per_90, 2) if stats.total_goals_assists_per_90 is not None else None,
        non_pk_goals_per_90=round(stats.non_pk_goals_per_90, 2) if stats.non_pk_goals_per_90 is not None else None,
        non_pk_goal_and_assists_per_90=round(stats.non_pk_goal_and_assists_per_90, 2) if stats.non_pk_goal_and_assists_per_90 is not None else None
    )


def get_player_seasons_stats(db: Session, player_id: int) -> tuple[Optional[PlayerInfo], List[SeasonData]]:
    """Get player information with statistics across all seasons."""
    player = db.query(Player).options(joinedload(Player.nation)).filter(Player.id == player_id).first()
    
    if not player:
        return None, []
    
    player_stats_query = (
        db.query(PlayerStatsModel, Season, Team, Competition, TeamStats)
        .select_from(PlayerStatsModel)
        .join(Season, PlayerStatsModel.season_id == Season.id)
        .join(Team, PlayerStatsModel.team_id == Team.id)
        .join(Competition, Season.competition_id == Competition.id)
        .outerjoin(
            TeamStats,
            (TeamStats.team_id == PlayerStatsModel.team_id) & (TeamStats.season_id == PlayerStatsModel.season_id)
        )
        .filter(PlayerStatsModel.player_id == player_id)
        .order_by(Season.start_year.asc())
        .all()
    )
    
    seasons_data = [
        SeasonData(
            season=SeasonDisplay(
                id=season.id,
                start_year=season.start_year,
                end_year=season.end_year,
                display_name=format_season_display_name(season.start_year, season.end_year)
            ),
            team=TeamInfo(
                id=team.id,
                name=team.name
            ),
            competition=CompetitionInfo(
                id=competition.id,
                name=competition.name
            ),
            league_rank=team_stats.ranking if team_stats else None,
            stats=transform_player_stats(player_stats)
        )
        for player_stats, season, team, competition, team_stats in player_stats_query
    ]
    
    player_info = PlayerInfo(
        id=player.id,
        name=player.name,
        nation=build_nation_info(player.nation)
    )
    
    return player_info, seasons_data
