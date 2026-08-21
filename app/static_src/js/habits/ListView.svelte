<script lang="ts">
    import { todayUser } from '../shared/datetime';
    import type { HabitOverviewItemRead } from '../apiTypes';
    import { habitsState, postCompletionValue, toggleEntry } from './habitsState.svelte';
    import { tip } from '../shared/ui/tooltip';
    import { targetDesc } from './utils';

    // TODO(svelte):
    // 1. Add some way to edit habits, and delete.
    // 2. Fix "on pace"
    // 4. Implement "self-increasing" habits (ie auto-increments values per-some-time-period)
    //     ex: Set initially for 30min/day target, and after a few weeks that rises to 35, etc
    // 5. Completing habits / posts seem to emit a LOT of queries, see what we can prune

    let {
        onselect,
        onOpenMenu,
    }: {
        onselect: (id: number) => void;
        onOpenMenu: (id: number, x: number, y: number) => void;
    } = $props();

    function satisfiedOn(h: HabitOverviewItemRead, date: string) {
        return h.data.some((e) => e.entry_date === date && e.satisfied);
    }

    function intendedOn(h: HabitOverviewItemRead, date: string) {
        // frequency mode has no intended days: every day counts
        return h.week_intended === null || h.week_intended.includes(date);
    }

    function weekHits(h: HabitOverviewItemRead) {
        // ct of intended weekDates up to today where satisfiedOn(h, date)
        return weekDates.filter((x) => {
            const s = x.toString();
            return s <= todayStr && intendedOn(h, s) && satisfiedOn(h, s);
        }).length;
    }
    // Pace: actual / expected by now
    // weekly_frequency * days_elapsed / 7
    // for each habit?
    const sumWeekHits = $derived(habitsState.habits.reduce((sum, h) => sum + weekHits(h), 0));
    const expected = $derived(
        habitsState.habits.reduce(
            (sum, h) =>
                sum +
                (h.week_intended !== null
                    ? h.week_intended.filter((d) => d <= todayStr).length
                    : ((h.weekly_frequency ?? 0) * today.dayOfWeek) / 7),
            0,
        ),
    );
    // Actual / expected, expressed as a pct value
    const pace = $derived(expected > 0 ? (sumWeekHits / expected) * 100 : 0);

    const remainingToday = $derived(
        habitsState.habits.filter((h) => !satisfiedOn(h, todayStr)).length,
    );

    // For duration Hbitduration stuff
    let editing = $state<{ id: number; date: string } | null>(null);
    let draft = $state('');

    function beginEdit(h: HabitOverviewItemRead, date: string) {
        draft = String(readValue(h, date) ?? 0);
        editing = { id: h.id, date };
    }

    function focusAndSelect(node: HTMLInputElement) {
        node.focus();
        node.select();
    }
    function commit() {
        if (editing === null) return;
        const h = habitsState.habits.find((d) => d.id === editing?.id);
        const n = Number(draft);
        if (h && Number.isFinite(n) && n >= 0) {
            postCompletionValue(editing.id, editing.date, Math.round(n));
        }
        editing = null;
    }

    function weekCells(h: HabitOverviewItemRead) {
        return weekDates.map((wd) => {
            const dateStr = wd.toString();
            return {
                date: dateStr,
                value: h.data.find((x) => x.entry_date === dateStr)?.value ?? null,
            };
        });
    }

    function readValue(h: HabitOverviewItemRead, date: string) {
        const entry = h.data.find((e) => e.entry_date === date);
        return entry != null ? entry.value : undefined;
    }

    function isEditing(h: HabitOverviewItemRead, date: string) {
        return editing !== null && editing.id === h.id && editing.date === date;
    }

    const DAY_INITIALS = 'MTWTFSS';
    const today = todayUser();
    const todayStr = today.toString();
    const monday = today.subtract({ days: today.dayOfWeek - 1 });
    const weekDates = Array.from({ length: 7 }, (_, i) => monday.add({ days: i }));
</script>

{#snippet binaryCell(h: HabitOverviewItemRead)}
    {@const done = satisfiedOn(h, todayStr)}
    <span class="today-log">
        <input type="checkbox" checked={done} onchange={() => toggleEntry(h.id, todayStr)} />
        <span class="log-value" class:satisfied={done}>{done ? 'Done' : 'Not yet'}</span>
    </span>
{/snippet}

{#snippet numValCell(h: HabitOverviewItemRead, step: number)}
    <span class="today-log">
        <button
            class="step-btn"
            onclick={() =>
                postCompletionValue(
                    h.id,
                    todayStr,
                    Math.max(0, (readValue(h, todayStr) ?? 0) - step),
                )}>-{step}</button>

        <span class="log-value" class:satisfied={satisfiedOn(h, todayStr)}>
            {#if isEditing(h, todayStr)}
                {@render editInput()}
            {:else}
                <button class="value-btn" onclick={() => beginEdit(h, todayStr)}>
                    {readValue(h, todayStr) ?? 0}
                </button>
            {/if}/{h.target?.threshold}
        </span>
        <button
            class="step-btn"
            onclick={() =>
                postCompletionValue(h.id, todayStr, (readValue(h, todayStr) ?? 0) + step)}
            >+{step}</button>
    </span>
{/snippet}

{#snippet editInput()}
    <input
        type="text"
        class="value-input"
        inputmode="numeric"
        bind:value={draft}
        use:focusAndSelect
        onblur={commit}
        onkeydown={(e) => {
            if (e.key === 'Enter') commit();
            if (e.key === 'Escape') editing = null;
        }} />
{/snippet}

<section>
    <div class="summary-bar">
        <div><span class="count">{remainingToday}</span> remaining today</div>
        <div class="pace">
            <span
                class="label"
                use:tip={'Satisfied days this week versus expected by today, across all habits'}
                >On pace:</span>
            <span class="pct">{pace.toFixed(0)}%</span>
            <span class="meter-cell">
                <span class="meter">
                    <span class="meter-fill" style:width="{Math.min(100, pace)}%"></span></span>
            </span>
        </div>
    </div>

    <ul class="habit-grid">
        <div class="row">
            <span class="secondary">Habit</span>
            {#each weekDates as wd (wd.day)}
                <span class="secondary day-label">{DAY_INITIALS[wd.dayOfWeek - 1]} {wd.day}</span>
            {/each}
            <span
                class="secondary"
                use:tip={'Number of completions this calendar week out of the target frequency'}
                >Week</span>
            <span
                class="secondary"
                use:tip={"Satisfied days over the last 4 complete weeks vs. your target. This week doesn't count yet."}
                >Consistency</span>
        </div>

        {#each habitsState.habits as d (d.id)}
            <li
                class="row"
                oncontextmenu={(e) => {
                    e.preventDefault();
                    onOpenMenu(d.id, e.clientX, e.clientY);
                }}>
                <span class="name-and-desc">
                    <button type="button" onclick={() => onselect(d.id)}>{d.name}</button>
                    {#if d.type !== 'binary'}
                        <span class="secondary">{targetDesc(d)}</span>
                    {/if}
                </span>

                {#each weekCells(d) as cell}
                    {#if cell.date === todayStr}
                        {#if d.type === 'binary'}
                            {@render binaryCell(d)}
                        {:else if d.type === 'duration'}
                            {@render numValCell(d, 5)}
                        {:else}
                            {@render numValCell(d, 1)}
                        {/if}
                    {:else if cell.date > todayStr}
                        <span class="day-cell future"></span>
                    {:else if d.type === 'binary'}
                        <button
                            class="day-cell"
                            class:satisfied={satisfiedOn(d, cell.date)}
                            class:unintended={!intendedOn(d, cell.date)}
                            onclick={() => toggleEntry(d.id, cell.date)}>
                            {satisfiedOn(d, cell.date) ? '✓' : ''}
                        </button>
                    {:else if isEditing(d, cell.date)}
                        {@render editInput()}
                    {:else}
                        {@const fraction = Math.min(
                            Number(cell.value ?? 0) / (d.target?.threshold ?? Infinity),
                            1,
                        )}
                        <button
                            class="day-cell"
                            class:satisfied={satisfiedOn(d, cell.date)}
                            class:partial={!satisfiedOn(d, cell.date) &&
                                Number(cell.value ?? 0) > 0}
                            class:unintended={!intendedOn(d, cell.date)}
                            style:--fill="{Math.round(fraction * 100)}%"
                            onclick={() => beginEdit(d, cell.date)}>
                            {cell.value?.toFixed(0) ?? ''}
                        </button>
                    {/if}
                {/each}
                <span>
                    {weekHits(d)}/{d.week_intended?.length ?? d.weekly_frequency}
                </span>
                <!-- TODO: consistency requires backend changes, stubbing for now here -->
                <span class="meter-cell">
                    {#if d.consistency}
                        <span class="meter"
                            ><span class="meter-fill" style:width="{d.consistency}%"></span></span>
                        {d.consistency}%
                    {/if}
                </span>
            </li>
        {/each}
    </ul>
</section>

<style>
    .summary-bar {
        display: flex;
        justify-content: space-between;
    }
    .habit-grid {
        display: grid;
        grid-template-columns: 1fr repeat(8, auto) auto;
        gap: var(--space-sm);
    }
    .name-and-desc {
        display: flex;
        flex-direction: column;

        & > button {
            text-align: left;
        }
    }
    .row {
        grid-column: 1 / -1;
        display: grid;
        grid-template-columns: subgrid;
        align-items: center;
    }
    .row + .row {
        border-top: var(--border-default);
    }

    .value-input {
        background: none;
        width: 4ch;
        text-align: right;
    }

    .meter-cell {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    .meter {
        display: inline-block;
        background: var(--bg-light);
        overflow: hidden;
        border-radius: var(--border-radius);
        width: 80%;
        height: 10px;
    }
    .meter-fill {
        display: block;
        background: var(--accent-strong);
        height: 100%;
    }

    .pace {
        padding: var(--space-sm);
        display: grid;
        grid-template-areas:
            'label pct'
            'bar bar';

        & .label {
            grid-area: label;
        }
        & .pct {
            grid-area: pct;
        }
        & .meter-cell {
            grid-area: bar;
        }
    }

    .count {
        color: var(--accent-strong);
        font-size: 2rem;
    }

    .day-label {
        justify-self: center;
    }
    .day-cell {
        display: grid;
        place-items: center;
        justify-self: center;
        width: 26px;
        height: 26px;
        border: none;
        background: var(--bg-light);
        border-radius: var(--border-radius);

        &.partial {
            color: var(--text-inverse);
            background: linear-gradient(
                to top,
                color-mix(in srgb, var(--clr-success) 45%, var(--bg-light)) var(--fill),
                var(--bg) var(--fill)
            );
        }
        &.satisfied {
            background: var(--clr-success);
            color: var(--text-inverse);
        }
        &.future {
            background: none;
            border: 1px dashed var(--line-strong);
            cursor: default;
        }
        &.unintended {
            opacity: 0.35;
        }
    }
    .log-value.satisfied {
        color: var(--clr-success);
    }

    .today-log {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-sm);
        border: 1px solid var(--line-strong);
        border-radius: var(--border-radius-mild);
        padding: var(--space-sm) var(--space-sm);

        & > button {
            display: grid;
            place-items: center;
            width: 24px;
            height: 24px;
            padding: 0;
            background: none;
            border: 1px solid var(--line-strong);
            border-radius: var(--border-radius);
        }
    }

    .value-btn {
        background: none;
        border: none;
        padding: 0;
        font: inherit;
        color: inherit;
        cursor: text;
    }
    input[type='checkbox'] {
        accent-color: var(--clr-success);
    }
</style>
