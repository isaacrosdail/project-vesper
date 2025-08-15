# soft_delete, bulk operations, etc
# Exact intention of this file TBD

from datetime import datetime, timezone

from app.shared.constants import TABLES_WITH_USERS, TABLES_WITHOUT_USERS
from flask import current_app
from sqlalchemy import text


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
    # TODO: NOTES: find home for following note here:
    # engine.begin() creates connection-level transaction that
    # auto-commits when the context exits

    # Delete data
    for table in tables:
        current_app.logger.info("Deleting all rows from table: %s", table)
        # Double quotes tell PostrgeSQL to treat it as an identifier, not a keyword (for our 'user' table)
        session.execute(text(f'DELETE FROM "{table}"'))

    # Reset sequences if desired
    if reset_sequences:
        for table in tables:
            seq_name = f"{table}_id_seq"
            current_app.logger.info("Resetting sequences: %s", seq_name)
            session.execute(text(f'ALTER SEQUENCE "{seq_name}" RESTART WITH 1'))


# TODO: Implement soft delete for DB entries, then use this function for handling soft delete for products
def safe_delete(session, item):
    """
    Deletes the given SQLAlchemy model instance.
    If the model supports soft delete (has a 'deleted_at' column), marks it as deleted.
    Otherwise, permanently deletes it from the database.
    """
    if hasattr(item, 'deleted_at'):
        item.deleted_at = datetime.now(timezone.utc)
    else:
        session.delete(item)