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

## [Sat 13.09.25]
**Log:**
1. Navbar adjustments
	- Fix: Gated profile settings behind login
	- Adjusted navbar -> hamburger breakpoint to 768px
2. Dashboard Visuals
	- Bolded Today’s Frog & LeetCode text for emphasis (WIP)
	- Lined up tasks list styling to that of habits checklist (Need to apply AJAX completion, too)
	- Moved "Add Habit" button into title row, intersecting border (did the same with 'Add Task' for 'My Day' section)
	- Unified card header pattern -> `[Title] (+)` now consistent/applied across all cards and dashboards
		- Added new `.btn-icon` styling to pair with `plus_svg()` for denser UI
3. Macro Cleanup (WIP)
	- Renamed _components.html -> _ui.html
	- Moved all form modal markup into new _forms.html (imports _ui.html)

## [Wed 10.09.25]
**Log:**
0. Added last few days to project log
1. Quick UI Fixes
	- delete_btn: Fixed SVG icon display issues (sizing/visibility)
	- Legends: Added basic styling for presentable appearance
	- Changed product table barcode column to essential in groceries viewmodels.py
2. Form Improvements
	- Add Transaction form: Quantity -> type="number" with step + min attributes
	- Add Transaction & Add Product forms:
		- Net weight -> type="number" with step + min
		- Cals per 100g -> type="number" with step + min
3. Table Functionality
	- Added "No items yet" text when removing the last row of a table via JS
	- Table references: Added id="{{subtype}}-table" attribute to responsive_table marco for consistent, maintainable references
	- Subtype standardization: Updated tasks & habits to use consistent subtypes (task, habit instead of "none")

## [Tues 09.09.25]
**Log:**
1. Groceries Module
	- Scrap "next_item" flow for add_X pages, not worth the headache right now
	- Add basic placeholder text for "no items in shopping list" on card

## [Mon 08.09.25]
**Log:**
1. Shopping List feature:
	- Add qty to model + add basic "increment if exists" logic to repo function
	- Start on inline x/-/+ controls for shopping list items list
		- Use SVGs for plus/minus (added to macros)
		- Drafting styling for item-controls (outer span for above elements)
		- Hover states to show/hide controls
		- Add increment/decrement/delete logic
			- Button disabled states during API calls to prevent double-clicks
2. Added api.js to clean up that disgusting fetch boilerplate all over & centralize response formats
	- Switched almost all fetch() requests to using new apiRequest helper
		- Eliminated entire submitModalForm function :D
	- Made apiRequest able to handle both FormData & JSON bodies
	- Left userStore & weather service with manual fetch due to different state mgmt needs

## [Sun 07.09.25]
**Log:**
1. Shopping List feature: Started small but extensible:
	1. Added ShoppingList model
	2. Added context menu option "Add to ShoppingList" for Transaction table by conjoining base options (Delete, Close, etc) for options to transaction-specific options
	3. Dead simple list UI in its own card for now simply displaying our current list
2. Navbar: Reorganizing & trimming
	- Scrap "Home" navlink entirely (clicking branding already now takes us home)
	Settings modal:
	- Move "Log out" into the settings cog options (this will inevitably become a sidebar in the future, but in the interim, this'll work)
	- Replaced settings cog with profile SVG
	- Use proper form for both Log out & Reset Dev buttons
3. Misc:
	- Tweaked modal-manager submit listener to return early if any form has a "data-noajax" attribute, for modals with forms that shouldn't be treated the same (ie, our log out button)
	- Add guards to forms.js
	- Removed debug borders from app.css/components.css

## [Fri 05.09.25]
**Log:**
1. Divied up PROJECT_LOG into archival files, separated by year/month

## [Thurs 04.09.25]
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


## [Wed 03.09.25]
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