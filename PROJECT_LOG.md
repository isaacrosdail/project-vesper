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



## [Wed 1.10.25] - Validator Refactor
**Log:**
1. Validators key notes
    - Validators own type conversion - Receive strings, return typed values
    - Optional vs Required - Denoted via tuple returns
    - Clean typed_data - Omits invalid/empty keys entirely
    - Expanded & aligned tests to match
    - Overall pattern is:
        - Route: pulls raw form_data, gets parsed_data via parsers, gets typed_data validators
        - Service: assumes input is valid & typed, applies business logic/validation (if any), persists data, & returns plain dict responses.
2. Bug fix:
    - `validate_numeric` - Now correctly enforces (precision - scale) digits before decimal

## [Tues 30.09.25]
**Log:**
0. Install time-machine to start testing datetime-related functions
1. Testing datetimes
	- view_mixins: Test for due_date_label
	- Generally start testing other datetime helpers
2. Datetime helpers changes/improvements
	- Make `now_in_timezone()` to clean up `convert_to_timezone` (had two different jobs - bad)
	- Simplify: 
        - scrap start_of_day_utc, add_mins_to_datetime
        - inlined logic for day_range & made today_range ref day_range, then renamed the latter two to "xx_utc" for clarity

## [Mon 29.09.25]
**Log:**
0. Uppercase unit_enum values (tweak models.py, revision with manual op.executes since Postgres is touchy about this). Updated viewmodel to include .lower()
1. Smoke testing forms

## [Sun 28.09.25]
**Log:**
0. Dissolve `core/` -> Move templates to _templates, healthcheck to app/routes.py
1. Smoke Testing Forms: tasks (frog + normal), habits (promotion-based + normal)
2. Tweaking
	- Habits: Make status nullable & add as an option toggle on form. Users can opt-in to promotion-based mechanic. Also removed the promotion-threshold field: Letting the user dictate target days + threshold would let them game the system, which defeats the purpose. Habit-building SHOULD have friction, so we'll handle the math/targets/etc behind the scenes, based on actual behavioral psychology notes.
	- Updated enum/string parsing logic
		- Switched from form_data.get("field", "") to the safer (form_data.get("field") or "") idiom.
			- Reason: dict.get(key, default) only uses the default if the key is missing, not if the value is None. Without this, None.upper() could occur.
			- Added _upper_or_none helper for enum fields so parsers now return either an uppercased string or None. This shifts all “required vs. optional” decisions to the validators.
	- Validation changes
		- Made validate_status optional-aware: if status is None, skip enum validation entirely.
		- Added cross-field invariant: status and promotion_threshold must both be set, or both be None.
	- Tweaked due_date viewmodel property for due_date_label with some "fancier" logic for displaying due dates

## [Sat 27.09.25]
**Log:**
1. Repository Layer Improvements
	- Expanded BaseRepository class with automatic user scoping across all modules
		- Created _user_query() helper to eliminate repetitive user_id scoping with .filter()
		- Added base CRUD operations to BaseRepository
	- Refactored Habits, Tasks, Metrics, Time Tracking, Groceries to use more consistent patterns
	- Cleaned up typecasting => Moved to services/routes instead
2. Service Layer work
	- Moved business logic out of repositories to service layer (shoppinglist operations, transaction upserts)
		- Generally enforced separation: repos stay pure, services handle orchestration
	- Introduced shared/parsers.py to clean raw form_data, update validators to assume clean inputs
	- Trying out casting in Service layer, unsure about it

## [Fri 26.09.25] - Validation Cleanup/Standardization
**Log:**
0. Explored Hypothesis (property-based testing); tweaked parse_decimal to handle Inf, added `.coveragerc` to exclude certain paths from pytext-cov
1. Models refactoring:
  - Extracted Tag model + association tables to shared/models.py
  - Applied constants.py across models, validators, DB constraints
  - Added CheckConstraints + table_args for business rules
  - Habits: added `__repr__` to HabitCompletion & LeetCodeRecord
2. Validation standardization:
  - Completed: auth, groceries, metrics modules
  - Centralized constants usage in validators & models
  - Updated return type hints (`dict[str, list[str]]`)
  - Formatting pass on all models.py files

## [Thurs 25.09.25] - Validation & API Response Standardization
**Log:**
1. Infrastructure Changes
    - Updated `check_numeric()` to return `(is_valid, error_type)` tuples & added minimum/strict_min params
2. API response standardization
    - Introduced api/responses.py with:
        - `api_response(success, message, data=None)`
        - `validation_failed(errors)`
    - Replaced manual `jsonify({...})` responses across routes with these helpers
    - API routes now return payloads under a uniform `data` key instead of ad-hoc structures
    - Errors are now returned in a consistent format instead of arbitrary inline messages
3. Validation Work (cont.)
    - Moved from `validate_{model}` functions toward field-specific validators (eg `validate_username`, `validate_price`)
    - 'Coordinator' validators now return `dict[str, list[str]]` keyed by field instead of dumping all errors in one list, to make it easier to consume by frontend/UI
    - Removed hardcoded strings & magic numbers; now pulled from `constants.py` & enums
    - Updated some / added new parametrized tests to align with changes from today as well
4. Routes standardization
    - Converted all success/error responses to use `api_response()`/`validation_failed()`
    - Structured data responses more consistently under `data`

## [Wed 24.09.25] - Models & Validation
**Log:**
0. Rebased to squash/edit quite a few commits
1. Model standardization & Enum overhaul
	- Went through `models.py` systematically
	- Introduced proper enums (*Enum suffix, name="my_enum" property)
	- Unified `UserRoleEnum`, `UserLangEnum`, `PriorityEnum`, `StatusEnum`, `DifficultyEnum`, etc. (all refs & imports should now be up-to-date)
		- Added `ProductCategoryEnum` with categories meaningful for analytics (vegetables, legumes, processed_convenience, etc.)
	- Standardized field definitions: consistent string lengths, numeric precision, constraints.
	- Added database constraints (eg, CheckConstraint on promotion_threshold)

2. Validation Infrastructure
	- Created module-level constants.py for: auth, groceries, habits
	- Updated `validators.py` in each to pull error messages + field rules from these constants
	- Added shared/validators.py with `check_numeric()` helper for `Decimal` validation
	- Extended model constraints (numeric limits, better defaults)
	- Validations & tests now share a central definition of rules


## [Tues 23.09.25] - Style Reference Page Refinement/Overhaul
**Log:**
1. Continued organization/trimming of style-reference Page
	- Made notes on catalog of components to avoid missing anything
	- Refactored CSS: tidier with `-section` & `-subsection` classes for grids
	- Flattened markup & stripped inline styles
	- Organized into logical sections with clearer hierarchy
		- Separated "visual reference" from "iteractive demos"
	- Use stepped gradients for bg/accent tiles
	- Added btn-icons page-specific styling using `data-page` attribute on `<html>`
X. Misc
	- Added docstrings for: `makeToast`, `initPasswordToggles`


## [Mon 22.09.25] - Validators & Service/Route Integration
**Log:**
1. Validators (all modules)
	- Installed regex module for Unicode pattern matching for User stuff
	- Centralized error strings in validators.py for each module, then import in tests
	- Set up a bunch of initial parametrized tests / test cases
2. Started integrating `validators.py` changes into routes/service layers
	- Made service.py for time_tracking (timeentries), mirroring `GroceriesService`
	- Updated `AuthService` constructor to take repository; adjusted methods to match current patterns
3. Login/Register form pages
	- Draft "click eye icon to toggle password visibility" effect with basic JS hookup
4. Style reference:
	- Reorganized into two main sections: Swatches/tokens & Components
X. Misc:
	- Added registry mapping in main.js so page-specific JS is executed based on our new data-page attribute in the html tag itself
	- Added dev CSP rules so we can win back our style-reference page


## [Sun 21.09.25] - Validators & CSS Experimenting
**Log:**
1. CSS: practice with `::before`/`::after` & transitions
	- Replace bg-color nav-link effect with expanding underline using `::before`/`::after`
2. Added basic validation + test cases to get us mostly functional
	- Made up-to-date validators.py for all modules (excl. api/)
	- Made some parametrized tests to cover our basics
	- Integrated validators into routes/services (mostly, needs more testing)
	- Also: refactored parse_and_validate_form_data to use our validators (needs more work)
X. Misc:
	- Added `habit_tags` & `task_tags` to NEVER_DELETE list (assoc. tables use composite keys & no *_id_seq)

## [Sat 20.09.25] - Tabbed Modal, Homepage Redesign Work, & Navigation
**Log:**
1. Tabbed modal
	- Added SVG icons to each tab
	- Dialed in more on pill-shaped design for tab buttons
2. Homepage
	- Folded time/metric/leetcode entry buttons into custom dropdown
	- "Animated" chevron SVG with rotate
3. Drafted hamburger menu -> X transition effect too
	- Learned `transform-box: fill-box;`, `transform-origin`, & stacking rotate+scaleX in one transform
	- Also split SVG into 3 separate lines so we could manipulate independently
X. Misc:
	- Cleaned up SVGs/usage & added proper attributions

## [Fri 19.09.25] - Task Completion & Metric Modal
**Log:**
1. Implemented `markTaskComplete` for tasks list on homepage as well
2. Tabbed modal (metric_entry) work:
	- Adjusted metrics route to handle multiple metrics & ignore empty-valued entries (ie, populated only)
	- Revise classes: tab-group for container, tab for each button/tab
	- Adjust styling to follow a ??	
3. Attempting moon/sleep SVG

## [Thurs 18.09.25] - Shopping List & Navbar Improvements
**Log:**
1. ShoppingList feature
	- Added "Add to shopping list" from Product table menu
	- Fixed bug where AJAX gave new shopping list item entry the product ID instead of the shoppinglistitem ID from backend
	- Fixed duplicate detection logic => now properly checks for existing products before adding to list
	- Implemented realtime quantity updates when adding existing items
2. Navbar improvements
	- Implemented click-away closing for mobile nav
	- Cleaned up navbar.js (better parameters, removed duplicates)
	- Refactored naming conventions across navbar system (nav-desktop, nav-mobile, nav-mobile-container)
X. Misc:
	- Fixed bug preventing add_transaction form fields from being hidden

## [Wed 17.09.25] Dark Mode & Color System Tuning
**Log:**
1. CSS: Completed dark mode color tuning & OKLCH conversion
	- Converted all remaining HSL/hex colors to OKLCH for consistency
	- Added hover states: Created --bg-hover token for secondary button hover (neutral counterpart to accent hover)
	- Introduced tertiary color: Added amber/orange selection colors as third color family (will support future data visualization)
	- Replaced global color-error & color-success tokens with theme-specific ones for better control -> *-clr-success & *-clr-error
	- Made --text-destructive reference --clr-error to reduce duplication while maintaining semantic naming
	- Some organization stuff:
		- Moved ::selection styling from base.css to app.css
		- Renamed `--fade-in` to `--transition-fade`

## [Tues 16.09.25]
**Log:**
1. Stepped down all neutrals in light mode facilitate stepping UP for hover/active states

## [Mon 15.09.25] - CSS Cleanup/Refactoring
**Log:**
1. CSS for buttons: Retooled to better accommodate text buttons vs icon (SVG) buttons
	- Separated base types: btn -> text-first buttons, btn-icon -> icon-only buttons
	- Split into composable modifiers for intent (Already had -> primary, secondary, destructive), form factor (btn-round, btn-square), & size (defaults are medium, modifier for btn-lg)
	- Centralized icon sizing: SVGs scale proportionately
	- Above changes include adding btn-size-* & icon-scale tokens as well
	- Add plus_btn macro for centralization
	- Accessibility & states:
		- Cursor, :focus-visible outlines, etc.
	- Now .delete-btn styling is decoupled from JS/behavior

## [Sun 14.09.25]
**Log:**
1. Quick fixes:
	- Apply type=number, step+min+max changes for cals per 100g to add_transaction form page
2. Standardize module/subtype naming conventions a bit, added new CONVENTIONS.md for documenting these centrally
3. CSS tidying
	- Move to components.css: dialog, modal-close, tooltip-popup, 
	- Declare text color in base.css (why didn't I start with this??), prune stupid excess declarations everywhere else
	- Tidied up base.css a bit - de-duped, reorganized

## [Sat 13.09.25]
**Log:**
1. Navbar adjustments
	- Fix: Gated profile settings behind login
	- Adjusted navbar -> hamburger breakpoint to 768px
2. Dashboard Visuals
	- Bolded Today’s Frog & LeetCode text for emphasis (WIP)
	- Lined up tasks list styling to that of habits checklist (Need to apply AJAX completion, too)
	- Moved "Add Habit" button into title row, intersecting border (did the same with 'Add Task' for 'My Day' section)
	- Unified card header pattern -> `[Title] (+)` now consistent/applied across all cards & dashboards
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
		- Rewrite filterUnitOptions to use a 2-stage dict lookup & single loop!
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