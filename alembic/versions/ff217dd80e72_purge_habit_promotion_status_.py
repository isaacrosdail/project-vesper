"""purge habit promotion: status, established date, status_enum

Revision ID: ff217dd80e72
Revises: 0253a41020e0
Create Date: 2026-08-06 21:49:39.255222+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ff217dd80e72'
down_revision: Union[str, None] = '0253a41020e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Also removed CheckConstraint for established requires established status; dropped when columns are dropped
    op.drop_column('habits', 'established_date')
    op.drop_column('habits', 'status')
    sa.Enum(name="status_enum").drop(op.get_bind())


def downgrade() -> None:
    """Downgrade schema."""
    sa.Enum('experimental', 'established', name='status_enum').create(op.get_bind())
    op.add_column('habits', sa.Column('status', postgresql.ENUM('experimental', 'established', name='status_enum', create_type=False), autoincrement=False, nullable=True))
    op.add_column('habits', sa.Column('established_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.create_check_constraint(
        op.f('ck_habits_established_requires_established_status'),
        'habits',
        "established_date IS NULL OR status = 'established'",
    )
