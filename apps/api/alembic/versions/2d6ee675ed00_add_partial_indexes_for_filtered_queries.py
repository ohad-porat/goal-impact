"""add partial indexes for filtered queries

Revision ID: 2d6ee675ed00
Revises: 5d13cbaa0d0f
Create Date: 2025-11-01 23:57:27.240055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d6ee675ed00'
down_revision: Union[str, None] = '5d13cbaa0d0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('idx_player_stats_goal_value', table_name='player_stats')
    op.drop_index('idx_team_stats_ranking', table_name='team_stats')
    
    op.execute(
        "CREATE INDEX idx_player_stats_goal_value_partial "
        "ON player_stats(goal_value) WHERE goal_value IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX idx_team_stats_ranking_partial "
        "ON team_stats(ranking) WHERE ranking IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index('idx_player_stats_goal_value_partial', table_name='player_stats')
    op.drop_index('idx_team_stats_ranking_partial', table_name='team_stats')
    
    op.create_index('idx_player_stats_goal_value', 'player_stats', ['goal_value'])
    op.create_index('idx_team_stats_ranking', 'team_stats', ['ranking'])
