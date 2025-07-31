# Centralized location for error messages, since I intend on localizing to German in (far-ish off) future

from app.core.constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH

## TODO: Find a way to mimic template literal behavior here for dynamic messages. Specifically: Make our password message reference the MIN-/MAX_PASSWORD_LENGTH constants in constants.py

# Top level keys are lang codes, second-level keys are message IDs (ie, "username_invalid")
MESSAGES = {
    "en": {
        "username_invalid": "Username must be 3-30 alphanumeric characters.",
        "username_taken": "Username already taken.",
        "password_short": "Password must be at least 8 characters.",
        "name_invalid": "Name invalid.",
        "register_success": "[name] successfully registered!",
    },
    "de": {
        "username_invalid": "Invalid.",
        "username_taken": "Benutzername bereits vergeben.",
        "password_short": "Passwort muss mindestens 8 Zeichen lang sein.",
        "name_invalid": "Name nicht gültig.",
        "register_success": "[name] erfolgreich registriert!",
    },
}

def msg(code: str, lang: str = "en") -> str:
    """Return the message in requested language, default to English."""
    return MESSAGES.get(lang, {}).get(code, MESSAGES["en"][code])