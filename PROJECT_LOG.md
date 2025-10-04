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
