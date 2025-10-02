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

Utility classes will be prefixed with `_` to distinguish themselves from other styling classes

## API Response Standardization

# TODO: Under construction

## Validation Architecture Pattern

Overall Notes:
1. Validators own type conversion (with some bespoke exceptions)
2. Optional vs Required handled via tuple returns:
    - `(None, [])` = "I'm empty but that's okay (optional)"
    - `(None, [ERROR])` = "I'm empty but that's not okay (required)"
3. `typed_data` dict structure:
    - Only contains successfully validated fields
    - Omits keys entirely rather than storing `None` values
    - Applies to both error cases and optional-empty cases

Field validators:
Return: `(typed_value | None, list[str])`
Handles type conversion: str → int/float/enum/str
Uses `(None, [])` for "optional field, empty is valid"
Uses `(None, [ERROR])` for "required field, empty is invalid"
Pattern uses `if not X` checks for normalization

Composite validators:
- Return: `(typed_data: dict, errors: dict[str, list[str]])`
- Aggregates individual field validation results
- `typed_data` only includes successfully validated fields (omits keys with errors or optional empty fields rather than storing `None` values)
- Pattern: loop through field validators, add to `typed_data` only if `typed_value` is not None