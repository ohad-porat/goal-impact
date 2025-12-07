"""Player-related business logic services."""

from datetime import date

from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session, aliased, joinedload

from app.models import Competition, Event, Match, Player, Season, Team, TeamStats
from app.models import PlayerStats as PlayerStatsModel
from app.schemas.clubs import PlayerBasic, PlayerGoalLogEntry
from app.schemas.players import (
    CompetitionInfo,
    PlayerInfo,
    PlayerStats,
    SeasonData,
    SeasonDisplay,
    TeamInfo,
)
from app.services.common import build_nation_info, format_season_display_name
from app.services.goal_log import (
    build_player_career_goal_log_entry_from_data,
    sort_and_format_player_career_goal_entries,
)


def transform_player_stats(stats: PlayerStatsModel) -> PlayerStats:
    """Transform PlayerStats model to PlayerStats schema with rounding.

    Converts database model to API schema, rounding floating-point values
    to 2 decimal places for display consistency.

    Args:
        stats: The PlayerStatsModel database object

    Returns:
        PlayerStats schema object with rounded values
    """
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
        total_goals_assists_per_90=round(stats.total_goals_assists_per_90, 2)
        if stats.total_goals_assists_per_90 is not None
        else None,
        non_pk_goals_per_90=round(stats.non_pk_goals_per_90, 2)
        if stats.non_pk_goals_per_90 is not None
        else None,
        non_pk_goal_and_assists_per_90=round(stats.non_pk_goal_and_assists_per_90, 2)
        if stats.non_pk_goal_and_assists_per_90 is not None
        else None,
    )


def get_player_seasons_stats(
    db: Session, player_id: int
) -> tuple[PlayerInfo | None, list[SeasonData]]:
    """Get player information with statistics across all seasons.

    Uses subquery to find earliest goal date per team/season for sorting when
    player played for multiple teams in same season.

    Args:
        db: Database session
        player_id: ID of the player

    Returns:
        Tuple of (PlayerInfo, list[SeasonData]). Sorted by start_year and earliest goal date.
    """
    player = (
        db.query(Player).options(joinedload(Player.nation)).filter(Player.id == player_id).first()
    )

    if not player:
        return None, []

    team_case = case(
        (Event.home_team_goals_post_event > Event.home_team_goals_pre_event, Match.home_team_id),
        else_=Match.away_team_id,
    )

    earliest_dates_subquery = (
        db.query(
            Match.season_id, team_case.label("team_id"), func.min(Match.date).label("earliest_date")
        )
        .select_from(Event)
        .join(Match, Event.match_id == Match.id)
        .filter(
            Event.player_id == player_id,
            or_(Event.event_type == "goal", Event.event_type == "own goal"),
        )
        .group_by(Match.season_id, team_case)
        .subquery()
    )

    player_stats_query = (
        db.query(
            PlayerStatsModel,
            Season,
            Team,
            Competition,
            TeamStats,
            earliest_dates_subquery.c.earliest_date,
        )
        .select_from(PlayerStatsModel)
        .join(Season, PlayerStatsModel.season_id == Season.id)
        .join(Team, PlayerStatsModel.team_id == Team.id)
        .join(Competition, Season.competition_id == Competition.id)
        .outerjoin(
            TeamStats,
            (TeamStats.team_id == PlayerStatsModel.team_id)
            & (TeamStats.season_id == PlayerStatsModel.season_id),
        )
        .outerjoin(
            earliest_dates_subquery,
            (earliest_dates_subquery.c.season_id == Season.id)
            & (earliest_dates_subquery.c.team_id == PlayerStatsModel.team_id),
        )
        .filter(PlayerStatsModel.player_id == player_id)
        .order_by(Season.start_year.asc())
        .all()
    )

    seasons_data = [
        (
            SeasonData(
                season=SeasonDisplay(
                    id=season.id,
                    start_year=season.start_year,
                    end_year=season.end_year,
                    display_name=format_season_display_name(season.start_year, season.end_year),
                ),
                team=TeamInfo(id=team.id, name=team.name),
                competition=CompetitionInfo(id=competition.id, name=competition.name),
                league_rank=team_stats.ranking if team_stats else None,
                stats=transform_player_stats(player_stats),
            ),
            earliest_date,
        )
        for player_stats, season, team, competition, team_stats, earliest_date in player_stats_query
    ]

    seasons_data.sort(key=lambda x: (x[0].season.start_year, x[1] if x[1] else date.max))
    seasons_data = [sd[0] for sd in seasons_data]

    player_info = PlayerInfo(
        id=player.id, name=player.name, nation=build_nation_info(player.nation)
    )

    return player_info, seasons_data


def get_player_career_goal_log(
    db: Session, player_id: int
) -> tuple[PlayerBasic | None, list[PlayerGoalLogEntry]]:
    """Get goal log for a player across their entire career.

    Includes match details, season, assist info, goal value, xG, and opponent.
    Goals matched to assists by match_id and minute.

    Args:
        db: Database session
        player_id: ID of the player

    Returns:
        Tuple of (PlayerBasic, list[PlayerGoalLogEntry]). Sorted by season, date, minute.
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None, []

    EventAssist = aliased(Event)
    PlayerAssist = aliased(Player)

    scoring_team_id_case = case(
        (Event.home_team_goals_post_event > Event.home_team_goals_pre_event, Match.home_team_id),
        else_=Match.away_team_id,
    )

    TeamScoring = aliased(Team)
    TeamOpponent = aliased(Team)

    goals_query = (
        db.query(Event, Match, Season, EventAssist, PlayerAssist, TeamScoring, TeamOpponent)
        .join(Match, Event.match_id == Match.id)
        .join(Season, Match.season_id == Season.id)
        .outerjoin(
            EventAssist,
            and_(
                EventAssist.match_id == Event.match_id,
                EventAssist.minute == Event.minute,
                EventAssist.event_type == "assist",
            ),
        )
        .outerjoin(PlayerAssist, EventAssist.player_id == PlayerAssist.id)
        .join(TeamScoring, scoring_team_id_case == TeamScoring.id)
        .options(joinedload(TeamScoring.nation))
        .join(
            TeamOpponent,
            case(
                (Match.home_team_id == TeamScoring.id, Match.away_team_id), else_=Match.home_team_id
            )
            == TeamOpponent.id,
        )
        .options(joinedload(TeamOpponent.nation))
        .filter(
            Event.player_id == player_id,
            or_(Event.event_type == "goal", Event.event_type == "own goal"),
        )
        .all()
    )

    goal_entries_with_date_season = []
    for (
        goal_event,
        match,
        season,
        assist_event,
        assist_player,
        player_team,
        opponent_team,
    ) in goals_query:
        season_display_name = format_season_display_name(season.start_year, season.end_year)
        goal_entry = build_player_career_goal_log_entry_from_data(
            goal_event,
            match,
            player,
            season_display_name,
            player_team,
            opponent_team,
            assist_event,
            assist_player,
        )
        if goal_entry:
            goal_entries_with_date_season.append(
                (match.date if match.date else None, season.start_year, goal_entry)
            )

    goal_entries = sort_and_format_player_career_goal_entries(goal_entries_with_date_season)

    player_basic = PlayerBasic(id=player.id, name=player.name)

    return player_basic, goal_entries
