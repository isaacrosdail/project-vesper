

from app.shared.validation_messages import invalid_enum, invalid_range, required

# Username: 3-30, Unicode letters, numbers, & underscores
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
USERNAME_REGEX = rf"^[\p{{L}}0-9_]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}$"

USERNAME_REQUIRED = required("Username")
USERNAME_CHARSET = (
    f"Username must be {USERNAME_MIN_LENGTH}-{USERNAME_MAX_LENGTH} characters "
    "and may only include letters, numbers, and underscores"
)

# Password: 5-128 characters, any allowed
# NOTE: Will use a more relaxed 5-128 length requirement (as opposed to 12-128)
# Less friction for demo accounts, and easier for testing on my end.
PASSWORD_MIN_LENGTH = 5
PASSWORD_MAX_LENGTH = 128
PASSWORD_REGEX = (
    rf"^.{{{PASSWORD_MIN_LENGTH},{PASSWORD_MAX_LENGTH}}}$"
)

PASSWORD_REQUIRED = required("Password")
PASSWORD_INVALID = invalid_range("Password", PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH)

# Name (optional): 1-50, Unicode letters, plus space/apostrophe/hyphen
NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 50

NAME_REGEX = rf"^[\p{{L}}' -]{{1,{NAME_MAX_LENGTH}}}$"
NAME_CHARSET = (
    f"Name must be {NAME_MIN_LENGTH}-{NAME_MAX_LENGTH} characters "
    "and may only include letters, spaces, apostrophes, and hyphens"
)

# UserRole
USERROLE_REQUIRED = required("UserRole")
USERROLE_INVALID = invalid_enum("UserRole")

# UserLang
USERLANG_REQUIRED = required("UserLang")
USERLANG_INVALID = invalid_enum("UserLang")

# Timezone
# NOTE: Use ZoneInfo's actual list: ZoneInfo.available_timezones()
TIMEZONE_MAX_LENGTH = 50
