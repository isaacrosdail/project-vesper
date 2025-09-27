
from decimal import Decimal, InvalidOperation

FORMAT_ERROR = 'format_error'
CONSTRAINT_VIOLATION = 'constraint_violation'
PRECISION_EXCEEDED = 'precision_exceeded'
SCALE_EXCEEDED = 'scale_exceeded'

def validate_numeric(value, precision, scale, minimum=None, strict_min=False) -> tuple[bool, str | None]:
    """Returns `(is_valid: bool, error_type: str | None)`"""
    
    ok, dec = parse_decimal(value)
    if not ok:
        return False, FORMAT_ERROR
    
    # Cases:
    # minimum=None → no lower-bound check at all.
    # minimum=0 + strict_min=True → require dec > 0.
    # minimum=0 + strict_min=False → require dec >= 0.
    if minimum is not None:
        if strict_min and dec <= minimum:
            return False, CONSTRAINT_VIOLATION
        if not strict_min and dec < minimum:
            return False, CONSTRAINT_VIOLATION

    
    # Check precision/scale
    digits = dec.as_tuple().digits
    exponent = dec.as_tuple().exponent
    total_digits = len(digits)
    fractional_digits = abs(exponent) if exponent < 0 else 0

    if fractional_digits > scale:
        return False, SCALE_EXCEEDED
    if total_digits > precision:
        return False, PRECISION_EXCEEDED

    return True, None


def validate_id_field(id_value: str, required_error: str, invalid_error: str) -> list[str]:
    errors = []
    if not id_value:
        errors.append(required_error)
    else:
        try:
            int(id_value)
        except (ValueError, TypeError):
            errors.append(invalid_error)
    return errors

def validate_enum(enum_str: str, enum_cls, required_error: str, invalid_error: str) -> list[str]:
    errors = []
    if not enum_str:
        errors.append(required_error)
    else:
        valid_enums = [enum_val.value for enum_val in enum_cls]
        if enum_str not in valid_enums:
            errors.append(invalid_error)
    return errors

def parse_decimal(value):
    try:
        dec = Decimal(str(value)) # str() avoids float artifacts & ensures proper parsing?
    except InvalidOperation:
        return False, None
    
    if dec.is_infinite() or dec.is_nan():
        return False, None

    return True, dec