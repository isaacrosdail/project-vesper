
from sqlalchemy import text

# Delete all data without nuking schema, optionally reset ID sequencing
# Does NOT delete from User table
def delete_all_db_data(engine, reset_sequences=False):
    # Delete in dependency order -> children first
    tables = [
        "habitcompletion",   # child: references habit
        "transaction",       # child: references product
        "habit",             # parent table
        "product",           # parent table
        "task"               # independent
    ]
    sequences = [
        "habitcompletion_id_seq",  # references habit
        "transaction_id_seq",      # references product
        "habit_id_seq",            # parent table
        "product_id_seq",  # parent table
        "task_id_seq"
    ]
    # New way with Alembic instead of create_all()
    with engine.begin() as conn:
        # Delete data
        for table in tables:
            conn.execute(text(f"DELETE FROM {table}"))

            # Reset sequences if desired
            if reset_sequences:
                for seq in sequences:
                    conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))