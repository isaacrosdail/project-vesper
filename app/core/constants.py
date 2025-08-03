# Centralizing some constants for sanity? We'll see how this goes and pivot later
# Really not sure about this :D

DEFAULT_LANG = "en"
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 14
MAX_NAME_LENGTH = 50
DEFAULT_CHART_DAYS = 14 # How many days back to look when plotting with Plotly

DATA_TABLES = [
    # Arranged in dependency order -> children first
    "habitcompletion",   # child: references habit
    "transaction",       # child: references product
    "timeentry",
    "habit",             # parent table
    "product",           # parent table
    "task",              # independent
]

ALL_TABLES = DATA_TABLES + ["user"] # For complete database deletions

# Corresponding sequences for ID reset
DATA_SEQUENCES = [
    "habitcompletion_id_seq",  # references habit
    "transaction_id_seq",      # references product
    "timeentry_id_seq",        #
    "habit_id_seq",            # parent table
    "product_id_seq",  # parent table
    "task_id_seq"
]

ALL_SEQUENCES = DATA_SEQUENCES + ["user_id_seq"]