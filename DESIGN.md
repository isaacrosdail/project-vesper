
## Sales pitch for this app: Every app tracks - we tell you what to do about it.
This is the load-bearing idea, and Pillars, as well as pandas-driven insight throughout dashboards/pages, are what makes it true.

## OVERVIEW notes to self:

Modules:

1. Tasks
    NOW:
        - Track tasks: priority, Frog, subtasks relationships, drag-n-drop list re-ordering, tasks web visualizer.
    AIMING TOWARD:
        - ?? Polished tasks view page for now.
2. Habits
    NOW:
        - Can list recurring habits, set how often per wk, and mark them done. It tracks your streak.
    AIMING TOWARD:
        - Something that doesn't just count, but rewards you visibly for consistency, warns you when
        you're about to break a streak, and shows your "best ever" so you can chase it.
3. Metrics
    NOW:
        - Can track daily weight, steps, sleep time/duration, calories. Charts show how those move over time.
    AIMING TOWARD:
        - Trustworthy daily diary of our body's numbers that other parts of the app can use/feed to tell us bigger-picture stuff (Pillars)
4. Time Tracking
    NOW:
        - You can log "I spent 90 minutes on work, 30 minutes on exercise" etc., and a donut chart shows
        where your time went.
    AIMING TOWARD:
        - An honest mirror of how you actually spent your hours, so the app can tell you whether
        your time matches your intentions.
5. Groceries
    NOW:
        - You can track what you bought, what's on your shopping list, what recipes you have, and keep an accurate count of what's actually in our kitchen right now by recording every purchase, consumption, and waste event.
    Aiming toward:
        - A kitchen that knows itself — what's in stock, what you ate this week, and (eventually)
        whether what you ate was actually good for you.
6. Auth / Accounts:
    NOW:
        - Can sign up / log in, set city/country, unit preferences, theme. Multi-tenant.
7. Pillars
    NOW:
        - Not much. Draft page still very much a WIP. We've wired things up so a task/habit/time entry can be tagged with which "life area" it belongs to (Health, Career, Relationships, Rest, Purpose)
    AIMING TOWARD:
        - A single picture: a five-pointed shape that tells us at a glance whether our life is in balance. If any pillar is shrinking, the shape goes lopsided. If we've ignored a pillar for 3 weeks, it warns us. Pitch: Trackers usually just track stuff and tell you data, this one should tell you what to do about it.
8. Analytics
    NOW:
        - Still experimenting, can notice "on days you complete more habits, you also tend to log more deep-work time". Not visible to user yet.
    AIMING TOWARD:
        - Sentences in plain English like "you seem happiest when your time splits roughly 40%
        career, 25% relationships, 35% health." The app reading patterns back to you.


### Sooo... 'insight'. How do we tackle that?

Rung 1: Mirror. Don't interpret yet, just expose data back to the user.
Rung 2: Threshold. ???
Rung 3: Notice. Add the neglect callout - "Health has been below threshold for 12 days". Now the app is pointing instead of just displaying.
Rung 4: Context. Compare recent to baseline. "Health is 30% below your usual". Not just "below standard" - below OUR standard.
Rung 5: Cascade. "Health dropping usually shows up in Rest within two weeks". Now we're making predictions based on current behavior/recent history to inform what the user should do/correct.
Rung 6: Suggestion. "Your Health drop is mostly driven by sleep, not steps".


## Find a home for these notes:
- Pillars:
    - Score history isn't queryable as data (since we haven't given Pillars a proper backend yet)
    - neglect detection / cascade warning logic from TODOs also has nowhere natural to live since we haven't wired those into a backend thing yet either.

### Areas to mature:
- SQL/SQLAlchemy: window functions, CTEs, subqueries, hybrid_property.
    The pillar scoring, streak calculations, and correlation analytics will push into real SQL.
- Data modeling — the pillars feature is pushing into real relational design (join tables, aggregation across modules, time-series windowing). Lean into that.
-- Writing tests first for the pillar scoring logic would force us to nail the interfaces.
-- @hybrid_property (using now for is_done), also @hybrid_expression
    - lets us write one property that works in both contexts? useful once we start doing pillar score
        aggregation in queries?

SQL/SQLAlchemy stuff:
- 



-- emit/on decorator pattern in hooks.py - literally event listening, could replace patch hooks?

-- Type narrowing in validators:
Our validators return tuple[dict, dict] — both untyped dicts. After validation, we know the shape of the data, but the type system doesn't. The next level: validators return a TypedDict or dataclass:

```py
class ValidatedTask(TypedDict):
    name: str
    priority: PriorityEnum | None
    due_date: date | None
    is_frog: bool
    subtask_ids: list[int]
    pillar_ids: list[int]
```

Then save_task receives ValidatedTask instead of dict[str, Any].
No more typed_data.get("priority") guessing — we know the keys
exist and their types. The Any disappears from our service layer.


---




## Feb 19: Taking a stab at analytics

Built:
- get_daily_completion_counts() on HabitsService, returns DataFrame of completions per day
- get_daily_time_stuff() on TimeTrackingService - returns DataFrame of duration per day
- AnalyticsService in shared/analytics.py - composes both services, 
    computes Pearson correlation with pandas merge + .corr()
- create_analytics_service() factory
- seed_rich_data() - Updated this to include 30 days of correlated habit/time data using productivity score

Learned/used:
  - pandas: DataFrame, groupby, size(), sum(), merge, fillna, corr()
  - Python random: random(), randint, choice, sample
  - Pearson correlation: what the -1 to 1 range means
  - Association table rationale (many-to-many vs self-referential FK)
  - DESIGN.md: problem -> decision -> why -> example structure

To wrap up later:
  - Strip debug print/import sys from service methods
  - Wire analytics to a real route/template beyond the dummy index placeholder
  - Revisit Tasks Web section of DESIGN.md
  - Per-habit correlation breakdown (instead of the simpler, flatter one we have now)
  - Showing/getting the p-value? -> scipy.stats.pearsonr
  - Consider promoting shared/analytics.py to a proper module once we iron out the basics
  - Flesh out seed_rich_data() later with the rest of our modules. Update seed_data() (guest) too



### Analytics notes
Streak consistency for habits
Task aging? / cycle time?
Price-per-calorie for groceries
Time allocation drift for time_tracking?

Metrics:
    - Windowed deltas & anomalies (eg steps vs sleep correlation)
    - Week-over-week change
    - Outlier detection for steps / calories

Habits:
    - Adherence rate
    - Longest streak
    - Decay after missed days
    - Forecast of next-week completions from recent windows?

Tasks:
    - Overdue rate
    - Frog task completion impact on same-day throughput

Time tracking:
    - Fragmentation index?
    - Rolling averages


## Starting on Tasks page today:
- Add macro for stat_circle (header/rate/numerator/denominator), with progress ring styling
- Tasks service (defaulting to 7d in route calls)
    - calc_overdue_rate()
    - calc_frog_completion_rate()


## Mar 9, 2026:
Dataclass DTOs across all modules:
- Tasks: ValidatedTask — replaced dict[str, Any] with typed dataclass
- Habits: ValidatedHabit — same pattern
- Groceries: ValidatedProduct, ValidatedTransaction, ValidatedShoppingList,
ValidatedShoppingListItem, ValidatedRecipe
- Metrics: ValidatedDailyEntry
- Time Tracking: ValidatedTimeEntry
- All validators now return tuple[Dataclass | None, ValidationErrors] instead of tuple[dict, dict]
- All services accept typed dataclasses instead of dict[str, Any], use attribute access instead of
dict access
- Eliminated unsafe setattr loops over arbitrary dict keys — now either explicit field assignments or
gated dataclasses.fields() loops

Model simplifications:
- Merged is_frog boolean into PriorityEnum.FROG — eliminated column, two check constraints, and
cross-field validation dance
- Dropped is_done column — hybrid_property from completed_at is the single source of truth
- Dropped promotion_threshold column — moved to service constant (formula, not data)
- Added WeightUnitsEnum + weight_units column — store raw weight + units instead of lossy conversion
at write time
- Tightened steps/calories constraints from >= 0 to > 0 (0 is meaningless, use null for missing)
- Added ck_weight_requires_units constraint (weight and units are always paired)

Naming convention cleanup:
- Constraint names no longer manually prefixed with ck_ (naming convention handles it)

Still pending (revision notes):
1. Fix log_validator decorator generics
2. Audit all Mapped[] annotations against nullable=
3. Create shared/conversions.py for display-time unit conversion
4. Remove dead code: debug prints, commented-out old dict code, _convert_weight, lbs_to_kg import
5. Extract shared assign_pillars() helper
6. Update ValidationResult type alias / deprecate it
7. Rename remaining old-style constraint names across all models
8. Frontend: remove frog checkbox, add FROG to priority dropdown
9. Habit to_api_dict still references self.promotion_threshold — will error



## March 10:

  Backend cleanup:
  - Reverted weight_units on metrics model — back to "always store
  kg, convert on display"
  - Traced the form submission flow confirming formToJSON picks up
  all named inputs automatically
  - Viewmodel weight_label property now converts based on
  current_user.units
  - Migration to drop weight_units column, constraint, and enum
  type
  - Fixed is_acyclic (was kahns) — return value was inverted,
  rejecting every valid link
  - Mapped annotation audit — added | None to nullable columns
  across models
  - Ruff linting pass — learned --ignore flags, raise from None
  pattern, pathlib preference

  Style reference page overhaul:
  - Restructured from sprawling vertical sections into compact card
   grid
  - New sections: Design Tokens (swatch strips), Controls
  (buttons), Input States, Input Types, Custom Controls, Feedback,
  Drafts, Table
  - Killed redundant demos, dead TODOs, duplicate sections

  New components:
  - Toggle switch — CSS-only with ::before (knob) and ::after (icon
   via mask), color-mix() for theme-adaptive knob color, glow on
  active state
  - Radio tabs with glider — pure CSS using :has(:nth-child)
  selectors, sliding animated glider
  - Theme toggle — replaced dropdown select with binary toggle,
  sun/moon SVG masks, simplified JS (no more
  themeMap/reverseThemeMap)
  - Drag and drop — native API on style reference cards, FLIP
  animation technique learned

  CSS/3D exploration:
  - CSS 3D transforms — perspective, rotateX/Y/Z, translateZ,
  transform-style: preserve-3d
  - Built stacked layer prototype for future pillars radar chart
  effect
  - Mouse-tracking card tilt via mousemove + custom properties
  - IntersectionObserver basics for scroll-triggered animations

  Light mode tokens:
  - Identified the core issue: surface range too narrow, accents
  too light
  - Introduced --active-bg / --active-text semantic tokens that
  swap strategy between themes (glow in dark, weight in light)
  - Started applying to timeframe pills and toggle


