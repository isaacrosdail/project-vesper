# Project Conventions

## Module Architecture
- Module names: lowercase, plural where appropriate
- Subtypes: snake_case, singular
- Models: PascalCase, singular -> Table names are derived therefrom

## HTML Attributes Ordering
1. Identity: id, class
2. State & data: type, name, value, `data-*`, `aria-*`
3. Behavior: href, src, action, method, for, from, role
4. Presentation: alt, title, placeholder, disabled, checked, selected, loading, async
5. Boolean attrs & others: hidden, open, required, etc.

Note: Will begin defaulting to classes over IDs for everything except: form inputs and auto-discovery modal-related stuff

Utility classes will be prefixed with _ to distinguish themselves from other styling classes

## API Response Standardization

# Use api_response() wrapper for all JSON responses
```python
return api_response((success: bool, message: str, data: dict = None, errors: dict = None))
```

# Validation errors use validation_failed()
```python
return validation_failed(errors), 400
```

## Validation Architecture Pattern
```python
## Constants in each module's constants.py, from which validators & tests draw

# 1. Individual field validation functions
def validate_field_name(field_value: str) -> list[str]:
    errors = []
    # validation logic with elif chains
    return errors

# 2. Mapping dictionary
ENTITY_VALIDATION_FUNCS = {
    "field1": validate_field1,
    "field2": validate_field2,
}

# 3. Main validation function using loop
def validate_entity(data: dict) -> dict[str, list[str]]:
    errors = {}
    for field, func in ENTITY_VALIDATION_FUNCS.items():
        value = data.get(field, "").strip()
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
    return errors
```