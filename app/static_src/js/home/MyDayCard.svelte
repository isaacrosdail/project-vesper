
<script lang="ts">
    import ProgressBar from '../shared/components/ProgressBar.svelte';
    import { tasksState, toggleTask, refreshTasks } from '../tasks/tasksState.svelte';
    import Dropdown from '../shared/components/Dropdown.svelte';


    let { openTimeEntryForm, openMetricsForm }: {
        openTimeEntryForm: any;
        openMetricsForm: any;
    } = $props();

    const actions: Record<string, () => void> = {
        time_entries: openTimeEntryForm,
        daily_metrics: openMetricsForm,
    }

    refreshTasks();

    let todayFrog = $derived(tasksState.tasks.find(t => t.priority === 'frog' && t.due_datetime === null))
    let completed = $derived(tasksState.tasks.reduce((acc, t) => acc + Number(t.is_done), 0));
</script>

<section id="my-day-card" class="card-dashboard surface grid-2col">
    <div class="card-title">
        <h2>My Day</h2>
        <Dropdown label="Quick Add" opts={[['Time Entry', 'time_entries'], ['Metric Entry', 'daily_metrics']]}
            onSelect={(value) => actions[value]?.()} />
    </div>

    <div class="tasks-section">
        {#if todayFrog}
        <div class="highlight-item">
            <span>Today's Frog: </span>
            <span class="highlight-label">
                {todayFrog.name}
            </span>
        </div>
        {/if}
        <ul class="item-list">
        {#each tasksState.tasks as t (t.id)}
            <li class="item" class:completed={t.is_done}>
                <div class="item-row">
                    <input type="checkbox" class="task-checkbox"
                    checked={t.is_done}
                    onchange={() => toggleTask(t) }>
                    <span class="item-title">{t.name}</span>
                </div>
            </li>
        {/each}
        </ul>
    </div>

    <ProgressBar label="Today:" completed={completed} total={tasksState.tasks.length}/>
</section>

<style>
    /* Vertical stack for frog + task list */
    .tasks-section {
        display: grid;
        gap: var(--space-sm);
    }
    /* Styling for text of today's frog to subtly emphasize them */
    .highlight-label { 
        font-weight: var(--font-weight-semibold);
    }

    /* Accent 'card' to highlight priority items (accent lborder + bg-light) used for today's frog */
    .highlight-item {
        padding: var(--space-xs);
        padding-left: var(--space-sm);
        background: var(--surface-1);
        border-left: 4px solid var(--accent-subtle);
        border-radius: calc(0.8 * var(--border-radius));
    }
</style>
