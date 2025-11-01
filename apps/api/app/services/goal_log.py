"""Goal log related services - reusable for teams and players."""

from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload

from app.models.events import Event
from app.models.matches import Match
from app.models.players import Player
from app.models.teams import Team
from app.schemas.clubs import GoalLogEntry, PlayerBasic, PlayerGoalLogEntry
from app.services.common import build_club_info


def is_goal_for_team(goal_event: Event, match: Match, team_id: int) -> bool:
    """Determine if a goal was scored FOR the specified team."""
    home_scored = goal_event.home_team_goals_post_event > goal_event.home_team_goals_pre_event
    
    if home_scored and match.home_team_id == team_id:
        return True
    elif not home_scored and match.away_team_id == team_id:
        return True
    return False


def format_score(goal_event: Event) -> Tuple[str, str]:
    """Format score before and after the goal."""
    score_before = f"{goal_event.home_team_goals_pre_event}-{goal_event.away_team_goals_pre_event}"
    score_after = f"{goal_event.home_team_goals_post_event}-{goal_event.away_team_goals_post_event}"
    return score_before, score_after


def get_assist_for_goal(db: Session, match: Match, goal_event: Event) -> Optional[PlayerBasic]:
    """Get the assisting player for a goal, if available."""
    assist_event = (
        db.query(Event)
        .filter(
            Event.match_id == match.id,
            Event.minute == goal_event.minute,
            Event.event_type == "assist"
        )
        .first()
    )
    
    if not assist_event:
        return None
    
    assisting_player = db.query(Player).filter(Player.id == assist_event.player_id).first()
    if not assisting_player:
        return None
    
    return PlayerBasic(
        id=assisting_player.id,
        name=assisting_player.name
    )


def format_scorer_name(scorer: Player, event_type: str) -> str:
    """Format scorer name, adding (OG) for own goals."""
    if event_type == "own goal":
        return f"{scorer.name} (OG)"
    return scorer.name


def get_venue_for_team(match: Match, team_id: int) -> str:
    """Get venue (Home/Away) for a team in a match."""
    return "Home" if match.home_team_id == team_id else "Away"


def get_opponent_team(db: Session, match: Match, team_id: int) -> Optional[Team]:
    """Get the opponent team for a given team in a match."""
    opponent_team_id = match.away_team_id if match.home_team_id == team_id else match.home_team_id
    return db.query(Team).options(joinedload(Team.nation)).filter(Team.id == opponent_team_id).first()


def build_team_season_goal_log_entry(
    db: Session,
    goal_event: Event,
    match: Match,
    scorer: Player,
    team_id: int
) -> Optional[GoalLogEntry]:
    """Build a GoalLogEntry from goal event data for a team/season (only goals FOR the team)."""
    if not is_goal_for_team(goal_event, match, team_id):
        return None
    
    venue = get_venue_for_team(match, team_id)
    
    opponent_team = get_opponent_team(db, match, team_id)
    if not opponent_team:
        return None
    
    score_before, score_after = format_score(goal_event)
    assisted_by = get_assist_for_goal(db, match, goal_event)
    scorer_name = format_scorer_name(scorer, goal_event.event_type)
    
    return GoalLogEntry(
        date="",
        venue=venue,
        scorer=PlayerBasic(
            id=scorer.id,
            name=scorer_name
        ),
        opponent=build_club_info(opponent_team),
        minute=goal_event.minute,
        score_before=score_before,
        score_after=score_after,
        goal_value=goal_event.goal_value,
        xg=goal_event.xg,
        post_shot_xg=goal_event.post_shot_xg,
        assisted_by=assisted_by
    )


def sort_and_format_goal_entries(
    goal_entries_with_date: List[Tuple[Optional[date], GoalLogEntry]]
) -> List[GoalLogEntry]:
    """Sort goal entries by date and minute, then format dates."""
    goal_entries_with_date.sort(key=lambda g: (
        g[0] if g[0] is not None else "",
        g[1].minute
    ))
    
    goal_entries = []
    for date_obj, goal_entry in goal_entries_with_date:
        date_str = date_obj.strftime("%d/%m/%Y") if date_obj else ""
        goal_entry.date = date_str
        goal_entries.append(goal_entry)
    
    return goal_entries


def build_player_career_goal_log_entry(
    db: Session,
    goal_event: Event,
    match: Match,
    scorer: Player,
    season_display_name: str
) -> Optional[PlayerGoalLogEntry]:
    """Build a PlayerGoalLogEntry from goal event data for a player/career (all goals BY the player)."""
    home_scored = goal_event.home_team_goals_post_event > goal_event.home_team_goals_pre_event
    scoring_team_id = match.home_team_id if home_scored else match.away_team_id
    
    player_team = db.query(Team).options(joinedload(Team.nation)).filter(Team.id == scoring_team_id).first()
    if not player_team:
        return None
    
    venue = get_venue_for_team(match, scoring_team_id)
    opponent_team = get_opponent_team(db, match, scoring_team_id)
    if not opponent_team:
        return None
    
    score_before, score_after = format_score(goal_event)
    assisted_by = get_assist_for_goal(db, match, goal_event)
    
    return PlayerGoalLogEntry(
        date="",
        venue=venue,
        team=build_club_info(player_team),
        opponent=build_club_info(opponent_team),
        minute=goal_event.minute,
        score_before=score_before,
        score_after=score_after,
        goal_value=goal_event.goal_value,
        xg=goal_event.xg,
        post_shot_xg=goal_event.post_shot_xg,
        assisted_by=assisted_by,
        season_id=match.season_id,
        season_display_name=season_display_name
    )
