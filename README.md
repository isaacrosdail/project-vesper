# Vesper - Personal Life OS (WIP)
Vesper is a data-driven productivity web app designed for my own use to help me track
habits, metrics (like weight, steps, sleep, etc), and time, all from the same, centralized interface.

# Project Status
Actively expanding. Current focus: refining core modules, improving efficiency across systems, and
implementing tests to solidify progress.
 
# Key Feaures
- Modular architecture: Each domain (Tasks, Metrics, etc.) is mostly relegated to its own module, with 
separate models, services, and routes.
- Typed Python  TypeScript: Strong typing with strict defaults across backend and fronted, using `mypy` and
TS for improved safety and maintainability.
- Time-aware data tracking: All entries are timezone-aware, with structured and consistent JSON responses for charting & historical
analysis.
- PostgreSQL & Alembic: Production-grade schema with migrations and versioned changes.
- Multi-tenant auth: Supports an arbitrary number of individual users, with persistent sessions and protected routes.
- Production Deployment (from scratch): Deployed via NGINX on a self-managed Linode VPS (Dockerized)
- Custom components: Reusable tooltips, sort/filter-able tables, visual progress indicators, light/dark themes
using CSS tokens.
- D3.js: Dynamic visualizations for habit completions, time logs, and physical metrics (weight, steps, etc)
- Time tracking module: Manual and category-based time logs, with viewmodels for readable durations and time windows.

# Tech Stack
**Backend**:
    - Python, Flask, SQLAlchemy, PostgreSQL  Alembic
    - Testing with pytest
    - Development: Docker, NGINX
    - Linting: `ruff` (Python), `eslint` (TS/JS), `stylelint` (CSS)
    - Build: `esbuild` (minifies CSS/JS for deployment)
    - Type Checking: `mypy` (Python), TypeScript (strict)
**Frontend**: 
    - HTML, CSS (token-based theming), TypeScript
    - Custom UI toolkit (no frameworks)
    - Charts: D3.js

## How to Get Running Locally:
Tested / Operational with the following:
- Linux (or WSL2 if on Windows)
- Python 3.12.3+
- Node: 25.5.0 (Node 23-25 *should* work but are unverified)

Docker:
- Docker Engine (Linux) (see install options for your Linux distro: https://docs.docker.com/engine/install/)
OR
- Docker Desktop on Windows using WSL2 (install here: https://docs.docker.com/desktop/setup/install/windows-install/)
    - I initially developed on Windows inside WSL2, have since moved to full Linux

- Optionally: Bun (use for SOME testing, otherwise not required of course)

#### Note:
- Repository includes both an `.nvmrc` as well as a `.python-version` for optional use with nvm and pyenv to match my local setup.

1. Clone repository & install requirements:
```bash
git clone git@github.com:isaacrosdail/project-vesper.git

# Install requirements for Python & Node
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

npm install
```

2. Configure env
```bash
cp .env.example .env
```
The default values in `.env.example` are safe for local dev. You do not key real API keys to run the app locally, just note that
the weather data fetch itself will of course fail.

3. Start Postgres (Docker, dev default)
```bash
docker compose up -d
```
Compose here refers to the `docker-compose.yml` file in project root. This will build the Postgres image if needed.

Optional alternative: Run the full containerized stack (prod-style; includes both db & web services)
```bash
docker compose -f docker-compose.prod.yml up -d
```

4. Run the app (dev path)
```bash
npm run dev
```

4B. If you chose the prod version, the web service should now be running at:
`http://localhost:5000`


#### Some further notes:
- Bun is optional and only used for some tests
- Postgres is containerized for dev; prod uses full containerization (both db & web services)


## Attributions
Weather data provided by [OpenWeatherMap](https://openweathermap.org/), licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## Icons
- Heroicons (MIT License) [LICENSE.heroicons](app/static_src/img/icons/originals/LICENSE.heroicons)
  © Tailwind Labs, Inc.
  https://heroicons.com | https://github.com/tailwindlabs/heroicons
  Used icons (some modified for sizing/positioning):
  - minus
  - plus
  - bars-3
  - x-mark
  - scale
  - fire
  - trash
  - user-circle
  - chevron-down
  - eye
  - eye-slash
  - ellipsis-horizontal-circle
  - check-circle

- SVG Repo (MIT / CC0) [LICENSE.svgrepo](app/static_src/img/icons/originals/LICENSE.svgrepo)
  Used icons (some modified for sizing/positioning):
  - Moon Zzz SVG Vector
  - Tracking Shoe SVG
  - Construction SVG
