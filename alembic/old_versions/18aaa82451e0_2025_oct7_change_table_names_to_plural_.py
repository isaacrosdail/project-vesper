"""2025_oct7_change table names to plural, update FKey declarations

Revision ID: 18aaa82451e0
Revises: b6625db1ca91
Create Date: 2025-10-07 18:51:12.587054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18aaa82451e0'
down_revision: Union[str, None] = 'b6625db1ca91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Rename all tables
    op.rename_table('apicallrecord', 'api_call_records')
    op.rename_table('user', 'users')
    op.rename_table('dailyentry', 'daily_entries')
    op.rename_table('habit', 'habits')
    op.rename_table('habitcompletion', 'habit_completions')
    op.rename_table('leetcoderecord', 'leet_code_records')
    op.rename_table('product', 'products')
    op.rename_table('shoppinglist', 'shopping_lists')
    op.rename_table('shoppinglistitem', 'shopping_list_items')
    op.rename_table('tag', 'tags')
    op.rename_table('task', 'tasks')
    op.rename_table('timeentry', 'time_entries')
    op.rename_table('transaction', 'transactions')
    
    # Update association table FKs (won't auto-update?)
    op.drop_constraint('fk_task_tags_task_id_task', 'task_tags', type_='foreignkey')
    op.drop_constraint('fk_task_tags_tag_id_tag', 'task_tags', type_='foreignkey')
    op.create_foreign_key('fk_task_tags_task_id_tasks', 'task_tags', 'tasks', ['task_id'], ['id'])
    op.create_foreign_key('fk_task_tags_tag_id_tags', 'task_tags', 'tags', ['tag_id'], ['id'])
    
    op.drop_constraint('fk_habit_tags_habit_id_habit', 'habit_tags', type_='foreignkey')
    op.drop_constraint('fk_habit_tags_tag_id_tag', 'habit_tags', type_='foreignkey')
    op.create_foreign_key('fk_habit_tags_habit_id_habits', 'habit_tags', 'habits', ['habit_id'], ['id'])
    op.create_foreign_key('fk_habit_tags_tag_id_tags', 'habit_tags', 'tags', ['tag_id'], ['id'])

def downgrade() -> None:
    # Reverse everything
    op.drop_constraint('fk_habit_tags_tag_id_tags', 'habit_tags', type_='foreignkey')
    op.drop_constraint('fk_habit_tags_habit_id_habits', 'habit_tags', type_='foreignkey')
    op.create_foreign_key('fk_habit_tags_tag_id_tag', 'habit_tags', 'tag', ['tag_id'], ['id'])
    op.create_foreign_key('fk_habit_tags_habit_id_habit', 'habit_tags', 'habit', ['habit_id'], ['id'])
    
    op.drop_constraint('fk_task_tags_tag_id_tags', 'task_tags', type_='foreignkey')
    op.drop_constraint('fk_task_tags_task_id_tasks', 'task_tags', type_='foreignkey')
    op.create_foreign_key('fk_task_tags_tag_id_tag', 'task_tags', 'tag', ['tag_id'], ['id'])
    op.create_foreign_key('fk_task_tags_task_id_task', 'task_tags', 'task', ['task_id'], ['id'])
    
    op.rename_table('transactions', 'transaction')
    op.rename_table('time_entries', 'timeentry')
    op.rename_table('tasks', 'task')
    op.rename_table('tags', 'tag')
    op.rename_table('shopping_list_items', 'shoppinglistitem')
    op.rename_table('shopping_lists', 'shoppinglist')
    op.rename_table('products', 'product')
    op.rename_table('leet_code_records', 'leetcoderecord')
    op.rename_table('habit_completions', 'habitcompletion')
    op.rename_table('habits', 'habit')
    op.rename_table('daily_entries', 'dailyentry')
    op.rename_table('users', 'user')
    op.rename_table('api_call_records', 'apicallrecord')