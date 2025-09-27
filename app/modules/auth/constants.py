

# User constraints

# Username
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
USERNAME_REGEX = rf"^[\p{{L}}0-9_]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}$" # 3-30, Unicode letters, numbers, & underscores

USERNAME_REQUIRED = "Username is required"
USERNAME_CHARSET = f"Username can only contain up to {USERNAME_MIN_LENGTH}-{USERNAME_MAX_LENGTH} characters of letters, numbers, and underscores"


# Password
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 50
PASSWORD_REGEX = rf"^.{{{PASSWORD_MIN_LENGTH},{PASSWORD_MAX_LENGTH}}}$" # 8-50 chars, any allowed

PASSWORD_REQUIRED = "Password is required"
PASSWORD_LENGTH = f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters"


# Name (optional)
NAME_MAX_LENGTH = 50
NAME_REGEX = rf"^[\p{{L}}' -]{{1,{NAME_MAX_LENGTH}}}$" # 1-50, Unicode letters, plus space/apostrophe/hyphen
NAME_CHARSET = f"Name can only contain up to {NAME_MAX_LENGTH} characters of letters, spaces, apostrophes, and hyphens"


# UserRole
USERROLE_REQUIRED = "UserRole is required"
USERROLE_INVALID = "UserRole not a valid enum"

# UserLang
USERLANG_REQUIRED = "UserLang is required"
USERLANG_INVALID = "UserLang not a valid enum"

# Timezone (TODO: Regex for IANA strings? Pull from dict/list?)
TIMEZONE_MAX_LENGTH = 50
