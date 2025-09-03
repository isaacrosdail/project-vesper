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