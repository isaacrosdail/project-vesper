"""store macro goals in percentages of calories

Revision ID: 01089882687c
Revises: f68eaa750d0d
Create Date: 2026-08-12 02:33:26.508247+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01089882687c'
down_revision: Union[str, None] = 'f68eaa750d0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("user_goals", "protein", new_column_name="protein_pct", existing_type=sa.Integer())
    op.alter_column("user_goals", "carbs", new_column_name="carbs_pct", existing_type=sa.Integer())
    op.alter_column("user_goals", "fat", new_column_name="fat_pct", existing_type=sa.Integer())

    # Migrate from using grams to percents; nudge values into fitting since
    # realistically none would sum to 100 as-is
    # FLOOR since round might produce negative values
    op.execute("""
        UPDATE user_goals SET
            protein_pct = FLOOR(protein_pct * 4 * 100.0 / (protein_pct * 4 + carbs_pct * 4 + fat_pct * 9)),
            fat_pct     = FLOOR(fat_pct     * 9 * 100.0 / (protein_pct * 4 + carbs_pct * 4 + fat_pct * 9)),
            carbs_pct   = 100
                - FLOOR(protein_pct * 4 * 100.0 / (protein_pct * 4 + carbs_pct * 4 + fat_pct * 9))
                - FLOOR(fat_pct     * 9 * 100.0 / (protein_pct * 4 + carbs_pct * 4 + fat_pct * 9))
        WHERE num_nonnulls(protein_pct, carbs_pct, fat_pct) = 3
            AND protein_pct * 4 + carbs_pct * 4 + fat_pct * 9 > 0
""")
    # Since derived splits won't land on 100 as our constraint demands
    op.execute("""
        UPDATE user_goals SET protein_pct = NULL, carbs_pct = NULL, fat_pct = NULL
        WHERE num_nonnulls(protein_pct, carbs_pct, fat_pct) <> 3
            OR protein_pct + carbs_pct + fat_pct <> 100
""")

    op.create_check_constraint(op.f("ck_user_goals_macro_split_complete"), "user_goals",
        "num_nonnulls(protein_pct, carbs_pct, fat_pct) = 0 OR (num_nonnulls(protein_pct, carbs_pct, fat_pct) = 3 AND protein_pct + carbs_pct + fat_pct = 100)"
    )
    op.create_check_constraint(
        op.f("ck_user_goals_protein_pct_range"), "user_goals", "protein_pct BETWEEN 0 AND 100"
    )
    op.create_check_constraint(
        op.f("ck_user_goals_carbs_pct_range"), "user_goals", "carbs_pct BETWEEN 0 AND 100"
    )
    op.create_check_constraint(
        op.f("ck_user_goals_fat_pct_range"), "user_goals", "fat_pct BETWEEN 0 AND 100"
    )



def downgrade() -> None:
    """Downgrade schema."""
    for name in (
        "ck_user_goals_macro_split_complete",
        "ck_user_goals_protein_pct_range",
        "ck_user_goals_carbs_pct_range",
        "ck_user_goals_fat_pct_range",
    ):
        op.drop_constraint(op.f(name), "user_goals")

    # Convert pcts back into grams
    op.execute("""
        UPDATE user_goals SET
            protein_pct = ROUND(calories * protein_pct / 100.0 / 4),
            carbs_pct   = ROUND(calories * carbs_pct   / 100.0 / 4),
            fat_pct     = ROUND(calories * fat_pct     / 100.0 / 9)
        WHERE calories IS NOT NULL
            AND num_nonnulls(protein_pct, carbs_pct, fat_pct) = 3
""")
    op.execute("""
        UPDATE user_goals SET protein_pct = NULL, carbs_pct = NULL, fat_pct = NULL
        WHERE calories IS NULL
""")

    op.alter_column("user_goals", "protein_pct", new_column_name="protein", existing_type=sa.Integer())
    op.alter_column("user_goals", "carbs_pct", new_column_name="carbs", existing_type=sa.Integer())
    op.alter_column("user_goals", "fat_pct", new_column_name="fat", existing_type=sa.Integer())

