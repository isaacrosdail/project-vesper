# soft_delete, bulk operations, etc
# Exact intention of this file TBD

from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import text

from app.shared.constants import (SKIP_SEQUENCES, TABLES_WITH_USERS,
                                  TABLES_WITHOUT_USERS)


# Delete all data without nuking schema, optionally reset ID sequencing
# Does NOT delete from User table
def delete_all_db_data(session, include_users=False, reset_sequences=False):
    """Delete all database data. Optionally delete users, sequences."""

    tables = TABLES_WITH_USERS if include_users else TABLES_WITHOUT_USERS
    # sequences = ALL_SEQUENCES if include_users else DATA_SEQUENCES

    # Debug
    current_app.logger.info(
        "delete_all_db_data: include_users=%s, reset_sequences=%s",
        include_users, reset_sequences
    )

    # Delete data
    for table in tables:
        current_app.logger.info("Deleting all rows from table: %s", table)
        # Double quotes tell PostrgeSQL to treat it as an identifier, not a keyword (for our 'user' table)
        session.execute(text(f'DELETE FROM "{table}"'))

    # Reset sequences if desired
    if reset_sequences:
        for table in tables:
            seq_name = f"{table}_id_seq"
            if seq_name in SKIP_SEQUENCES:
                current_app.logger.debug("Skipping missing sequence: %s", seq_name)
                continue

            session.execute(text(f'ALTER SEQUENCE "{seq_name}" RESTART WITH 1'))
            current_app.logger.info("Resetting sequence: %s", seq_name)

def safe_delete(session, item):
    """
    Soft-delete if `deleted_at` column exists, else hard-delete. Returns the item.
    """
    if hasattr(item, 'deleted_at'):
        if item.deleted_at is None:
            item.deleted_at = datetime.now(timezone.utc)
        return item
    session.delete(item)
    return item