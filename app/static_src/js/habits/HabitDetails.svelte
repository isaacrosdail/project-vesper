<script lang="ts">
    import { Temporal } from 'temporal-polyfill';
    import type { HabitOverviewItemRead } from '../apiTypes';
    import { fmtDateTime, nowUser, todayUser } from '../shared/datetime';
    import { api } from '../shared/services/api';
    import { habitsState } from './habitsState.svelte';
    import type { HeatmapApiEntry } from './heatmap';
    import Heatmap from './Heatmap.svelte';
    import { asUserDT } from '../shared/datetime';
    import { targetDesc } from './utils';

    // TODO(svelte):
    // 1. Make heatmap cells bigger, and try to sequeeze int he date in the corners
    // so you can see it w/o having to hover.
    // 2. Also constrain the range to like ~month, not the full year?

    let {
        habitId,
        wipeId,
    }: {
        habitId: number;
        wipeId: () => void;
    } = $props();

    let view: 'progress' | 'about' = $state('progress');

    const habit = $derived(habitsState.habits.find((h) => h.id === habitId));
    if (!habit) throw new Error(`habit ${habitId} not in habitsState`);

    let heatmapData = $state<HeatmapApiEntry[] | null>(null);
    await api.habitCompletions
        .heatmap(new URLSearchParams({ habit_id: String(habitId) }))
        .then(({ data }) => {
            heatmapData = data;
        });

    const { data: habitCompletionData } = await api.habitCompletions.get(habitId, {
        start: habit.start_date,
        end: todayUser().add({ days: 1 }).toString(),
    });
    const daysSatisfied = $derived(
        habitCompletionData.reduce((sum, d) => (d.satisfied ? (sum += 1) : sum), 0),
    );
    const numDone = $derived(
        habitCompletionData.reduce((sum, d) => (d.value ? sum + d.value : sum), 0),
    );

    // [created_at, tomorrow)
    const daysRange = nowUser().since(asUserDT(habit.created_at), {
        largestUnit: 'days',
        smallestUnit: 'days',
    }).days;
</script>

<div class="header">
    <button class="btn btn-ghost" onclick={wipeId}>back</button>
    <h2>{habit.name} | {targetDesc(habit)}</h2>
</div>

<div class="view-toggle">
    <button onclick={() => (view = 'progress')} class:active={view === 'progress'}>Progress</button>
    <button onclick={() => (view = 'about')} class:active={view === 'about'}>About</button>
</div>

{#if view === 'progress'}
    {@const map = { frequency: 'weeks', weekly: 'days', monthly: 'months', interval: 'times' }}
    <section>
        <span>Current streak: {habit.streak_count} {map[habit.schedule_type]}</span>

        <div class="heatmap-group">
            Completion Activity
            <Heatmap data={heatmapData} />
        </div>

        <!-- So we have .data as [date, count] -->
        <!-- sum where each day with non-zero count = 1 -->
        <p>Days completed: {daysSatisfied} days</p>
        {#if habit.type !== 'binary'}
            <p>Total: {numDone} {habit.type === 'numeric_value' ? habit.units : 'mins'}</p>
        {/if}
        <!-- days where there are NO completions whatsoever OR where target wasn't satisfied? -->
        <p>Days missed: {habitCompletionData.length - daysSatisfied} days</p>
    </section>
{:else if view === 'about'}
    <section>
        Info
        <span>Created at: {fmtDateTime(habit.created_at)} ({daysRange}d ago)</span>
    </section>
{/if}

<style>
    .header {
        position: relative;
        display: flex;
        justify-content: center;
        & > button {
            position: absolute;
            left: 0;
            top: 50%;
            translate: 0 -50%;
        }
    }

    .heatmap-group {
        grid-area: heatmap;
        overflow-x: scroll;
        overflow-y: hidden;
    }

    /* TODO: Ripped verbatim from tasks dashboard, should centralize this view-toggle styling */
    .view-toggle {
        display: flex;
        align-items: center;
        width: fit-content;
        margin-inline: auto;
    }
    .view-toggle button {
        background: none;
        border: 1px solid transparent;
        border-radius: var(--border-radius-mild);
        padding: 0.15rem 0.75rem;
        font: inherit;
        color: var(--text-muted);
        cursor: pointer;
    }
    .view-toggle button:hover {
        color: var(--text);
    }
    .view-toggle button.active {
        color: var(--accent-strong);
        background: var(--surface-3);
        border-color: var(--line);
    }
    /* the pipe */
    .view-toggle button + button {
        position: relative;
        margin-left: 1.1rem;
    }
    .view-toggle button + button::before {
        content: '';
        position: absolute;
        left: -0.6rem;
        top: 20%;
        bottom: 20%;
        width: 1px;
        background: var(--border-color);
    }
</style>
