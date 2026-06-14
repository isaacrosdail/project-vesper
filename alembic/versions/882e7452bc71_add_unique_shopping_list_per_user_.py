"""add unique shopping list per user constraint

Revision ID: 882e7452bc71
Revises: 7040c9022897
Create Date: 2026-06-14 23:40:25.156850+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '882e7452bc71'
down_revision: Union[str, None] = '7040c9022897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_user_shopping_list",
        "shopping_lists",
        ["user_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_user_shopping_list",
        "shopping_lists",
        type_="unique",
    )
