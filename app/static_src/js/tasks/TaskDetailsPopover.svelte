<script lang="ts">
    import { fmtDate } from '../shared/datetime';
    import { subtasksOf, tasksState, toggleTask } from './tasksState.svelte';

    // TODO(svelte):
    // 1. If we add a subtask for a completed task (ie all its subtasks are complete before adding)
    //   we should UN-complete that task automatically huh?

    let {
        detailsTaskId,
        onDismiss,
        onAddSubtask,
        onEdit,
        onDelete,
    }: {
        detailsTaskId: number | null;
        onDismiss: () => void;
        onEdit: (id: number) => void;
        onDelete: (id: number) => void;
        onAddSubtask: (id: number) => void;
    } = $props();

    const task = $derived(tasksState.tasks.find((t) => t.id === detailsTaskId));
    const subtasks = $derived(task ? subtasksOf(task) : []);
    let el: HTMLDivElement;

    $effect(() => {
        if (task) el.showPopover();
        else el.hidePopover();
    });
</script>

<div
    bind:this={el}
    popover
    id="task-details-popover"
    class="task-details-popover popover-overlay"
    ontoggle={(e) => {
        if (e.newState === 'closed') onDismiss();
    }}>
    {#if task}
        <div class="task-details__header">
            <input type="checkbox" checked={task.is_done} onchange={() => toggleTask(task)} />
            <h2 class="name">{task.name}</h2>
        </div>

        <div class="properties task-details__props">
            {#if task.due_datetime}
                <div class="task-details__prop">
                    <svg class="label icon"><use href="#icon-calendar"></use></svg>
                    <p class="value due_datetime">{fmtDate(task.due_datetime)}</p>
                </div>
            {/if}
            <div class="task-details__prop">
                <svg class="label icon"><use href={`#badge-priority-${task.priority}`}></use></svg>
                <p class="value priority">{task.priority}</p>
            </div>
            <div class="task-details__prop pillars-row">
                <svg class="label icon"><use href="#icon-pillars"></use></svg>
                <p class="value pillars">{task.pillars.map((p) => p.name).join(' · ')}</p>
            </div>
        </div>

        <div class="subtasks-plus-add">
            <div>
                Subtasks <span>{subtasks.filter((st) => st.is_done).length}/{subtasks.length}</span>
            </div>
            <div class="subtasks-container">
                {#each subtasks as st (st.id)}
                    <div class="subtask-group">
                        <input
                            type="checkbox"
                            checked={st.is_done}
                            onchange={() => toggleTask(st)} />
                        <div>{st.name}</div>
                    </div>
                {/each}
            </div>
            <button
                class="btn btn-ghost add-subtask secondary"
                onclick={() => onAddSubtask(task.id)}>+ Add Subtask</button>
        </div>

        <div class="task-details__footer">
            <div>
                <span class="secondary">Created </span>
                <span class="created_at secondary">{fmtDate(task.created_at)}</span>
            </div>
            <div class="task-details__actions">
                <button class="btn btn-ghost" onclick={() => onEdit(task.id)}>Edit</button>
                <button
                    aria-label="Delete task"
                    class="btn btn-destructive" onclick={() => onDelete(task.id)}>
                    <svg class="icon"><use href="#icon-trash"></use></svg>
                </button>
            </div>
        </div>
    {/if}
</div>

<style>
    .task-details-popover {
        padding: var(--space-md);
        gap: var(--space-lg); /* bigger gap between sections */

        & .task-details__header {
            display: inline-flex;
            gap: var(--space-sm);
        }

        & .pillars-row {
            display: inline-flex;
            color: var(--text-muted);
            font-size: var(--font-size-sm);
        }
    }

    .task-details__footer {
        display: flex;
        align-items: center;
        justify-content: space-between;

        & .task-details__actions {
            display: flex;
            gap: var(--space-xs);
        }
    }

    .task-details__props {
        display: flex;
        gap: var(--space-md);
        align-items: center;

        & .label {
            color: var(--text-muted);
        }
        & .value {
            color: var(--text);
            display: inline-flex;
            align-items: center;
            gap: var(--space-xs);
        }
    }

    .subtasks-plus-add {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);

        & .add-subtask {
            justify-content: start;
            padding-block: var(--space-xs);
        }
    }

    .subtasks-container {
        display: flex;
        flex-direction: column;
        overflow-y: auto;

        &:empty {
            display: none;
        }

        & .subtask-group {
            display: inline-flex;
            gap: var(--space-sm);
        }

        & .subtask-group {
            padding-left: var(--space-md);
        }
    }
</style>
