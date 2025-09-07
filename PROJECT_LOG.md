# Project Log

## Archive - Logs for Previous Months
- [2025-03](PROJECT_LOG_ARCHIVE/2025/03.md)
- [2025-04](PROJECT_LOG_ARCHIVE/2025/04.md)
- [2025-05](PROJECT_LOG_ARCHIVE/2025/05.md)
- [2025-06](PROJECT_LOG_ARCHIVE/2025/06.md)
- [2025-07](PROJECT_LOG_ARCHIVE/2025/07.md)
- [2025-08](PROJECT_LOG_ARCHIVE/2025/08.md)

**Pinned First Entry** (for perspective)
## [Wed 26.02.25] *(Old - obviously replaced by Flask app)*
**Log:**
- Installed Raspberry Pi OS (RPi 4 Model B), installed Node.js, & got MagicMirror running
- Installed MMM-Remote-Control via `npm install` in `~/modules/MMM-Remote-Control`
- Whitelisted all local IPs for access from laptop/etc


## [Fri 05.09.25] - Tying Up Loose Ends, Day 3
**Log:**
1. 

## [Thurs 04.09.25] - Tying Up Loose Ends, Day 2
**Log:**
1. JS
	- theme-manager.js: Refactored if/else chains to clean object lookups, now uses between() string helper
	- forms.js: Removed console logs, streamlined unit filtering logic
2. CSS
	- Added some design tokens: spacing, font-size-xl, & standard border
	- Add padding to cards for spacing away from edge
	- Refined navbar styling
3. Template cleanup
	- Moved dev settings cog modal outside main navbar structure
	- Removed commented out, leftover chart containers
	- Simplified grid layouts in greeting card a bit


## [Wed 03.09.25] - Tidying & Tying up loose ends
**Log:**
0. Extensions: Learn Vim & Vim
	- ESC => Normal mode (ie, Vim mode) // `i` => Insert mode (ie, what we're used to)
	- Settings:
		- vim.handleKeys so copy/paste are still "normal"
		- vim.startInInsertMode: true
1. Some Datetime helpers
	- Move resolve_start & resolve_end from time_tracking/service.py to datetime/helpers.py (& rename for clarity)
	- Extract 'due_date' datetime modulation logic from tasks/routes.py into helper (parse_eod_datetime_from_date)
	
2. Revamping database/operations.py
	- Rename to helpers.py
	- Extract delete table logic into _delete_rows() & add delete_user_data() intended as a user-facing "Delete all entries from X table?" thing
	- Build SQL in _delete_rows() using optional where & params clauses (parametrize for SQL injection safety)
	- Scrap hardcoded lists approach & use SQLAlchemy's sorted_tables, which respects FKeys
		- Needed to add NEVER_DELETE list as well for apicallrecord & alembic_version tables to be skipped/ignored
	- Align sequence resets with only the tables actually wiped
3. Improving some of our older JS
	-Fixing product-forms.js
		- Move to shared/forms.js & have guarded init there instead of groceries dashboard.js
		- Rewrite filterUnitOptions to use a 2-stage dict lookup and single loop!
	- Fixing theme-manager.js:
		- Apply similar refactor here: scrap if/else & instead 
4. JS strings practice
	- Made strings.ts to store helpers, started with a handful to drill basics
5. Misc:
	- Separated practice/stub sorting algos from codebase, moved to _playground/

## [Tues 02.09.25]
**Log:**
1. Finally integrated / sifted through our backlog of day logs!
2. Tackling loose ends
	- Merged exception handlers in errors.py
	- Deleted unused catch_errors decorator

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