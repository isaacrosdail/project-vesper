# Project Log

## Archive - Logs for Previous Months
- [2025-03](PROJECT_LOG_ARCHIVE/2025/03.md)
- [2025-04](PROJECT_LOG_ARCHIVE/2025/04.md)
- [2025-05](PROJECT_LOG_ARCHIVE/2025/05.md)
- [2025-06](PROJECT_LOG_ARCHIVE/2025/06.md)
- [2025-07](PROJECT_LOG_ARCHIVE/2025/07.md)
- [2025-08](PROJECT_LOG_ARCHIVE/2025/08.md)
- [2025-09](PROJECT_LOG_ARCHIVE/2025/09.md)

**Pinned First Entry** (for perspective)
## [Wed 26.02.25] *(Old - obviously replaced by Flask app)*
**Log:**
- Installed Raspberry Pi OS (RPi 4 Model B), installed Node.js, & got MagicMirror running
- Installed MMM-Remote-Control via `npm install` in `~/modules/MMM-Remote-Control`
- Whitelisted all local IPs for access from laptop/etc


## [Sun 2.11.25]
**Log:**
1. Drafting ABTesting functionality
	- Add ABTest, ABVariant models (to Metrics for now)
		- ABTest will serve as the test model itself, while ABVariant serves as the record for each individual trial
	- For each, add: form modal, POST route, parser
2. Added some basic logging

-----

## [Wed 29.10.25]
**Log:**
1. Fixed detached tooltip carrot: just made the tooltip-popup itself positioned centered to targetEl
2. Hooked up habits barchart to actual data, made backend route, tweaked repo funcs
	- TODO: Make it show ALL habits on chart even those for which there are no completions

## [Tues 28.10.25]
**Log:**
1. Metrics Chart
	- Add calories option to dropdown (7d), as well as a BMR line

## [Mon 27.10.25]
**Log:**
1. D3 Charting - add line chart to metrics
2. Metrics service - update/fix service stuff, include sleep duration & entry_datetime changes, also changed repo stuff a bit

## [Sun 26.10.25]
**Log:**
1. D3 Charting
	- Added pie chart w/ legend + dropdown draft for time_tracking dashboard
2. Metrics Model Changes
	- Adding entry_datetime since using created_at is sloppy now that we can choose/edit dates an entry "applies to" (ie, inputting my step count for Dec 12 on Dec 15 means created_at = Dec 15 -> NOT the date it applies to)
	- While I'm at it, also finally adding sleep_duration_minutes (int)
	- Also, since we'll often be querying daily_entries by user_id + entry_datetime, adding a composite Index for user_id + entry_datetime

## [Thurs 23.10.25]
**Goals:**
1. Improve time_tracking entry form/service to take dates+times
**Log:**
1. Improve time_tracking entry form/service to take dates+times
	1A. Added 'date' field to time_tracking form (id="entry_date")
	1B. Add current_date parameter to form macro, with routes for home & dashboard now passing that in based on user's timezone, as an ISO .date()
	1C. Add entry_date to time_entry_form_data parser, add validation using generic validate_date_iso() so it gets into typed_data dict as desired
	1D. Adjust service.py to use entry_date instead of 'today'
	1E. Adjust populateModalFields:
		1. If input.type is number, round if the field's 'step' value is 1/none, otherwise use Decimal format
		2. Special handling so entry_date field's date is extracted from started_at for edits

## [Sun 19.10.25]
**Log:**
1. Misc:
	- Tweaked canvas JS to include "margins" - feels more natural/sensible now that canvas is "baked into" greeting-card
	- Tweaked markup/css too to condense the greeting-card into one thing instead of two grid cells/columns

## [Sat 11.10.25]
**Log:**
1. Make similar Task progress bar for current day
2. Expand habit progress logic to per-habit as well

To do #2, we need to address an issue: generic PATCH doesn't know to run calculate_tasks_percentage.
To fix this we can use a post-PATCH hook that runs the calculate_tasks_percentage function intelligently

3. Consists of 3 overall pieces:
	1. Central registry & decorator in app/shared/hooks.py
		- Global dict PATCH_HOOKS = {} mapping subtype -> hook function
		- Simple decorator @register_patch_hook('tasks') that auto-registers functions into the dict
	2. Module Service - Actual hook logic
		@register_patch_hook('tasks')
		def tasks_patch_hook(item, data, session, current_user):
		...service to calculate_tasks_percentage...
		return {"progress": progress}
	3. Generic Patch Route - Dispatch to Hook if exists
		- In generic_routes.py, we modify the PATCH handler to have:
		hook = PATCH_HOOKS.get(subtype)
		if hook:
			extra_data = hook(item, data, session, current_user)
			response_data |= extra_data   # merge onto normal dict

## [Fri 10.10.25]
**Log:**
0. Add proper SVG icon for dots option button on side of tables
1. Habits Progress Bar Polish
    - Implemented animated progress bar using statis gradient (red->yellow->green) as the backdrop
    - Switched to a masking approach by applying `transform-origin: right` & animating `scaleX()` to reveal the gradient smoothly
    - JS updates percentage from backend routes
    - Handled initial page load by disabling transitions for first render, then re-enabling them

## [Thurs 9.10.25]
**Log:**
1. Refactoring context-menu.js
    1. Converted `MENU_CONFIG` from array of strings -> array of objects
        - eg, `['Edit', 'Delete']` -> `[{text: 'Edit', action: 'edit'}, ...]`
        - Supports separate display text & action identifiers
    2. Updated menu creation: to include data-action attributes
        - `.map()` now sets textContent + dataset.action from config
        - Replaces fragile text-matching with explicit data binding
    3. Replace conditionals action handler lookup pattern
        - Mapped action strings -> handler functions via `actionHandlers` object
        - Extracted logic into `handleEdit()`, `handleDelete()`, `handleAddToShoppingList()`
2. Submission/Validator fix (updated tests accordingly)
    - `typed_data` form fields weren't updating when optional fields were cleared (set to empty string / None)
    - Fix: Changed `elif typed_value is not None:` to `else:` in per-model validators  
        - Allows explicit `null` on submission (e.g. `"field": null`)  
    - Exception: `validate_daily_entry()` still omits blank fields (opt-in model, left unchanged for now)
3. Habits Progress Bar (initial draft)
    - Very rough but functional version, on homepage
    - Logic added to `habits_routes` (dict merging)
    - `index.js`: attached update call to each `markHabitComplete()` AJAX success callback


## [Tues 7.10.25]
**Log:**
1. `APISerializable` Implementation
Note: Services return raw models (e.g., `entry`), routes return serialized dicts (e.g., `entry.to_api_dict()`)
Added `.to_api_dict()` support via `APISerializable` for: Task, Habit, LeetCodeRecord, DailyEntry

2. Model Revisions
    - Table naming cleanup: Enabled automatic conversion to `snake_case` + pluralized table names
        - Example: `ShoppingList` → `shopping_lists`, `User` → `users`, etc.
    - Updated all foreign keys and relationships across models to match new table names
    - Verified alignment across all major layers (models, tables, API routes, frontend endpoints)

### Naming Schema
Everything now follows a unified convention:

| Model Class   | Table Name      | API Subtype     | ✅ All Match |
| ------------- | --------------- | --------------- | ----------- |
| `Task`        | `tasks`         | `tasks`         | ✅           |
| `Habit`       | `habits`        | `habits`        | ✅           |
| `TimeEntry`   | `time_entries`  | `time_entries`  | ✅           |
| `DailyEntry`  | `daily_entries` | `daily_entries` | ✅           |
| `Product`     | `products`      | `products`      | ✅           |
| `Transaction` | `transactions`  | `transactions`  | ✅           |

Now: API routes = table names = subtypes = frontend module names


## [Mon 6.10.25] - Context Menu Refactoring & API Alignment Work
1. Context Menu Refactor
    - Unified `createContextMenu(e)` → `openMenu(type, triggerInfo)` to support both right-click (`context`) and button-based (`dots`) menus
    - Standardized `triggerInfo` object:
        - `x/y` for cursor-based positioning (right-click)
        - `rect` for button-based positioning (dots menu)
        - `context`: row-level metadata (`itemId`, `subtype`, etc.) passed to action handlers
    - Added global Escape key handler to close the menu from anywhere
    - Menu now always removes existing instances before creating a new one (prevents duplicates)
    - WIP: `Delete` and `Add to Shopping List` actions still need to be wired up for the Tasks module

2. API:
    - Moved `/api` routes from `app/modules/` → `app/api/` with a centralized blueprint in `app/api/__init__.py`
    - Pluralization convention: all endpoints now use pluralized `module` and `subtype`
    - Format: `/api/<modules>/<subtypes>/<id>` (e.g., `/api/tasks/tasks/123`)
    - Updated `MODULE_CLASSES`, dashboard templates, and JS context menu URLs
    - Modal system cleanup:
        - Modals now use `data-module`, `data-subtype`, and `data-endpoint` directly
        - Removed separate endpoint variables — URLs are now built from dataset attributes
        `apiRequest()` auto-prefixes `/api`
    - Consolidated completions POST/DELETE routes into a single handle
    - `triggerInfo.context` is now bound to `menu.context` for downstream use
    - Modal `data-endpoint` = `${module}/${subtype}` (aligned with pluralization)

## [Sun 5.10.25]
**Log:**
1. Refactored `add_transaction` flow (product-driven instead of barcode)
    - Route logic:
        - `product_id == '__new__'` -> create new product, then transaction
        - else: use existing product for transaction only
    - Service: `create_transaction()` now assumes product_id is always valid
    - Form logic:
        - Removed `show_product_fields`, product fields now hidden/disabled by default
        - JS toggles field visibility on dropdown change
    - Groceries dashboard:
        - Show '--' for products without barcodes
        - Removed barcode column from transaction table (viewmodel + template)
    - Validation updates:
        - Product: all fields required except `barcode` & `calories`
2. CRUD Update flow (WIP, started with Tasks)
    - Renamed `create_thing()` with `save_thing()` in service layer — now branches:
        - If `id` -> update
        - Else -> insert
    - Began wiring update: Generalized GET route returns .to_dict()
3. Model & Schema Fixes
    - Task: made `priority` nullable; removed default.
    - LeetCode: removed defaults for `difficulty`, `language`, & `status`.

## [Sat 4.10.25]
**Log:**
1. Viewmodels + TimestampedMixin Tuning
	- Update templates to reference `*_label` properties for most fields
	- Refactored `TimestampedMixin` to reference self._tz directly instead of requiring it as a parameter - we'll nearly always want to display in user's timezone anyway.
	- Add label mappings for `ProductCategoryEnum` & `UnitEnum` values for readability
	- Pruned a few methods
	- Fixed several broken columns' displays & standardized date/time formatting across modules
2. Model Retooling
	- Added metadata for auto-naming FKeys, constraints, etc to db_base.py
	- Replaced all instances of `unique=True` with `UniqueConstraint(user_id, field)` via `__table_args__` for multi-user uniqueness enforement
3. Retooling "Add Transaction" form:
	- Barcode entry was clunky -> Pivoting to product name via dropdown
		- Made `barcode` nullable, updated validators accordingly
	- This simplifies the "product exists" case, but will require more handling for the "add new product" case
	- Progress:
		1. Add select dropdown populated by all current products [DONE]
		2. Unhides/enables all inputs in form when "+ Create new product" is selected [DONE]
		3. Tweak route for following cases:
			1. If product_id == '__new__' -> Run all parsing/validation
			2. Else -> Run only transaction parsing/validation + add transaction using product_id we now already have

## [Fri 3.10.25] - Validation & Service/Route Cleanup
**Log:**
### All Modules
- Moved validation to routes, removed typecasting from services
- Repo signatures made explicit (removed **kwargs unpacking)
- Generally tidied comments/imports/etc, updated/aligned type hints

1. Habits:
	- Status & promotion_threshold no longer user inputs; service sets based on is_promotable
	- Adjusted tests accordingly
2. Tasks:
	- Cross-field validation in validate_task:
		- is_frog=True  -> due_date required, priority must be None
		- is_frog=False -> priority required, due_date optional
	- Added test cases for validate_task to cover our bases
	- Adjust due_label to timedelta -1 second since we now use exclusive EOD
3. Groceries:
    - Rewrote/simplified process_transaction_form -> create_transaction
    - Inverted condition logic (Case C -> B -> A)
    - Removed silly inclusion of product_id in transaction validation
4. Auth:
    - Removed register_user_from_form(), condensed get_or_create_X_user() methods into one
    - Deleted hardcoded create_demo_user/create_owner_user from repo
5. Shared:
    - Datetime helpers + validators: fleshed out, fixed naming, added tests
	- BaseRepository: added delete method
	- Added REMEMBER_COOKIE_DURATION in BaseConfig. Flask automatically picks it up for our "remember me" thing.
	- Updated requires_owner decorator to wrap requires_login decorator

## [Thurs 2.10.25]
**Log:**
1. Add validate_time_hhmm() in shared validators, add test cases
	- For required fields: uberfuncs will call shared helper directly (ie `"started_at": validate_time_hhmm`)
	- For optional fields: uberfuncs will call thin wrapper funcs to allow "if not field: return (None, [])" before returning the validator (ie `"wake_time": validate_time_hhmm_format`)
2. Scrapped `parse_eod_datetime_from_date` helper - replaced with validate_date_iso in shared validators to parse raw date_str + to_eod_datetime in service layer for tasks to convert that date into a full EOD datetime
	- Refactored task service to apply `to_eod_datetime` directly to the `due_date` field from validate_task, remove redundant typecast declarations, and dropped the prepped_data dict -- now using `typed_data` consistently from validation thru to repo.

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
