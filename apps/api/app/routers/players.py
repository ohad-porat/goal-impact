"""Players router for FastAPI application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models import Player, PlayerStats, Season, Team, Competition, TeamStats
from app.schemas.players import (
    PlayerDetailsResponse,
    PlayerInfo,
    NationInfo as PlayerNationInfo,
    SeasonData,
    SeasonDisplay,
    TeamInfo,
    CompetitionInfo as PlayerCompetitionInfo,
    PlayerStatsDetailed,
)

router = APIRouter()

@router.get("/{player_id}", response_model=PlayerDetailsResponse)
async def get_player_details(player_id: int, db: Session = Depends(get_db)):
    """Get detailed player information with statistics across all seasons"""
    
    player = db.query(Player).options(joinedload(Player.nation)).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player_stats_query = db.query(
        PlayerStats,
        Season,
        Team,
        Competition,
        TeamStats
    ).select_from(PlayerStats)\
     .join(Season, PlayerStats.season_id == Season.id)\
     .join(Team, PlayerStats.team_id == Team.id)\
     .join(Competition, Season.competition_id == Competition.id)\
     .outerjoin(TeamStats, (TeamStats.team_id == PlayerStats.team_id) & (TeamStats.season_id == PlayerStats.season_id))\
     .filter(PlayerStats.player_id == player_id)\
     .order_by(Season.start_year.asc())\
     .all()
    
    seasons_data = [
        SeasonData(
            season=SeasonDisplay(
                id=season.id,
                start_year=season.start_year,
                end_year=season.end_year,
                display_name=f"{season.start_year}/{season.end_year}" if season.start_year != season.end_year else str(season.start_year)
            ),
            team=TeamInfo(
                id=team.id,
                name=team.name
            ),
            competition=PlayerCompetitionInfo(
                id=competition.id,
                name=competition.name
            ),
            league_rank=team_stats.ranking if team_stats else None,
            stats=PlayerStatsDetailed(
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
        )
        for stats, season, team, competition, team_stats in player_stats_query
    ]
    
    return PlayerDetailsResponse(
        player=PlayerInfo(
            id=player.id,
            name=player.name,
            nation=PlayerNationInfo(
                id=player.nation.id if player.nation else None,
                name=player.nation.name if player.nation else None,
                country_code=player.nation.country_code if player.nation else None
            )
        ),
        seasons=seasons_data
    )
