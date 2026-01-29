# Message templates
def required(field: str) -> str:
    return f"{field} is required"

def positive(field: str) -> str:
    return f"{field} must be greater than 0"

def too_long(field: str, max_len: int) -> str:
    return f"{field} cannot exceed {max_len} characters"

def invalid_range(field: str, min_val: int, max_val: int) -> str:
    return f"{field} must be {min_val}-{max_val} alphanumeric characters"

def invalid(field: str) -> str:
    return f"{field} is invalid"

def invalid_enum(field: str) -> str:
    return f"{field} must be a valid enum"

def negative(field: str) -> str:
    return f"{field} cannot be negative"

