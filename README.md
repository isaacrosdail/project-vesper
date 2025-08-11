# Project Vesper
Vesper is a personal dashboard + home assistant hybrid focused on intelligent habit tracking, system automation, and self-accountability.

## Core Features
- Daily habit prompts (anchor routines, reflections)
- Major goal logging and intention tracking
- Future: Voice, barcode, and gesture control
- Modular, expandable system

## Modules
- Pomodoro Timer
- Grocery scanning with database to enable shopping tracking, etc (eventually budgeting & calories, TBD)
- Scanning module (centralized functions for other modules in future)
  
## Tech Stack
**Languages & Frameworks**: Python, Flask/Jinja2, SQLAlchemy  
**Frontend**: HTML, JS, TailwindCSS  
**Database**: PostgreSQL (via Docker; originally SQLite)  
**Testing**: Pytest (with coverage via pytest-cov)  
**Tools**: VScode, Git, Docker  

## Notes to Self (Organize Me):
Python dependencies: pip install -r requirements.txt
Node.js dependencies: npm install

# Common commands
npm run dev
npm audit fix  # Fix security issues
pip freeze > requirements.txt   # Update Python deps

# Makefile?
install:
  pip install -r requirements.txt
  npm install

audit:
  npm audit fix
  pip-audit  # if i use it

clean:
  rm -rf node_modules/
  rm -rf __pycache__/

## Note to self:
Module structure:

module_name/
├── __init__.py
├── models.py
├── repository.py  
├── routes.py
├── services.py    # Business logic (like habit_logic.py)
├── utils.py       # Module-specific utilities only
└── templates/

## Attributions
Weather data provided by [OpenWeatherMap](https://openweathermap.org/), licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)



## TIDY (From DEV_SETUP.md):
# Development Setup

## Docker Configs
- `docker-compose.yml` - Local development (database only)
- `docker-compose.prod.yml` - Full production stack with Nginx
- `docker-compose.pi.yml` - My Raspberry Pi deployment

## Development Tools

### TypeScript & Linting

**Commands:**
- `npm run lint` - Check for issues

### Pre-Commit Hooks
Husky runs automatic checks before each commit:
- Linting
- Type checking
- Security audit

To bypass: `git commit --no-verify` OR (for the session) simply do `export HUSKY=0`

## Setup / General Config Stuff

1. Install Docker (on linux)
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```

2. Install Node.js (on linux)
```
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```

## Package.json Scripts:
```json
"build": "cross-env NODE_ENV=production tailwindcss -i .app/static/css/input.css -o .app/static/css/output.css --minify"
```
```json
"scripts": {
"tailwind": "npx tailwindcss -i ./app/static/css/style.css -o ./app/static/css/output.css --watch",
"flask": "flask run --debug",
"sync": "browser-sync start --proxy localhost:5000 --files 'app/**/templates/**/*.html' 'static/css/*.css'",
"dev": "concurrently \"npm:tailwind\" \"npm:flask\" \"npm:sync\""
}
```

## Dependencies Reasoning
- cross-env ->
- browser-sync -> Live reloads, part of npm run dev script
- concurrently -> ????
- jest-environment-jsdom -> Needed for Jest to mimic DOM?
