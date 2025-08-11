# Loving this so far, using this to better centralize constants that ought to be centralized & consistent

# Requirements for various forms (to keep a single source of truth for myself)
USERNAME_LENGTH = [3, 50]
PASSWORD_LENGTH = [8, 50]

DEFAULT_LANG = "en"
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 14
MAX_NAME_LENGTH = 50
DEFAULT_CHART_DAYS = 14 # How many days back to look when plotting with Plotly
DEFAULT_HEALTH_TIMEZONE = 'America/Chicago' # Default TZ to be used for _internal health check via HTTP
                                            # Note: Above uses IANA timezone names

# DATA_TABLES = [
#     # Arranged in dependency order -> children first
#     "habitcompletion",   # child: references habit
#     "transaction",       # child: references product
#     "timeentry",
#     "habit",             # parent table
#     "product",           # parent table
#     "task",              # independent
# ]

TABLES_WITHOUT_USERS = [
    # Arranged in dependency order -> children first, parents last
    "habitcompletion",   # child: references habit + user
    "transaction",       # child: references product + user  
    "timeentry",         # child: references user
    "dailycheckin",      # child: references user
    "dailyintention",    # child: references user
    "dailymetric",       # child: references user
    "dailyreflection",   # child: references user
    "task",              # child: references user
    "habit",             # child: references user (but parent to habitcompletion)
    "product",           # child: references user (but parent to transaction)
]

# To keep editing/deletion of users separate
TABLES_WITH_USERS = TABLES_WITHOUT_USERS + ["user"] # For complete database deletions