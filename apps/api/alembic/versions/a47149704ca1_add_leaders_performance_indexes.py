"""add_leaders_performance_indexes

Revision ID: a47149704ca1
Revises: 9a3e74284998
Create Date: 2025-11-13 14:19:40.280117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a47149704ca1'
down_revision: Union[str, None] = '9a3e74284998'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX idx_player_stats_player_goal_value "
        "ON player_stats(player_id, goal_value) "
        "WHERE goal_value IS NOT NULL"
    )
    
    op.execute(
        "CREATE INDEX idx_player_stats_season_player_goal_value "
        "ON player_stats(season_id, player_id, goal_value) "
        "WHERE goal_value IS NOT NULL"
    )
    
    op.create_index(
        'idx_player_stats_season_team_player',
        'player_stats',
        ['season_id', 'team_id', 'player_id']
    )
    
    op.create_index(
        'idx_matches_date',
        'matches',
        ['date']
    )
    
    op.execute(
        "CREATE INDEX idx_events_goal_value "
        "ON events(goal_value) "
        "WHERE goal_value IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index('idx_events_goal_value', table_name='events')
    op.drop_index('idx_matches_date', table_name='matches')
    op.drop_index('idx_player_stats_season_team_player', table_name='player_stats')
    op.execute("DROP INDEX IF EXISTS idx_player_stats_season_player_goal_value")
    op.execute("DROP INDEX IF EXISTS idx_player_stats_player_goal_value")
