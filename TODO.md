# TODO

The single canonical TODO list. Prune against actual code regularly.

Pending merges into this file: DESIGN.md "TODOs" section, memory `project_pending_todos.md`, memory `backend-improvements.md` (mine against code first — much of it is dead).

## Metrics charts
- [ ] `drawStaticLines` (`app/static_src/js/metrics/linechart.ts:78`) reported broken: update branch uses `y1`/`y2` on a `<rect>` (should be `y`). Verify and fix.
- [ ] Audit metrics charts for dead code, duplicate y-axis call, hardcoded weight target.

## Groceries dashboard
- [ ] Quick Log card: replace stub with `meals_today` payload slice from `groceries_dashboard` (service already holds the logs at `service.py:395`; pure shaping). Blocked on name rule: `recipe.name` with meal-slot fallback vs meal slot only. If recipe names: eager-load or batch-resolve names (avoid per-row lazy load — `NutritionLog.recipe_id` is `models.py:459`).

## Frontend housekeeping
- [ ] Divvy up `app/static_src/js/shared/utils.ts` into focused modules (formatters.ts, math.ts, ...). Grep for newly-dead exports first (swapField/swapToInput/swapToText/restoreOriginal/calculateBMR lose callers with the profile-sidebar.ts funeral).
- [ ] Toggle switch (`components.css:566-645`): tighten the contract. Fragile bits: requires `.toggle` as the input's *immediate* next sibling (`+` selector), empty track element easy to forget, `display: none` on `.toggle-input` kills keyboard access (use visually-hidden positioning like `.pill input` + `:focus-visible` ring on the track). Consider documenting the 3-piece markup contract next to the CSS or extracting a Svelte `Toggle.svelte` wrapper so the markup can't be assembled wrong.

## UI leftovers (button redesign)
- [ ] SVG icons: add missing `viewBox` on calendar/funnel; global `stroke: currentColor; fill: none` on `.icon`.
- [ ] Per-filter icon colors via existing `[data-filter]` attributes (today=red, upcoming=orange), if still wanted.

## Habits backend (blocks TodayView real-data swap)
- [ ] Typed habits: discriminant on `Habit` (`yn` / `duration` / `count`) + `units` for count habits. Model, schema, migration. Frontend union in `TodayView.svelte` is the target shape.
- [ ] Per-day values: `HabitCompletion` is currently row-exists=done. Needs a `value` column (bool/number semantics per habit type) so duration/count habits can log partial progress. Powers week-strip partial fill + backfill.
- [ ] Log endpoint: upsert by (habit, date, value) — matches frontend `logValue(h, date, value)`; backfill sends past dates, reject future dates.
- [ ] Week data in overview: each habit ships current week's `data: [{date, value}]` (Mon–Sun window, user tz) for the week strip.
- [ ] Consistency (server-computed): trailing 28 days, satisfied-days ÷ expected (`target_frequency × 4`); pro-rate expected for habits younger than the window (days-since-creation) so new habits aren't shown at ~35%.

## Tasks web canvas
- [ ] Undo/redo via command pattern: commands as `{ execute(), undo() }` objects capturing inverse data at do-time; two stacks (undo/redo), new action clears redo. Start where inverses are free: node moves (capture old `{x,y}`), then link add/remove. Delete needs backend soft-delete (`deleted_at` + reaper, cf. demo-user `reap`) before it can join the stack — or ship the simpler 30s "pending-kill" toast deferral first (interaction pattern, not undo; keep it out of the command stacks; filter pending-kill ids from all `tasksState.tasks` readers or `refreshTasks()` resurrects them).
- [ ] Cumulative time estimate on parent nodes: NOT Dijkstra — descendant-set sum (walk subtask edges, `Set` dedupe for diamond deps, sum estimates). Home: `js/tasks/graph.ts` alongside generalized shape-free `kahns(nodeIds, edges)`; pure functions, bun-testable (diamond case).
