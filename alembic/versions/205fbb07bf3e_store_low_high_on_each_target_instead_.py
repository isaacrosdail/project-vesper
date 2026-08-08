"""store low/high on each target instead of kinds

Revision ID: 205fbb07bf3e
Revises: ff217dd80e72
Create Date: 2026-08-08 00:24:34.758625+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '205fbb07bf3e'
down_revision: Union[str, None] = 'ff217dd80e72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop constraints referencing the kind/value/tolerance columns first.
    # DROP COLUMN would take these implicitly, but then downgrade wouldn't restore them.
    op.drop_constraint(op.f("ck_habits_habit_type_shapes"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habits_target_positive"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habits_target_tolerance_only_exists_on_within_typed_habits"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habits_target_tolerance_positive"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_group_all_or_nothing"), "habit_completions", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_requires_value"), "habit_completions", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_tolerance_only_on_within"), "habit_completions", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_tolerance_positive"), "habit_completions", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_value_positive"), "habit_completions", type_="check")

    op.add_column("habits", sa.Column("target_low", sa.Float(), nullable=True))
    op.add_column("habits", sa.Column("target_high", sa.Float(), nullable=True))
    op.add_column("habit_completions", sa.Column("target_low_snapshot", sa.Float(), nullable=True))
    op.add_column("habit_completions", sa.Column("target_high_snapshot", sa.Float(), nullable=True))

    # (kind, value, tolerance) -> (low, high). CASE with no ELSE yields NULL for the open side.
    op.execute("""
        UPDATE habits SET
            target_low = CASE
                WHEN target_kind = 'at_least' THEN target_value
                WHEN target_kind = 'within'   THEN target_value - target_tolerance
            END,
            target_high = CASE
                WHEN target_kind = 'at_most'  THEN target_value
                WHEN target_kind = 'within'   THEN target_value + target_tolerance
            END
        WHERE target_kind IS NOT NULL
    """)
    op.execute("""
        UPDATE habit_completions SET
            target_low_snapshot = CASE
                WHEN target_kind_snapshot = 'at_least' THEN target_value_snapshot
                WHEN target_kind_snapshot = 'within'   THEN target_value_snapshot - target_tolerance_snapshot
            END,
            target_high_snapshot = CASE
                WHEN target_kind_snapshot = 'at_most'  THEN target_value_snapshot
                WHEN target_kind_snapshot = 'within'   THEN target_value_snapshot + target_tolerance_snapshot
            END
        WHERE target_kind_snapshot IS NOT NULL
    """)

    op.drop_column("habits", "target_tolerance")
    op.drop_column("habits", "target_value")
    op.drop_column("habits", "target_kind")
    op.drop_column("habit_completions", "target_tolerance_snapshot")
    op.drop_column("habit_completions", "target_value_snapshot")
    op.drop_column("habit_completions", "target_kind_snapshot")

    op.create_check_constraint(
        op.f("ck_habits_habit_type_shapes"), "habits",
        "(type = 'binary' AND num_nonnulls(target_low, target_high, units) = 0) "
        "OR (type = 'numeric_value') "
        "OR (type = 'duration' AND units IS NULL)",
    )
    op.create_check_constraint(
        op.f("ck_habits_target_positive"), "habits",
        "target_low > 0 AND target_high > 0",
    )
    op.create_check_constraint(
        op.f("ck_habits_low_le_high"), "habits",
        "target_low <= target_high",
    )
    op.create_check_constraint(
        op.f("ck_habit_completions_snapshot_requires_value"), "habit_completions",
        "num_nonnulls(target_low_snapshot, target_high_snapshot) = 0 OR value IS NOT NULL",
    )
    op.create_check_constraint(
        op.f("ck_habit_completions_snapshot_targets_positive"), "habit_completions",
        "target_low_snapshot > 0 AND target_high_snapshot > 0",
    )
    op.create_check_constraint(
        op.f("ck_habit_completions_low_snapshot_le_high_snapshot"), "habit_completions",
        "target_low_snapshot <= target_high_snapshot"
    )

    op.execute("DROP TYPE target_kind_enum")


def downgrade() -> None:
    """Downgrade schema."""
    target_kind_enum = postgresql.ENUM("at_least", "at_most", "within", name="target_kind_enum")
    target_kind_enum.create(op.get_bind(), checkfirst=True)

    op.drop_constraint(op.f("ck_habits_habit_type_shapes"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habits_target_positive"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habits_low_le_high"), "habits", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_requires_value"), "habit_completions", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_snapshot_targets_positive"), "habit_completions", type_="check")
    op.drop_constraint(op.f("ck_habit_completions_low_snapshot_le_high_snapshot"), "habit_completions", type_="check")

    # create_type=False
    op.add_column("habits", sa.Column("target_kind", postgresql.ENUM(name="target_kind_enum", create_type=False), autoincrement=False, nullable=True))
    op.add_column("habits", sa.Column("target_value", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column("habits", sa.Column("target_tolerance", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column("habit_completions", sa.Column("target_kind_snapshot", postgresql.ENUM(name="target_kind_enum", create_type=False), autoincrement=False, nullable=True))
    op.add_column("habit_completions", sa.Column("target_value_snapshot", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column("habit_completions", sa.Column("target_tolerance_snapshot", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    ## NOTE: Previously, point targets (those with tolerance of 0, ie low = high) weren't valid since
    #  tolerance has a constraint for > 0. For downgrade here, we'll use:
    # THEN GREATEST((target_high - target_low) / 2, 1e-9)
    # so that they clear the tolerance > 0 check
    op.execute("""
        UPDATE habits SET
            target_kind = (CASE
                WHEN target_low IS NOT NULL AND target_high IS NOT NULL THEN 'within'
                WHEN target_low IS NOT NULL THEN 'at_least'
                WHEN target_high IS NOT NULL THEN 'at_most'
            END)::target_kind_enum,
            target_value = CASE
                WHEN target_low IS NOT NULL AND target_high IS NOT NULL
                    THEN (target_low + target_high) / 2
                WHEN target_low IS NOT NULL THEN target_low
                ELSE target_high
            END,
            target_tolerance = CASE
                WHEN target_low IS NOT NULL AND target_high IS NOT NULL
                    THEN GREATEST((target_high - target_low) / 2, 1e-9)
            END
        WHERE num_nonnulls(target_low, target_high) > 0
    """)
    op.execute("""
        UPDATE habit_completions SET
            target_kind_snapshot = (CASE
                WHEN target_low_snapshot IS NOT NULL AND target_high_snapshot IS NOT NULL THEN 'within'
                WHEN target_low_snapshot IS NOT NULL THEN 'at_least'
                WHEN target_high_snapshot IS NOT NULL THEN 'at_most'
            END)::target_kind_enum,
            target_value_snapshot = CASE
                WHEN target_low_snapshot IS NOT NULL AND target_high_snapshot IS NOT NULL
                    THEN (target_low_snapshot + target_high_snapshot) / 2
                WHEN target_low_snapshot IS NOT NULL THEN target_low_snapshot
                ELSE target_high_snapshot
            END,
            target_tolerance_snapshot = CASE
                WHEN target_low_snapshot IS NOT NULL AND target_high_snapshot IS NOT NULL
                    THEN GREATEST((target_high_snapshot - target_low_snapshot) / 2, 1e-9)
            END
        WHERE num_nonnulls(target_low_snapshot, target_high_snapshot) > 0
    """)

    op.drop_column("habits", "target_high")
    op.drop_column("habits", "target_low")
    op.drop_column("habit_completions", "target_high_snapshot")
    op.drop_column("habit_completions", "target_low_snapshot")

    op.create_check_constraint(
        op.f("ck_habits_habit_type_shapes"), "habits",
        "(type = 'binary' AND num_nonnulls(target_kind, target_value, target_tolerance, units) = 0) "
        "OR (type = 'numeric_value' AND num_nulls(target_kind, target_value) IN (0, 2)) "
        "OR (type = 'duration' AND units IS NULL AND num_nulls(target_kind, target_value) IN (0, 2))",
    )
    op.create_check_constraint(op.f("ck_habits_target_positive"), "habits", "target_value > 0")
    op.create_check_constraint(
        op.f("ck_habits_target_tolerance_only_exists_on_within_typed_habits"), "habits",
        "(target_kind = 'within' AND target_tolerance IS NOT NULL) "
        "OR (target_kind != 'within' AND target_tolerance IS NULL) "
        "OR (target_kind IS NULL AND target_tolerance IS NULL)",
    )
    op.create_check_constraint(op.f("ck_habits_target_tolerance_positive"), "habits", "target_tolerance > 0")
    op.create_check_constraint(
        op.f("ck_habit_completions_snapshot_group_all_or_nothing"), "habit_completions",
        "num_nulls(target_kind_snapshot, target_value_snapshot) IN (0, 2)",
    )
    op.create_check_constraint(
        op.f("ck_habit_completions_snapshot_requires_value"), "habit_completions",
        "target_kind_snapshot IS NULL OR value IS NOT NULL",
    )
    op.create_check_constraint(
        op.f("ck_habit_completions_snapshot_tolerance_only_on_within"), "habit_completions",
        "(target_kind_snapshot = 'within' AND target_tolerance_snapshot IS NOT NULL) "
        "OR (target_kind_snapshot != 'within' AND target_tolerance_snapshot IS NULL) "
        "OR (target_kind_snapshot IS NULL AND target_tolerance_snapshot IS NULL)",
    )
    op.create_check_constraint(op.f("ck_habit_completions_snapshot_tolerance_positive"), "habit_completions", "target_tolerance_snapshot > 0")
    op.create_check_constraint(op.f("ck_habit_completions_snapshot_value_positive"), "habit_completions", "target_value_snapshot > 0")
