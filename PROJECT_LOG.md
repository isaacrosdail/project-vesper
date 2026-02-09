# Project Log

## Archive - Logs for Previous Months
- [2025-03](PROJECT_LOG_ARCHIVE/2025/03.md)
- [2025-04](PROJECT_LOG_ARCHIVE/2025/04.md)
- [2025-05](PROJECT_LOG_ARCHIVE/2025/05.md)
- [2025-06](PROJECT_LOG_ARCHIVE/2025/06.md)
- [2025-07](PROJECT_LOG_ARCHIVE/2025/07.md)
- [2025-08](PROJECT_LOG_ARCHIVE/2025/08.md)
- [2025-09](PROJECT_LOG_ARCHIVE/2025/09.md)
- [2025-10](PROJECT_LOG_ARCHIVE/2025/10.md)


**Pinned First Entry** (for perspective)
## [Wed 26.02.25] *(Old - obviously replaced by Flask app)*
**Log:**
- Installed Raspberry Pi OS (RPi 4 Model B), installed Node.js, & got MagicMirror running
- Installed MMM-Remote-Control via `npm install` in `~/modules/MMM-Remote-Control`
- Whitelisted all local IPs for access from laptop/etc



## [Thurs 12.02.2026]
1. Add instructions to README for how to run locally
    - Add .env.example


## [Mon 09.02.26]

TODO: Add "clean up / dedupe dialog stylings for confirmation vs form-modal" to checklist somewhere

1. Commit contextMenu changes
2. URLs:
    - api.ts: Add routes mapping const thing
    - MORE STUFF
3. Style improvements:
    1. Ingredients row in form: Gave more visual distinctness & positioned delete svg in top right,
        with hover effects to make it clear what it references
            - ALSO: Un-wrapped delete_btn SVG from button inside macro, just svg now. Need to update name & remove commented part
    2. Confirmation modal styling:
        - Switch from using form-actions to new confirmation-actions (kinda sloppy but works)
        - 

## [Tues 03.02.26]
1. Recipe feature
    - Add Recipe, RecipeIngredient models & revision
    - Add RecipeRepository
    

## [Thurs 21.01.26]
1. Finish updating parsers.py
2. Switched wake_time/sleep_time fields to using datetime-local
    - Then removed the weird sleep_time logic since it's now unambiguous

## [Wed 20.01.26]
1. Further JS-side validation stuff
2. Start fixing up `parsers.py` & updating call sites
3. Start adding datetime-local to metrics form for wake/sleep fields

MISC:
- Updated calculate_habit_streak to use `pairwise()`
- Renamed datetime/ to datetime_/ to avoid shadowing stdlib

## [Tues 19.01.26]
1. 

## [Mon 18.01.26]
1. Implement frontend validation for register.html
2. Refactor modal-manager.ts so form submission logic is in forms.ts, not mixed in with modal-manager.
    - Added `form-type` data attribute to distinguish between modal, full-page, and "single action" forms. Added to all form tags (I think)


## [Sat 17.01.26]
1. Learn proxies, do some frontend validation setup (just login page atm)
2. Tweak LeetCode record table to condense - batch LC_ID and Title together into one cell
3. Add thorough documentation to view_mixins.py for the whole "viewmodels/presenters" system.
4. Add border-left & increase stroke-width on password toggle eye SVG so it's more visible.

## [Sun 15.01.26]
1. CSRF Token implementation
    - 
2. Viewmodels (most): 
    - Split TimestampedViewModel into BaseViewModel & HasDueDateMixin
    - Cut timezone conversions from here, instead using model properties now

3. Model changes (ORM-side, not Postgres-side)
    - Added `*_local` properties for all applicable model fields involving datetimes
    - Added proper relationships between User <-> (models) class defs

## [Sat 14.01.26]
1. Mostly learning/drills - generators, sets, comprehensions

## [Thurs 08.01.26]
1. Move to custom script on prod
    - ./scripts/deploy.sh
2. 

## [Sun 04.01.26]
**Log:**
1. Fix up HTTP status codes throughout
2. Actually implement the units field thing
    - User model already had units: UnitSystemEnum (imperial/metric)
    - DailyMetrics stores in master units (kg)
    - Convert inbound data at service, outbound weight in generic GET route
    - Added needed pieces in parsers, validators (requires weight_units if weight is present, must be "kg" or "lbs")
    - Added weight units dropdown to daily metrics form (units default to value of user's units field)

LEFT OFF: ruff check codebase-wide, working on pruning debug terminal output
    Once done with that, onto other linting/etc.

## [Sat 03.01.26]
**Log:**
1. Purge 'Any' typing from most, if not all, functions/view functions

Misc. Replace manual query parameter handling with native options (JavaScript's `URLSearchParams`, Python's `request`)

## [Fri 02.01.26]
**Log:**
1. Refactoring Service/Repository
    - Moving to one repository (class) per model (Applied to all modules, although only a few needed real splitting-up here as not all even have 2+ models to them.)
    - Removed `user_tz` from BaseRepository since, duh, only services need timezone.
    - Services hold session, pruned/rethought parameters/args passed into services and repositories
    - Add factory functions for convenience
2. Ripped out ABTests/Trials 'feature' entirely.
    - This was half-baked, and doesn't really fit with what I wanna do here anyway?
3. Naming consistency: DailyMetrics
    - Renamed model to DailyMetrics for clarity (better fits 'composite metrics')
    - Since we auto-gen table names, and this is the only one which is already plural, our auto-gen added another 's' mistakenly. So we just explicitly set the tablename for dailymetrics as a (likely) one-time exception case.

## [Thurs 01.01.26]
**Log:**
1. `apiRequest` improvements
    - Added `onFailure` callback for failure handling
        - Both `onSuccess` and `onFailure` callbacks are optional (destructuring options obj with default {})
    - Tightened `data` parameter typing to prevent passing functions as data
        - Now using `unknown` rather than `any`
        - Previously valid but not what we want: `apiRequest('DELETE', url, () => item.remove())` 
            - We restricted to `unknown` to TS still typechecks
    - Fixed Promise return behavior
        - Previously swallowed the `fetch` Promise, now returns it explicitly.
        - Now supports either pattern: `await apiRequest()` for data, or callbacks for DOM manipulation
        - Eliminated wrapper Promises in D3 chart data-fetching functions
            - Previously had to wrap apiRequest in `new Promise()` because it didn't return anything useful. This was goofy, and we can now
                simply return apiRequest().


## [Wed 31.12.25]
1. Wrap up tooltip.ts fixing
    - Fixed bug. Cause: getBoundingClientRect needed to be re-invoked in the else clause AFTER we did style.top and style.left. I think this is because we needed a fresh layout calculation since it seemed the bug was it not updating the width of the tooltip box AFTER we add text. Meaning a tooltip with text of 'h' and another with text of 'Hey there this is a long msg omg hahahahaha' would both be equal, which is of course wrong.
2. Fix: page-gating wasn't working for landing_page since it's also part of main.home route. So in base.html, added exception for main.home but not logged in for data-page="main.landing_page". Left userStore auth guard the same since auth guarding obv is the right play there.
3. Navbar Work
    - CSS: added missing bg styling for mobile nav-links on hover/active. Scrapped .active class here (where'd that get set anyway?).
        - Also: Moved nav-link active/hover styling to media queries. (<=768) for mobile bg-color, (>768) for desktop underline
4. Frog Task display in My Day:
    - Added accent border + bg-light for emphasis
    - Add tasks-section grid container for vertical spacing
5. Style/MIsc/Cleanup:
    - Made .context-menu position absolute so it scrolls with page. This doesn't "fix" the resize weirdness where it floats detached, but.
    - tables.ts: removeTableRow takes element instead of itemId, caller does query, export closeMenu()
    - context-menu.ts: Clean up addShoppingListItemToDOM naming
    - Changes to `api/`:
        - Renamed `api/service.py` -> `api/rate_limiter.py` for clarity
        - Cleaned up `/weather` route: removed old defaults, aligned city/country/units to current setup
        - Refined docstrings & pruned comments

## [Tues 30.12.25]
**Log:**
1. Fix: Sleep/wake time calculation in metrics service
    - Previously assumed sleep_time was always from previous day, which...doesn't quite work (eg, sleep 14:00 -> wake 15:00 = 25 hours of sleep!)
    - We now auto-adjust sleep_time to previous day only when sleep_time >= wake_time
    - Added tooltip to sleep_time form group explaining the auto-adjustment behavior
2. Fix: Tooltip positioning in dialog modals
    - Problem: Dialogs create their own stacking context, causing our tooltips to render beneath them
    - We now detect parent dialog via `.closest('dialog')` & append tooltip as ITS child (with absolute positioning)
    - Non-dialog tooltips still append to document body (with fixed positioning)
    - Also: cleaned up JSDocs, fixed typos and learned a new word (carrot -> caret)
3. In hell: tooltip is being a NIGHTMARE. LEFT OFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF========================================32423423=================================


## [Sun 28.12.25]
**Log:**
1. Cleanup:
    - tasks/dashboard.html: Add "Is Frog?" column to table + frog_label property to viewmodels.py to indicate which tasks are frog tasks
    - D3 charts:
        - Addressing D3 charts' "pop-down" on load due to JS setting size: Made/Extracted code into `getChartDimensions()` to handle setting/getting margins, height/width, & innerHeight/innerWidth (also set fallbacks for height/width and moved height/width values/setting to CSS vars)
        - For time_entries chart, we check angular size of slice to decide whether to enable the hover effect for that slice, rather than checking `data.length`, which was semantically sloppy.
    - Fix: add daily_entries singular/plural to types.ts for our modal legend text (forgot it before)
    - Groceries:
        - dashboard.html: Enforce new Hungarian-style Jinja naming conventions (type prefixes in form of: 'l_' for list, 'd_' for dict, etc. see: [conventions.md](CONVENTIONS.md))
        - Add include_soft_deleted param for get_all_products_in_window()
        - Aligned context keys from route with variable names (????)
    - Login/Register pages:
        - Fixed border caused now by fieldset/legend styling. We'll just ditch fieldset/legend entirely for these pages and use a div with form-column instead.



## [Wed 24.12.25]
**Log:**
1. Bun test stuff
    - Got happydom for DOM-related Bun testing. For happydom we needed to install it, then added happydom.ts to inject DOM APIs stuff as well as add bunfing.toml to preload happydom.ts to run before tests.
MISC:
	- Updated node/npm (updated .nvmrc)
	- Added linting/testing scripts to have a more complete toolkit for dev'ing
	- Added said scripts to our Husky pre-commit hook, and then added a pre-push hook for running tests.

## [ 21.12.25]
**Log:**
1. Forms continuation
	- Refreshed all form stylings. field-pairs now show horizontally inline, form is a grid column now with .form-column
	- Groceries forms fixing:
		- Fixed bug in transaction add form where clicking new, filling out fields, then instead selecting a product (therefore re-hiding the product fields) does NOT wipe field values.
		- Fixed bug where product form fields in transaction form were disabled but NOT required, meaning that adding new then just submitting without filling out any product fields would submit to an inevitable 400 error
		
		(MISSING SOME LOG STUFF BTW)
		
		LEFT OFF: Debugging some openMenu stuff in context-menu.ts. Namely refactoring listeners a bit, need to reorganize, and also made closeMenu() but need to figure out semantics since openMenu/closeMenu really should be called makeAndShowMenu and destroyMenu lmao.


## [Sat 20.12.25] - Continue Cleanup
**Log:**
1. Extend ... changes to all other form modals/modules
	A. Tasks:
		1. Rearrange form / add grid(s) if needed
		2. Toggle "show completed tasks" in table
			A. Add checkbox with JS to ......something something...
			B. Set display none if completed I guess?
2. CSS Tweaks/cleanup alongside
3. Linting/Formatting tooling additions/changes:
	- ALL: Rolled configs for mypy, pytest, Ruff, and djLint into a new `pyproject.toml` to better unify configs.
	- Stylelint (CSS): Config is `stylelint.config.mjs`
		Steps: `npm create styelint@latest`, `npm install -D stylelint-config-recess-order` (latter just for chosen config)
		DEPS: stylelint, stylelint-config-standard, stylelint-config-recess-order (this config orders properties in blocks by position -> display -> etc. Yay :D)
		Lint our CSS files with: `npx stylelint "**/*.css"
	- djLint (Jinja): Tested on landing_page.html | CONFIG: pyproject.toml?
		Steps: `pip install djlint`
		DEPS: djlint, 
	- Ruff (Python): Already had Ruff :D Tested using `ruff format app/routes.py`. | CONFIG: pyproject.toml?
========== LEFT OFF:	Radio form control styling (and generally applying a better, more compact grid layout for some forms)


## [Fri 19.12.25]
1. Form tweaks
    - Changed time_entries description input field to `<textarea>`
    - Added justify-content: center; to .tab stylings so the icon+text groupings are horizontally centered in their button elements.
    - Changed from inline-flex to flex for some elements
    - Worked a bit on tuning grid styling for "price + quantity" type groupings

## [Wed 17.12.25]
**Log:**
1. Login/Register page styling
	- Cleaned up checkbox jank
	- Made "Log in" & "Sign up" link texts visually distinct
	- Made card narrower, added spacing
	- Updated placeholder texts
2. Frontend validation basics
	- Created shared/validators.ts
	- Validaton on blur (only when non-empty)
	- Adding/removing in/valid classes (moving away from using native user-in/valid pseudo)
	- Creating inline error messages dynamically (appendChild to div so it sits below input field)
	- Moving away from :user-in/valid CSS to custom classes

## [Tues 16.12.25]
**Log:**
1. Misc cleanup to start :D
	- Purged split_hamburger_svg() (remove from _ui.html & usage in navbar)
	- Added Register link when not logged in (looks weird with just login lmao)
	- Change + move owner template user password to .env
	- Add docstrings to set_toast + some comments as breadcrumbs to that set_toast/makeToast system
	- Changed all `.route()` to the newer Flask 2.x syntax like `api_bp.post("/my-route")`
	- Stripped some old stylings, tokenized others
	- Facelift for login/register pages:
		- Improve vertical spacing between items
		- Add basic styling for links for visual clarity
		- Added slight margin-bottom to <legend> globally
	- Added `data-authenticated` attribute to root, which initUserStore() uses to bail on pages where we're not logged in, like register/login

## [Sun 14.12.25]
**Log:**
1. Bug fixing: Transactions 'edit' modal issues
    - Problem: In edit mode for transactions, we disable `select#product_id`, which of course broke submission. Also,
    (soft-)deleted products' names wouldn't show since they weren't in the Jinja-populated options.
    - Fix:
        - Add hidden input to submit `product_id`
        - Replace select options with product name from API (handles deleted products)
        - Store/restore original state on modal close (legend text, select innerHTML, disabled states)
        - Add `getSubtypeLabel()`
        - Add `not-allowed` cursor on disabled controls

## [Sat 13.12.25]
**Log:**
1. Habits dashboard:
	- Fix refreshChart() function to also clear axis labels
	- Removed dropdown from Habits (doesn't make sense for Habits)
	- Added timeframe selection to leetcoderecords
	- Moved dropdown inline with card-title => looks a lot slicker tbh
	- Minor: fix spacing issue with card-title
2. Improving "labels for (module) subtypes" dilemma in TS:
	- `types.ts`:
		- Added Subtype type (mirrors what we have in backend :D)
		- Added SubtypeLables type (singular vs plural)
		- Exporting a const SUBTYPE_LABELS so we can do stuff like "console.log(`${SUBTYPE_LABELS[subtype].plural`);"

## [Thurs 11.12.25]
**Log:**
1. Fixing shopping list bug
	Problems:
		1. Typo where we referenced shopping list item ID as data.item_id
			- This also broke our delete shopping list item functionality since that does .remove() on success of DELETE
			FIX: change to data.id
		2. IDs transaction vs product shit: PROBLEM?
			- Added data-product-id to <tr> when subtype is transactions
			- Ternary in JS assigns productId -> productId if subtype is transactions, itemId otherwise
			- Added productId to menuContext object & roped its collection in for context menu + dots-btn
MISC.
	- Fix mistake where pointer-events: none; meant that disabled state cursor wouldn't show

## [Wed 10.12.25]
**Log:**
1. theme-manager.ts revisions
    - Rewrote getCookie() to use split() instead of between() for exact substring matching
        - **Why:** Old approach found the first "=" in entire cookie string, causing false matches
        - EX: `user_theme=magenta; theme=light` would return "magenta" for getCookie('theme')
        - **Fix:** Split by "; " first to isolate cookies, then find() the one starting with `${name}=`
    - Added dispatchEvent to ensure cookie gets written on first load
    - `base.html`: Added `else` to fix lack of covering "system" case
    - Added JSDocs
2. 

## [Tues 9.12.25]
**Log:**
1. Context menu was extracting `name` using `td:nth-child(2)` which is obviously terrible. This breaks on any changes, and relies on specific ordering. It's a remnant of my not grasping how to tack on product_name efficiently to our api_dict.
`Name` was thus far only used for groceries to display toasts related to the shopping list feature.
Cleanup:
    - Removed `name` entirely
    - Extended `.to_api_dict()` for ShoppingListItem & Transaction using `super()` to augment with `product_name`
    - Sorted out a pattern for including relational data in API responses

## [Sat 6.12.25]
**Log:**
1. Wrapped up toggling Task completion via table context menu
	- Merged name+status into one column
    - Added checkmark_svg() macro+attributions
    - Tidied up TS as I went, namely context-menu.ts and tables.ts
2. 
MISC. Refactor index.ts: add JSDocs, refactor some pieces for clarity/simplicity

## [Fri 5.12.25]
**Log:**
1. DevOps: Docker/Compose cleanup
    - Fix broken Pi deployment
    - Cleaned up all compose files (dev/prod/pi)
        - Standardize service naming (db/flask)
        - Removed `environment` blocks with just `env_file`
2. Bug Fix: Dev Tools showing to non-owners in prod
    - Template was checking has_dev_tools (the function obj) instead of g.has_dev_tools
    - Moved APP_ENV check to has_dev_tools() itself (permissive for dev, owner-only for prod)
    - Removed nested template logic
3. Trying to wrap up `markComplete()` for Task table context menu
    - Renamed to `toggleTaskComplete()` so we can avoid conditional/dynamic menu options / text
    - NEXT: Finish implementation in apiRequest callback, need to rethink icon/symbol to use for status and/or Status column generally
Misc. Updated seed_db.py to work again after model/schema changes


## [Wed 12.11.25]
**Log:**
1. Metrics: Add timeframe filtering to table & separate type/timeframe dropdowns for chart
2. Habits:
    - Apply similar timeframe filtering (today/7d/30d) dropdown
    - Fixes:
        - Oversight where bar height was not updated for chart, leading to it not adjusting when dataset updates
        - Update 'this' type annotation: use d3.BaseType then cast as SVGRectElement
MISC. Fix: Dropdown bug where multiple could stay open when clicking a new one

## [Thurs 13.11.25]
**Log:**
1. Refine some D3 charts / brought them in line more
2. Habits: adding target_frequency to model + progress calcs
	- Required, represents target completion rate per week
	
	
## [Fri 14.11.25]
**Log:**
1. Fix linter warnings
2. Bug fix: Fix remove button on shopping list display not working

## [Wed 5.11.25]
**Log:**
1. Adding user config stuff to User model + userStore
	- Fields for city, country (ISO), units (metric vs imperial). Created UnitSystemEnum
	- Default to Chicago, US + imperial
	- Expanded profile/me route and userStore.ts to incl new fields
	- index.ts: Removed hardcoded city/units/country. Passing now to function:
		fetchWeatherData(city, country, units);
2. Converting to TS
	- index.ts, 
	- Dashboards for: habits, metrics

## [Tues 4.11.25]
**Log:**
1. Converting to TS:
	- modal-manager.js, dropdown.js

## [Mon 3.11.25]
**Log:**
1. Polishing D3 charts-related stuff for habits, metrics, & time_tracking
2. Converting JS files to TS:
	- tables.js, toast.js, api.js, forms.js, navbar.js, tooltip.js, userStore.js, canvas.js
	- dashboard.js for: tasks

## [Sun 2.11.25]
**Log:**
1. Drafting ABTesting functionality
	- Add ABTest, ABVariant models (to Metrics for now)
		- ABTest will serve as the test model itself, while ABVariant serves as the record for each individual trial
	- For each, add: form modal, POST route, parser
2. Added some basic logging