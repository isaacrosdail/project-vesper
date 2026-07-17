"""
Database utility functions.
Provides helpers for low-level database operations that don't
belong to any single model/repository/service.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import ColumnElement, Table
    from sqlalchemy.orm import Session

import logging

from sqlalchemy import delete, text

from app._infra.db_base import Base

logger = logging.getLogger(__name__)

NEVER_DELETE = {
    "api_call_records",
    "alembic_version",
}
# Skip sequence reset for association tables
NO_SEQ = {
    "habit_tags", "task_tags", "task_links",
    "habit_pillars", "task_pillars", "time_entry_pillars"
}

def user_scoped_tables() -> Iterator[Table]:
    for t in reversed(Base.metadata.sorted_tables):
        if "user_id" in t.c:
            yield t

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
        if not include_users and table.name == "users":
            continue

        _delete_rows(session, table)
        filtered_names.append(name)

    if reset_sequences:
        for name in filtered_names:
            if name not in NO_SEQ:
                if seq_name := _get_sequence_name(session, name):
                    session.execute(text(f'ALTER SEQUENCE "{seq_name}" RESTART WITH 1'))
                    logger.debug("Sequence %s reset", seq_name)


def delete_user_activity_data(session: Session, user_id: int) -> None:
    # Core-table DELETE (delete(table) here)
    session.flush() # reconcile session -> DB so pending work is processed
    for table in user_scoped_tables():
        if table.name in {"user_goals", "user_profiles"}:
            continue
        # delete_user_data(session, table, user_id)
        stmt = delete(table).where(table.c.user_id == user_id)
        session.execute(stmt)
        logger.debug("Deleted user %s data from: %s", user_id, table)

    session.expire_all() # reconcile DB -> session: loaded state ORM-side is now invalidated

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
