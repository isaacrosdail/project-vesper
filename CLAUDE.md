# CLAUDE.md

## Project Identity
Project Vesper is a web app made with Flask+SQLAlchemy+Postgres+Alembic+D3+TypeScript. It is meant to
track a user's day-to-day tasks/stats/etc and provide visual and statistical feedback for improved decision-making.

## Key Commands
- `bun test` - run the Bun test suite.
- `pytest` - run the Python tests (`testpaths=tests`, `pythonpath=.`, `APP_ENV=testing`)
- `npm run check` — the full gate: eslint + tsc + ruff + mypy + stylelint
- `ruff check .` (`npm run lint:python`) — ruff runs `select = ["ALL"]` with a curated ignore list in `pyproject.toml`
- `mypy .` (`npm run type-check:python`) — `strict = true`; `tests/` and `alembic/` are excluded
- `eslint app/static_src/js` (`npm run lint:ts`) · `tsc --noEmit` (`npm run type-check`) · `stylelint '**/*.css'` (`npm run lint:css`)
- Other scripts are in package.json, and should be vetted if questionable.
- Flask CLI: `init-owner`, `reset-dev`, and others via Click CLI library, defined in `app/__init__.py`. WIP.
- `alembic upgrade head` · `alembic revision --autogenerate -m "..."` · `alembic downgrade -1`

## Conventions
@CONVENTIONS.md

## Hard Stops
- Do not read `.env`. Use `.env.example` only.

## Known Gotchas

## Links
(paths to files/docs that matter)


### Module anatomy
Every domain under `app/modules/<domain>/` follows the same layout:
`models.py` · `repository.py` · `service.py` · `routes.py` (server-rendered HTML) · `api_routes.py` (JSON) · `schemas.py` (Pydantic) · `viewmodels.py` (display shaping) · `templates/`.
Domains: `auth`, `groceries`, `habits`, `metrics`, `tasks`, `time_tracking`.

### Layering and boundaries
Request flow is `routes → service → repository → models`. The boundaries are load-bearing:
- **Services** hold domain logic. They **return models and raise `ServiceError`** — they never format user-facing strings.
- **Routes** own user-facing messages and own nothing else. There is **no try/except for domain errors in routes**: `app/errors.py` registers app-level handlers for Pydantic `ValidationError` and `ServiceError` that turn them into HTML error pages or JSON error bodies (API requests are detected by `request.path.startswith("/api")`).
- **Repositories are pre-scoped to `user_id`** so an unscoped, cross-tenant query is not even expressible from a route/service. Respect this when adding queries.
- **Error hygiene:** throw for the *unexpected*, return for *expected* domain outcomes.

### Base model mixin (`app/_infra/db_base.py`)
`Base` auto-injects, for every model **except `User` and `ApiCallRecord`**:
- a `user_id` FK with `ondelete="CASCADE"` (via `declared_attr.directive`)
- a pluralized snake_case `__tablename__` derived from the class name

This mixin is why per-user data cascades at the DB level (e.g. the `reap` command bulk-deletes demo users and their rows follow). When deleting through the ORM, note the pairing that recurs across models: DB `ondelete="CASCADE"` on the child FK travels with `passive_deletes=True` + `cascade="all, delete-orphan"` on the parent relationship — the two mechanisms are a matched set, not interchangeable.

### Data conventions
- All timestamps are timezone-aware; values are stored canonically (e.g. weight always in kg) and converted at display time.
- Enums are `StrEnum` + `auto()`, mapped with `values_callable` so the DB stores the value, not the name.
- Pydantic schemas are the validation source of truth at the API boundary; models carry DB-level `CHECK` constraints.

### Frontend
TypeScript compiled by esbuild (`build.mjs`), D3 for charts, CSS token theming via `light-dark()`. Jinja templates live beside their module in `templates/`; shared partials in `app/_templates/`.

## Reference docs
Read before large or cross-cutting changes — they carry rationale this file intentionally omits:
- `ARCHITECTURE.md` — layering decisions, user-scoping, schema notes
- `CONVENTIONS.md` — naming, Hungarian-style Jinja type prefixes
- `DESIGN.md` — product direction and analytics notes
- `README.md` — stack, local setup, deployment


