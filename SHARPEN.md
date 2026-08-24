# Sharpen the Saw

- db: full pass on constraint naming — reconcile model-computed names vs actual DB names (drift exists: explicit ck_ names double via convention, hand-written migrations used literal names). Rule: ck template composes (`ck_%(table_name)s_%(constraint_name)s` — pass bare semantic name), uq/ix/fk/pk explicit names pass through verbatim. Migration ops are ALWAYS literal.
- db: verify computed constraint names without touching the DB:
  ```
  flask shell
  >>> from app.modules.groceries.models import Product
  >>> for c in Product.__table__.constraints:
  ...     print(type(c).__name__, c.name)
  ```
  prints exactly what the migration must reference. Check actual DB side with: `SELECT conname FROM pg_constraint WHERE conrelid = 'products'::regclass;`

- neovim: auto-complete brackets/parentheses/etc
- neovim: hotkey to apply autocomplete / choose autocomplete option
- tooling: make some kind of '/vesper-wrapup' command to leave succinct breadcrumbs at EOD for next work session


- add utils/scripts for psql inspecting

- db: make nicer formatted views for tables

- db: make nicer formatted views for tables

- download docs for our stack and make it easy for claude to reference them

- download docs for our stack and make it easy for claude to reference them

- for docs stuff: pytest, flask, ts, d3

- flask megatutorial look into having errors auto-sent to email

- improve logging across vesper tbh

- set up autocomplete in nvim

- learn about postgres domains

- window functions, CTEs, subqueries, hybrid_property

- hybrid_expression

- need to get open in terminal actually working for ghosttyclaude

- -h

- fix memory hogs just bringing pc to its knees

- add to nvim: find all references

- add to nvim: autocomplete hotkey?

