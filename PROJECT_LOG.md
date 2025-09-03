## Used to track daily/per-session progress

## [Wed 26.02.25] *(Old - obviously replaced by Flask app)*

**Log:**
- Installed Raspberry Pi OS (RPi 4 Model B), installed Node.js, & got MagicMirror running
- Installed MMM-Remote-Control via `npm install` in `~/modules/MMM-Remote-Control`
- Whitelisted all local IPs for access from laptop/etc

## [Sun 02.03.25] Pomodoro Timer Prototype
**Goal(s):**
- Build a Pomodoro timer that:
  - Runs locally on desktop
  - Has start, stop, reset functions
  - Tracks work vs break sessions
  - Can later be ported to MagicMirror
**Log:**
- Added SSH key to new PC
- Cloned Vesper repo to `Desktop/Projects`
- Installed Python 3.13 to `C:\Program Files\Python313`
- Set up basic file structure:
  - `pomodoro.py` – timer logic
  - `cli.py` – handles input/output
- Added multithreading for timer logic

**Next Up:**
1. Fix input handling so user can type `stop` during countdown


## [Fri 07.03.25] *(Deprecated – replaced by Flask app)*
**Log:**
- Made desktop shortcut on Pi to initiate MagicMirror
- Added hotkey (CTRL+Q) using xbindkeys to killall node
  - Appended line to `~/.xbindkeysrc`
- Created `scripts` folder on Pi 4B
  - Used `crontab -e` to add:  
    `@reboot /home/pi/scripts/start_xbindkeys.sh`

## [Sat 08.03.25]

**Log:**
- Installed OpenVoice to `user/tools` directory
  - Created venv `myvenv` and installed `requirements.txt`
  - Uses Python 3.10 (`Users/Name/Python310`)
- Installed MeloTTS (multi-lang lib?) and `unidic`

## [Tue 18.03.25]

**Goal:**
- Get barcode scanner functionality running in CLI to scan groceries and add/update DB

**Log:**
- Installed Flask, `requests`, and SQLAlchemy in venv
  - `requests` for API calls
  - SQLAlchemy to ease future PostgreSQL migration

## [Thu 20.03.25]

**Goal:**
- Basic Flask web app UI to function as "homepage" (equivalent to MagicMirror) and display current time

**Log:**
- Created basic Flask app in `app.py`
- Made `index.html` template
- Successfully displayed static date & time


## [Sat 22.03.25] 

**Goal:**
- Add `grocery.html` template to add new product to database
**Log:**
- Added templates:
  - `grocery.html` (to list grocery DB?)  
  - `add_product.html` (form to add product) ← UNFINISHED
- Quick side quest:
  - Need to merge into one unified DB under `core/database.py`
- Implemented basic barcode input: prints to terminal to confirm
  - Windows can't run scanner listener as daemon; will use `evdev` on Linux to read input from barcode scanner specifically
**Next Up:**
- Write function to add product from barcode
**Stretch Goal:**
- Make Vesper detect repeat scans and increment quantity instead of duplicating


## [Mon 24.03.25]

**Goal:**
- Add product to grocery DB from barcode  
- (Stretch) Detect repeat scans & increase quantity
**Log:**
- Switched to ORM style for DB + queries
- Created `Product` model using ORM `Base` class (will expand later)
- Stretch goal not reached (big sad)
**Next time:**
1. Tweak `add_product` to detect repeats and increment quantity  
2. Fix `grocery.html` to generate table headers dynamically


## [Tue 25.03.25]

**Goals:**
1. Tweak `add_product` logic to detect repeat scans and increase quantity
2. Make `grocery.html` table headers generate dynamically
**Log:**
- Forgot to log steps, but both goals were completed


## [Wed 26.03.25]
**Log:**
- Installed Remote Development extension in VSCode
- Successfully connected to Raspberry Pi via SSH
**Next Time:**
1. Implement `add_product` route: accept scanned barcode, enter rest of product info, add to DB, show in UI  
2. Set up Flask-Migrate: init, create/apply schema version, test with `Product` model


## [Fri 28.03.25]
**Log:**
- Finalized `Product` model as permanent barcode-to-product record
- Introduced `Transaction` model for individual scans
- Fixed barcode being incorrectly used as primary key
**Next Time:**
1. On barcode scan:
   - If **not** in `Product`, prompt for name/price → add to `Product` and create `Transaction`
   - If **exists**, just create new `Transaction`
   - Need to finalize `add_product` and `add_transaction` functions


## [Sat 29.03.25]
**Goal:**
- Sort out logic for `add_product` and `add_transaction`
**Log:**
- Updated logic for both functions (still messy, need tests)
- Installed `pytest` and `pytest-mock`
**Tests to add:**
- Validation for DB entries (e.g., price formatting)
- Make `add_product` and `add_transaction` form fields mandatory


## [Sun 30.03.25]

**Goal:**
- Begin implementing tests using `pytest` / `pytest-mock`
**Log:**
- Cleaned up DB functions in `models.py` for better modularity
- Renamed `handle_barcode` → `process_scanned_barcode`
  - Retooled to auto-add transaction upon scan
  - Still need logic to trigger `add_product` UI if product not found
- Started unit tests:
  - `conftest.py`: In-memory DB fixture
  - `test_models.py`: Initial test for `add_product`
**Next Time:**
- Add WebSocket support to redirect to `/add_product` in real-time when scanned barcode doesn't exist


## [Tue 01.04.25]

**Goal(s):**
- Add "daily tether(s)" UI element to dashboard page  
  - Use Flexbox  
  - Centered card layout  
  - Hover effects  
  - Editable state  
  - Clean styling  
**Log:**
- Modified `index.html` to include `tether-card` div
- Began styling the card layout


## [Wed 02.04.25]
**Goal(s):**
- Finish JS logic for `tether-card` input  
  - Centered card, hover effects, editable state  
  - Clean styling, padding, spacing
**Log:**
- Block 1: Added JS to handle `tether-card` input
- Block 2: Added JS to hide button/input field once tether text is submitted
- Got sidetracked writing a couple unit tests—will revisit after completing styling
**Next Steps:**
- Finish JS styling
- Add unit tests for all functions in `groceries/repository.py`
- Add DB model for storing `tether-card` info (optional)
- Add WebSocket support to redirect to `/add_product` when scanned barcode is not found


## [Fri 04.04.25]

**Goal(s):**
- Expand unit testing coverage, starting with DB logic in `groceries/repository.py`
**Log:**
- Added input validation to `add_product`
- Added test cases for `add_product`:
  - Happy path  
  - Missing data  
  - Invalid price range
- Added 'no entries' & 'with entries' test cases for `get_all_products`
- Added test cases for `get_all_transactions`:  
  - No entries  
  - With entry  
  - Confirmed `joinedload` still works after session close
**Next Time:**
1. Expand test coverage:
   - `add_product`, `add_transaction`
   - `process_scanned_barcode`, `ensure_product_exists`


## [Wed 09.04.25]
**Goals:**
- Add `tasks` module and corresponding template
**Log:**
- Migrated to Blueprint architecture for routes:
  - `main`, `grocery`, and `tasks` (auth pending)
- Restructured `app/` directory
- Added pytest config


## [Thu 10.04.25]

**Goals:**
- Flesh out `tasks.html` and implement 3 recurring habits  
- *(Stretch)* Add habit streak UI
**Log:**
- Added `add_task` template
- Created `modules/tasks/repository.py` for DB logic
- Used GET/POST in `tasks_routes.py` to process form data and render `tasks.html` with task table

**Log:**
- Rendered “Today’s Habits” list on dashboard  
  - Filtered `Tasks` by habit type and `is_anchor` flag
- Added checkbox to mark task complete:
  - Used `fetch()` to POST to DB when clicked (via `onclick`)
  - Current state:
    - ❌ Feature not yet functional
    - `complete_task()` in `tasks_routes.py` needs to:
      - Identify task
      - Extract data from request
      - Set `is_done = True` and `completed_at = today`
    - JS only handles marking complete (unchecking doesn't undo)
    - Need to sanitize `completed_at` as date object
**Next Up:**
- Mark habit complete → update timestamp  
- Auto-reset daily via cronjob or first-run check


## [Fri 11.04.25]

**Log:**
- `complete_task()`:
  - Locates task
  - Sets `is_done = True`
  - Adds `completed_at = today`
  - Returns `jsonify(success=True)` to JS
- Updated `create_app()` to accept environment config params (`testing`, `dev`, etc)
  - Added `config.py` with `BaseConfig`, `DevConfig`, and `TestConfig`
- Installed Docker for PostgreSQL to replace SQLite
- Created `vesper` and `vesper_test` DBs in Docker container
  - Updated Vesper config to point to correct URIs
- Installed `psycopg2-binary` in venv + added to `requirements.txt`
- All tests now run against PostgreSQL test DB  
  - Accurate `datetime` behavior and schema validation

## [Sat 12.04.25]

**Log:**
- Switched fully to PostgreSQL
- Installed `pytest-postgresql` for testing (added to `requirements.txt`)
- Uninstalled `psycopg2-binary`, installed `psycopg[binary]` instead (backend performance?)
- Installed local PostgreSQL for `pytest-postgresql` usage  
  - Local → for tests  
  - Docker container → for dev
- Ditched `pytest-postgresql` (broken / unmaintained)
  - Will connect tests directly to container DB
- Blocker: `pytest` can’t authenticate to DB
  - Password auth keeps failing despite being correct
  - Tried editing `pg_hba.conf` to allow local password auth (`md5`), no success


## [Sun 13.04.25]

**Log:**
- Set up PostgreSQL in Docker using `docker-compose.yml` and `init.sql`
- Integrated DB with Flask app and verified via:
  - Connection test
  - Table creation
  - Rollbacks
  - Constraint enforcement
- Structured test suite:
  - `unit/` and `integration/` folders
  - Configured `pytest.ini`
- Wrote first integration test: full task creation + completion flow
- Merged GET/POST logic into unified `/add_transaction` route
- Refactored DB session handling:
  - Switched to `scoped_session` with automatic teardown
  - No more manual `.close()`
  - Monkeypatched `get_db_session()` in tests to unify test + app session → avoids `DetachedInstanceError`
- Replaced unnecessary `.commit()`s in tests with `.flush()` for isolation
- All tests pass, including edge cases
- Achieved near/full 100% test coverage
- Used test failures to detect & fix real bugs
- Cleaned up:
  - Removed dead comments
  - Renamed helpers
  - Standardized naming across modules
**TODOs:**
- Add toggle logic to tasks checkbox  
  → e.g., `/tasks/toggle/<id>`
- Design anchor habit model (`is_anchor: bool`)  
  → Add repo, route, test flow
- Maintain 100% test coverage  
  → Track deltas post-commit


## [Tue 15.04.25]

**Log:**
- Created `Backups/Vesper` directory for PostgreSQL container DB backups
- Centralized scripts under `User/Scripts` and added to `PATH`
  - Now `vesper-db-backup` command works from anywhere in PowerShell
- Implemented full CRUD for `tasks` (except DELETE)
  - Merged `complete_task` logic into PATCH section of new `update_task` route
- Created `tasks/dashboard.js`:
  - Enables direct cell editing via JS + `fetch()` PATCH requests
- Began generalizing `editTableField()` JS function to support editing across any Vesper table
- Initialized `npm`, set up Jest for JS unit testing:
  - Chose `node` env, used `v8` for coverage
  - Disabled coverage reports for now
  - Enabled auto-clear of mocks before each test
- Installed `jest-environment-jsdom` to mimic DOM & confirmed test runs
**NOTE:**
- Plan: Use **Jest** for unit testing, **Cypress** for end-to-end tests
- Consider generalizing CRUD into a shared `crud_routes.py` later


## [Wed 16.04.25]
**Log:**
- Added DELETE route for `tasks`
- Added JS to dynamically show delete button on row hover
- Began switch from Bootstrap → Tailwind CSS
	- Recreated most of the navbar styling in Tailwind


## [Fri 02.05.25]

**Log:**
- Refactored/renamed "Tether" → "Critical Task"
- Discovered Tailwind styles require manually restarting Flask server to update 😅
- Fixed `launch.json` to point to correct entry for F5 Debug mode + breakpoints
- Implemented delete-on-hover functionality for `Tasks` table rows
**Remaining Before Hosting:**
- Finalize and stylize delete-on-hover in `Tasks` dashboard
- Ensure checking off anchor habits works as intended
- Add input validation + warning messages for `add_task`, `add_product`, `add_transaction` templates
- Add placeholders to forms (both English & German — for lang toggle)
- Copy language toggle from Resume Site into Vesper
- Extend `editTableField()` to work across all `Tasks` fields (except ID)
**Next Time:**
1. Tweak `Groceries` dashboard to support delete-on-hover behavior

## [Sat 03.05.25]

**Log:**
- Added conditional product creation flow to `add_transaction` route
- Normalized/parsed form data, enabled re-submission with `net_weight` if product not found
- Cleanly separated `product` and `transaction` data
- Added fallback logic for `price` during product creation  
  *(Temporary hack — will remove `price` from `Product` model later)*
- Used `show_product_fields` flag to dynamically reveal required inputs
- Centralized `deleteTableItem()` JS function inside `js/utils.js`
- Enabled marking anchor habit complete via checkbox  
  → also persists across reload!
- Updated endpoints to follow RESTful structure  
  → adjusted tests accordingly
- Added consistent table styles in `base.html`  
  → also polished "date completed" display for tasks
- Added `flash()` messages for `add_task`, `add_product`, and `add_transaction`

## [Sun 04.05.25]

**Log:**
- Began styling home dashboard cards
2. Add script to enable npm run dev to run Flask app, BrowserSync, and Tailwind watch
  - Tailwind watch + BrowserSync to update styling & reload automatically
  - Installed concurrently for this too?

## [Mon 05.05.25]

**Log:**
1. Table styling
  - Removed `.card` & `table-wrapper` remnants
  - Converted layout + visuals to Tailwind
  - Centralized table styles in `base.html`:
    - Distinct header styling for clarity
    - Alternating row stripes + hover effect (need to refine colors)
    - Red delete button
    - Standardized spacing across all tables
    - Wrapped tables in card-style divs to match home dashboard layout
2. Made `Transaction.date_scanned` timezone-aware (UTC)
3. UI Polish
  - Polished table + heading/caption styling
  - Replaced delete button text with SVG icon
4. Installed `cross-env` & set up npm run build script for Tailwind:
     
## [Tue 06.05.25]
**Git Goal:** Practice branching & merging

**Log:**
- Removed price tag from `Add Product` template

## [Sun 11.05.25]
**Goal:**
1. Auto-seed dummy data in dev mode after app startup
**Log:**
- Cleaned up `config.py` to use proper ENV flags (Flask built-in environment detection)
- Created `seed_db.py`, invoked during app creation to seed DB with dummy data
- Added `reset_db` route/function to:
  - Clear DB
  - Run `seed_db.py` again  
  - Return to previous page after reset (demo/dev quality-of-life)
  - Flow: Button → `/reset_db` → clears/seeds → redirect

## [Tue 13.05.25]

**Goal:**
1. Add "Reset" button for dummy DB data (drop tables → run `seed_data.py` again)
**Log:**
- Expanded `reset_db()` logic
- Discovered potential **PostgreSQL deadlock** when Reset DB button is pressed

## [Wed 14.05.25]

**Log:**
- Created custom `Dockerfile.postgres` to include `nano`
- Modified `package.json` to add new script:
  - `npm run debug` → allows breakpoint-based debugging
- Fixed deadlock bug:
  - Cause: lingering "idle in transaction" connections  
  - Solution: clean session handling / teardown
**Next Up:**
1. Add logic to redirect `reset_db` route back to referrer page (referrer check)


## [Sun 18.05.25]

**Log:**
- Installed `python-dotenv`, created `.env` file  
  → Obfuscates sensitive config (e.g., DB URI) from repo

**To implement env-based config:**
- Added Flask container config to `docker-compose.prod.yml`
- Updated `config.py` to pull values from environment variables instead of hardcoding
- Flow:
  1. `.env` → contains secrets  
  2. `Config.py` reads from `.env`  
  3. Flask app gets configured  
  4. DB connects using proper URI

- Installed `gunicorn` locally to test `docker-compose.prod.yml`
  - Replaced `flask run` with gunicorn command
    - First `app`: the module (`app.py`)  
    - Second `app`: the Flask app instance inside

## [Tue 20.05.25]

**Before:**
- Configured `docker-compose.prod.yml` with proper services:
  - `db` for PostgreSQL  
  - `web` for Flask app
- Switched from `pycopg2` to `psycopg2-binary` for Docker compatibility

**Log:**
- Removed unused `pytest-postgresql`
- Cleaned up `requirements.txt` (removed unused deps)
- Added `ProdConfig` to `config.py` for production settings
- Made `create_app()` automatically use config based on `FLASK_ENV`
- Set up distinct DB URIs for different environments
- Created `wsgi.py` as prod entry point
- Set up `gunicorn` with `wsgi:app` in `Dockerfile`
- Finalized environment-aware config across codebase

---

**Project Cleanup To-Do (Post-Hosting):**
1. Write `README.md` (features, setup)
2. Refactor code structure / architecture
3. Add comments to complex logic
4. Prune comments in main + merged branches

---

**Linode Hosting Prep:**
- Installed Docker and Node.js, set up Nginx (set up Nginx to serve static directly), got a proper domain name & SSL certs

## [Wed 21.05.25]
**Goal(s):**
- Configure HTTPS access on Linode server, sort out timeout issue
- Standardize project logging format, tidy PROJECT_LOG.md
- Set up CI, establish git branch workflow
**Log:**
- Configure HTTPS - done.
- Implemented refined log format across all existing project logs
- Setting up CI/CD (continuous deployment) w/Github Actions:
	- To project root, add: .github/workflows/docker-ci.yml
	- Add SSH on server & secrets needed for CI
	- Now CI runs via Actions when we push main!
*Note: PuTTY for ssh
**Next Up:**
- Ensure local dev stuff is solid again
- Begin tackling post-hosting checklist

## [Fri 23.05.25]
**Goals:**
- Clean up obvious issues on live site first ("£None" and "Today's Intention:[text]")
**Log:**
- Fixed above issues
- Fixed CI pipeline issue (added --build to ensure containers rebuild)
- Removed Tailwind styles output from gitignore (silly me)
**Next Up:**
1. Clean up readme/tech stack info, w/ decisions for choices
2. 2. Clean up readme/tech stack info (with decisions for choices)
3. Sort out dev/prod database separation (dev-> personal use, prod-> demo info only)
	Options:
		- Different database URIs in .env vs production environment variables
		- Maybe different database names entirely (vesper_dev vs vesper_prod) SMART, do this!
4. Add "This Week's Improvements" feature

## [Sat 24.05.25]
**Log:**
- While syncing what I did in my resume site, I made some adjustments in Vesper to match:
	- Use more semantic HTML (header, main) in base.html
		- Wrap navbar include in `<header>`, change block content from being in a div to in `<main>`
	- Condense outside 2 wrapper divs into one in navbar.html
		- Inside that, we have LEFT div (Branding & Links) then RIGHT div (Reset DB button) -> 2 birds, 1 stone :P
	- Add cursor pointer styling for btn_classes() macro

## [Sun 25.05.25]
**Goals:**
1. Not much today, mostly worked on resume site

**Log:**
- Tweak/trim launch.json (FLASK_APP: app:create_app('dev') -> flask_app.py)
- Update font family to match resume site
- Update groceries dashboard to reference styling macros properly

**Next Up:**
- Tidy up code/comments/etc, enforce branching pipeline

## [Fri 30.05.25] - dev branch
**Goal(s):**
- Install Alembic
**Log:**
- Consolidate env configs to config.py
	- Removed redudant env detection from create_app()
	- Centralized env logic in config.py with auto-selection
	- Simplified create_app() with pre-configured Config class
	- Maintained flexibility for testing/overrides (can pass in configs to create_app() if desired)
	- Eliminated duplicate load_dotenv() calls
- Install Alembic and basic setup
- Create new Habit model, prune type and is_anchor fields from Task model accordingly
	- Cleanup/Refactor todos:
		- Add dashboard & CRUD routes
		- DONE?: Add dashboard.html and add_habit.html     
		- DONE?:  Remove anything for type="habit" and is_anchor from Add Task form/page
		- Refactor JS for index.html checkbox stuff to change API endpoints

## [Fri 06.06.25]
**Goals:**
1. Add 2 models:
	1. DailyIntention model -> DONE
	2. DailyMetric model -> DONE
	3. Alembic revision!
2. Make Daily Intention on homepage now use/update our new model instead of just the element's text!

**Log:**
1. Made DailyIntention & DailyMetric models
	- Alembic revision
		- Ran into issue: Since we switched from vesper to vesper_dev for our dev DB, vesper_dev didn't have an 'alembic_version' table (which is why alembic current showed nothing), but it DID have actual tables from previous migrations.
			- Fix: Just needed to run 'alembic stamp head', which basically tells Alembic: "Hey Alembic, we're actually at the latest migration"
				- It creates the alembic_version table in vesper_dev, marks it as being our latest migration, & gets everything in sync!
				- Then, we could run our revision and run alembic upgrade head
				
2. Updated Daily Intention on homepage to use DB for persistence
	- Added created_at field to DailyIntention model
	- Created get_today_intention() function in habits_repository.py
	- Updated homepage route to fetch & pass today's intention to template
	- Modified index.html: added Jinja conditional to use intention OR default text, refactor critical-task to daily-intention
Key Changes: DB schema, repository layer, route logic, template rendering

3. Other changes:
	- Fixed lazy loading errors (sneaky!) by moving habit completion logic from templates to backend
	- Refactored index.html dashboard route to pre-calculate completion status and streaks as dictionaries

**Where I Left Off:**
- Started test_habits_habit_logic.py unit test file to suss out possible race condition with our AJAX

## [Sun 08.06.25]
**Log:**
- Refactored DB management from create_all() to Alembic migrations

## [Mon 09.06.25]
**Log:**
- Added a custom base class for basics like id & timestamp information
	- Ran Alembic revision & refactored accordingly to use updated references
- Clean up environment variable handling a bit, wrap seed_dev_db route in env var conditional check

## [Tues 10.06.25]
**Goals:**
1. Get started with weather API calls
**Log:**
1. Weather API calls
	- Sign up for OpenWeatherMap (personal em, made filter for it)
	- Add API key to .env (local & server)
	- Make new api.py to use it via Flask
**Learned:**
- Async/await, basic JSON handling

## [Wed 11.06.25]
**Goals:**
1. Expand weather API widget functionality a bit
2. Start implementing an animated sun arc
	- Begin with Jest for testing pieces of this
	- Added "testEnvironment: 'jsdom'" to jest.config.js (fake browser environment)
	- Wrapped DOM code in safety checks: if (element) { element.onclick = ... }
**Log:**
1. Expanded weather API widget functionality
	- Grab sunset time
	- Make emojis display conditionally depending on weather description
2. Animated Sun arc
	- Figured out the math for a moving sun that follows actual sunrise/sunset times
	- Learned Canvas basics for this: Set up first Canvas element & drawing functions
	- Refactored these functions to separate pure match function to prep for testing
3. Diving back into Jest testing
	- Made a basic 2 + 2 = 4 Jest test
	- then a test to calc sun position at midday (should be 1)
4. Using setInterval for both getWeatherInfo & sun drawing functionalities
	- Weather info updates every hour, sun position updates every 10mins
**Learned:**
- JS modules are a mess
- Canvas coordinate system & basic transform
- Async/await flow with setInterval timing
- Separating data fetching from data usage (global caching)

**Up Next:**
1. Stylize sun so it's clearer what it is (add horizon, sun rays, etc?)
2. Add tooltip for onhover of canvas to further clarify that it moves in realtime/follows the real sun position based on sunrise and sunset of the city
3. Make it read user's timezone/city so it's not hardcoded to London

## [Thurs 12.06.25]
**Log:**
- Remove super() usage in templates, refactor completed_at to created_at to fix bug with HabitCompletion

## [Fri 13.06.25] - Mobile Nav Polish & Dev Tooling
**Log:**
1. Began hamburger/mobilenav menu
  - Started with JS resize detection (incl. throttling) but simplified to CSS media queries with JS for state cleanup later.
2. Docker & Deployment Standardization
  - Restructured compose files: docker-compose.yml (dev), docker-compose.pi.yml (pi deployment), docker-compose.prod.yml (production)
  - Updated all APP_ENV variables from old FLASK_ENV pattern
  - Added proper volume and container naming conventions (-dev, -pi, -prod suffixes)
3. CI/CD Updates
  - Modified Actions to use correct compose files per environment
  - Added deployment flow for Pi vs prod
4. Code Quality Infra
  - Set up TypeScript, ESLint, and Husky for code quality and pre-commit checks
5. Misc
 - Fixed some ESLint warnings, cleaned up rest of super() usage, & added notes for future moon implementation.

## [Sun 15.06.25]
**Log:**
- Added sunrays using stroke to clarify sun styling

## [Wed 18.06.25]
**Log:**
1. Revamped Product model & Tables
	- Hide ID columns in production (is_dev reference)
	- Replaced price field with category, unit_type, and calories_per_100g
	- Updated migrations, seed data, forms, and repository functions
	- Added dropdown selects for category & unit_type fields
	- Tweaked groceries Products table to reflect schema changes
	- Cleaned up zombie 'price' references
2. Added Category system to Habits
	- Added 'Category' field to Habit model (default='misc')
	- Added dropdown input in add_habit form
	- Updated seed_db & seed_dev_db accordingly
3. Start on "Daily Check-In" widget (index.html)
	
## [Thurs 19.06.25]
**Log:**
1. Implemented User model basics
	- Created User model with username field & user_id
	- Refactored CustomBase to be split into Timestamp mixin & BaseModel
	- Updated seed_db to create default user
2. Updated Product/Transaction models
	- Added str methods
	- Fixed routes to handle new Product fields
3. Bit more on Daily Check-In Feature
	- Began mocking up card UI
	- Created DailyCheckin model

## [Fri 20.06.25]
**Log:**
1. Play around with grid styling on DailyCheckin card
2. Cleaning up forms & adding basic frontend validation
	- Use form-group styling to clean up form layout
	- Add user-valid/invalid
	- Add HTML5 validation with required, pattern, min/max
	- Add tooltips to some form fields
3. Tests
	- Remove a couple dumb tests
	- Add fixture for sample_product
	- Add test for __str__ for Product/Transaction
	
## [Sat 21.06.25]
**Log:**
1. Getting Started with Data Visualization (Plan: Start with Plotly, check out D3.js later)
	- Install plotly & plotly express: pip install plotly , and pip install plotly[express]
	- Install pandas: pip install pandas

## [Sun 22.06.25]
**Log:**
1. Code Quality, UI/UX, & Architecture Improvements
	- Added generalized PATCH route (remove redundant update_task & delete_task)
	- Extended double-click inline cell editing to habit titles
	- Moved styling to form-group CSS classes for consistency
	- Associated labels with inputs for better accessibility
	- Transitioned from inline event handlers to addEventListener for cell editing
	- Moved table cell edit functions to dedicated tables.js file
	- DailyIntention: Replaced clunky submit button with blur/enter-to-save pattern
	- Updated all other fetch() requests to more modern async/await pattern
	- Improved error handling in some routes & implemented better JSON responses for success/error
	- Fixed critical issue in seed_db where I didn't commit deletes before proceeding (oops!)
	- Add seed data for DailyMetrics - weight, steps, movement
	- Make metric inputs & chart containers stack vertically on smaller screens
2. Added Metrics module
	- Added blueprint, basic route, navbar links, etc.
	- Added utility function to make bar graphs & added a couple basic graphs

## [Mon 23.06.25]

**Log:**
1. Event Delegation Refactoring
	- Converted from individual event listeners to centralized event delegation
	- Generally cleaned up listeners
2. Input editing UX
	- Made input field size to accommodate text
	- Fallback to original text if input is empty
3. Organization / Documentation
	- Added JSDocs to several functions
	- Extracted drawSun magic numbers into SUN_CONFIG constant
	- Standardized backend JSON responses a bit
	- Cleaned up some variable naming
4. Data Export via CSV
	- Key components:
		1. Python csv handling (csv module or pandas)
		2. Flask file download mechanics (send_file, proper headers)
		3. Data formatting & Cleaning before export
		4. Frontend polish for button/options
	- Getting started with DictWriter/DictReader
5. Adding Price per 100g
	- Added function basics to groceries/utils.py (& type annotated)
	- Made basic test to check
	- Added column for this in Transaction table
6. Metrics tweak: Added aspect-ratio CSS to make graphs match height

## [Wed 09.07.25]
* Working in mini_sprint branch *
**Log:**
1. Made "METRICS WE'RE TRACKING" note in Obsidian to keep the following straight
	- Put all metrics I'm thinking of tracking into a card on main page, seeing where the dust settles just to get things moving
# TODOS:
1. Add Docker checkhealth
2. Add health/status API endpoints (have Docker checkhealth ping these too)
3. Add external monitoring (also ping our health/status endpoint(s))

## [Mon 23.06.25]
1. Routes & REST Improvements
  - Made route structure more RESTful
  - Updated completions/delete route to accept arbitrary dates (was hardcoded to /today)
2. Time Entry Integration
  - Wired up route for adding time entries
3. Schema & Repo Layer Changes
  - Product model: Added deleted_at for soft deletion
  - Habit model: Added cascade delete on completions to prevent orphan records
  - Repo functions updated to exclude soft-deleted products (deleted_at.is_(None))
4. DB Connection Cleanup
  - Added database_connection() context manager in database.py
  - Refactored multiple routes to use this, with try/except for route-level error handling
5. Repo Fixes
  - Updated add_product() repo function to support newly added fields

## [Tues 29.07.25] - CSS/UI Tweaks
**Log:**
1. Style & Theme Adjustments
  - Changed placeholder text color from blue → red (blue looked too link-like)
  - Will revisit color once card background is finalized
  - Moved all theming rules into themes.css, imported via style.css
2. Misc:
  - UX Improvement: On double-click edit, auto-highlight text to make field editable state obvious
  - Found bug: update_daily_intention returning 500, unresolved at this point

## [Wed 30.07.25] - Auth Work, Flask-Login Start
**Log:**
1. Flask-Login Setup & User model enhancements
  - Installed flask-login
  - Drafted login & register forms, validate_username/validate_password, & register_route
  - Centralized error messages in app/core/messages.py (currently only login-related msgs)
  - Added name and role fields to User model
  - Moved model to app/core/auth/models.py
2. Misc:
  - Bug fix: Fixed update_daily_intention 500 error
  - Dev Tool Streamlining: hid & unified reset buttons used for dev/debugging


## [Fri 01.08.25]
**Log:**
1. Minor work
  - Renamed utils/ folders to common/ in both Python and JS
  - Tweaked seed functions and folded UI into "admin panel" controls

## [Sat 02.08.25]
**Log:**
1. Auth Retrofitting & DB Layer Cleanup
  - Refactored delete_all_db_data to use session instead of engine
  - Escaped Postgres reserved identifiers (e.g. "user")
  - Fixed test isolation issues: clear_tables fixture had uncommitted transactions
  - Added missing timeentry table to DATA_TABLES in constants.py
  - Found bug: disabled form fields return "" not None
2. Testing Infrastructure
  - Added AuthActions class + authenticated_client fixture for protected route testing
  - Fixed monkeypatching issues by fully switching to db_session in tests
  - Fixtures updated to include required user_id for sample data
  - Added commit() calls in clear_tables fixture
3. Validation Refactor
  - Switched from pytest.raises to returning error lists (update tests accordingly)
  - Added conditional validation (e.g. creating_product flag)
4. Dependencies
  - Removed mirakuru, port-for (legacy, left breadcrumb), Added ruff==0.12.7 for linting
5. Monitoring Setup
  - External: Configured UptimeRobot to ping new _internal/health_routes endpoint
  - Docker: Added health checks (currently prod only)
6. Misc
  - Migrated from docker-compose (binary) → docker compose (plugin)

## [Thurs 07.08.25] - Security Hardening, CSP, Plotly Debugging
**Log:**
1. CSP & Security Headers
  - Added security headers to NGINX config
  - Injected CSP with per-request nonce for inline theme JS; didn't work with Plotly - injects its own scripts/styles
  - Removed oninvalid from form (CSP)

## [Fri 08.08.25] - Form Overhaul, Accessibility, UX Improvements
**Log:**
1. Form Cleanup & Modals
  - Added `<fieldset>/<legend>` to all forms
  - Converted 'add task' & 'add habit' pages to modals using `<dialog>`
  - Removed now-unused templates for add_task/add_habit
  - Cleaned up redundant divs (eg, dashboard-container)
2. Input & Accessibility
  - Added sensible min/max/maxlength/placeholder attributes
  - Marked required fields where appropriate
  - Added basic Cancel/Return buttons to grocery & login/register forms
  - A11y: Fixed label for/id associations & added aria-labels to icon buttons
3. Git Workflow
  - Improved commit message hygiene
  - Practiced better staging/reset discipline

## [Sat 09.08.25]
**Log:**
1. API Limiting Logic (Draft complete)
  - Only counts successful calls; reverts stored count on upstream failures
  - Atomicity: explored `ON CONFLICT ... WHERE` (Postgres)
  - UPSERT pattern with 429 (limit), 502 (fail)
2. Errors & Debugging
  - Added `raise` in context manager to allow errors to propagate
  - Tweaked debug.py: prefer Flask logging over print, mask DB URI password in logs
3. Docker Compose (prod)
  - DB kept internal (db:5432, no published port -> 5432:5432)
  - Added healthchecks:
    - DB: pg_isready + specific user/db name
    - Web: curl/health
  - Added log rotation (limits size & file count)
4. Dockerfile
  - env_file: (eg, prod.env) values injected into container; read via os.getenv()
  - .env + load_dotenv() is for local dev only - never runs in prod
  - config.py picks up DB URIs etc, loads into app.config. Always read config from current_app.config[], not env
5. Enforce ENV vs Auth Separation
  - Roles = what someone can do
  - ENV = what the app shows/does regardless of user
  - load_env() gated in prod (in config.py)
6. ENV Handling Improvements
  - Switched from os.environ['APP_ENV'] -> app.config['APP_ENV']
  - Centralized in __init__.py: sets APP_ENV & injects DB URL into Alembic
  - AUTO_MIGRATE: Defaults on, overridden off in prod.
7. Updated tests to reflect above changes

## [Sun 10.08.25]
**Log:**
1. Practiced git rebase on resume-site backup repo to get acquianted
2. Updated docker-compose.pi.yml to mirror other compose file updates

## [Wed 13.08.25]
**Log:**
1. Created theme-demo page (what is now style-reference.html) for easier styling workflow
2. Implemented tooltips using JS with custom styling
3. CSS Overhaul
  - Clarified roles of .wrapper, .content, .dashboard-container, and .card-dashboard
  - Pruned & reorganized styles so spacing & layout comes mostly from gap instead of random margins
  - Moved several utility classes to selector-based approach (nav, navlinks, etc.)
  - Simplified & streamlined selector usage
  - Began simplifying/tuning table styling
  - Stripped remaining Tailwind stylings from codebase (I think?)
  - Extracted styles to "base" variants for DRY CSS:
    - .btn (shape/ergo) + variants
    - Added "pressed" effect to .btn
    - Used `:where(input..)` + minimal input-inline overrides
  - Wrapped hover effects in @media queries
  - Revamped "Daily Habits" section: extracted styling to class selectors, added labels, began planning JS for fire emoji and strikethrough animations

## [Fri 15.08.25]
**Log:**
1. Build Pipeline Overhaul
  - Migrated to esbuild building for JS+CSS
  - Revamped npm scripts accordingly (dev/watch vs build vs lint/test)
  - Added cross-env & wait-on for scripts
  - Some TS / linting config stuff
2. Refined style-reference.html
  - Condensed swatches into compact squares to save space
  - Improved targeting of swatches vs components
3. Debug Logging Improvements
  - Compacted output, prevented repeat logs on reloads
  - Added setup_request debugging to log requests only in dev mode
4. Error Page Implementation
  - Added 404 page with solid setup/styling
  - Learned about SVGs, animate/keyframes, & clamp()
  - Added animation with @media query for reduced motion
5. A11y Stuff
  - Added aria-hidden to SVGs, aria-labelledBy elsewhere
  - Added aria-labels for main navigation

## [Sat 16.08.25]
**Log:**
1. Drilled JS loops/arrays & applied by converting weatherInfo's if/else chain to "Object.entries(..).find()"
2. Installed Bun

## [Sun 17.08.25]
**Log:**
1. Timezone Infrastructure Implementation
  - Added timezone column to User model (default: Berlin)
  - Enforcing rule: Store/query in UTC only, convert local -> UTC on input, UTC -> local on output
  - Added/cleaned helper functions in time_utils.py
  - Refactored home() route:
    - Replaced inline datetime math with helpers usage
    - Isolated  hardcoded "Europe/London" to single location (setting stage for current_user.timezone)
    - Tied greeting logic to localized 'now'
2. JS Modules migration to esbuild
  - Switched to esbuild with bundle.js output
  - Adopted modular init() pattern with guards
  - Learning separation between auto-runners vs export-only
  - Cleaned up theme-manager, toast, tooltip
3. Misc
  - Added `/admin/reset-dev` POST route for db reset/reseed workflow
  - Fixed some activity log bugs

## [Mon 18.08.25]
**Log:**
1. Model changes
  - Drop completed_at column from HabitCompletions, added Priority (enum) to Tasks & changed 'type' column to 'category'
  - ALL: Changed 'title' columns to 'name' for clarity


## [Sat 23.08.25] - Docker/Nginx Cleanup, CI/CD refinements, Theme Work
**Log:**
1. DevOps / Infra
  - Moved NGINX into a third stage of the Docker build (no longer using host NGINX)
  - Added nginx/nginx.conf & bind mount for favicon.ico (favicon still returning 404)
  - Cleaned up docker-compose.prod.yml: removed outdated substitutions (now using `env_file:`)
2. Database & Migrations
  - Dropped custom Dockerfile.postgres; switched to official postgres:17.4 image
  - Enabled Alembic auto-migrate under ProdConfig (CI integration planned)
3. CI/CD Pipeline
  - Updated deploy workflow to performs `git reset --hard` to resolve conflict issues
  - Wrapped url_for('style_reference') in APP_ENV check to avoid dev/prod mismatch
4. Misc Frontend & Theme Refinements
  - Tweaked black tones in theme definitions to be less harsh
  - Adjusted scripts: minified builds for prod, build:watch for dev (uses bundled assets in both cases)

## [23.08.25] - Milestone: First Major Refactor
*(Spanning work from ~15th-21st, finalized & rebased on the 23rd)

1. Architecture Overhaul
  - Introduced Repository Pattern with BaseRepository inheritance to centralize DB logic
  - Added Service Layer for clearer separation of business logic (AuthService, GroceriesService, etc.)
  - Standardized (mostly) DB session handling with @with_db_session decorator
  - Enhanced models with enums (UserRole, Priority, Status, Unit), improved relationships
2. Database & Infrastructure
  - Fixed SQLAlchemy identity map issues with expunge_all() for test isolation
  - Added timezone-aware datetime utilities (user context)
  - Added safe_delete helper to easily handle deletes vs soft-deletes
  - Moved core/database.py → _infra/database.py and core/db_base.py → _infra/db_base.py
3. Frontend Modernization
  - Began migration to esbuild for JS/CSS bundling
  - Converted frontend to ES6 modules with import/export + init guards
  - Dropped Tailwind in favor of design tokens via CSS custom properties and cascade layering
  - Fixed a few JS bugs (undefined elements, error handling)
4. File Structure Reorganization
  - Split much of core/ into domain-focused modules/ (auth, api, etc.)
  - Moved base.html & _macros.html → app/_templates/, extracted partials (_navbar.html, _flash.html)
  - Renamed common/ & utils/ → shared/, _internal/ → devtools/
  - Cleaned up comments, sorted imports, updated .ini files, refined .gitignore


## [Sun 24.08.25] - Dev Environment & Global Tools (pipx)
1. Dependency Hygiene
  - Installed pipx & added to PATH (WSL)
    - pyenv selects Python version; pipx installs global tools in isolated envs
  - Began global installs via pipx: isort, pipdeptree, pyflakes (initial set)


## [Mon 25.08.25] - Build Scripts & Color Work
**Log**:
1. Build Tools: Updated scripts & moved to modern esbuild usage: separate “build” vs “watch”
2. Color Work: Began OKLCH migration; started converting palette & tweaking colors

## [Tues 26.08.25] – D3.js, Modal Refactor, Template/JS Cleanup
**Log:**
1. D3 Setup: added shared/charts.js
2. Modal System Refactor
  - Created modal macro in _partials/_modal.html using {% call %} / caller()
  - Standardized modal naming convention: {type}-entry-{context}-modal/btn
  - Built auto-detecting modal-manager.js with URL-based config
  - Removed conflicting modal handlers from index.js
3. Template Architecture
  - Moved nav_link macro into _navbar.html (co-located with navbar HTML)
  - Standardized modal structure across forms with parameterized macro + content blocks
  - Merged macros/misc.html into partials/_components.html
4. JS Module Organization
  - Centralized modal behavior in modal-manager.js
  - Added config object keyed by window.location.pathname
  - Documented modal system with inline notes / docstrings
5. Backend Integration Setup
  - Updated Flask route to return created entity data in response
  - Set up data flow for real-time table updates after form submission
  - Prepared for integrating toast notifications + table manipulation functions
6. Misc
  - Added per-route CSP policy for style-reference (allow inline styles only there)
  - Navbar: clicking “Vesper” now routes to home

## [Wed 27.08.25]
**Log:**
1. Bugfixing for habit completion checkbox logic
2. Add SIGTERM SIGNIT things for build.mjs so esbuild properly exits

## [Thurs 28.08.25] - ViewModels, Homepage Redesign, & Some Refactoring
**Log:**
1. ViewModel Architecture
  - Applied ViewModel / Presenter pattern across:
    - Tasks, Time Tracking, Habits, Metrics
  - Added build_columns() classmethod for table config
  - Separated presentation logic from business logic
  - Created TimestampedViewMixin for datetime formatting
2. Homepage Redesign
  - Restructured into "My Day" card layout
  - Removed Daily Intentions section -> replaced with "Today's Frog" task
  - Integrated modal forms into homepage sections
3. Modal System Overhaul
  - Converted modal system to macro + -modal auto-discovery
  - Centralized form submission + validation (required fields, etc.)
  - Cleaned up modal-manager logic to remove config overhead
4. Task Model Enhancements
  - Added is_frog boolean to Task (1 frog per day logic) & added get_today_frog() in repository layer
  - Task creation consists of: priority, due date, frog status
5. Time Tracking
  - Added ended_at to TimeEntry model
  - Improved input processing for time intervals
  - Refined repo & form logic for time start/end handling
6. Metrics & Habits
  - Removed now-deprecated DailyIntention model
  - Consolidated into new DailyEntry model
  - Updated habit tracking:
  - Timestamped completions, streak logic fixed
7. Frontend & JS Improvements
  - Modularized modal JS logic,
  - Improved error handling and inline editing
  - Enabled real-time updates via dynamic table rows (need to further flesh out)

## [Fri 29.08.25] - Confirmation Modal, JS Refactor, Toast Work
**Log:**
1. UI Feedback & Modals
  - Built initial confirmation modal
  - Started wiring up toast message logic
  - Created style-reference.js for shared style hooks (included in app bootstrap via app.js)
2. JS Refactoring
  - Reorganized shared/ -> split out services/ and ui/ subfolders
  - Moved fetchWeatherData() → services/weather-service.js
  - Cleaned up datetime.ts & reused formatTimeString() in updateClock()

## [Sat 30.08.25] - JS Refactor, Tabbed Modals
**Log:**
1. JS Cleanup
  - Split getWeatherInfo into:
  - Display-side function
  - fetchWeatherData() (fetch + parsing from backend)
  - Added tabbed modal logic in modal-manager (special case):
  - Checks for .tabbed-modal on `<dialog>` OR .tabs anywhere on page
2. Macro Work
  - Added metric entry modal to homepage
  - Used composition to create time_entry_modal + metric_entry_modal from base form-modal macro
  - Centralized definitions into _components.html
  - Replaced metric entry buttons and time entry buttons to use these shared macros

## [Fri 31.08.25] - Canvas Rendering, LeetCode Tracker
**Log:**
1. Canvas Work
  - Created canvas.js (with setupCanvas() to sync internal resolution to display resolution)
  - Added debounced resize event listener to trigger redrawCanvas()
  - Began learning JS classes: folded drawCelestialBody into new CelestialRenderer class
2. LeetCode Tracking
  - Added LeetCode span + editable-cell (needs renaming) for quick additions
    - NOTE: Not yet functional, still working through positioning/overall flow ideas
  - Created LeetCodeRecord model
  - Wired up modal + button on homepage, POST route, repo (create+read), & integrated route


## [Mon 01.09.25] – Entry Point Split, Toast Migration, Error Handling, Table/Styling Work
**Log**:
1. Structure Changes
  - Made app.js solely the esbuild entrypoint
  - Created main.js as the app bootstrapper (imports, grab toasts, etc.)
2. Toast Migration
  - Removed all flash() usage → replaced with set_toast
  - Added set_toast helper in shared/middleware.py (placement TBD) to reduce route boilerplate
3. Error Handling Improvements
  - Implemented first draft of 500.html error page
  - Added Exception errorhandler: logs error, returns 500.html
  - Applied cleanup in:
  - Groceries → products(), transactions() (incl. service.py tweaks), dashboard()
  - Auth → register() (decided not to preserve form data for login/register)
4. Tables, Toast Styling, Mobile Nav
  - Added BasePresenter in view_mixins.py; centralized build_columns() there
  - Updated COLUMN_LABELS → COLUMN_CONFIG (structured dict)
  - Extracted table markup into a macro (major line reduction; easier to extend with D3)
  - Started mobile nav styling: created mobilenavlink, added “swoosh down” behavior