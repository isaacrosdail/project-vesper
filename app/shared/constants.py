# Loving this so far, using this to better centralize constants that ought to be centralized & consistent

# Requirements for various forms (to keep a single source of truth for myself)
USERNAME_LENGTH = [3, 50]
PASSWORD_LENGTH = [8, 50]

DEFAULT_LANG = "en"
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 14
MAX_NAME_LENGTH = 50
DEFAULT_CHART_DAYS = 14
DEFAULT_HEALTH_TIMEZONE = 'America/Chicago' # Default TZ to be used for devtools health check via HTTP
                                            # Note: Above uses IANA timezone names

TABLES_WITHOUT_USERS = [
    "habitcompletion",   # FK to habit + user
    "habit_tags",        # FK to habit + tag
    "task_tags",         # FK to task + tag
    "transaction",       # FK to product + user
    "timeentry",         # FK to user
    "dailyentry",        # FK to user
#    "dailyintention",    # FK to user
    "task",              # FK to user
    "habit",             # FK to user
    "product",           # FK to user
    "tag",               # FK to user
]

SKIP_SEQUENCES = [
    "habit_tags_id_seq",
    "task_tags_id_seq"
]


# To keep editing/deletion of users separate
TABLES_WITH_USERS = TABLES_WITHOUT_USERS + ["user"] # For complete database deletions