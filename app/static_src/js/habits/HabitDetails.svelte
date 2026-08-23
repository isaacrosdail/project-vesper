<script lang="ts">
    import { Temporal } from 'temporal-polyfill';
    import type { HabitDayRead, HabitOverviewItemRead } from '../apiTypes';
    import { fmtDate, fmtDateTime, nowUser, todayUser } from '../shared/datetime';
    import { api } from '../shared/services/api';
    import { habitsState } from './habitsState.svelte';
    import type { HeatmapApiEntry } from './heatmap';
    import Heatmap from './Heatmap.svelte';
    import { asUserDT } from '../shared/datetime';
    import { targetDesc } from './utils';
    import StatsTile from '../shared/components/StatsTile.svelte';

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

    const { data: stats } = await api.habits.stats(habitId);
    let heatmapData = $state<HeatmapApiEntry[] | null>(null);
    await api.habitCompletions
        .heatmap(new URLSearchParams({ habit_id: String(habitId) }))
        .then(({ data }) => {
            heatmapData = data;
        });

    const { data: habitCompletionData } = await api.habitCompletions.get(habitId, {
        start: habit.start_date, // TODO: backend fulfills this in service
        end: todayUser().add({ days: 1 }).toString(),
    });
    const daysSatisfied = $derived(
        habitCompletionData.reduce((sum, d) => (d.satisfied ? (sum += 1) : sum), 0),
    );
    const numDone = $derived(
        habitCompletionData.reduce((sum, d) => (d.value ? sum + d.value : sum), 0),
    );
    const rhythm = $derived.by(() => {
        const counts = Array(7).fill(0);
        for (const c of habitCompletionData) {
            if (c.satisfied) counts[Temporal.PlainDate.from(c.entry_date).dayOfWeek - 1]++;
        }
        return counts;
    });
    const rhythmMax = $derived(Math.max(...rhythm));

    const bestSingleDay = $derived(
        habitCompletionData.reduce<HabitDayRead | null>(
            (best, d) => ((best?.value ?? 0) > (d?.value ?? 0) ? best : d),
            null,
        ),
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
        <span>Streak: {habit.streak_count} {map[habit.schedule_type]}</span>

        <div class="stats">
            <p>TODO: add? -> consistency trend</p>

            <StatsTile
                label="Best Streak"
                value={stats.best_streak}
                detail={map[habit.schedule_type]} />
            <StatsTile label="Days completed" value={daysSatisfied} />
            {#if habit.type !== 'binary'}
                {@const units = habit.type === 'numeric_value' ? habit.units : 'mins'}
                <StatsTile label="Total" value={numDone} detail={units} />
                {#if bestSingleDay}
                    <StatsTile label="Best" value={bestSingleDay.value} detail={units} />
                {/if}
            {/if}
            <!-- days where there are NO completions whatsoever OR where target wasn't satisfied? -->
            <StatsTile label="Days missed" value={stats.days_missed} />

            <!-- Weekday rhythm: count completions by isoweekday, render as 7 tiny bars -->
            <div class="rhythm-cells">
                {#each rhythm as n, i}
                    <span class="rhythm-cell">
                        <span class="rhythm">
                            <span
                                class="rhythm-fill"
                                style:height="{rhythmMax ? (n / rhythmMax) * 100 : 0}%"></span>
                        </span>
                        <span>{'MTWTFSS'[i]}</span>
                    </span>
                {/each}
            </div>
        </div>

        <div class="heatmap-group">
            Completion Activity
            <Heatmap data={heatmapData} />
        </div>
    </section>
{:else if view === 'about'}
    <section>
        <h2>Info</h2>
        <p>Created at: {fmtDateTime(habit.created_at)} ({daysRange}d ago)</p>

        <p>Start date: {fmtDate(habit.start_date)}</p>
        {#if habit.end_date}
            <p>End date: {fmtDate(habit.end_date)}</p>
        {/if}
    </section>
{/if}

<style>
    .rhythm-cells {
        display: flex;
    }
    .rhythm-cell {
        height: 40px;
        width: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .rhythm {
        flex: 1;
        display: flex;
        align-items: flex-end;
        align-self: stretch;
        background: var(--surface-3);
        border-radius: var(--border-radius);
    }
    .rhythm-fill {
        width: 100%;
        background: var(--clr-success);
    }

    /* TODO: WIP display, maybe should use statstiles once dust settles? */
    .stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--space-sm);
    }

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
