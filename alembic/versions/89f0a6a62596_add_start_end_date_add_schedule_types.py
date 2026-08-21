"""add start/end date, add schedule types

Revision ID: 89f0a6a62596
Revises: 737328abcd51
Create Date: 2026-08-20 22:20:43.541085+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '89f0a6a62596'
down_revision: Union[str, None] = '737328abcd51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('habits', sa.Column('start_date', sa.Date(), nullable=True))
    # Backfill start_dates using created_at:
    op.execute("UPDATE habits SET start_date = created_at::date")
    op.alter_column('habits', 'start_date', nullable=False)

    op.add_column('habits', sa.Column('end_date', sa.Date(), nullable=True))
    op.create_check_constraint(op.f('ck_habits_end_date_after_start_date'), 'habits', "end_date >= start_date")

    # Also seed this nullable=True, seed, nullable=False
    sa.Enum('frequency', 'weekly', 'monthly', 'interval', name='schedule_type_enum').create(op.get_bind())
    op.add_column('habits', sa.Column('schedule_type', sa.Enum('frequency', 'weekly', 'monthly', 'interval', name='schedule_type_enum'), nullable=True))
    op.execute("UPDATE habits SET schedule_type = 'frequency'")
    op.alter_column('habits', 'schedule_type', nullable=False)

    op.add_column('habits', sa.Column('scheduled_days', postgresql.ARRAY(sa.Integer()), nullable=True))
    op.add_column('habits', sa.Column('monthly_days', postgresql.ARRAY(sa.Integer()), nullable=True))
    op.add_column('habits', sa.Column('interval_days', sa.Integer(), nullable=True))
    op.alter_column('habits', 'weekly_frequency',
               existing_type=sa.INTEGER(),
               nullable=True)

    op.create_check_constraint(op.f('ck_habits_schedule_shapes'), 'habits', """
        num_nonnulls(weekly_frequency, scheduled_days, monthly_days, interval_days) = 1
        AND ((schedule_type = 'frequency' AND weekly_frequency IS NOT NULL)
        OR (schedule_type = 'weekly' AND scheduled_days IS NOT NULL)
        OR (schedule_type = 'monthly' AND monthly_days IS NOT NULL)
        OR (schedule_type = 'interval' AND interval_days IS NOT NULL))
""")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('ck_habits_schedule_shapes'), 'habits')
    op.drop_constraint(op.f('ck_habits_end_date_after_start_date'), 'habits')

    # Reverse backfill (lossy :( )
    op.execute("""
        UPDATE habits SET weekly_frequency = COALESCE(weekly_frequency,
            CASE WHEN schedule_type = 'weekly' THEN array_length(scheduled_days, 1) ELSE 1 END)
""")
    op.alter_column('habits', 'weekly_frequency',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('habits', 'interval_days')
    op.drop_column('habits', 'monthly_days')
    op.drop_column('habits', 'scheduled_days')
    op.drop_column('habits', 'schedule_type')
    op.execute("DROP TYPE schedule_type_enum")

    op.drop_column('habits', 'end_date')
    op.drop_column('habits', 'start_date')
