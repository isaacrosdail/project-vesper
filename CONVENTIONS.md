# Project Conventions

## Systems to keep in mind
- We don't use type=number, instead use data-type-float and data-type-int (plus inputmode for mobile)
- To regroup on:
    1. Model/subtype/table name convention/pattern
    2. Subtype names used globally (ie even in markup etc)
        - `types.ts` & `MODEL_CLASSES` (in generic_routes.py) are our de facto master lists, so let's remember to keep those synced.
    3. Split styling from JS behavior by prefixing class names for the latter with 'js-'? Scan for that
        - Or consider using data-attrs?
Default to classes over IDs for everything except form inputs and auto-discovery modal-related stuff
    4. CSS properties in recess order (enforced by stylelint)

Validation preferences:
    - Backend regex, frontend informational responses?

## Jinja Naming Convention for Types (Hungarian-style a la Charles Simonyi)
- `l_` = list/array
- `d_` = dict
- `o_` = object/model
- `s_` = string
- `b_` = bool