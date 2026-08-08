"""add product_id fkey col to nutrition log for source

Revision ID: f68eaa750d0d
Revises: 205fbb07bf3e
Create Date: 2026-08-08 17:49:15.167750+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f68eaa750d0d'
down_revision: Union[str, None] = '205fbb07bf3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('nutrition_logs', sa.Column('product_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_nutrition_logs_product_id_products'), 'nutrition_logs', 'products', ['product_id'], ['id'], ondelete='SET NULL')
    op.create_check_constraint(op.f('ck_nutrition_logs_single_log_entry_source'), 'nutrition_logs', 'NOT (recipe_id IS NOT NULL AND product_id IS NOT NULL)')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('ck_nutrition_logs_single_log_entry_source'), 'nutrition_logs')
    op.drop_constraint(op.f('fk_nutrition_logs_product_id_products'), 'nutrition_logs', type_='foreignkey')
    op.drop_column('nutrition_logs', 'product_id')
