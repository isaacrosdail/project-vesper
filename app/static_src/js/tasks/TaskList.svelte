<script lang="ts">
    import { sortByField } from '../shared/tables';
    import type { PriorityEnum, TaskRead } from '../apiTypes';
    import { fmtDate, todayUser, userDay } from '../shared/datetime';
    import { editTaskIndex, subtasksOf, tasksState, toggleTask } from './tasksState.svelte';
    import Dropdown from '../shared/components/Dropdown.svelte';
    import { SvelteSet } from 'svelte/reactivity';

    // TODO(svelte):
    // 1. Add styling for subtasks expanding container thing
    // 2. Remove sort by priority? Since we can alter filter by priority?
    // 3. Styling/structure for subtasks (when we click the dropdown ofc)

    let {
        onOpenDetails,
        onOpenMenu,
    }: {
        onOpenDetails: (id: number) => void;
        onOpenMenu: (id: number, x: number, y: number) => void;
    } = $props();

    type Filter = 'all' | 'today' | 'upcoming';
    type TaskListState = {
        filter: Filter;
        priority: PriorityEnum | 'all';
        sort: 'manual' | 'due_datetime' | 'priority' | 'name';
        order: 'asc' | 'desc';
        showCompleted: boolean;
    };
    let controls: TaskListState = $state({
        filter: 'all',
        priority: 'all',
        sort: 'manual',
        order: 'asc',
        showCompleted: false,
    });

    type DueStatus =
        | { kind: 'overdue'; days: number }
        | { kind: 'due-today' }
        | { kind: 'due-soon'; days: number }
        | { kind: 'later' }
        | { kind: 'undated' };

    function dueStatus(t: TaskRead): DueStatus {
        if (!t.due_datetime) return { kind: 'undated' };
        const daysLeft = todayUser().until(userDay(t.due_datetime)).days;
        if (daysLeft === 0) return { kind: 'due-today' };
        if (daysLeft < 0) return { kind: 'overdue', days: -1 * daysLeft };
        if (daysLeft <= 5) return { kind: 'due-soon', days: daysLeft };
        return { kind: 'later' };
    }
    function urgencyOf(due: DueStatus): number {
        switch (due.kind) {
            case 'overdue':
            case 'due-today':
                return 1;
            case 'due-soon':
                return 1 - due.days / 5;
            default:
                return 0;
        }
    }

    // Filter by today vs upcoming, priority, then sort?
    const tasks = $derived.by(() => {
        const today = todayUser().toString();
        let result = tasksState.tasks;

        if (!controls.showCompleted) {
            result = result.filter((t) => !t.is_done);
        }
        if (controls.filter === 'today') {
            result = result.filter(
                (t) => t.due_datetime && userDay(t.due_datetime).toString() === today,
            );
        } else if (controls.filter === 'upcoming') {
            result = result.filter(
                (t) => t.due_datetime && userDay(t.due_datetime).toString() > today,
            );
        }

        if (controls.priority !== 'all') {
            result = result.filter((t) => t.priority === controls.priority);
        }

        if (controls.sort === 'manual') {
            result = result.toSorted((a, b) =>
                a.sort_key < b.sort_key ? -1 : a.sort_key > b.sort_key ? 1 : 0,
            );
        } else {
            result = sortByField(result, controls.sort, controls.order);
        }
        return result;
    });

    type Edge = 'above' | 'below' | null;
    type DragState = { draggedId: number | null; targetId: number | null; edge: Edge };
    let dragState: DragState = $state({ draggedId: null, targetId: null, edge: null });

    const resetDragState = () => {
        dragState.draggedId = null;
        dragState.targetId = null;
        dragState.edge = null;
    };

    async function moveTask(did: number, tid: number, edg: Edge) {
        if (controls.sort !== 'manual') return;

        const keyof = (id: number | null) => tasks.find((t) => t.id === id)?.sort_key ?? null;
        let prevIdx, prev;
        let nextIdx, next;
        if (edg === 'above') {
            // put did before tid in both arr and sort key?
            prevIdx = tasks.findIndex((t) => t.id === tid) - 1;
            prev = tasks[prevIdx]?.sort_key ?? null;
            next = keyof(tid);
        } else {
            nextIdx = tasks.findIndex((t) => t.id === tid) + 1;
            next = tasks[nextIdx]?.sort_key ?? null;
            prev = keyof(tid);
        }
        await editTaskIndex(did, prev, next);
    }
    type PriorityFilters = PriorityEnum | 'all';
    const PRIORITIES = [
        'all',
        'low',
        'medium',
        'high',
        'frog',
    ] as const satisfies PriorityFilters[];
    type DateFilters = 'all' | 'today' | 'upcoming';
    const DATE_FILTERS = ['all', 'today', 'upcoming'] as const satisfies DateFilters[];

    // TODO: clean this mechanism up?
    // For clicking the chevron to expand/collapse subtasks
    let expanded = new SvelteSet<number>();
    function toggleSubtasks(id: number) {
        if (expanded.has(id)) expanded.delete(id);
        else expanded.add(id);
    }

    function cyclePriority() {
        const idx = PRIORITIES.indexOf(controls.priority);
        const next = PRIORITIES[(idx + 1) % PRIORITIES.length]!;
        controls.priority = next;
    }
</script>

<section id="tasks-dashboard-list-view">
    <div class="task-list-controls">
        <div class="controls-left">
            <h2 class="header">Active Tasks <span class="secondary">{tasks.length}</span></h2>
        </div>
        <div class="controls-right">
            <div class="filter-group">
                {#each DATE_FILTERS as f (f)}
                    <button
                        class:active={controls.filter === f}
                        onclick={() => (controls.filter = f)}>{f}</button>
                {/each}
            </div>
            <button class="btn" onclick={cyclePriority}>
                <svg class="icon"
                    ><use
                        href={controls.priority === 'all'
                            ? '#icon-funnel'
                            : `#badge-priority-${controls.priority}`}></use
                    ></svg>
                <span class="secondary">Priority</span>
            </button>
            <Dropdown
                opts={[
                    ['Manual', 'manual'],
                    ['Due Date', 'due_datetime'],
                    ['Priority', 'priority'],
                    ['Name', 'name'],
                ]}
                label="Sort By"
                onSelect={(v) => (controls.sort = v)} />
            <button
                class="sort-order-toggle"
                disabled={controls.sort === 'manual'}
                class:flip={controls.order === 'asc'}
                aria-label="Toggle sort order"
                onclick={() => (controls.order = controls.order === 'asc' ? 'desc' : 'asc')}>
                <svg class="icon"><use href="#icon-chevron"></use></svg>
            </button>
            <label class="toggle-group secondary" for="show-completed">
                <input
                    type="checkbox"
                    class="toggle-input"
                    id="show-completed"
                    bind:checked={controls.showCompleted} />
                <span class="toggle"></span>
                Completed
            </label>
        </div>
    </div>

    <ul class="task-list" class:sortable={controls.sort === 'manual'}>
        {#each tasks as t (t.id)}
            {@const due = dueStatus(t)}
            <li
                class="task {due.kind}"
                style:--urgency={urgencyOf(due)}
                class:drop-above={t.id === dragState.targetId && dragState.edge === 'above'}
                class:drop-below={t.id === dragState.targetId && dragState.edge === 'below'}
                draggable={t.id === dragState.draggedId}
                ondragstart={(e) => e.dataTransfer?.setData('text/plain', String(t.id))}
                ondragover={(e) => {
                    e.preventDefault();
                    const r = e.currentTarget.getBoundingClientRect();
                    dragState.targetId = t.id;
                    dragState.edge = e.clientY < r.top + r.height / 2 ? 'above' : 'below';
                }}
                ondragend={resetDragState}
                ondrop={() => {
                    if (dragState.draggedId !== null && dragState.targetId !== null) {
                        moveTask(dragState.draggedId, dragState.targetId, dragState.edge);
                    }
                    resetDragState();
                }}
                oncontextmenu={(e) => {
                    e.preventDefault();
                    onOpenMenu(t.id, e.clientX, e.clientY);
                }}>
                <div class="task__gutter">
                    <button
                        class="task__drag-handle"
                        aria-label="Reorder {t.name}"
                        onmousedown={() => (dragState.draggedId = t.id)}>
                        <svg class="icon"><use href="#icon-drag-handle"></use></svg>
                    </button>
                    {#if t.subtasks.length}
                        <button
                            aria-label="Expand subtasks of {t.name}"
                            aria-expanded={expanded.has(t.id)}
                            class="task__expander"
                            onclick={() => toggleSubtasks(t.id)}>
                            <svg class="icon expand-chevron" class:open={expanded.has(t.id)}
                                ><use href="#icon-chevron"></use></svg>
                        </button>
                    {/if}
                </div>
                <div class="task__main">
                    <input
                        type="checkbox"
                        class="task__done-toggle"
                        checked={t.is_done}
                        onchange={() => toggleTask(t)} />
                    <span>
                        <svg class="icon"><use href="#badge-priority-{t.priority}"></use></svg>
                    </span>
                    <button onclick={() => onOpenDetails(t.id)} class="task__name">
                        {t.name}
                    </button>
                </div>
                <div class="task__meta">
                    <span class="task__due-date">
                        <!-- TODO: Ensure applying color urgency to icon, span text, & left border -->
                        {#if t.due_datetime}
                            <svg class="icon"><use href="#icon-calendar"></use></svg>
                            <span class="due_datetime">{fmtDate(t.due_datetime)}</span>
                            {#if due.kind === 'overdue'}<span>- {due.days}d late</span>
                            {:else if due.kind === 'due-today'}<span>- due today</span>
                            {:else if due.kind === 'due-soon'}<span>- in {due.days}d</span>
                            {/if}
                        {/if}
                    </span>
                    {#if t.subtasks.length}
                        <span class="task__subtask-count">
                            <span>
                                <svg
                                    class="icon"
                                    class:checked={subtasksOf(t).every((st) => st.is_done)}
                                    ><use href="#icon-checklist"></use></svg>
                            </span>
                            <span
                                >{subtasksOf(t).filter((st) => st.is_done).length}/{t.subtasks
                                    .length}</span>
                        </span>
                    {/if}

                    <span class="task__pillars">
                        {#each t.pillars as p (p.id)}<span>{p.name}</span>{/each}
                    </span>
                </div>
                <div hidden={!expanded.has(t.id)}>
                    {#if t.subtasks.length}
                        {#each subtasksOf(t) as st (st.id)}
                            <div>{st.name}</div>
                        {/each}
                    {/if}
                </div>
            </li>
        {:else}
            <div>No entries yet</div>
        {/each}
    </ul>
</section>

<style>
    .expand-chevron {
        transform: rotate(-90deg);

        &.open {
            transform: rotate(0deg);
        }
    }
    .filter-group {
        display: flex;
        padding: 3px;
        background: var(--bg);
        border: 1px solid var(--line);
        border-radius: var(--border-radius);
        gap: var(--space-xs);

        & button {
            padding: 0.15rem 0.75rem;
            border: none;
            background: transparent;
            color: var(--text-muted);
            border-radius: var(--border-radius);
            text-transform: capitalize;

            &:hover {
                background: var(--surface-3);
            }
            &.active {
                background: var(--surface-3);
                color: var(--text);
            }
        }
    }

    /* TODO(style): fix these up to look uniform */
    .sort-order-toggle {
        background: var(--surface-1);
        border: var(--border-default);
        border-radius: var(--border-radius);

        & svg {
            transition: transform 120ms ease;
        }

        &.flip svg {
            transform: rotate(180deg);
        }
    }

    .task-list-controls {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-sm);
        margin-bottom: var(--space-sm);
        font-size: var(--font-size-sm);

        & .controls-right {
            display: flex;
            align-items: stretch;
            gap: var(--space-sm);

            & > * {
                height: 2rem;
                border: var(--border-default);
                border-radius: var(--border-radius);
                background: var(--surface-1);
            }
        }

        & .controls-right > button:hover {
            background: var(--surface-3);
        }
    }

    /* TODO: Sketching conversion for tasks from table to ul */
    .task-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
    }

    /* Disallow drag-n-drop when 'sortable' class is active */
    .task-list:not(.sortable) .task__drag-handle {
        cursor: default;
        opacity: 0;
    }
    /* Have completed tasks recede visually */
    .task:has(input:checked) {
        & .task__name {
            text-decoration: line-through;
            opacity: 0.5;
        }
        & input:checked {
            opacity: 0.5;
        }
    }

    .task {
        position: relative;
        display: grid;
        grid-template-columns: [gutter] 3rem [content] 1fr;
        padding: var(--space-xs);
        border: var(--border-default);

        background: var(--surface-1);
        border-left: 2px solid var(--due-clr);
        border-radius: var(--border-radius);
        cursor: pointer;

        &:hover {
            background: var(--surface-3);
        }

        /* Stretched link pattern?
            Instead of onclick on entire li (bc a11y), make task name
            a button, then stretch it s.t. entire li is still clickable
            also means no "if click not on checkbox or..." checks needed?        
        */
        & .task__name::after {
            content: '';
            position: absolute;
            inset: 0; /* covers entire li? */
        }
        /* Overlay sits on top of checkbox, expander, etc, eating their clicks
            lift them back above it:
        */
        & .task__done-toggle,
        & .task__expander,
        & .task__drag-handle {
            position: relative;
            z-index: 1;
        }

        /* --due-clr is set per li el;
            due-soon goes yellow->orange,
            due-today is orangeish,
            overdue is full red
        */
        --due-clr: var(--text-muted);
        &.due-soon,
        &.overdue,
        &.due-today {
            --due-clr: oklch(0.65 0.17 calc(85 - var(--urgency) * 60));
        }

        & .task__main,
        & .task__meta {
            grid-column: content;
        }

        & .task__subtask-count {
            display: inline-flex;
            align-items: center;
            gap: var(--space-xs);

            & .checked {
                color: var(--clr-success);
            }
        }

        /* Gutter: fixed lane so rows never jitter, opacity fades in on hover/focus */
        & .task__gutter {
            grid-column: gutter;
            grid-row: 1; /* aligns with .task__main row, not full height? */
            display: flex;
            gap: var(--space-xs);
            opacity: 0;
            transition: opacity 120ms ease;
        }
        &:hover .task__gutter,
        &:focus-within .task__gutter {
            opacity: 1;
        }
        & .task__gutter > button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.75rem;
            height: 1.75rem;
            padding: 0;
            gap: var(--space-sm);
            background: transparent;
            border: none;
            border-radius: var(--border-radius);
            color: var(--text-muted);

            &:hover {
                background: var(--surface-3);
            }
        }

        & .task__main {
            display: flex;
            align-items: center;
            gap: var(--space-sm);
        }

        & .task__due-date {
            /* grid-column: 1; */
            display: flex;
            align-items: center;
            gap: var(--space-xs);
            color: var(--due-clr);
        }
        & .task__meta {
            display: flex;
            gap: var(--space-sm);
            align-items: center;
            font-size: var(--font-size-sm);
            color: var(--text-muted);

            & .task__pillars {
                /* grid-column: 2; */
                display: inline-flex;
                gap: var(--space-xs);
            }

            & .task__pillars > span {
                padding: 0.1em 0.6em;
                background: var(--surface-3); /* TODO: finalize color */
                border-radius: var(--border-radius);
                font-size: var(--font-size-sm);
            }
        }
    }

    .task.drop-above {
        border-top: 3px solid var(--accent-subtle);
        margin-top: -1px;
        box-shadow: 0 -3px 0 0 var(--accent-subtle);
    }
    .task.drop-below {
        border-bottom: 3px solid var(--accent-subtle);
        margin-bottom: -1px;
        box-shadow: 0 3px 0 0 var(--accent-subtle);
    }
</style>
