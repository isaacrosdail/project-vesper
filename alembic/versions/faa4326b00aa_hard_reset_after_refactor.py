"""HARD RESET after refactor

Revision ID: faa4326b00aa
Revises: e682fc5fb1e7
Create Date: 2025-08-19 21:27:34.087723

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'faa4326b00aa'
down_revision: Union[str, None] = 'e682fc5fb1e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Thanos snap."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    table_names = [t for t in inspector.get_table_names() if t != 'alembic_version']

    # Drop foreign key constraints first
    for table_name in table_names:
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            op.drop_constraint(fk['name'], table_name, type_='foreignkey')

    # Drop all tables
    for table_name in table_names:
        op.drop_table(table_name)


def downgrade() -> None:
    """Error: Cannot undo."""
    pass
