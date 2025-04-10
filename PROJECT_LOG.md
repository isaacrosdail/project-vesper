## Use this file for tracking progress / steps / challenges per session/day worked

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
