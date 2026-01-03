"""drop abvariantenum type

Revision ID: c737b9d53143
Revises: c77d567dce10
Create Date: 2026-01-02 20:38:00.297399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c737b9d53143'
down_revision: Union[str, None] = 'c77d567dce10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TYPE IF EXISTS abvariantenum CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("CREATE TYPE abvariantenum AS ENUM ('A', 'B')")
