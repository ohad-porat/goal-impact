"""remove_points_added_columns

Revision ID: 999172017925
Revises: d707e75e22c9
Create Date: 2025-10-15 17:33:43.227280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '999172017925'
down_revision: Union[str, None] = 'd707e75e22c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop points_added column from events table
    op.drop_column('events', 'points_added')
    
    # Drop points_added and pa_avg columns from player_stats table
    op.drop_column('player_stats', 'points_added')
    op.drop_column('player_stats', 'pa_avg')


def downgrade() -> None:
    # Add back points_added column to events table
    op.add_column('events', sa.Column('points_added', sa.Float(), nullable=True))
    
    # Add back points_added and pa_avg columns to player_stats table
    op.add_column('player_stats', sa.Column('points_added', sa.Float(), nullable=True))
    op.add_column('player_stats', sa.Column('pa_avg', sa.Float(), nullable=True))
