"""add demo to user role enum

Revision ID: 4813d8fa6ac3
Revises: 7dd05acb7fb9
Create Date: 2026-07-17 03:40:20.251572+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4813d8fa6ac3'
down_revision: Union[str, None] = '7dd05acb7fb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE user_role_enum ADD VALUE 'demo'")

def downgrade() -> None:
    """Downgrade schema."""
    # Postgres can't DROP a value/member from an enum. Would entail recreating the type and
    #  rewriting every column that uses it - not worth it.
