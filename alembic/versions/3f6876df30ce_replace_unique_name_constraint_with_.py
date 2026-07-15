"""replace unique name constraint with partial index tasks

Revision ID: 3f6876df30ce
Revises: 011ebd7315fb
Create Date: 2026-07-15 15:43:02.233878+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f6876df30ce'
down_revision: Union[str, None] = '011ebd7315fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('uq_user_task_name'), 'tasks', type_='unique')
    op.create_index(
        'uq_user_task_name',
        'tasks',
        ['user_id', 'name'],
        unique=True,
        postgresql_where=sa.text('completed_at IS NULL')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_user_task_name', table_name='tasks', postgresql_where=sa.text('completed_at IS NULL'))
    op.create_unique_constraint(op.f('uq_user_task_name'), 'tasks', ['user_id', 'name'], postgresql_nulls_not_distinct=False)
