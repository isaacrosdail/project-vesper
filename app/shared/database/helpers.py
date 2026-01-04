"""
Database utility functions. 
Provides helpers for low-level database operations that don't belong to any single model/repository/service.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import text
from app._infra.db_base import Base
from app.modules.groceries.models import Product, ShoppingListItem

import logging
logger = logging.getLogger(__name__)

NEVER_DELETE = {
    "api_call_records",
    "alembic_version",
}
# Skip sequence reset for association tables of course
NO_SEQ = {
    "habit_tags",
    "task_tags"
}

def _delete_rows(session: 'Session', table: str, where: str | None = None, params: dict[str, Any] | None = None) -> None:
    """
    Notes:
        - Uses parameter binding (:param style) to avoid SQL injection.
        - params (dict, optional): bound parameters for the WHERE clause
    """
    logger.info(f"Deleting from {table} {where if where else 'all rows'}")

    sql = f'DELETE FROM "{table}"'  #  "" -> Postgres treats as identifier, not a keyword (for our 'user' table)
    if where:
        sql += f' WHERE {where}'
    
    # params or {} ensures safe binding even if None is passed
    session.execute(text(sql), params or {})


def delete_all_db_data(session: 'Session', include_users: bool = False, reset_sequences: bool = False) -> None:
    """Delete all database data. Optionally delete users, sequences."""

    logger.info(
        f"delete_all_db_data: include_users={include_users}, reset_sequences={reset_sequences}"
    )

    # Reversing .sorted_tables gives us tables in dependency order (ie, respecting FKeys)
    # Also build filtered, dependency-ordered list once for resetting sequences hereafter
    filtered_names = []
    for table in reversed(Base.metadata.sorted_tables):
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
            if name not in NO_SEQ:
                seq_name = _get_sequence_name(session, name)
                if seq_name:
                    session.execute(text(f'ALTER SEQUENCE "{seq_name}" RESTART WITH 1'))
                    logger.debug(f"Resetting sequence: {seq_name}")

def delete_user_data(session: 'Session', user_id: int, table: str) -> None:
    """User-facing delete: Delete data for a specific user from a single table."""
    logger.debug(f"Deleting user {user_id} data from: {table}")
    _delete_rows(session, table, "user_id = :user_id", {"user_id": user_id}) # parametrized -> avoids SQL injection risk


def safe_delete[T](session: 'Session', item: T) -> T:
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

def _get_sequence_name(session: 'Session', table_name: str) -> str | None:
    """Get actual sequence name for a table's id column."""
    result = session.execute(text("""
        SELECT pg_get_serial_sequence(:table_name, 'id')
"""), {'table_name': table_name}).scalar()
    
    if result:
        return str(result).split('.')[-1] # get just sequence name
    return None