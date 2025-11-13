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


## [Wed 12.11.25]
**Log:**
1. Metrics: Add timeframe filtering to table & separate type/timeframe dropdowns for chart
2. Habits:
    - Apply similar timeframe filtering (today/7d/30d) dropdown
    - Fixes:
        - Oversight where bar height was not updated for chart, leading to it not adjusting when dataset updates
        - Update 'this' type annotation: use d3.BaseType then cast as SVGRectElement
MISC. Fix: Dropdown bug where multiple could stay open when clicking a new one


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