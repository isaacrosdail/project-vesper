"""change completedat to completedon as date

Revision ID: a6690e87104b
Revises: 618dfe67bac1
Create Date: 2026-07-23 03:28:33.612333+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a6690e87104b'
down_revision: Union[str, None] = '618dfe67bac1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('habit_completions', sa.Column('completed_on', sa.Date(), nullable=True))
    # Backfill completed_on:
    op.execute("""
        UPDATE habit_completions hc
        SET completed_on = (hc.completed_at AT TIME ZONE u.timezone)::date
        FROM users u
        WHERE u.id = hc.user_id
""")
    # Dedupe
    op.execute("""
        DELETE FROM habit_completions a
        USING habit_completions b
        WHERE a.habit_id = b.habit_id
            AND a.completed_on = b.completed_on
            AND a.id > b.id
""")
    op.alter_column('habit_completions', 'completed_on', nullable=False)
    op.drop_index(op.f('ix_habit_completions_user_habit_completed_at'), table_name='habit_completions')
    op.create_index('ix_habit_completions_user_habit_completed_on', 'habit_completions', ['user_id', 'habit_id', 'completed_on'], unique=False)
    op.create_unique_constraint(op.f('uq_habit_completions_habit_id_completed_on'), 'habit_completions', ['habit_id', 'completed_on'])
    op.drop_column('habit_completions', 'completed_at')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('habit_completions', sa.Column('completed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.execute("""
        UPDATE habit_completions hc
        SET completed_at = (completed_on::timestamp AT TIME ZONE u.timezone)
        FROM users u
        WHERE u.id = hc.user_id
""")
    op.alter_column('habit_completions', 'completed_at', nullable=False)
    op.drop_constraint(op.f('uq_habit_completions_habit_id_completed_on'), 'habit_completions', type_='unique')
    op.drop_index('ix_habit_completions_user_habit_completed_on', table_name='habit_completions')
    op.create_index(op.f('ix_habit_completions_user_habit_completed_at'), 'habit_completions', ['user_id', 'habit_id', 'completed_at'], unique=False)
    op.drop_column('habit_completions', 'completed_on')
