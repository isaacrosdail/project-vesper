"""add constraints for several models.pys

Revision ID: 55d29346f6d4
Revises: 3f6876df30ce
Create Date: 2026-07-15 16:25:09.527294+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55d29346f6d4'
down_revision: Union[str, None] = '3f6876df30ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NUTRITION_FIELDS = ("calories", "protein", "fat", "carbs", "fat_mono", "fat_poly",
                    "fat_sat", "carbs_fiber", "carbs_sugar", "sodium", "potassium")

def _non_negative_sql(cols):
    return " AND ".join(f"({c} IS NULL OR {c} >= 0)" for c in cols)

def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(op.f('uq_recipe_ingredient_recipe_product'), 'recipe_ingredients', ['recipe_id', 'product_id'])

    op.create_check_constraint(
        op.f("ck_products_nutrition_non_negative"), "products",
        _non_negative_sql([f"{f}_per_100g" for f in _NUTRITION_FIELDS])
    )
    op.drop_constraint(op.f("ck_products_ck_product_calories_non_negative"), "products", type_="check")

    op.create_check_constraint(
        op.f("ck_nutrition_logs_nutrition_non_negative"), "nutrition_logs",
        _non_negative_sql(_NUTRITION_FIELDS),
    )

    op.create_check_constraint(
        op.f("ck_shopping_trips_total_price_non_negative"), "shopping_trips",
        "total_price >= 0",
    )
    op.alter_column(
        "recipes", "name",
        type_=sa.String(length=100),
        existing_type=sa.String(),
        existing_nullable=False,
    )

    op.create_check_constraint(
        op.f("ck_habits_established_requires_established_status"), "habits",
        "established_date IS NULL OR status = 'established'",
    )

    op.drop_constraint(op.f("ck_daily_metrics_calories_positive"), "daily_metrics", type_="check")
    op.create_check_constraint(op.f("ck_daily_metrics_calories_non_negative"), "daily_metrics", "calories >= 0")
    op.drop_constraint(op.f("ck_daily_metrics_steps_positive"), "daily_metrics", type_="check")
    op.create_check_constraint(op.f("ck_daily_metrics_steps_non_negative"), "daily_metrics", "steps >= 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("recipes", "name", type_=sa.String(), existing_type=sa.String(length=100), existing_nullable=False)
    op.drop_constraint(op.f("ck_shopping_trips_total_price_non_negative"), "shopping_trips", type_="check")
    op.drop_constraint(op.f("ck_nutrition_logs_nutrition_non_negative"), "nutrition_logs", type_="check")
    op.create_check_constraint(op.f("ck_products_ck_product_calories_non_negative"), "products", "calories_per_100g >= 0")
    op.drop_constraint(op.f("ck_products_nutrition_non_negative"), "products", type_="check")
    op.drop_constraint(op.f('uq_recipe_ingredient_recipe_product'), 'recipe_ingredients', type_='unique')
    op.drop_constraint(op.f('ck_habits_established_requires_established_status'), 'habits')

    op.drop_constraint(op.f("ck_daily_metrics_steps_non_negative"), "daily_metrics", type_="check")
    op.create_check_constraint(op.f("ck_daily_metrics_steps_positive"), "daily_metrics", "steps > 0")
    op.drop_constraint(op.f("ck_daily_metrics_calories_non_negative"), "daily_metrics", type_="check")
    op.create_check_constraint(op.f("ck_daily_metrics_calories_positive"), "daily_metrics", "calories > 0")
