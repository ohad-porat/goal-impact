"""Home page services."""

from datetime import date, timedelta

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, aliased

from app.models.competitions import Competition
from app.models.events import Event
from app.models.matches import Match
from app.models.players import Player
from app.models.seasons import Season
from app.models.teams import Team
from app.schemas.home import RecentGoalMatch, RecentGoalPlayer, RecentImpactGoal


def get_recent_impact_goals(
    db: Session, days: int = 7, limit: int = 5, league_id: int | None = None
) -> list[RecentImpactGoal]:
    """Get top goals by goal value from the most recent N days.

    Finds most recent match date, then gets top goals from last N days before that date.

    Args:
        db: Database session
        days: Days to look back (default: 7)
        limit: Max goals to return (default: 5)
        league_id: Optional league filter. None = all leagues.

    Returns:
        List of RecentImpactGoal sorted by date (descending), then goal value.
    """
    date_query = db.query(func.max(Match.date))

    if league_id is not None:
        date_query = (
            date_query.join(Season, Match.season_id == Season.id)
            .join(Competition, Season.competition_id == Competition.id)
            .filter(Competition.id == league_id)
        )

    most_recent_match_date = date_query.scalar()

    if not most_recent_match_date:
        return []

    cutoff_date: date = most_recent_match_date - timedelta(days=days)

    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)

    query = (
        db.query(Event, Match, Player, HomeTeam, AwayTeam)
        .join(Match, Event.match_id == Match.id)
        .join(Player, Event.player_id == Player.id)
        .join(HomeTeam, Match.home_team_id == HomeTeam.id)
        .join(AwayTeam, Match.away_team_id == AwayTeam.id)
    )

    if league_id is not None:
        query = (
            query.join(Season, Match.season_id == Season.id)
            .join(Competition, Season.competition_id == Competition.id)
            .filter(Competition.id == league_id)
        )

    goals_query = (
        query.filter(
            or_(Event.event_type == "goal", Event.event_type == "own goal"),
            Event.goal_value.isnot(None),
            Match.date >= cutoff_date,
            Match.date <= most_recent_match_date,
        )
        .order_by(desc(Event.goal_value))
        .limit(limit)
        .all()
    )

    goals_with_date = []
    for goal_event, match_obj, player_obj, home_team_obj, away_team_obj in goals_query:
        match_date_obj = match_obj.date
        if match_date_obj:
            day = match_date_obj.day
            month_name = match_date_obj.strftime("%B")
            year = match_date_obj.year
            match_date = f"{month_name} {day}, {year}"
        else:
            match_date = ""

        if (
            goal_event.home_team_goals_pre_event is not None
            and goal_event.away_team_goals_pre_event is not None
            and goal_event.home_team_goals_post_event is not None
            and goal_event.away_team_goals_post_event is not None
        ):
            score_before = (
                f"{goal_event.home_team_goals_pre_event}-{goal_event.away_team_goals_pre_event}"
            )
            score_after = (
                f"{goal_event.home_team_goals_post_event}-{goal_event.away_team_goals_post_event}"
            )
        else:
            score_before = ""
            score_after = ""

        goals_with_date.append(
            (
                match_date_obj if match_date_obj else date.min,
                RecentImpactGoal(
                    match=RecentGoalMatch(
                        home_team=home_team_obj.name if home_team_obj else "Unknown",
                        away_team=away_team_obj.name if away_team_obj else "Unknown",
                        date=match_date,
                    ),
                    scorer=RecentGoalPlayer(id=player_obj.id, name=player_obj.name),
                    minute=goal_event.minute,
                    goal_value=goal_event.goal_value,
                    score_before=score_before,
                    score_after=score_after,
                ),
            )
        )

    goals_with_date.sort(key=lambda x: x[0], reverse=True)
    recent_goals = [goal for _, goal in goals_with_date]

    return recent_goals
