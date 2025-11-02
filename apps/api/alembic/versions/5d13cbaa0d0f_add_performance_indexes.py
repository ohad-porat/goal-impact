"""add performance indexes

Revision ID: 5d13cbaa0d0f
Revises: 231e4ea5b1a8
Create Date: 2025-11-01 20:04:24.206089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d13cbaa0d0f'
down_revision: Union[str, None] = '231e4ea5b1a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Events table indexes
    op.create_index('idx_events_player_id', 'events', ['player_id'])
    op.create_index('idx_events_match_id', 'events', ['match_id'])
    op.create_index('idx_events_match_minute_type', 'events', ['match_id', 'minute', 'event_type'])
    op.create_index('idx_events_player_type', 'events', ['player_id', 'event_type'])
    
    # Matches table indexes
    op.create_index('idx_matches_season_id', 'matches', ['season_id'])
    op.create_index('idx_matches_home_team_id', 'matches', ['home_team_id'])
    op.create_index('idx_matches_away_team_id', 'matches', ['away_team_id'])
    op.create_index('idx_matches_season_teams', 'matches', ['season_id', 'home_team_id', 'away_team_id'])
    
    # PlayerStats table indexes
    op.create_index('idx_player_stats_player_id', 'player_stats', ['player_id'])
    op.create_index('idx_player_stats_season_id', 'player_stats', ['season_id'])
    op.create_index('idx_player_stats_team_id', 'player_stats', ['team_id'])
    op.create_index('idx_player_stats_season_team', 'player_stats', ['season_id', 'team_id'])
    op.create_index('idx_player_stats_player_season', 'player_stats', ['player_id', 'season_id'])
    op.create_index('idx_player_stats_goal_value', 'player_stats', ['goal_value'])
    
    # TeamStats table indexes
    op.create_index('idx_team_stats_team_id', 'team_stats', ['team_id'])
    op.create_index('idx_team_stats_season_id', 'team_stats', ['season_id'])
    op.create_index('idx_team_stats_team_season', 'team_stats', ['team_id', 'season_id'])
    op.create_index('idx_team_stats_ranking', 'team_stats', ['ranking'])
    
    # Seasons table indexes
    op.create_index('idx_seasons_competition_id', 'seasons', ['competition_id'])
    op.create_index('idx_seasons_start_end_year', 'seasons', ['start_year', 'end_year'])
    
    # Teams table indexes
    op.create_index('idx_teams_nation_id', 'teams', ['nation_id'])
    
    # Competitions table indexes
    op.create_index('idx_competitions_nation_id', 'competitions', ['nation_id'])
    op.create_index('idx_competitions_tier', 'competitions', ['tier'])


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_competitions_tier')
    op.drop_index('idx_competitions_nation_id')
    op.drop_index('idx_teams_nation_id')
    op.drop_index('idx_seasons_start_end_year')
    op.drop_index('idx_seasons_competition_id')
    op.drop_index('idx_team_stats_ranking')
    op.drop_index('idx_team_stats_team_season')
    op.drop_index('idx_team_stats_season_id')
    op.drop_index('idx_team_stats_team_id')
    op.drop_index('idx_player_stats_goal_value')
    op.drop_index('idx_player_stats_player_season')
    op.drop_index('idx_player_stats_season_team')
    op.drop_index('idx_player_stats_team_id')
    op.drop_index('idx_player_stats_season_id')
    op.drop_index('idx_player_stats_player_id')
    op.drop_index('idx_matches_season_teams')
    op.drop_index('idx_matches_away_team_id')
    op.drop_index('idx_matches_home_team_id')
    op.drop_index('idx_matches_season_id')
    op.drop_index('idx_events_player_type')
    op.drop_index('idx_events_match_minute_type')
    op.drop_index('idx_events_match_id')
    op.drop_index('idx_events_player_id')
