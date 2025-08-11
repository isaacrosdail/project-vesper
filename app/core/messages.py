# Centralized location for error messages, since I intend on localizing to German in (far-ish off) future

from app.core.constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH

# Top level keys are lang codes, second-level keys are message IDs (ie, "username_invalid")
MESSAGES = {
    "en": {
        "username_invalid": "Username must be 3-30 alphanumeric characters.",
        "username_taken": "Username already taken.",
        "username_nonexistent": "Invalid username: No matching user exists.",
        "db_reset": "Database has been reset successfully!",
        "db_reset_dev": "(Dev) Database has been reset successfully!",
        "demo_ready": "Welcome to the demo!",
        "password_incorrect": "Incorrect password.",
        "password_short": "Password must be at least 8 characters.",
        "name_invalid": "Name invalid.",
        "register_success": "Successfully registered!",
        "invalid_data": "Error invalid data.",
    },
    "de": {
        "username_invalid": "Invalid.",
        "username_taken": "Benutzername bereits vergeben.",
        "username_nonexistent": "Invalid username: No matching user exists.",
        "db_reset": "Database has been reset successfully!",
        "db_reset_dev": "(Dev) Database has been reset successfully!",
        "demo_ready": "Welcome to the demo!",
        "password_incorrect": "Incorrect password.",
        "password_short": "Passwort muss mindestens 8 Zeichen lang sein.",
        "name_invalid": "Name nicht gültig.",
        "register_success": "Erfolgreich registriert!",
        "invalid_data": "Error invalid data.",
    },
}

def msg(code: str, lang: str = "en") -> str:
    """Return the message in requested language, default to English."""
    return MESSAGES.get(lang, {}).get(code, MESSAGES["en"][code])