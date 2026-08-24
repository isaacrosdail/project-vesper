
## THOUGHTS to sort out:
1. Stop feeding data from both backend into Jinja AND from api to frontend -> 

# Architecture

Deliberate monolith: one Flask codebase, modules under `app/modules/`, one Postgres database.

## Layering
- `routes → service → repository → models`. Services hold domain logic, raise `ServiceError` (app.shared.exceptions), never format user-facing strings; routes own messages.
- Error hygiene: throw for the unexpected, return for expected domain outcomes.
- Repositories are pre-scoped to `user_id`, so an unscoped cross-tenant query isn't expressible from a route or service.

## User data
- `User`: identity, credentials, role, timezone. Core auth only.
- `UserProfile` (1:1): unit_system, hour_cycle, city/country/lat/lon (all-or-none constraint; lat/lon derived from geocode for weather), sex, birth_date, height_cm.
- `UserGoals` (1:1): typed target columns - weight (kg, canonical-unit rule), calories, steps, sleep_duration_minutes, protein/fat/carbs, potassium, sodium.
- This replaced the old EAV preferences bag. Goals are schema now, not keys.

## Devtools / permissions
- Destructive or admin operations (wiping data, seeding, reaping demo users) go through the Click CLI, not web routes.

## Schema decisions
- `InventoryLedger`: append-only ledger, single source of truth for grocery inventory.

## Frontend
- CSS: layered cascade, token system via `light-dark()`.

Unidirectional data flow, where the view is a pure function of state - Trying to move away from imperative DOM mutation / using the DOM as a source-of-truth as much as is sensible.
This also means using a pub/sub and store for resource lists - observer pattern?


## Permissions
Basic setup using .is_owner property on user or data-dev data-attr for env gated stuff

---

## Study notes (→ cut or move out of repo)
- Monolithic: all modules in one codebase, tightly coupled.
- Microservices: features deployed as smaller loosely-coupled services composing a distributed whole.
- Serverless/FaaS: functions hosted by a third party (AWS Lambda, Azure Functions, Firebase).


## Tooling / DX

1. 