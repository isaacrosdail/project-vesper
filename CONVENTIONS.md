# Project Conventions

## Style
- Use modern ESM.
- Prefer object arguments when a function needs more than two inputs.
- Keep UI text concise. This is a dashboard, not a landing page.

## Testing
- Test the happy path and at least one edge case for domain changes.

## UI
- Keep cards dense and scannable.
- Modal edit flows use the `onPopulated` callback (shared/ui/modal-manager.ts).
- Mobile nav active/hover: left-border indicator + bg tint, one consolidated rule (navigation.css).

## Charts (D3)
- CSS owns container size; D3 reads `clientWidth`/`clientHeight`. No hardcoded fallbacks.
- Shared constants live in `shared/charts.ts`: `D3_TICKS`, `D3_GRIDLINES_DASHARR_VALS`, `D3_GRIDLINES_OPACITY`, `D3_OTHER_DIM_OPACITY`, `D3_TRANSITION_DURATION_MS`.
- Date parsing: `new Date(d.date.split('T')[0] + 'T00:00:00')` to avoid the UTC offset shift.
- X (time) axis: `getTickValues()` from shared/charts.ts + `.tickValues(...)`, formatted with `d3.timeFormat("%b %d")`. Y axis: `.ticks(D3_TICKS)`.
- Gridlines piggyback on the y-axis: extend `.tick line` to `innerWidth`, dashed with `D3_GRIDLINES_DASHARR_VALS`.
- Axis groups get classes `axis-x` / `axis-y`.
- Hover/crosshair: a full-size `<rect>` overlay captures the mouse; decorations drawn above it get `pointer-events: none` so they don't hijack mousemove.
- Bisect: `d3.bisector(...).left`, then compare left/right neighbors — nearest wins (barchart) or interpolate between them (linechart). Bisect requires date-ascending data; the backend repo methods guarantee this and must keep doing so.
- Radar: `d3.lineRadial()` + `curveLinearClosed`, `-Math.PI/2` offset for 12 o'clock start; polygon gridlines, not circular (discrete categories); all layers drawn in a single `.join("path")` over layers zipped with a per-layer style config array.
