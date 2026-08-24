
<script lang="ts">
    import StatTile from '../shared/components/StatsTile.svelte';
    import PaginatedTable from '../shared/components/PaginatedTable.svelte';
    import { fmtDate, fmtTime, todayUser } from '../shared/datetime';
    import { hourMinsDisplay } from '../shared/formatters';
    import type { TimeEntryRead } from '../apiTypes';
    import TimeEntryForm from './TimeEntryForm.svelte';
    import { api } from '../shared/services/api';
    import * as d3 from 'd3';
    import { Temporal } from 'temporal-polyfill';
    import { TimeEntriesChart } from './chart';
    import type { PieDatum } from './chart';
    import { openContextMenu } from '../shared/components/ContextMenu.svelte';
    import { sortByField } from '../shared/tables';
    import { askConfirm } from '../shared/components/ConfirmDialog.svelte';

    let timeEntryForm: TimeEntryForm;
    let chart: TimeEntriesChart;

    $effect(() => {
        chart ??= new TimeEntriesChart('#time_tracking-chart-container');
        chart.updatePieChart(pieData);
    })

    // Pro tips:
    // 1. Write every aggregate asking "What does this return for [] (empty input)?"
    // 2. Normalize once, at the boundary
    // 3. Two states (timeframe, raw) everything else derived
    // 4. Positional data gets one line to live: destructure unnamed tuples STAT
    // 5. Keep math ignorant of delivery
    // 6. Aggregate with named verbs, not loops
    // 7. Filter before you aggregate (remember: reduction before computation!)
    //     Data should shrink before the next does arithmetic
    // 8. Embrace types as always

    const config = {
        cols: [
            { label: 'Date', key: 'started_at', fmt: (r) => fmtDate(r.started_at) },
            { label: 'Category', key: 'category' },
            { label: 'Time', key: 'started_at', fmt: (r) => `${fmtTime(r.started_at)} - ${fmtTime(r.ended_at)}` },
            { label: 'Duration', key: 'duration_minutes', fmt: (r) => hourMinsDisplay(r.duration_minutes) },
            { label: 'Description', key: 'description' },
        ]
    }

    let timeframe = $state(7);
    let raw = $state<TimeEntryRead[]>([]);
    let entries = $derived(raw.map(toStatsShape));
    const cutoff = $derived(todayUser().subtract({ days: timeframe}));
    let currentRaw = $derived(raw.filter(e => e.started_at.split('T')[0] >= cutoff.toString()));

    let currentEntries = $derived(entries.filter(e => e.date >= cutoff.toString()));
    let priorEntries = $derived(entries.filter(e => e.date < cutoff.toString()));

    let sortState = $state({ field: 'started_at', order: 'asc' });
    const sorted = $derived(sortByField(currentRaw, sortState.field, sortState.order));
    const TIMEFRAMES = [
        { label: '7d', value: 7 },
        { label: '30d', value: 30 },
        { label: '90d', value: 90 },
    ]

    async function load() {
        const params = new URLSearchParams({ lastNDays: String(timeframe * 2 )});
        raw = (await api.time_entries.summary(params)).data;
    }
    $effect(() => { load(); });
    $inspect(entries);
    // async function loadRange(range: number) {
    //     const raw = await fetchEntries(range * 2);
    //     const entries = raw.map(toStatsShape);
    //     const cutoff = todayUser().subtract({ days: range });
    //     this.#table.setItems(raw.filter(e => e.started_at.split('T')[0] >= cutoff));

    //     const current = entries.filter(e => e.date >= cutoff);
    //     const prior = entries.filter(e => e.date < cutoff);
    //     renderStats(deriveStatsView(current, prior));
    //     this.#chart.updatePieChart(toPieData(current));

    //     // update label:
    //     const prefix = range === 7 ? 'This week' : `Last ${range} days`;
    //     const header = required(document.querySelector('.page-h2'), '.page-h2');
    //     header.textContent = prefix;
    //     const timeFrameLabel = required(document.querySelector('.timeframe-label'), '.timeframe-label');
    //     timeFrameLabel.textContent = rangeLabel(range);
    // }
    // load();
    type StatsEntry = { date: string; category: string; duration: number };
    function totalsBy(entries: StatsEntry[], keyFn: (e: StatsEntry) => string) {
        const obj: Record<string, number> = {};
        for (const e of entries) {
            const k = keyFn(e);
            obj[k] = (obj[k] ?? 0) + e.duration;
        }
        return obj;
    }

    const totalMinutesCurr = $derived(currentEntries.reduce((acc, e) => acc + e.duration, 0));
    const totalMinutesPrev = $derived(priorEntries.reduce((acc, e) => acc + e.duration, 0));
    const totalsByCategory = $derived(totalsBy(currentEntries, e => e.category));
    const [topCat, topCatMinutes] = $derived(d3.greatest(Object.entries(totalsByCategory), ([, v]) => v) ?? [null,null]);
    const topCategoryLabel = $derived.by(() => {
        if (topCatMinutes == null) return;
        const part1 = hourMinsDisplay(topCatMinutes);
        const pct = Math.round(topCatMinutes / totalMinutesCurr * 100);
        return `${part1} · ${pct}% of time`;
    });
    const daySpan = $derived.by(() => {
        const days = entries.map(e => e.date).toSorted();
        if (days.length === 0) return;
        const first = Temporal.PlainDate.from(days[0]);
        const last = Temporal.PlainDate.from(days[days.length - 1]);
        return first.until(last).days + 1; // inclusive
    });
    const dailyAvg = $derived(daySpan != null ? totalMinutesCurr/ daySpan : null);

    const deltaPct = $derived.by(() => {
        if (totalMinutesPrev === 0) return null;
        return Math.round((totalMinutesCurr - totalMinutesPrev) / totalMinutesPrev * 100);
    });

    const mostActiveDay = $derived(
        d3.greatest(Object.entries(totalsBy(currentEntries, e => e.date)), ([, v]) => v)
    );
    const mostActiveDayView = $derived.by(() => {
        if (!mostActiveDay) return { day: '-', label: '-' };
        const d = Temporal.PlainDate.from(mostActiveDay[0]);
        const day = `${d.toLocaleString(undefined, { weekday: 'short' })}, ${fmtDate(d)}`
        return {
            // day: d.toLocaleString(undefined, { weekday: 'short' }),
            day: day,
            // label: `${hourMinsDisplay(mostActiveDay[1])} logged ${d.toLocaleString(undefined, {
            //     month: 'short', day: 'numeric'
            // })}`,
            label: `${hourMinsDisplay(mostActiveDay[1])} logged`
        };
    });

    const pieData: PieDatum[] = $derived(Object.entries(totalsByCategory).map(([category, value]) => ({ category, value })));
    
    const deleteTimeEntry = async (id: number) => {
        const confirmed = await askConfirm("Are you sure you\'d like to delete this entry?");
        if (!confirmed) return;
        await api.time_entries.delete(String(id));
        await load();
    }

    // function getTimeWindowLabel(entry: TimeEntryRead) {
    //     const start = fmtTime(new Date(entry.started_at));
    //     const end = fmtTime(new Date(entry.ended_at));
    //     return `${start} - ${end}`;
    // }
    export function toStatsShape(t: TimeEntryRead): StatsEntry {
        return {
            date: t.started_at.split('T')[0]!,
            category: t.category,
            duration: t.duration_minutes,
        }
    }

</script>

<TimeEntryForm bind:this={timeEntryForm}/>

<div class="page-header">
    <div>
        <h2 class="page-h2">{timeframe === 7 ? 'This week' : `Last ${timeframe} days`}</h2>
        <div class="timeframe-label secondary">{fmtDate(todayUser().subtract({ days: 5 }))} - {fmtDate(todayUser())}</div>
    </div>
    <!-- TODO -->
    <div class="timeframe-selector surface">
        {#each TIMEFRAMES as tf (tf.label)}
            <button type="button" class:active={timeframe === tf.value}
                onclick={() => timeframe = tf.value}>{tf.label}
            </button>
        {/each}
    </div>
</div>
<div class="stats-row">
    <StatTile label="TOTAL TRACKED" value={hourMinsDisplay(totalMinutesCurr)} detail={deltaPct ? `${deltaPct >= 0 ? "▲" : "▼"} ${Math.abs(deltaPct)}% vs prior period` : ''} />
    <StatTile label="DAILY AVERAGE" value={dailyAvg ? hourMinsDisplay(dailyAvg) : ''} detail={`across ${Object.keys(totalsBy(currentEntries, e => e.date)).length} active days`} />
    <StatTile label="TOP CATEGORY" value={topCat ?? ''} detail={topCategoryLabel} />
    <StatTile label="MOST ACTIVE DAY" value={mostActiveDayView.day} detail={mostActiveDayView.label} />
</div>
<div class="charts-row">
    <div class="chart-categories surface">
        <div class="chart-categories__header">Where your time goes</div>
        <div class="chart" id="time-stats">
        <div id="time_tracking-chart-container"></div>
        {#if !pieData.length}
            <div>No entries in this period.</div>
        {/if}
        </div>
        <!-- // {# TODO(ui): per-category breakdown list (legend + time + %) #} -->
        <div class="breakdown">BREAKDOWN RIGHT</div>
    </div>
    <!-- // {# TODO(ui): daily bar chart - the "OTHER CHART" panel #} -->
    <div class="chart-daily surface">
        OTHER CHART
    </div>
</div>

<template id="time-row-template">
    <tr data-item-id="" data-module="time_tracking" data-subtype="time_entries">
        <td class="date"></td>
        <td class="category"></td>
        <td class="time text-right"></td>
        <td class="duration_minutes text-right"></td>
        <td class="description text-right"></td>
        <td class="table-cell delete-cell">
            <button class="js-table-options row-actions dots-btn btn-icon btn-square" data-item-id="">ui.ellipsis_svg</button>
        </td>
    </tr>
</template>

<section id="time_entries-table-section" class="card-dashboard surface">
    <div class="card-title">
        <h2>Time Entries</h2>
        <button class="btn-icon btn-round btn-primary"
            aria-label="TODO"
            onclick={() => timeEntryForm.open()}>
            <svg class="icon"><use href="#icon-plus"></use></svg>
        </button>
    </div>

    <PaginatedTable items={sorted} pageSize={15} getKey={(r) => r.id}>
        {#snippet header()}
            <tr>
                {#each config.cols as col (col.label)}
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
                    { label: 'Edit', action: () => timeEntryForm.open({ editId: r.id }) },
                    { label: 'Delete', action: () => deleteTimeEntry(r.id) },
                ])
            }}>
                {#each config.cols as col (col.label)}
                    <td>{col.fmt ? col.fmt(r) : r[col.key]}</td>
                {/each}
            </tr>
        {/snippet}
    </PaginatedTable>
</section>


<style>
    .sort-label svg {
        pointer-events: none;
        transition: transform 0.2s ease;

        opacity: 0;
        &.visible { opacity: 1; }
        &.flip { transform: rotate(180deg); }
    }
    .page-header {
        display: flex;
        justify-content: space-between;
    }

    .stats-row {
        display: flex;
        gap: var(--space-sm);
        width: 100%;
        justify-content: space-between;

        & > * {
            padding: var(--space-sm);
        }
    }


    .charts-row {
  display: flex;
  justify-content: space-between;

  & .chart-categories {
    display: grid;
    grid-template-areas:
      "header header"
      "chart breakdown";

    & .chart-categories__header { grid-area: header; }
    & .chart { grid-area: chart; }
    & .breakdown { grid-area: breakdown; }
  }
}
</style>