"""typed habits: targets + completion values with goals snapshots

Revision ID: 0253a41020e0
Revises: a6690e87104b
Create Date: 2026-08-06 00:07:06.028421+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0253a41020e0'
down_revision: Union[str, None] = 'a6690e87104b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

habit_type_enum = sa.Enum('binary', 'numeric_value', 'duration', name='habit_type_enum')
target_kind_enum = sa.Enum('at_least', 'at_most', 'within', name='target_kind_enum')


def upgrade() -> None:
    """Upgrade schema."""
    habit_type_enum.create(op.get_bind())
    target_kind_enum.create(op.get_bind())

    # -- habits: rename + repair before the constraint that assumes it --
    op.alter_column('habits', 'target_frequency', new_column_name='weekly_frequency')
    op.execute("UPDATE habits SET weekly_frequency = LEAST(GREATEST(weekly_frequency, 1), 7)")

    op.add_column('habits', sa.Column(
        'type',
        postgresql.ENUM(name='habit_type_enum', create_type=False),
        nullable=False, server_default='binary',
    ))
    op.add_column('habits', sa.Column('target_value', sa.Float(), nullable=True))
    op.add_column('habits', sa.Column(
        'target_kind',
        postgresql.ENUM(name='target_kind_enum', create_type=False),
        nullable=True,
    ))
    op.add_column('habits', sa.Column('target_tolerance', sa.Float(), nullable=True))
    op.add_column('habits', sa.Column('units', sa.String(length=50), nullable=True))

    # -- habit_completions: rename + new columns --
    op.alter_column('habit_completions', 'completed_on', new_column_name='entry_date')
    op.add_column('habit_completions', sa.Column('value', sa.Float(), nullable=True))
    op.add_column('habit_completions', sa.Column(
        'target_kind_snapshot',
        postgresql.ENUM(name='target_kind_enum', create_type=False),
        nullable=True,
    ))
    op.add_column('habit_completions', sa.Column('target_value_snapshot', sa.Float(), nullable=True))
    op.add_column('habit_completions', sa.Column('target_tolerance_snapshot', sa.Float(), nullable=True))

    # index/unique renamed via drop+recreate (definitions survive the column rename; names don't)
    op.drop_index(op.f('ix_habit_completions_user_habit_completed_on'), table_name='habit_completions')
    op.drop_constraint(op.f('uq_habit_completions_habit_id_completed_on'), 'habit_completions', type_='unique')
    op.create_index('ix_habit_completions_user_habit_entry_date', 'habit_completions', ['user_id', 'habit_id', 'entry_date'], unique=False)
    op.create_unique_constraint('uq_habit_completions_habit_id_entry_date', 'habit_completions', ['habit_id', 'entry_date'])

    # -- CHECKs last: they assume the columns and repaired data above --
    # habits: shapes must stay in sync with models.py & the Target union (app/shared/target.py)
    op.create_check_constraint(
        op.f('ck_habits_habit_type_shapes'), 'habits',
        "(type = 'binary' AND num_nonnulls(target_kind, target_value, target_tolerance, units) = 0) "
        "OR (type = 'numeric_value' AND num_nulls(target_kind, target_value) IN (0, 2)) "
        "OR (type = 'duration' AND units IS NULL AND num_nulls(target_kind, target_value) IN (0, 2))",
    )
    op.create_check_constraint(
        op.f('ck_habits_target_tolerance_only_exists_on_within_typed_habits'), 'habits',
        "(target_kind = 'within' AND target_tolerance IS NOT NULL) "
        "OR (target_kind != 'within' AND target_tolerance IS NULL) "
        "OR (target_kind IS NULL AND target_tolerance IS NULL)",
    )
    op.create_check_constraint(op.f('ck_habits_weekly_frequency_range'), 'habits', "weekly_frequency BETWEEN 1 AND 7")
    op.create_check_constraint(op.f('ck_habits_target_positive'), 'habits', "target_value > 0")
    op.create_check_constraint(op.f('ck_habits_target_tolerance_positive'), 'habits', "target_tolerance > 0")

    # habit_completions
    op.create_check_constraint(
        op.f('ck_habit_completions_snapshot_group_all_or_nothing'), 'habit_completions',
        "num_nulls(target_kind_snapshot, target_value_snapshot) IN (0, 2)",
    )
    op.create_check_constraint(
        op.f('ck_habit_completions_snapshot_tolerance_only_on_within'), 'habit_completions',
        "(target_kind_snapshot = 'within' AND target_tolerance_snapshot IS NOT NULL) "
        "OR (target_kind_snapshot != 'within' AND target_tolerance_snapshot IS NULL) "
        "OR (target_kind_snapshot IS NULL AND target_tolerance_snapshot IS NULL)",
    )
    op.create_check_constraint(
        op.f('ck_habit_completions_snapshot_requires_value'), 'habit_completions',
        "target_kind_snapshot IS NULL OR value IS NOT NULL",
    )
    op.create_check_constraint(op.f('ck_habit_completions_value_nonnegative'), 'habit_completions', "value >= 0")
    op.create_check_constraint(op.f('ck_habit_completions_snapshot_value_positive'), 'habit_completions', "target_value_snapshot > 0")
    op.create_check_constraint(op.f('ck_habit_completions_snapshot_tolerance_positive'), 'habit_completions', "target_tolerance_snapshot > 0")


def downgrade() -> None:
    """Downgrade schema."""
    # CHECKs first (reverse of upgrade)
    op.drop_constraint(op.f('ck_habit_completions_snapshot_tolerance_positive'), 'habit_completions')
    op.drop_constraint(op.f('ck_habit_completions_snapshot_value_positive'), 'habit_completions')
    op.drop_constraint(op.f('ck_habit_completions_value_nonnegative'), 'habit_completions')
    op.drop_constraint(op.f('ck_habit_completions_snapshot_requires_value'), 'habit_completions')
    op.drop_constraint(op.f('ck_habit_completions_snapshot_tolerance_only_on_within'), 'habit_completions')
    op.drop_constraint(op.f('ck_habit_completions_snapshot_group_all_or_nothing'), 'habit_completions')
    op.drop_constraint(op.f('ck_habits_target_tolerance_positive'), 'habits')
    op.drop_constraint(op.f('ck_habits_target_positive'), 'habits')
    op.drop_constraint(op.f('ck_habits_weekly_frequency_range'), 'habits')
    op.drop_constraint(op.f('ck_habits_target_tolerance_only_exists_on_within_typed_habits'), 'habits')
    op.drop_constraint(op.f('ck_habits_habit_type_shapes'), 'habits')

    # habit_completions
    op.drop_constraint('uq_habit_completions_habit_id_entry_date', 'habit_completions', type_='unique')
    op.drop_index('ix_habit_completions_user_habit_entry_date', table_name='habit_completions')
    op.drop_column('habit_completions', 'target_tolerance_snapshot')
    op.drop_column('habit_completions', 'target_value_snapshot')
    op.drop_column('habit_completions', 'target_kind_snapshot')
    op.drop_column('habit_completions', 'value')
    op.alter_column('habit_completions', 'entry_date', new_column_name='completed_on')
    op.create_unique_constraint(op.f('uq_habit_completions_habit_id_completed_on'), 'habit_completions', ['habit_id', 'completed_on'])
    op.create_index(op.f('ix_habit_completions_user_habit_completed_on'), 'habit_completions', ['user_id', 'habit_id', 'completed_on'], unique=False)

    # habits
    op.drop_column('habits', 'units')
    op.drop_column('habits', 'target_tolerance')
    op.drop_column('habits', 'target_kind')
    op.drop_column('habits', 'target_value')
    op.drop_column('habits', 'type')
    op.alter_column('habits', 'weekly_frequency', new_column_name='target_frequency')

    # enum types last: columns using them are gone now
    target_kind_enum.drop(op.get_bind())
    habit_type_enum.drop(op.get_bind())
