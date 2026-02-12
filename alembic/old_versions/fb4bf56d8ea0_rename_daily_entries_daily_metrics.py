"""rename daily_entries -> daily_metrics

Revision ID: fb4bf56d8ea0
Revises: c737b9d53143
Create Date: 2026-01-02 21:38:56.769969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb4bf56d8ea0'
down_revision: Union[str, None] = 'c737b9d53143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('daily_entries', 'daily_metrics')


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('daily_metrics', 'daily_entries')
