# Design

Pitch: every app tracks; this one tells you what to do about it. Pillars plus pandas-driven insight are what make that claim true.

## Misc.
- All timezone/date handling uses the USER's timezone, not the browser's, wherever possible.

## Modules: now / toward

0. Spine
    - CSP + CSRF hooks
    - Error handlers: ServiceError/ValidationError -> page or JSON envelope
    - CLI (init-owner, reset-dev, seed, reap)
    - Weather proxy w/ live rate limiter
    - Seeding works

1. Tasks
    - Now: priority, Frog, subtasks, task links w/ cycle check, drag-and-drop reorder via fractional indexing, tasks-web visualizer.
    - Toward: polished tasks view page.
2. Habits
    - Now: Full CRUD, completions, streaks, summary + heatmap endpoints, per-week frequency, mark done.
    - Unifinished: Promotion logic
    - Toward: visible reward for consistency, warn before a streak breaks, show best-ever.
3. Metrics 
    - Now: daily weight/steps/sleep/calories. Windowed/bucketed aggregates, compare endpoint, charts.
    - Toward: trustworthy body-numbers diary that other modules (Pillars) consume.
4. Time tracking 
    - Now: log durations per category, donut chart. 
    - Toward: honest mirror of hours so the app can compare time spent against intentions.
5. Groceries 
    - Now: Products/transactions/recipes/shopping-list CRUD, recipe shortfalls, live kitchen inventory via append-only event ledger.
            CSV nutrition import (only one "shape" for Myfitnesspal)
            Cook flow
    - Unfinished: InventoryLedgerRepository?
    - Toward: a kitchen that knows what's in stock, what you ate, and eventually whether it was good for you.
6. Auth/Accounts 
    - Now: signup/login, city/country, units, theme. Multi-tenant. Register/login/logout, demo-user init, /profile/me + PATCH endpoints for user profile/goals. Profile/Goals split is complete.
    - Toward: Finishing Demo stuff?
7. Pillars 
    - Now: draft page only; tasks/habits/time entries taggable with a life area.
    - Missing: Metrics and groceries exist outside of Pillars entirely atm.
    - Toward: one five-pointed shape showing life balance at a glance; goes lopsided when a pillar shrinks; warns after ~3 weeks of neglect.
8. Analytics (Effectively abandoned rn :( )
    - Now: experimental correlations (habit completions vs deep-work time), not user-visible. 
    - Toward: plain-English readbacks ("you seem happiest when time splits ~40% career / 25% relationships / 35% health").

## Smaller scaffolds parked mid-start:
1. `Page[T]` pagination dataclass (never instantiated)
2. Target value objects (only Within is used)
3. Hooks.py event bus (emit/on stuff?; zero importers)


## Pillars

Research-backed core life domains critical to long-term wellbeing. All other modules feed into this as aggregate scoring for "how we're doing." Fixed enum, not user-defined.

| Pillar | Scope | MM |
|---|---|---|
| Health | exercise, sleep, nutrition | 0.6 (highest, foundational) |
| Rest/Recovery | downtime, leisure, fun | 0.5 |
| Relationships | friends, family, community | 0.35 |
| Career/Growth | work, learning, skills | 0.3 |
| Purpose/Meaning | spirituality, volunteering, reflection | 0.2 (lowest) |

MM = "Maslow Minimum": per-pillar minimum threshold. Lower Maslow levels get higher minimums because everything downstream collapses without them.

Research backing: SDT (Deci & Ryan), PERMA (Seligman), Ryff's Six Dimensions, Blue Zones all converge on the same ~5 themes: Health/Body, Growth/Mastery, Connection, Meaning, Balance/Rest.

### Radar chart (prototype in progress)
Three layers, same axes, drawn floor-first so the actionable shape sits on top:
1. MM threshold - dashed stroke, no fill, muted. Asymmetric pentagon.
2. Long-term baseline - rolling 6–12 month avg ("my normal"). Muted fill, context.
3. Short-term/current - last 30 days. Vivid fill, the actionable shape.

D3: `d3.lineRadial()` + `curveLinearClosed`, polygon gridlines (discrete categories, not circular), `-Math.PI/2` offset for 12 o'clock start.

### Neglect signal
- Flag when a pillar sits below MM for N consecutive days (rolling window).
- Grace period, like STREAK_GRACE_DAYS for habits.
- Cascade warning: Health dropping warns that downstream pillars are at risk.
- Color encoding: vibrant thriving → orange/red neglected.

### Pillar value computation (future)
- Activity-based (derive from time entries, habits, metrics, groceries), self-reported (periodic rating), or hybrid (data baseline + self-report adjustment).
- Floor-raising: new MM = 80% of 12-month rolling high, so standards ratchet up.

### Integration
PillarEnum tag on tasks, time entries, habits (simple enum, not a tag system). Examples: time entry "Walk" → Health; habit "drink water" → Health; task "prep interview" → Career; grocery categories → Health (veggie % of calories). Everything flows into the same radar shape.

## Insight ladder

1. Mirror - expose data back, no interpretation.
2. Threshold - ???
3. Notice - neglect callouts: "Health below threshold for 12 days."
4. Context - recent vs personal baseline: "Health 30% below your usual."
5. Cascade - prediction: "Health drops show up in Rest within two weeks."
6. Suggestion - attribution: "Your Health drop is mostly sleep, not steps."

## Unhomed notes
- Pillars score history isn't queryable; no backend yet. Neglect detection and cascade-warning logic have nowhere to live until that backend exists.
- `emit`/`on` decorator in hooks.py is event listening; could it replace patch hooks?

## TODOs (→ move to TODO.md)
1. Circuit breaker on weather service (also: rate limiting via token bucket?)
2. Health check endpoint: `/api/health`
3. Per-request cache on Flask `g`: pillar scores?

---

## Journal (→ move to PROJECT_LOG)

### Feb 19 - analytics spike
Built: `get_daily_completion_counts()` (HabitsService) and `get_daily_time_stuff()` (TimeTrackingService) returning per-day DataFrames; `AnalyticsService` in shared/analytics.py composing both with Pearson correlation (pandas merge + `.corr()`); `create_analytics_service()` factory; `seed_rich_data()` with 30 days of correlated habit/time data.
Follow-ups: strip debug prints; wire analytics to a real route/template; per-habit correlation breakdown; p-value via `scipy.stats.pearsonr`; maybe promote analytics to a proper module; extend seeds to remaining modules and guest `seed_data()`.

### Analytics ideas backlog
- Habits: adherence rate, longest streak, decay after missed days, next-week completion forecast.
- Tasks: overdue rate, Frog completion impact on same-day throughput, aging/cycle time.
- Metrics: week-over-week deltas, outlier detection (steps/calories), steps-vs-sleep correlation.
- Time tracking: fragmentation index, rolling averages, allocation drift.
- Groceries: price-per-calorie.

### Tasks page kickoff
`stat_circle` macro (header/rate/numerator/denominator, progress-ring styling); TasksService `calc_overdue_rate()` and `calc_frog_adherence_rate()`, routes defaulting to 7d.

### Mar 9 - dataclass DTOs + model simplifications *(DTO layer since superseded by Pydantic migration)*
- ValidatedX dataclasses across all modules; validators returned `(Dataclass | None, errors)`; services took typed dataclasses; killed unsafe setattr loops.
- Model changes that stuck: `is_frog` merged into `PriorityEnum.FROG`; `is_done` dropped (hybrid_property over `completed_at`); `promotion_threshold` → service constant; steps/calories constraints tightened to `> 0`; constraint-name prefixes delegated to naming convention.
- Pending list from that day (audit against code before trusting): log_validator generics, Mapped[] vs nullable audit, shared/conversions.py, dead-code sweep, shared `assign_pillars()` helper, ValidationResult deprecation, constraint renames, frog checkbox → priority dropdown, `to_api_dict` promotion_threshold reference.

### Mar 10 - cleanup
- Reverted `weight_units`: back to always-store-kg, convert on display; viewmodel `weight_label` converts via `current_user.units`; migration dropped column/constraint/enum.
- Fixed inverted `is_acyclic` return; `Mapped[... | None]` audit; ruff pass.
- Style-reference page restructured into card grid; new components: CSS-only toggle switch, radio tabs with glider, binary theme toggle, native drag-and-drop with FLIP.
- CSS 3D transform prototype for future pillars radar; light-mode tokens: `--active-bg`/`--active-text` swap strategy between themes (glow in dark, weight in light).
