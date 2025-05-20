## Used to track daily/per-session progress

## Mittwoch 26.02.25
1) Installed RaspberryPi OS on Raspberry Pi 4 Model B
2) Installed node.js & got MagicMirror software running
3) Set up remote control to use web app to tweak MagicMirror layout/config using MMM-Remote-Control, installed dependencies using npm install within ~/modules/MMM-Remote-Control
4) Whitelisted all local IPs to enable access from laptop/etc on same local network

To use MMM-Remote-Control:
1) Start with npm run start on Pi (or npm run server to access through browsers alone)
2) On other computer on same network, go to http://<Rasp Pi's IP address>:8080/remote.html


Commands:
To run (cd MagicMirror):
- npm run start
- npm run start:dev (to start with Dev Tools enabled)
ALT+F4 to escape fullscreen?
ALT to access toolbar menu when in mirror mode
CTRL+SHIFT+I to toggle (web) developer tools from mirror mode

To exit:
CTRL+ALT+T to open new terminal
```killall node```

## [Sonntag 02.03.25] Pomodoro Timer Prototype

Goal(s): Build a Pomodoro timer that:
1. Runs locally on desktop (first test version)
2. Has a start, stop, & reset function
3. Tracks work vs break sessions
4. Later, can be ported to Magic Mirror on Raspberry Pi

What I did this session:
- Added SSH key for new PC && cloned Vesper repo to Desktop/Projects
- Installed Python 3.13 to C:\Program Files\Python313
- Added basic file structure & files
- Implemented basic pomodoro prototype with pomodoro.py as logic for timer and cli.py for start/stop/print/etc for now
-     As part of above, added basic multithreading for timer logic

What to do next time!:
1. Fix user input to enable typing "stop" during the countdown to stop

## [Friday 07.03.25] 

What I did this session:
- Made desktop shortcut on Pi to initiate MagicMirror
- Added hotkey (CTRL+Q) using xbindkeys to killall node to exit MagicMirror
-     Added line to bottom of ~/.xbindkeysrc
- Made a scripts folder on Pi 4B
-     Then used crontab -e (Nano as editor) to add this to start xbindkeys on startup: @reboot /home/pi/scripts/start_xbindkeys.sh

## [Saturday 08.03.25]

What I did this session:
- Installed OpenVoice to user/tools dir, made venv myvenv and installed requirements.txt -> Uses Python 3.10 (Users/Name/Python310)
-    Installed MeloTTS (multi-lang lib?), unidic

## [Tuesday 18.03.25] Start at 15:00
Goal: Get barcode scanner functionality up and running, at least in CLI for now, to scan groceries & add/update to DB

Log:
- Installed Flask, requests (for API calls) in venv, SQLAlchemy (for easier potential migration to PostreSQL later)

## [Thursday 20.03.25]
Goal: Basic Flask web app UI to function as "homepage" (equivalent to Magic Mirror) and display current time

Log:
- Basic Flask web app in app.py, made index.html template and got it to display static date & time

## [Saturday 22.03.25] Start 20:20
Goal: Add grocery.html template where I can add a new product to database

Log:
- Added templates for grocery.html (to list grocery database?) & add_product.html (as form to add product to grocery db) <- UNFINISHED
- Quick side quest: Need to change to one unified database under core/database.py rather than segregated databases
- Implemented super basic barcode scanning input that prints to terminal to confirm. Can't really run as a background daemon on Windows, but will use evdev on Linux to grab input directly and specifically from the barcode scanner, so this won't be an issue there.

Tomorrow: Write function to add product to grocery database from barcode
Stretch goal: Make Vesper recognize repeat scans and increase a product's quantity accordingly instead of duplicating it

## [Monday 24.03.25] Start 22:35
Goal (from yesterday): Write function to add product to grocery database from barcode. Stretch goal: Make Vesper recognize repeat scans and increase a product's quantity accordingly instead of duplicating it

Log:
- Switched to ORM style for database / queries / etc
- Made model for Product using ORM Base class (will flesh out as we go)
- Did not reach stretch goal (big sad)

Next time:
1. Previous stretch goal: Tweak add_product logic to recognize repeat scans and increase product's quantity accordingly instead of duplicating it
2. Fix grocery.html template such that table headers for columns are dynamically made

## [Tuesday 25.03.25] Start 18:30

Goals:
1. Tweak add_product logic to recognize repeat scans and increase product's quantity accordingly instead of duplicating it
2. Fix grocery.html template such that table headers for columns are dynamically made

Log:
- Forgot to log, but above goals were done

## Wednesday [26.03.25] Start 22:00?

Log:
- Got Remote Development extension on VSCode to test on Raspberry Pi via SSH

Next Time:
1. Implement add_product route: Accept a scanned barcode, enter rest of info, then add it to the DB and show it in the UI
2. Set up Flask-Migrate: Initialize migrations, create & apply first schema version, and confirm it works with Product model

## Friday [28.03.25] Start 21:00
Log:
- Made Product model to act as permanent record tying barcodes to products, Transaction model will store data for individual scans
- Fixed barcode being used as primary key
Next Time:
1. When barcode is scanned, check if it exists in Product table. If not, prompt for product name and price. Then add it to Product and add a matching Transaction. If yes, just add a Transaction. Need to sort out add_product and add_transaction functions

## Saturday [29.03.25] Start 11:25
Goal: Sort out logic for add_product and add_transaction

Log:
- Updated logic for add_product and add_transaction, messy so need to add tests
- Installed pytest & pytest-mock
Tests to add:
- Validation for db entries (prices are actually prices, etc)
      Also make said fields in add_product and add_transaction forms mandatory

## Sunday [30.03.25] 11:55-15:00
Goal: Begin implementing tests with pytest/pytest-mock
Log:
- Cleaned up DB functions in models.py to compartmentalize function jobs
- Renamed handle_barcode to process_scanned_barcode and retooled to add transaction upon scan. Need to figure out way to enable it to pull up add_product page if product doesn't exist.
- Starting with unit tests:
	- conftest.py: Sets up in-memory db via fixtures
	- test_models.py: Made 1 test for add_product
Next Time:
- Add WebSocket support to enable real-time redirect to /add_product when a scanned barcode doesn't exist.

## Tuesday [01.04.25] Start 14:10
Goal(s): Add "daily tether(s)" into dashboard page
  Reqs:
    - Use Flexbox
    - Make a card that is centered, add hover effects, add state for editing, style it clean
  Later:
    - Add padding, spacing
Log:
- Altered index.html to have a div for tether-card, started styling

## Wednesday [02.04.25] 11:56 - 14:00, 17:00 - 18:00 ish
Goal(s): Finish adding JS function for tether-card input
  Reqs:
    - Make a card that's centered, add hover effects, add state for editing, style it clean
    - Add padding, spacing
Log:
- Block 1: Add JS to handle tether-card input
- Block 2: Add JS function to hide button/input field once tether text is added
- Got sidetracked adding a couple unit tests for functions, should flesh that out after finish above goals regarding styling for JS stuff from today

 Next Steps:
 - Finish JS styling from today
 - Unit tests for each function in groceries/repository.py
 - Add DB model so tether-card information can be stored somehow if desired?
 - Add WebSocket support to enable real-time redirect to /add_product when a scanned barcode doesn't exist

## Friday [04.04.25] 17:35 - 19:12
Goal(s): Expand unit testing coverage, starting with db logic functions in groceries/repository.py

Log:
- Add input validation to add_product function
- Add test functions for add_product which test for happy path, missing data, & invalid range for price
- Add test functions for get_all_products which test for no entries & with entries
- Add test functions for get_all_transactions which test for no entries, an entry for a pre-existing transaction, & to ensure joinedload works (can still get_all_transactions after session close)

Next Time:
1. Expand tests to finish coverage for add_product/add_transaction, as well as cover process_scanned_barcode, ensure_product_exists.

## Wednesday [09.04.25]
Goals: Add tasks module & template
Log:
- Migrate to Blueprint architecture for routes (main, grocery, & tasks, auth to be added)
- Restructure app/
- Add pytest config

## Thursday [10.04.25] 
Session 1: 13:27 - 15ish?
Goals: Flesh out tasks.html, implement 3 basic recurring habits (Stretch goal: Habit streak/streak UI)
Log:
- Add add_task template
- Add modules/tasks/repository.py for db logic for tasks module
- Use GET/POST in tasks_routes.py to handle form data & display table of tasks in tasks.html

Session 2: 19:00ish - 21:55
Log:
- Render “Today’s Habits” list on dashboard (Currently just Tasks filtered by habit type and is_anchor bool
- Add checkbox to dashboard display to enable marking as complete
    - Learned fetch() to enable JS to POST to db immediately when checkbox is clicked. Checkbox has onclick event
    - Loose ends:
	- This feature DOES NOT WORK YET
	- Need to finish complete_task function in tasks_routes.py to grab corresponding task, get data from fetch             request, then change task's is_done to True and add completed_at to be today's date
	- JS function only marks complete when checked, but unchecking does not "un-complete" the habit
	- Sanitize completed_at to be a date
Next for this feature:
- Mark habit complete → update timestamp
- Auto-reset daily (cronjob or first-run check)

## Friday [11.04.25]
Session 1: 14:40 - 22:02
Log:
- complete_task grabs corresponding task, updates is_done to True & adds completed_at as today's date, returns success to JS function via jsonify
- Retool create_app to take parameters (testing vs dev, etc)
	Add config.py (DevConfig, TestConfig extending from BaseConfig)
- Install Docker for Postgres to replace SQLite
- Created both vesper & vesper_test DBs in docker Postgres container and tweaked Vesper config file to point to them correctly too
- Install Postgres driver (psycopg2-binary) in venv & added to requirements.txt
- All tests now run against PostgreSQL test DB for accurate datetime + schema validation

## Saturday [12.04.25]
Session 1: 16:58 - 23:15
Log:
- Move entirely to PostgreSQL, installed pytest-postgresql for testing (added to requirements.txt)
- Uninstalled psycopg2-binary and installed psycopg[binary] (backend something?)
- Installed Postgres locally for pytest-postgresql (local for tests, then Docker postgres container for dev/regular db)
- Ditched pytest-postgresl! Seems broken & non-maintained. Will hook tests directly into container connections
- Now stuck trying to get pytest to be able to authenticate to connect
	- It insists the password authentication is failing but it literally cannot be the password being wrong
		- Not sure what it could be, tried changing the pg_hba.conf file to allow local connections to authenticate using password (md5) but no luck

## Sunday [13.04.25]
Session 1: 14:00 - 00:41
Log:
- Set up PostgreSQL via Docker using docker-compose.yml and init.sql; integrated with Flask app.
- Verified DB integration with connection, table, rollback, and constraint tests.
- Structured tests into unit/ and integration/; configured pytest.ini accordingly.
- Wrote first integration test covering full task creation + completion flow.
- Merged GET/POST logic into single /add_transaction route for groceries.
- Refactored DB handling to use scoped_session with automatic teardown (no more manual .close()).
- Monkeypatched get_db_session() in tests to unify app/test sessions and avoid DetachedInstanceError.
- Replaced unnecessary .commit()s in tests with .flush() for cleaner, isolated state.
- Achieved full test pass rate post-refactor, including all edge cases.
- Hit 100% test coverage (or near enough); enforced clean, idiomatic test structure.
- Used test failures to uncover and fix real bugs via test-first iteration.
- Removed dead comments, renamed helpers clearly, and standardized naming across all modules.

TODOs:
- Add toggle logic to tasks checkbox to mark complete/incomplete (/tasks/toggle/<id> maybe?).
- Design anchor habit model (e.g., is_anchor: bool) and write full repo/route/test flow.
- Keep test coverage at 100% (track coverage deltas after each commit)

## Tuesday [15.04.25]
Pre-Session:
Log:
- Created backup directory for PostgreSQL container DB backups under User.
- Centralized scripts by creating a Scripts folder under User, adding it to PATH (now "vesper-db-backup" can be run from anywhere in PowerShell to generate backups in Backups\Vesper).
-- TODO: Confirm the data folder in the backup properly stores the volume (still figuring out how to check this).
  
Session 1: 14:32 - 22:18
Log:
- Implemented CRUD for task routes (barring DELETE). Merged the complete_task route into the PATCH section of the new update_task route
- Added tasks/dashboard.js, enabling user to click on a table cell & directly edit the content. Changes are sent to the backend via JS fetch() PATCH requests to update the database.
- Started generalizing the editTableField JavaScript function to make it reusable across any table in Vesper
- Initialized npm and set up Jest for JavaScript testing. Chose the node environment, selected v8 as the coverage provider, disabled coverage reports for now, and enabled automatic clearing of mock calls, instances, contexts, and results before each test.
- Installed the jsdom environment using: npm install --save-dev jest-environment-jsdom
- Confirmed that tests can be run via npm test from the project root. Also tested npx jest --watch, which reruns tests on every file save and performs efficiently

NOTE:
- Adding JS testing: Jest for unit testing, then Cypress for end-to-end to simulate user interactions?
- Generalize CRUD stuff to something like crud_routes.py eventually?

## Wednesday [16.04.25]
Log:
- Adding DELETE route for tasks, JS to dynamically display delete button on row hover
- Switch off Bootstrap to Tailwind for styling
	- npm install -D tailwindcss postcss autoprefixer
	- npx tailwindcss init -p
- Re-created navbar styling (mostly) with Tailwind

## Friday [02.05.25]
Session 1: 17:00 - 20:55
Log:
- Refactor/rename "Tether" to "Critical Task"
- Discovered I just need to manually restart Flask server whenever Tailwind styles are updated in order to see them. so..yay!
- Fixed launch.json to point to the right place so we can use F5 to Run Debug mode and also use breakpoints to better debug
- Implement Delete on row hover functionality for Tasks table

Remaining Stuff before hosting:
- Make "hover over table row to delete item" on Tasks dashboard fuctional & stylize it so it's visually clearer
- Ensure checking off anchor habits actually works
- Input validation & warnings for the "add_X" templates! (Currently: task, product, transaction)
- Add placeholders to forms (Remember: Need one for English and one for German for lang toggle)
- Copy lang toggle into Vesper from Resume Site
- Get "editTableField" function to work for / apply to all fields in Tasks dashboard (except ID obv)

Next Time:
1. Tweak groceries dashboard table to accommodate the "delete option on row hover" function there

## Saturday [03.05.25] Session 1: 12:00 - 20:55
Log:
- Add conditional product creation flow to add_transaction route
- Normalize & parse form data, allow re-submission of add_transaction form with net_weight if product not found
- Cleanly split product & transaction data
- Gracefully handle 'price' fallback in product creation (temp hack - price for Product model will later be removed)
- Use show_product_fields flag to dynamically reveal needed inputs
- Centralize deleteTableItem JS function inside js/utils.js
- Enable marking anchor habit complete via dashboard checkbox, also appears checked on refresh/reload!
- Make endpoints RESTful & adjust tests accordingly
- Add style sets in base.html for tables, unify styling (also polish date completed display for task table)
- Add flash() for add_task, add_product, & add_transaction

## Sunday [04.05.25]
Log:
- Begin styling home dashboard cards
- Fix pain point: Tailwind changes didn't trigger Flask reload even with --debug
- SOLUTION: Set up 3-process workflow with hot reload
	1. Run Tailwind in watch mode: npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch  
	2. Run Flask in debug mode (separate terminal) flask run --debug
	3. Add BrowserSync
		1. Installed locally with: npm install browser-sync --save-dev
		2. Run BrowserSync with: browser-sync start --proxy "localhost:5000" --files "app/**/templates/**/*.html" "static/css/*.css"
  - Explanation:
     - Flask handles backend + Jinja templates
     - Tailwind watch updates output.css on save
     - BrowserSync reloads browser on HTML or CSS file changes
     - New Vesper dev workflow would be:
	1. npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch
        2. flask run --debug (separate terminal)
	3. npx browser-sync start --proxy "localhost:5000" --files "app/**/templates/**/*.html" "static/css/*.css"
	- BUT, we combined everything into a single command using npm scripts:
		1. Installed concurrently: npm install --save-dev concurrently
		2. Added to package.json:
		"scripts": {
			"tailwind": "npx tailwindcss -i ./app/static/css/style.css -o ./app/static/css/output.css --watch",
			"flask": "flask run --debug",
			"sync": "browser-sync start --proxy localhost:5000 --files 'app/**/templates/**/*.html' 'static/css/*.css'",
			"dev": "concurrently \"npm:tailwind\" \"npm:flask\" \"npm:sync\""
		}
		3. Final dev command after activating venv:
			1. .venv\Scripts\activate
			2. npm run dev
			3. Enjoy!

## Monday [05.05.25]
Log:
- Table styling overhaul
- Removed .card & table-wrapper remnants
	- Converted layout + visuals to Tailwind
	- Centralized table style sets in base.html
		- Distinct header style for clarity
		- Alternating row stripes + hover effect (colors still need refinement)
		- Red delete button
		- Standardized spacing across tables
		- Wrapped tables in card-style divs to match home dashboard layout
- Model fix
	- Made Transaction.date_scanned timezone-aware (UTC)
- Polish table & heading/caption styling, added svg for delete button icon instead of text
- Learned how to clean up CSS with Tailwind purge
	1. Got cross-env for a build script with: npm install --save-dev cross-env
	2. Added in package.json (under scripts):
		- "build": "cross-env NODE_ENV=production tailwindcss -i .app/static/css/input.css -o .app/static/css/output.css --minify"
	3. Now we can run: ```npm run build```

## Tuesday [06.05.25]
Git goal: Practice branching & merging
Log:
- Switched to dev/today
- Remove price tag from Add Product template

## Sunday [11.05.25]
Goal:
1. Seed dummy data automatically in dev mode after app startup
Log:
- - Cleaned up config.py with proper ENV usage (built-in Flask flags for environments)
- Add seed_db.py (invoked at app creation) to seed database with dummy info
- Add reset_db route and function to clear the DB, then run seed_db.py on it (nice for demo/dev purposes)
	Flow: Button -> reset_db route -> handles logic/seed_db invocation -> return to page we were on

## Tuesday [13.05.25]
Goal:
1. Add "Reset" button for dummy db data (drops tables then runs seed_data again)
Log:
- Flesh out reset_db()
- Determined some sort of deadlock is occurring in postgres when we press the Reset DB button.

## Wednesday [14.05.25]
Log:
- Created my own dockerfile (Dockerfile.postgres) so we can include a nano installation!
- Modified package.json to expand scripts option to make 'npm run debug' to allow for debugging with breakpoints
- Smash bug involving "idle in transaction" connections causing database deadlock

Next Up:
1. Make reset_db redirect to same page (involves "referrer check")

## Sunday [18.05.25]
Log:
- Install python-dotenv, create .env
	Obfuscates real info behind a layer between me as a dev and the stuff the repo sees
	- To implement this change, we:
		- Added our Flask container stuff to a new docker-compose.prod.yml
		- Tweaked that, config.py to use variables, NOT the real values
		- Env vars are loaded from .env -> Config.py reads those vars -> Flask app get configured properly -> DB connects using the configured URI
- Installed gunicorn locally to test docker-compose.prod.yml
	- Instead of using flask run, we use gunicorn [options] module:app (module in this case is our app.py)
		- So in our case: gunicorn --bind 0.0.0.0:5000 app:app (so then the first 'app' here is referring to app.py)

