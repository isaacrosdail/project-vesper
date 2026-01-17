# Project Conventions

## Systems to keep in mind
- We don't use type=number, instead use data-type-float and data-type-int (plus inputmode for mobile)


## Module Architecture / Naming
- Module names: lowercase, plural where appropriate
- Subtypes: snake_case, singular
- Models: PascalCase, singular -> Table names are derived therefrom
- Repository classes: Sg., match the model
- Repository instances: Sg., match model they manage
- Service classes: Pl., match the module
- Service instances: Pl., match the service class

Service object naming shorthand end in `_svc` -> ex: `groceries_svc`?

Subtype names will be used even in markup/etc, ex: `class="metric_entries-modal"` to enable some nice stuff facilitated by this parity.
    `types.ts` & `MODEL_CLASSES` (in generic_routes.py) are our de facto master lists, so let's remember to keep those synced.

## HTML Attributes Ordering
1. Identity: id, class
2. State & data: type, name, value, `data-*`, `aria-*`
3. Behavior: href, src, action, method, for, from, role
4. Presentation: alt, title, placeholder, disabled, checked, selected, loading, async
5. Boolean attrs & others: hidden, open, required, etc.

Default to classes over IDs for everything except form inputs and auto-discovery modal-related stuff


## API Notes

We'll return HTTP code 200 on DELETEs, since we'll return the item in the body of the return as well.
Semantically, it feels fuzzy, but the utility of having the full item info outweighs this, in my opinion.

This means every API operation returns the affected item.

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

### Validation Notes from txts, SORT:


Thoughts on validation handling strategy:
1. Frontend - Convenience only (UX feedback, not security)
2. validators.py - DB-independent, pure functions for format/shape (makes testing easy)
3. service.py - Business rules + DB-aware (eg, uniqueness)
4. repo/db -> persistence + hard stop (constraints, not logic)

Backend regex, frontend informational responses


## CSS Properties in recess order (enforced by stylelint)

## Jinja Naming Convention for Types (Hungarian-style a la Charles Simonyi)
- `l_` = list/array
- `d_` = dict
- `o_` = object/model
- `s_` = string
- `b_` = bool