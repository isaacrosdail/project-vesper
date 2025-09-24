"""
Database utility functions. 
Provides helpers for low-level database operations that don't belong to any single model/repository/service.
"""

from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import text
from app._infra.db_base import Base
from app.modules.groceries.models import Product, ShoppingListItem

NEVER_DELETE = {
    "apicallrecord",
    "alembic_version",
    "habit_tags", # Association tables for these two, which use composite keys & do not receive auto-inc IDs or *_id_seq
    "task_tags"
}

def _delete_rows(session, table, where=None, params=None):
    """
    Notes:
        - Uses parameter binding (:param style) to avoid SQL injection.
        - params (dict, optional): bound parameters for the WHERE clause
    """
    current_app.logger.info(f"Deleting from {table} {where if where else 'all rows'}")

    sql = f'DELETE FROM "{table}"'  #  "" -> Postgres treats as identifier, not a keyword (for our 'user' table)
    if where:
        sql += f' WHERE {where}'
    
    # params or {} ensures safe binding even if None is passed
    session.execute(text(sql), params or {})


def delete_all_db_data(session, include_users=False, reset_sequences=False):
    """Delete all database data. Optionally delete users, sequences."""

    current_app.logger.info(
        f"delete_all_db_data: include_users={include_users}, reset_sequences={reset_sequences}"
    )

    # sorted_tables gives us tables in dependency order (ie, respecting FKeys)
    # Also build filtered, dependency-ordered list once for resetting sequences hereafter
    filtered_names = []
    for table in Base.metadata.sorted_tables:
        name = table.name.lower()

        # skip deny-listed tables:
        if name in NEVER_DELETE:
            continue

        # skip user-scoped tables if flag is False
        if not include_users and "user_id" in table.c:
            continue

        _delete_rows(session, table.name)
        filtered_names.append(name)

    if reset_sequences:
        for name in filtered_names:
            seq_name = f"{name}_id_seq"
            session.execute(text(f'ALTER SEQUENCE "{seq_name}" RESTART WITH 1'))
            current_app.logger.info(f"Resetting sequence: {seq_name}")

def delete_user_data(session, user_id, table):
    """User-facing delete: Delete data for a specific user from a single table."""
    current_app.logger.info(f"Deleting user {user_id} data from: {table}")
    _delete_rows(session, table, "user_id = :user_id", {"user_id": user_id}) # parametrized -> avoids SQL injection risk


def safe_delete(session, item):
    """
    Soft-delete if `deleted_at` column exists, else hard-delete. Returns the item.
    """
    if isinstance(item, Product):
        # Clean up shopping list items
        session.query(ShoppingListItem).filter(
            ShoppingListItem.product_id == item.id
        ).delete()
    if hasattr(item, 'deleted_at'):
        if item.deleted_at is None:
            item.deleted_at = datetime.now(timezone.utc)
        return item
    session.delete(item)
    return item