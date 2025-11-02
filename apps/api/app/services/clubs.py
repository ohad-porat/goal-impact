"""Club-related business logic services."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func, case, and_, or_

from app.models.nations import Nation
from app.models.teams import Team
from app.models.team_stats import TeamStats
from app.models.competitions import Competition
from app.models.seasons import Season
from app.models.players import Player
from app.models.player_stats import PlayerStats
from app.models.events import Event
from app.models.matches import Match
from app.schemas.clubs import (
    ClubSummary,
    ClubByNation,
    NationBasic,
    ClubInfo,
    SeasonStats,
    CompetitionInfo,
    TeamStatsInfo,
    SquadPlayer,
    PlayerBasic,
    CompetitionDisplay,
    GoalLogEntry,
)
from app.services.goal_log import (
    build_team_season_goal_log_entry_from_data,
    sort_and_format_team_season_goal_entries,
)
from app.schemas.players import SeasonDisplay
from app.services.common import format_season_display_name, build_club_info
from app.services.players import transform_player_stats


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
    
    return build_club_info(team), seasons_data


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
    
    return build_club_info(team), season_display, competition_display, players_data


def get_team_season_goal_log(
    db: Session,
    team_id: int,
    season_id: int
) -> tuple[Optional[ClubInfo], Optional[SeasonDisplay], Optional[CompetitionDisplay], List[GoalLogEntry]]:
    """Get goal log for a team in a specific season."""
    team = db.query(Team).options(joinedload(Team.nation)).filter(Team.id == team_id).first()
    if not team:
        return None, None, None, []
    
    season = db.query(Season).options(joinedload(Season.competition)).filter(Season.id == season_id).first()
    if not season:
        return None, None, None, []
    
    EventAssist = aliased(Event)
    PlayerAssist = aliased(Player)
    TeamOpponent = aliased(Team)
    
    opponent_team_id_case = case(
        (Match.home_team_id == team_id, Match.away_team_id),
        else_=Match.home_team_id
    )
    
    goals_query = (
        db.query(
            Event,
            Match,
            Player,
            EventAssist,
            PlayerAssist,
            TeamOpponent
        )
        .join(Match, Event.match_id == Match.id)
        .join(Player, Event.player_id == Player.id)
        .outerjoin(
            EventAssist,
            and_(
                EventAssist.match_id == Event.match_id,
                EventAssist.minute == Event.minute,
                EventAssist.event_type == "assist"
            )
        )
        .outerjoin(PlayerAssist, EventAssist.player_id == PlayerAssist.id)
        .join(
            TeamOpponent,
            opponent_team_id_case == TeamOpponent.id
        )
        .options(joinedload(TeamOpponent.nation))
        .filter(
            Match.season_id == season_id,
            or_(Event.event_type == "goal", Event.event_type == "own goal"),
            or_(
                Match.home_team_id == team_id,
                Match.away_team_id == team_id
            )
        )
        .all()
    )
    
    goal_entries_with_date = []
    for goal_event, match, scorer, assist_event, assist_player, opponent_team in goals_query:
        goal_entry = build_team_season_goal_log_entry_from_data(
            goal_event, match, scorer, team_id,
            opponent_team, assist_event, assist_player
        )
        if goal_entry:
            goal_entries_with_date.append((match.date if match.date else None, goal_entry))

    goal_entries = sort_and_format_team_season_goal_entries(goal_entries_with_date)
    
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
    
    return build_club_info(team), season_display, competition_display, goal_entries
