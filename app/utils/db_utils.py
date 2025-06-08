
from sqlalchemy import text

def delete_all_db_data(engine, reset_sequences=False):
    # Delete in dependency order -> children first
    tables = [
        "habit_completions", # child: references habits
        "transaction",       # child: references products
        "habits",            # parent table
        "product",           # parent table
        "tasks"              # independent
    ]
    sequences = [
        "habit_completions_id_seq", # references habits
        "transaction_id_seq",       # references products
        "habits_id_seq",            # parent table
        "product_product_id_seq",   # parent table
        "tasks_id_seq"
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