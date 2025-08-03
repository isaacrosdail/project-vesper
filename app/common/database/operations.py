# soft_delete, bulk operations, etc
# Exact intention of this file TBD

from sqlalchemy import text
from app.core.constants import DATA_TABLES, ALL_TABLES, DATA_SEQUENCES, ALL_SEQUENCES

# Delete all data without nuking schema, optionally reset ID sequencing
# Does NOT delete from User table
def delete_all_db_data(engine, reset_sequences=False, include_users=False):
    """Delete all database data, with flags for also deleting users."""

    tables = ALL_TABLES if include_users else DATA_TABLES
    sequences = ALL_SEQUENCES if include_users else DATA_SEQUENCES

    # New way with Alembic instead of create_all()
    with engine.begin() as conn:
        # Delete data
        for table in tables:
            conn.execute(text(f"DELETE FROM {table}"))

        # Reset sequences if desired
        if reset_sequences:
            for seq in sequences:
                conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))


# TODO: Implement soft delete for DB entries, then use this function for handling our soft delete for products
def soft_delete():
    pass