"""Add soft delete column to products

Revision ID: 6846eb5b0d4e
Revises: 08e2b3e89f81
Create Date: 2025-06-26 19:12:36.267817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6846eb5b0d4e'
down_revision: Union[str, None] = '08e2b3e89f81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'deleted_at')
    # ### end Alembic commands ###
