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
