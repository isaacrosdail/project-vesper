"""rename tasks due date to due datetime

Revision ID: 737328abcd51
Revises: 01089882687c
Create Date: 2026-08-15 17:56:14.687038+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '737328abcd51'
down_revision: Union[str, None] = '01089882687c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('tasks', 'due_date', new_column_name='due_datetime')
    op.drop_index('ix_tasks_user_due_date', 'tasks')
    op.create_index('ix_tasks_user_due_datetime', 'tasks', ['user_id', 'due_datetime'])
    op.execute('ALTER TABLE tasks RENAME CONSTRAINT ck_tasks_frog_requires_due_date TO ck_tasks_frog_requires_due_datetime')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('ALTER TABLE tasks RENAME CONSTRAINT '
                'ck_tasks_frog_requires_due_datetime TO ck_tasks_frog_requires_due_date')
    op.drop_index('ix_tasks_user_due_datetime', table_name='tasks')
    op.alter_column('tasks', 'due_datetime', new_column_name='due_date')
    op.create_index('ix_tasks_user_due_date', 'tasks', ['user_id', 'due_date'])
