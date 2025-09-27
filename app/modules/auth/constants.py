

# Username: 3-30, Unicode letters, numbers, & underscores
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
USERNAME_REGEX = rf"^[\p{{L}}0-9_]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}$"

USERNAME_REQUIRED = "Username is required"
USERNAME_CHARSET = (
    f"Username must be {USERNAME_MIN_LENGTH}-{USERNAME_MAX_LENGTH} characters "
    "and may only include letters, numbers, and underscores"
)

# Password
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 50
PASSWORD_REGEX = rf"^.{{{PASSWORD_MIN_LENGTH},{PASSWORD_MAX_LENGTH}}}$" # 8-50 chars, any allowed

PASSWORD_REQUIRED = "Password is required"
PASSWORD_LENGTH = f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters"

# Name (optional): 1-50, Unicode letters, plus space/apostrophe/hyphen
NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 50

NAME_REGEX = rf"^[\p{{L}}' -]{{1,{NAME_MAX_LENGTH}}}$"
NAME_CHARSET = (
    f"Name must be {NAME_MIN_LENGTH}-{NAME_MAX_LENGTH} characters "
    "and may only include letters, spaces, apostrophes, and hyphens"
)

# UserRole
USERROLE_REQUIRED = "UserRole is required"
USERROLE_INVALID = "UserRole not a valid enum"

# UserLang
USERLANG_REQUIRED = "UserLang is required"
USERLANG_INVALID = "UserLang not a valid enum"

# Timezone
# TODO: Use ZoneInfo's actual list: ZoneInfo.available_timezones()
TIMEZONE_MAX_LENGTH = 50
