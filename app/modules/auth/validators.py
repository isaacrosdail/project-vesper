

def validate_user(data: dict) -> list[str]:
    
    errors = []

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()

    # Username: 3-50 chars
    if not username:
        errors.append("Username is required")
    if not 3 <= len(username) <= 50:
        errors.append("Username must be 3-50 characters")

    # Password: 8-50 chars
    if not password:
        errors.append("Password is required")
    if not 8 <= len(password) <= 50:
        errors.append("Password must be 8-50 characters")

    # Name (optional)
    if name and len(name) > 50:
        errors.append("Name must be under 50 characters")
    
    return errors