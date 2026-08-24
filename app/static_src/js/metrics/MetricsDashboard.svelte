
<script lang="ts">
    import { openContextMenu } from '../shared/components/ContextMenu.svelte';
    import PaginatedTable from '../shared/components/PaginatedTable.svelte';
    import { fmtDate } from '../shared/datetime';
    import { sortByField } from '../shared/tables';
    import BarChartView from './charts/BarChartView.svelte';
    import ConsistencyMapView from './charts/ConsistencyMapView.svelte';
    import DailyMetricsForm from './DailyMetricsForm.svelte';
    import LineChartView from './charts/LineChartView.svelte';
    import { getDense, getPairs, loadData, metricsData, metricsState } from './metricsState.svelte';
    import MultiChartView from './charts/MultiChartView.svelte';
    import ScatterPlotView from './charts/ScatterPlotView.svelte';
    import type { BarMetricType, LineMetricType, MetricType, ReferenceLine } from './shared';
    import { getMetricTargets, pearson, TYPE_LABELS, TYPE_UNITS } from './shared';
    import { api } from '../shared/services/api';
    import { askConfirm } from '../shared/components/ConfirmDialog.svelte';


    // TODO(svelte):
    // 1. Fix that "halfBar" width jank for Today view in barchart
    //   Involves switching from timeBand to scaleBand, but implicates changing bisector stuff
    // 2. Handle empty states for charts generally
    // 3. Bisect for "all" view to see all 4 metric types
    // 4. Wire in "targets" (atmost/atleast/within)


    $inspect(metricsData.compare)
    $effect(() => {
        metricsState.selected;
        metricsState.range;
        loadData();
    });
    let metricsForm: DailyMetricsForm;
    let contextMenu = $state<{ metricId: number; x: number; y: number; } | null>(null);
    $inspect(contextMenu);

    let sortState = $state({ field: 'entry_datetime', order: 'asc' });
    const sorted = $derived(sortByField(metricsData.allSeries, sortState.field, sortState.order));

    const TIMEFRAMES = [
        { label: 'Today', value: 1 },
        { label: 'Week', value: 7 },
        { label: 'Month', value: 30 },
    ];
    const bmrValue = 2000;

    const config = {
        cols: [
            { label: 'Date', key: 'entry_datetime', fmt: (r) => fmtDate(r.entry_datetime) },
            { label: 'Wake', key: 'wake_datetime', fmt: (r) => fmtDate(r.wake_datetime) },
            { label: 'Sleep', key: 'sleep_datetime', fmt: (r) => fmtDate(r.sleep_datetime) },
            { label: 'Weight', key: 'weight' },
            { label: 'Steps', key: 'steps' },
            { label: 'Calories', key: 'calories' },
        ]
    }

    const latest = $derived(metricsData.series.at(-1)?.value ?? null);
    const delta = $derived.by(() => {
        const prev = metricsData.compare.previous?.[metricsState.selected] ?? null;
        const curr = metricsData.compare.current?.[metricsState.selected] ?? null;
        let delta = null;
        if (prev !== null && curr !== null && prev !== 0) {
            delta = (curr - prev) / prev * 100;
        }
        return delta;
    });
    const trend = $derived.by(() => {
        let trend: 'up' | 'down' | 'flat' = 'flat';
        if (delta !== null) {
            trend = delta > 0 ? 'up' : 'down';
        }
        return trend;
    });
    const deltaLabel = $derived.by(() => {
        return delta !== null
            ? `${delta.toFixed(1)}% vs last ${metricsState.range}d`
            : '';
    });
    const targets = getMetricTargets();
    const valVSGoal = $derived(latest - targets[metricsState.selected]);
    const aboveOrBelow = $derived(valVSGoal > 0 ? 'above' : 'below');
    const recentValVSGoal = $derived(`${Math.abs(valVSGoal).toLocaleString()} ${aboveOrBelow} goal of ${targets[metricsState.selected]}`)
    const hits = $derived(metricsData.series.filter(d => d.value !== null && d.value >= targets[metricsState.selected]).length);
    const hitRate = $derived(Math.round(hits / metricsState.range * 100));
    const hitRateOfLogged = $derived(Math.round(hits / metricsData.series.length * 100));
    const consistencyRate = $derived(
        `${hitRate}% of the last ${metricsState.range} days hit goal | ${hitRateOfLogged}% of days logged`
    );
    const xOfNDays = $derived(`${hits} of ${metricsState.range} days`);
    const streak = $derived.by(() => {
        const dense = getDense();
        let streak = 0;
        // Walk state.dense backwards (last entry = today)
        for (let i = dense.length - 1; i >= 0; i--) {
            const { value } = dense[i];
            if (value !== null && value >= targets[metricsState.selected]) {
                streak++;
            } else {
                break;
            }
        }
        return streak;
    });
    const { corr: rVal, regressionSlope, regressionIntercept } = $derived(pearson(getPairs()));

    const abs = $derived(Math.abs(rVal));
    const tier = $derived(correlationTier(abs));
    const sign = $derived(rVal > 0 ? 'positive' : 'negative');
    const descriptor = $derived(abs < 0.10 ? tier : `${tier} ${sign}`);
    const rLabel = $derived(`r = ${rVal.toFixed(2)} (${descriptor})`);
    function correlationTier(abs: number): string {
        if (abs < 0.10) return 'no correlation';
        if (abs < 0.30) return 'weak';
        if (abs < 0.50) return 'moderate';
        if (abs < 0.70) return 'strong';
        return 'very strong';
    }
    const metrics = ['weight', 'steps', 'calories', 'sleep_duration_minutes'] as const;

    const referenceLines: Record<MetricType, ReferenceLine[]> = {
        weight: [{ value: targets.weight, class: 'weight-target-line', label: 'Goal' }],
        steps: [{ value: targets.steps, class: 'steps-target-line', label: 'Goal' }],
        calories: [
            { value: bmrValue, class: 'bmr-target-line', label: 'BMR' },
            { value: targets.calories, class: 'calories-target-line', label: 'Goal' },
        ],
        sleep_duration_minutes: [
            { value: targets.sleep_duration_minutes, class: 'sleep-target-line', label: 'Goal' }
        ]
    };


    const BAR_METRICS: BarMetricType[] = ['steps', 'calories', 'sleep_duration_minutes'] as const;
    const isBarMetric = (m: MetricType | 'all'): m is BarMetricType =>
        BAR_METRICS.includes(m as BarMetricType);
    const LINE_METRICS: LineMetricType[] = ['weight'] as const;

    const SELECTIONS: (MetricType | 'all')[] = ['all', ...BAR_METRICS, ...LINE_METRICS];
    const isSelection = (s: string): s is MetricType | 'all' =>
        (SELECTIONS as string[]).includes(s);

    const hiddenLines = $state<Record<MetricType, boolean>>({
        weight: false, steps: false, calories: false, sleep_duration_minutes: false,
    });
</script>

<DailyMetricsForm bind:this={metricsForm} />

<div class="whole" data-metric={metricsState.selected}>
    <div class="top">
        <div class="options">
            <div class="metric-selector">
                {#each ['all', ...metrics] as m (m)}
                <button class="metric-pill" data-metric={m} class:active={m === metricsState.selected}
                    onclick={() => metricsState.selected = m}>
                    <span class="metric-dot"></span>
                    <span>{TYPE_LABELS[m] ?? 'All'}</span>
                </button>
                {/each}
            </div>
        </div>
        <div class="timeframe-selector surface">
            {#each TIMEFRAMES as tf (tf.label)}
                <button type="button" class:active={metricsState.range === tf.value}
                    onclick={() => metricsState.range = tf.value}>{tf.label}
                </button>
            {/each}
        </div>
    </div>
    <div class="hero-card">
        <div class="hero-top">
            <div id="hero-chart-title">{TYPE_LABELS[metricsState.selected]}</div>
            {#if metricsState.selected === 'all'}
            <div id="all-chart-toggles">
                {#each metrics as m (m)}
                    <button data-metric={m} class:deemphasized={hiddenLines[m]}
                        onclick={() => hiddenLines[m] = !hiddenLines[m]}>{TYPE_LABELS[m]}</button>
                {/each}
            </div>
            {/if}
            {#if metricsState.selected !== 'all'}
                <div class="secondary">{recentValVSGoal}</div>
            {/if}
        </div>
        <div class="hero-header">
            <span id="hero-chart-recent-val">{latest}</span>
            <span id="hero-chart-units" class="units secondary">{TYPE_UNITS[metricsState.selected]}</span>
            {#if delta}
                <span id="hero-chart-delta" data-trend={trend}>{deltaLabel}</span>
            {/if}
        </div>
        <div id="hero-chart">
            {#if metricsState.selected === 'all'}
                <MultiChartView {hiddenLines} />
            {:else if isBarMetric(metricsState.selected)}
                <BarChartView {referenceLines} {targets} metric={metricsState.selected} />
            {:else}
                <LineChartView {referenceLines} {targets} metric={metricsState.selected} />
            {/if}
        </div>
        
    </div>

    <div class="triple-row">
        <div class="surface">
            <div>
                <div>Consistency</div>
                <div id="consistency-rate" class="secondary">{consistencyRate}</div>
            </div>
            <ConsistencyMapView {targets} />
        </div>
        <div class="surface">
            <div>
                <div>Correlation</div>
                <div class="secondary">
                    <span id="correlation-metric">{metricsState.selected}</span> vs
                    <span id="correlation-comparator">SLEEP</span>
                </div>
            </div>
            <ScatterPlotView {regressionIntercept} {regressionSlope} />
            <div class="r-val secondary">{rLabel}</div>
        </div>
        <div id="goal-and-streak" class="surface">
            <div class="header">Goal & Streak</div>
            
            <div id="goal-donut-container" class="goal-donut" style="--pct: {hitRate}">
                <svg class="goal-donut__ring" viewBox="0 0 100 100">
                    <circle class="goal-donut__track" cx="50" cy="50" r="42" pathLength="100" />
                    <circle class="goal-donut__value" cx="50" cy="50" r="42" pathLength="100" />
                </svg>
                <div class="goal-donut__label">
                    <span class="goal-donut__pct">{hitRate}%</span>
                    <span class="secondary">days hit</span>
                </div>
            </div>
            
            <div class="days-hit-count secondary">{xOfNDays}</div>
            <div class="streak-on-target">
                <span class="streak-value">{streak}</span>
                <span class="secondary">day streak on target</span>
            </div>
        </div>
    </div>
</div>

<section class="card-dashboard surface daily-log" id="daily_metrics-table-section">
    <div class="card-title">
        <h2>Daily Metric Entries</h2>
        <button class="btn-icon btn-round btn-primary"
            aria-label="TODO"
            onclick={() => metricsForm?.open()}>
            <svg class="icon"><use href="#icon-plus"></use></svg>
        </button>
    </div>

    <PaginatedTable items={sorted} pageSize={15} getKey={(r) => r.id}>
        {#snippet header()}
            <tr>
                {#each config.cols as col (col.key)}
                    <th onclick={() => {
                        sortState.field = col.key;
                        sortState.order = sortState.order === 'asc' ? 'desc' : 'asc'
                    }}>
                        <span class="sort-label">
                            {col.label}
                            <svg class="icon"
                                class:flip={sortState.order === 'asc'}
                                class:visible={sortState.field === col.key}><use href="#icon-chevron"></use></svg>
                        </span>
                    </th>
                {/each}
            </tr>
        {/snippet}

        {#snippet row(r)}
            <tr oncontextmenu={(e) => {
                e.preventDefault();
                openContextMenu(e.clientX, e.clientY, [
                    { label: 'Edit', action: () => { console.log("implement me") } },
                    {
                        label: 'Delete', action: async () => {
                            if (!(await askConfirm('Delete this entry?'))) return;
                            await api.daily_metrics.delete(String(r.id))
                            await loadData();
                        }
                    },
                ]);
            }}>
                {#each config.cols as col (col.key)}
                    <td>{col.fmt ? col.fmt(r) : r[col.key]}</td>
                {/each}
            </tr>
        {/snippet}
    </PaginatedTable>
</section>


<style>

    .deemphasized {
        opacity: 0.3;
    }

    .goal-donut {
        display: grid;
        aspect-ratio: 1;
    }
    /* stack ring + label in the same grid cell — no absolute positioning */
    .goal-donut > * {
        grid-area: 1 / 1;
    }
    .goal-donut__ring {
        width: 100%;
        transform: rotate(-90deg); /* move the arc's start to 12 o'clock */
    }
    .goal-donut__track,
    .goal-donut__value {
        fill: none;
        stroke-width: 8;
    }
    .goal-donut__track {
        stroke: var(--surface-2);
    }
    @property --pct {
        syntax: '<number>';
        inherits: true;
        initial-value: 0;
    }
    .goal-donut__value {
        stroke: var(--metric-color);
        stroke-linecap: round;
        stroke-dasharray: 100;                         /* full path = 100 units */
        /* visible arc length = --pct */
        /* 1% to append the % unit to the calc'ed number; */
        stroke-dashoffset: calc((100 - var(--pct)) * 1%);
        transition: stroke-dashoffset 300ms ease;
    }
    .goal-donut__label {
        place-self: center;
        text-align: center;
        display: flex;
        flex-direction: column;
    }

    /* Goal & Streak section drafting */
    #goal-and-streak {
    display: flex;
    flex-direction: column;
    
    &:not(.header) {
        place-items: center;
    }

    & .streak-value { color: var(--metric-color); font-size: var(--font-size-xl); }
    & > .streak-on-target {
        display: flex;
        flex-direction: column;
        place-items: center;
    }
    }

    /* TODO: For the weight vs steps vs etc chart selection */
    .metric-selector {

    }
    /* Each metric type button selector inside of metric-selector group/div */
    .metric-pill {
    /* border-radius: var(--border-radius); */
    padding: var(--space-xs) var(--space-md);
    border-radius: 999px;
    opacity: 0.5;
    background: var(--bg);
    border: 1px solid var(--line-strong);
    display: inline-flex;
    align-items: center;
    gap: var(--space-xs);

    &:hover { opacity: 0.8; }

    &.active {
        opacity: 1;
        border: 1px solid var(--metric-color);
        background: color-mix(in srgb, var(--metric-color) 12%, var(--bg));
    }

    & .metric-dot {
        display: inline-block;
        flex-shrink: 0;
        border-radius: 50%;
        height: 8px; width: 8px;
        /* color: var(--metric-color); */
        background: var(--metric-color);
    }
    }

    #hero-chart-title {
    color: var(--metric-color);
    }
    #hero-chart-recent-val {
    font-size: var(--font-size-xxl);
    }
    #hero-chart-delta {
    padding: 0 var(--space-xs);
    font-size: var(--font-size-xs);
    background: var(--bg);
    border-radius: 2.5rem;
    }
    #hero-chart-delta[data-trend="up"] {
        background: color-mix(in oklab, var(--clr-success) 15%, var(--surface-1));
        color: var(--clr-success);
    }
    #hero-chart-delta[data-trend="down"] {
        background: color-mix(in oklab, var(--clr-error) 15%, var(--surface-1));
        color: var(--clr-error);
    }

    [data-metric="all"]                    { --metric-color: var(--accent-subtle); }
    [data-metric="weight"]                 { --metric-color: #59aaf8; }
    [data-metric="steps"]                  { --metric-color: #55c483; }
    [data-metric="calories"]               { --metric-color: #ed9c55; }
    [data-metric="sleep_duration_minutes"] { --metric-color: #ac89e8; }

    .whole {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
    }

    /* Row with chart selector chips/pills + timeframe buttons */
    .top {
    display: flex;
    justify-content: space-between;
    }

    .hero-card,
    .triple-row > * {
        padding: var(--space-sm);
    }
    .triple-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-sm);

    /* Each box in the row */
    & > * {
        display: flex;
        flex-direction: column;
    }
    & .triple-row-chart { flex: 1; /* takes remaining vertical space */}
    }
    .hero-card {
    display: flex;
    flex-direction: column;
    border: 1px solid color-mix(in srgb, var(--metric-color) 30%, rgb(35,42,53));
    border-radius: var(--border-radius);
    background: linear-gradient(color-mix(in srgb, var(--metric-color) 9%, rgb(22, 27, 34)), rgb(20, 25, 31));

    & .hero-top {
        display: flex;
        justify-content: space-between;
    }
    }

</style>