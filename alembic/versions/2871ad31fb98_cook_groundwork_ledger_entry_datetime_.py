"""cook groundwork: ledger entry_datetime & sign constraint, nutrition_logs recipe id, quantity cols to numeric

Revision ID: 2871ad31fb98
Revises: 882e7452bc71
Create Date: 2026-07-07 20:33:34.215483+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2871ad31fb98'
down_revision: Union[str, None] = '882e7452bc71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    ## Thus far, no write path exists for inventory_ledgers anyway, so there should be no need to backfill/server_default
    # for this entry_datetime add here
    op.add_column('inventory_ledgers', sa.Column('entry_datetime', sa.DateTime(timezone=True), nullable=False))
    op.alter_column('inventory_ledgers', 'qty_delta',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=12, scale=3),
               existing_nullable=False)
    op.drop_index(op.f('ix_inventory_ledger_product_created'), table_name='inventory_ledgers')
    op.create_index('ix_inventory_ledger_user_product_entry', 'inventory_ledgers', ['user_id', 'product_id', 'entry_datetime'], unique=False)
    op.add_column('nutrition_logs', sa.Column('recipe_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_nutrition_logs_recipe_id_recipes'), 'nutrition_logs', 'recipes', ['recipe_id'], ['id'], ondelete='SET NULL')
    op.alter_column('product_inventories', 'qty_on_hand',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=12, scale=3),
               existing_nullable=False)
    op.drop_constraint(op.f('uq_product_inventories_product_id'), 'product_inventories', type_='unique')
    op.create_unique_constraint('uq_product_inventory_user_product', 'product_inventories', ['user_id', 'product_id'])
    op.alter_column('recipe_ingredients', 'amount_value',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Numeric(precision=12, scale=3),
               existing_nullable=False)
    op.alter_column('recipes', 'yields',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Numeric(precision=12, scale=3),
               existing_nullable=False)
    op.create_check_constraint(
        op.f("ck_product_net_weight_positive"), "products", "net_weight > 0",
    )
    op.create_check_constraint(
        op.f("ck_inventory_ledger_delta_sign"), "inventory_ledgers",
        "(event_type = 'purchase' AND qty_delta > 0) OR "
        "(event_type IN ('consumption', 'waste') AND qty_delta < 0) OR "
        "(event_type = 'correction' AND qty_delta != 0)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("ck_inventory_ledger_delta_sign"), "inventory_ledgers")
    op.drop_constraint(op.f("ck_product_net_weight_positive"), "products")
    op.alter_column('recipes', 'yields',
               existing_type=sa.Numeric(precision=12, scale=3),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)
    op.alter_column('recipe_ingredients', 'amount_value',
               existing_type=sa.Numeric(precision=12, scale=3),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)
    op.drop_constraint('uq_product_inventory_user_product', 'product_inventories', type_='unique')
    op.create_unique_constraint(op.f('uq_product_inventories_product_id'), 'product_inventories', ['product_id'], postgresql_nulls_not_distinct=False)
    op.alter_column('product_inventories', 'qty_on_hand',
               existing_type=sa.Numeric(precision=12, scale=3),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_constraint(op.f('fk_nutrition_logs_recipe_id_recipes'), 'nutrition_logs', type_='foreignkey')
    op.drop_column('nutrition_logs', 'recipe_id')
    op.drop_index('ix_inventory_ledger_user_product_entry', table_name='inventory_ledgers')
    op.create_index(op.f('ix_inventory_ledger_product_created'), 'inventory_ledgers', ['product_id', 'created_at'], unique=False)
    op.alter_column('inventory_ledgers', 'qty_delta',
               existing_type=sa.Numeric(precision=12, scale=3),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_column('inventory_ledgers', 'entry_datetime')
