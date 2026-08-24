"""remove is_checked from shopping list items

Revision ID: 53899236ad87
Revises: 89f0a6a62596
Create Date: 2026-08-24 00:28:17.446296+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53899236ad87'
down_revision: Union[str, None] = '89f0a6a62596'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('shopping_list_items', 'is_checked')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('shopping_list_items', sa.Column('is_checked', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
