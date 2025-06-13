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
