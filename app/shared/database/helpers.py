"""
Database utility functions.
Provides helpers for low-level database operations that don't
belong to any single model/repository/service.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import ColumnElement, Table
    from sqlalchemy.orm import Session

import logging
from datetime import datetime, timezone

from sqlalchemy import delete, text

from app._infra.db_base import Base
from app.modules.groceries.models import Product, ShoppingListItem

logger = logging.getLogger(__name__)

NEVER_DELETE = {
    "api_call_records",
    "alembic_version",
}
# Skip sequence reset for association tables
NO_SEQ = {"habit_tags", "task_tags", "task_links"}


def _delete_rows(
    session: Session, table: Table, where_clause: ColumnElement[bool] | None = None
) -> None:
    """Delete rows from an SQLAlchemy table object."""
    stmt = delete(table)
    if where_clause is not None:
        stmt = stmt.where(where_clause)

    session.execute(stmt)
    logger.debug("Deleted from %s", table.name)


def delete_all_db_data(
    session: Session, *, include_users: bool = False, reset_sequences: bool = False
) -> None:
    """Delete all database data. Optionally delete users, sequences."""

    logger.debug(
        "delete_all_db_data: include_users=%s, reset_sequences=%s",
        include_users,
        reset_sequences,
    )

    # Reversing .sorted_tables gives tables in dependency order (ie, respecting FKeys)
    # Also build filtered, dependency-ordered list once for resetting sequences after
    filtered_names = []
    for table in reversed(Base.metadata.sorted_tables):
        name = table.name.lower()

        # skip deny-listed tables:
        if name in NEVER_DELETE:
            continue

        # skip user-scoped tables if flag is False
        if not include_users and "user_id" in table.c:
            continue

        _delete_rows(session, table)
        filtered_names.append(name)

    if reset_sequences:
        for name in filtered_names:
            if name not in NO_SEQ:
                if seq_name := _get_sequence_name(session, name):
                    session.execute(text(f'ALTER SEQUENCE "{seq_name}" RESTART WITH 1'))
                    logger.debug("Sequence %s reset", seq_name)


def delete_user_data(session: Session, table: Table, user_id: int) -> None:
    """Delete data for a specific user from a single table."""
    stmt = delete(table).where(table.c.user_id == user_id)
    session.execute(stmt)
    logger.debug("Deleted user %s data from: %s", user_id, table)


def safe_delete[T](session: Session, item: T) -> T:
    """
    Soft-delete if `deleted_at` column exists, else hard-delete. Returns the item.
    """
    if isinstance(item, Product):
        # Clean up shopping list items
        session.query(ShoppingListItem).filter(
            ShoppingListItem.product_id == item.id
        ).delete()
    if hasattr(item, "deleted_at"):
        if item.deleted_at is None:
            item.deleted_at = datetime.now(timezone.utc)
        return item
    session.delete(item)
    return item


def _get_sequence_name(session: Session, table_name: str) -> str | None:
    """Get actual sequence name for a table's id column."""
    result = session.execute(
        text("""
        SELECT pg_get_serial_sequence(:table_name, 'id')
"""),
        {"table_name": table_name},
    ).scalar()

    if result:
        return str(result).split(".")[-1]  # get just sequence name
    return None
