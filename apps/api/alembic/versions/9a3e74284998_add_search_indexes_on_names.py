"""add_search_indexes_on_names

Revision ID: 9a3e74284998
Revises: 2d6ee675ed00
Create Date: 2025-11-04 16:09:48.179026

"""
from typing import Sequence, Union

from alembic import op


revision: str = '9a3e74284998'
down_revision: Union[str, None] = '2d6ee675ed00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_players_name', 'players', ['name'])
    op.create_index('idx_teams_name', 'teams', ['name'])
    op.create_index('idx_competitions_name', 'competitions', ['name'])
    op.create_index('idx_nations_name', 'nations', ['name'])


def downgrade() -> None:
    op.drop_index('idx_nations_name', table_name='nations')
    op.drop_index('idx_competitions_name', table_name='competitions')
    op.drop_index('idx_teams_name', table_name='teams')
    op.drop_index('idx_players_name', table_name='players')
