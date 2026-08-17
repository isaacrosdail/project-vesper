<script lang="ts">
    import { openContextMenu } from '../shared/components/ContextMenu.svelte';
    import StatsTile from '../shared/components/StatsTile.svelte';
    import TaskDetailsPopover from './TaskDetailsPopover.svelte';
    import TaskForm from './TaskForm.svelte';
    import TaskList from './TaskList.svelte';
    import TaskSearchPopover from './TaskSearchPopover.svelte';
    import { refreshStats, refreshTasks, tasksState, deleteTask } from './tasksState.svelte';
    import { askConfirm } from '../shared/components/ConfirmDialog.svelte';
    import TasksWeb from './TasksWeb.svelte';

    let detailsTaskId = $state<number | null>(null);
    let taskForm: TaskForm;
    let view = $state<'list' | 'web'>('list');

    const editTask = (id: number) => taskForm.open({ editId: id });
    const addSubtask = (id: number) => taskForm.open({ supertaskId: id });
    const handleDelete = async (id: number) => {
        if (!(await askConfirm("Are you sure you'd like to delete this entry?"))) return;
        await deleteTask(id);
        detailsTaskId = null;
    };
    const openTaskMenu = (id: number, x: number, y: number, extra: MenuItem[] = []) =>
        openContextMenu(x, y, [
            { label: 'Edit', action: () => editTask(id) },
            { label: 'Delete', action: () => handleDelete(id) },
            ...extra,
        ]);

    refreshTasks();
    refreshStats();
    export function openAddTask() {
        taskForm.open();
    }
</script>

<TaskForm
    bind:this={taskForm}
    onSuccess={() => {
        refreshTasks();
        refreshStats();
    }} />

<div class="view-toggle">
    <button onclick={() => (view = 'list')} class:active={view === 'list'}>List</button>
    <button onclick={() => (view = 'web')} class:active={view === 'web'}>Web</button>
</div>

{#if view === 'list'}
    {#if tasksState.stats}
        <div class="tiles">
            <StatsTile
                label={`Overdue - last ${tasksState.range} days`}
                tone="bad"
                value={`${tasksState?.stats?.overdue.rate}%`}
                progress={tasksState?.stats?.overdue.rate}
                detail={`${tasksState?.stats?.overdue.count}/${tasksState?.stats?.overdue.total}`} />
            <StatsTile
                label={`Frog Completion (Last ${tasksState.range} days)`}
                value={`${tasksState?.stats?.frog.rate}%`}
                progress={tasksState?.stats?.frog.rate}
                detail={`${tasksState?.stats?.frog.count}/${tasksState?.stats?.frog.total}`} />
        </div>
    {/if}
    <TaskList
        onOpenDetails={(id) => (detailsTaskId = id)}
        onOpenMenu={openTaskMenu} />
{:else}
    <TasksWeb onOpenMenu={openTaskMenu} />
{/if}

<TaskSearchPopover onOpenDetails={(id) => (detailsTaskId = id)} />

<TaskDetailsPopover
    {detailsTaskId}
    onDismiss={() => (detailsTaskId = null)}
    onEdit={editTask}
    onDelete={handleDelete}
    onAddSubtask={addSubtask} />

<style>
    .tiles {
        display: grid;
        grid-auto-flow: column;
        grid-auto-columns: 1fr;
        gap: var(--space-sm);
    }
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
