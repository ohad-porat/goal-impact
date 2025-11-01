"""Player-related business logic services."""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Player, PlayerStats as PlayerStatsModel, Season, Team, Competition, TeamStats, Event, Match
from sqlalchemy import or_, case, func
from app.schemas.players import (
    PlayerInfo,
    SeasonData,
    SeasonDisplay,
    TeamInfo,
    CompetitionInfo,
    PlayerStats,
)
from app.schemas.clubs import PlayerGoalLogEntry, PlayerBasic
from app.services.common import format_season_display_name, build_nation_info
from app.services.goal_log import build_player_career_goal_log_entry


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
    
    team_case = case(
        (Event.home_team_goals_post_event > Event.home_team_goals_pre_event, Match.home_team_id),
        else_=Match.away_team_id
    )
    earliest_dates = (
        db.query(
            Match.season_id,
            team_case.label('team_id'),
            func.min(Match.date).label('earliest_date')
        )
        .select_from(Event)
        .join(Match, Event.match_id == Match.id)
        .filter(
            Event.player_id == player_id,
            or_(Event.event_type == "goal", Event.event_type == "own goal")
        )
        .group_by(Match.season_id, team_case)
        .all()
    )
    
    date_map = {(season_id, team_id): earliest_date for season_id, team_id, earliest_date in earliest_dates}
    
    seasons_data = [
        (
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
            ),
            date_map.get((season.id, team.id))
        )
        for player_stats, season, team, competition, team_stats in player_stats_query
    ]
    
    seasons_data.sort(key=lambda x: (x[0].season.start_year, x[1] if x[1] else date.max))
    seasons_data = [sd[0] for sd in seasons_data]
    
    player_info = PlayerInfo(
        id=player.id,
        name=player.name,
        nation=build_nation_info(player.nation)
    )
    
    return player_info, seasons_data


def get_player_career_goal_log(
    db: Session,
    player_id: int
) -> tuple[Optional[PlayerBasic], List[PlayerGoalLogEntry]]:
    """Get goal log for a player across their entire career."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None, []
    
    goals_query = (
        db.query(Event, Match, Season)
        .join(Match, Event.match_id == Match.id)
        .join(Season, Match.season_id == Season.id)
        .filter(
            Event.player_id == player_id,
            or_(Event.event_type == "goal", Event.event_type == "own goal")
        )
        .all()
    )
    
    goal_entries_with_date_season = []
    for goal_event, match, season in goals_query:
        season_display_name = format_season_display_name(season.start_year, season.end_year)
        goal_entry = build_player_career_goal_log_entry(db, goal_event, match, player, season_display_name)
        if goal_entry:
            goal_entries_with_date_season.append((
                match.date if match.date else None,
                season.start_year,
                goal_entry
            ))
    
    goal_entries_with_date_season.sort(key=lambda g: (
        g[1] if g[1] is not None else 0,
        g[0] if g[0] is not None else "",
        g[2].minute
    ))
    
    goal_entries = []
    for date_obj, _, goal_entry in goal_entries_with_date_season:
        date_str = date_obj.strftime("%d/%m/%Y") if date_obj else ""
        goal_entry.date = date_str
        goal_entries.append(goal_entry)
    
    player_basic = PlayerBasic(
        id=player.id,
        name=player.name
    )
    
    return player_basic, goal_entries
