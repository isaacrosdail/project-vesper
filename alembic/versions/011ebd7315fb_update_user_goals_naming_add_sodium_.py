"""update user goals naming, add sodium potassium

Revision ID: 011ebd7315fb
Revises: d2400ff2d226
Create Date: 2026-07-13 20:32:55.598110+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011ebd7315fb'
down_revision: Union[str, None] = 'd2400ff2d226'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('user_goals', 'weight_target', new_column_name='weight')
    op.alter_column('user_goals', 'calories_target', new_column_name='calories')
    op.alter_column('user_goals', 'steps_target', new_column_name='steps')
    op.alter_column('user_goals', 'protein_target', new_column_name='protein')
    op.alter_column('user_goals', 'fat_target', new_column_name='fat')
    op.alter_column('user_goals', 'carbs_target', new_column_name='carbs')
    op.alter_column('user_goals', 'sleep_minutes_target', new_column_name='sleep_duration_minutes')
    op.add_column('user_goals', sa.Column('potassium', sa.Integer(), nullable=True))
    op.add_column('user_goals', sa.Column('sodium', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('user_goals', 'weight', new_column_name='weight_target')
    op.alter_column('user_goals', 'calories', new_column_name='calories_target')
    op.alter_column('user_goals', 'steps', new_column_name='steps_target')
    op.alter_column('user_goals', 'protein', new_column_name='protein_target')
    op.alter_column('user_goals', 'fat', new_column_name='fat_target')
    op.alter_column('user_goals', 'carbs', new_column_name='carbs_target')
    op.alter_column('user_goals', 'sleep_duration_minutes', new_column_name='sleep_minutes_target')
    op.drop_column('user_goals', 'potassium')
    op.drop_column('user_goals', 'sodium')
