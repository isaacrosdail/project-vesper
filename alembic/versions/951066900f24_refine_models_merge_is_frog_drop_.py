"""refine models: merge is_frog, drop promotion threshold, add weight units, tighten cosntraints

Revision ID: 951066900f24
Revises: 5cdf18e58c67
Create Date: 2026-03-09 20:07:08.273761+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '951066900f24'
down_revision: Union[str, None] = '5cdf18e58c67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Drop constraints that ref cols we're about to drop
    op.drop_constraint('ck_frog_priority_mutually_exclusive', 'tasks', type_='check')
    op.drop_constraint('ck_frog_requires_due_date', 'tasks', type_='check')
    op.drop_constraint('ck_promotion_threshold_range_0_1', 'habits', type_='check')

    # 2. Enum shuffle + backfill
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR")
    op.execute("DROP TYPE priority_enum")
    op.execute("CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high', 'frog')")
    op.execute("UPDATE tasks SET priority = 'frog' WHERE is_frog = true")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE priority_enum USING priority::priority_enum")

    # 3. Alter + drop columns
    op.alter_column('tasks', 'priority', existing_type=postgresql.ENUM('low', 'medium', 'high', 'frog', name='priority_enum'), nullable=False)
    op.drop_column('tasks', 'is_frog')
    op.drop_column('tasks', 'is_done')
    op.drop_column('habits', 'promotion_threshold')

    # 4. Add weight_units col
    op.execute("CREATE TYPE weight_units_enum AS ENUM ('lbs', 'kg')")
    op.add_column('daily_metrics', sa.Column('weight_units', sa.Enum('lbs', 'kg', name='weight_units_enum', create_type=False), nullable=True))
    # Backfill: existing weight entries were stored in kg
    op.execute("UPDATE daily_metrics SET weight_units = 'kg' WHERE weight IS NOT NULL")

    # 5. Swap metrics constraints
    op.drop_constraint('ck_steps_non_negative', 'daily_metrics', type_='check')
    op.drop_constraint('ck_calories_non_negative', 'daily_metrics', type_='check')

    # 6. Add new constraints
    op.create_check_constraint('frog_requires_due_date', 'tasks', "priority != 'frog' OR due_date IS NOT NULL")
    op.create_check_constraint('steps_positive', 'daily_metrics', 'steps > 0')
    op.create_check_constraint('calories_positive', 'daily_metrics', 'calories > 0')
    op.create_check_constraint('weight_requires_units', 'daily_metrics', '(weight IS NULL AND weight_units IS NULL) OR (weight IS NOT NULL AND weight_units IS NOT NULL)')



def downgrade() -> None:
    """Downgrade schema."""
    # Drop constraints
    op.drop_constraint('weight_requires_units', 'daily_metrics', type_='check')
    op.drop_constraint('calories_positive', 'daily_metrics', type_='check')
    op.drop_constraint('steps_positive', 'daily_metrics', type_='check')
    op.drop_constraint('frog_requires_due_date', 'tasks', type_='check')

    # Restore old metrics constraints
    op.create_check_constraint('ck_steps_non_negative', 'daily_metrics', 'steps >= 0')
    op.create_check_constraint('ck_calories_non_negative', 'daily_metrics', 'calories >= 0')

    # Drop weight_units
    op.drop_column('daily_metrics', 'weight_units')
    op.execute("DROP TYPE weight_units_enum")

    # Re-add dropped columns
    op.add_column('habits', sa.Column('promotion_threshold', sa.DOUBLE_PRECISION(), nullable=True))
    op.add_column('tasks', sa.Column('is_done', sa.BOOLEAN(), server_default=sa.text('false'), nullable=False))
    op.add_column('tasks', sa.Column('is_frog', sa.BOOLEAN(), server_default=sa.text('false'), nullable=False))

    # Priority back to nullable, backfill is_frog from 'frog' priority
    op.alter_column('tasks', 'priority', existing_type=postgresql.ENUM('low', 'medium', 'high', 'frog', name='priority_enum'), nullable=True)

    # Backfill is_frog from 'frog' priority (before constraints go back)
    op.execute("UPDATE tasks SET is_frog = true WHERE priority = 'frog'")
    op.execute("UPDATE tasks SET priority = NULL WHERE priority = 'frog'")

    # Restore old constraints
    op.create_check_constraint('ck_promotion_threshold_range_0_1', 'habits', 'promotion_threshold IS NULL OR (promotion_threshold >= 0 AND promotion_threshold <= 1.0)')
    op.create_check_constraint('ck_frog_requires_due_date', 'tasks', 'NOT is_frog OR due_date IS NOT NULL')
    op.create_check_constraint('ck_frog_priority_mutually_exclusive', 'tasks', '(is_frog = true AND priority IS NULL) OR (NOT is_frog AND priority IS NOT NULL)')

    # Enum shuffle back (remove 'frog')
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR")
    op.execute("DROP TYPE priority_enum")
    op.execute("CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high')")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE priority_enum USING priority::priority_enum")

