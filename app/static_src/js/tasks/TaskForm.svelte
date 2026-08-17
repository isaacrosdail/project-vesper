<script lang="ts">
    import FormModal from '../shared/components/FormModal.svelte';
    import { api } from '../shared/services/api';
    import { addToast } from '../shared/components/Toaster.svelte';
    import type { TaskRead, PillarRead, PriorityEnum } from '../apiTypes';
    import { toAwareISO, toDateTimeLocalValue } from '../shared/datetime';

    let { onSuccess } = $props<{ onSuccess?: (task: TaskRead, isEdit: boolean) => void }>();

    const PRIORITIES: { value: PriorityEnum; label: string }[] = [
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'frog', label: 'Frog' },
    ];

    let isOpen = $state(false);
    let editingId = $state<number | null>(null);
    let supertaskId = $state<number | null>(null); // "Add Subtask" flow
    let pillars = $state<PillarRead[]>([]);
    let allTasks = $state<TaskRead[]>([]);
    let search = $state('');
    let dropdownOpen = $state(false);
    let dropdownEl = $state<HTMLDivElement>();

    function blankForm() {
        return {
            name: '',
            priority: 'medium' as PriorityEnum,
            due_datetime: '', // yyyy-mm-dd from the date input
            pillar_ids: [] as number[],
            subtask_ids: [] as number[],
        };
    }

    let form = $state(blankForm());

    export type SubtaskDropdownState = {
        tasks: { id: number; name: string }[];
        selectedIds: Set<number>;
        excludeId: number | null;
        searchTerm: string;
    };

    export function visibleSubtaskIds(state: SubtaskDropdownState): Set<number> {
        const term = state.searchTerm.trim().toLowerCase();
        return new Set(
            state.tasks
                .filter((t) => !state.selectedIds.has(t.id)) // exclude tasks chosen (those are pills now)
                .filter((t) => t.id !== state.excludeId) // exclude 'this' task (in edit mode)
                .filter((t) => t.name.toLowerCase().includes(term)) // exclude those not matching search term
                .map((t) => t.id),
        );
    }

    const visibleIds = $derived(
        visibleSubtaskIds({
            tasks: allTasks.map((t) => ({ id: t.id, name: t.name })),
            selectedIds: new Set(form.subtask_ids),
            excludeId: editingId,
            searchTerm: search,
        }),
    );
    const visibleTasks = $derived(allTasks.filter((t) => visibleIds.has(t.id)));
    const selectedTasks = $derived(allTasks.filter((t) => form.subtask_ids.includes(t.id)));

    export async function open(opts: { editId?: number; supertaskId?: number } = {}) {
        editingId = opts.editId ?? null;
        supertaskId = opts.supertaskId ?? null;
        if (!pillars.length) api.pillars.getAll().then(({ data }) => (pillars = data));
        const { data } = await api.tasks.getAll();
        allTasks = data;
        const t = editingId === null ? undefined : data.find((t) => t.id === editingId);
        if (t) {
            form.name = t.name;
            form.priority = t.priority;
            form.due_datetime = t.due_datetime ? toDateTimeLocalValue(t.due_datetime) : '';
            form.pillar_ids = t.pillars.map((p) => p.id);
            form.subtask_ids = [...t.subtasks];
        } else {
            form = blankForm();
        }
        search = '';
        dropdownOpen = false;
        isOpen = true;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        const includeSupertaskIds = supertaskId !== null;
        const payload = {
            name: form.name.trim(),
            priority: form.priority,
            due_datetime: form.due_datetime ? toAwareISO(form.due_datetime) : null,
            pillar_ids: form.pillar_ids,
            subtask_ids: form.subtask_ids,
            ...(includeSupertaskIds && { supertaskId: [supertaskId] })
        };
        const isEdit = editingId !== null;
        const { data, message } = isEdit
            ? await api.tasks.patch(String(editingId), payload)
            : await api.tasks.post(payload);
        addToast(message, '', 'success');
        isOpen = false;
        onSuccess?.(data, isEdit);
    }

    function openDropdown() {
        if (dropdownEl && !dropdownEl.matches(':popover-open')) dropdownEl.showPopover();
    }
</script>

<FormModal title={editingId !== null ? 'Edit Task' : 'Add Task'} bind:open={isOpen}>
    <form class="form-column" onsubmit={submit}>
        <div>
            <label for="task-name">Name</label>
            <input id="task-name" type="text" bind:value={form.name} required />
        </div>
        <div>
            <label>Priority:</label>
            <!-- mirror ui.segmented's classes; radios drive it -->
            {#each PRIORITIES as p (p.label)}
                <label>
                    <input type="radio" value={p.value} bind:group={form.priority} />
                    {p.label}
                </label>
            {/each}
        </div>
        <div>
            <label for="task-due">Due</label>
            <input
                id="task-due"
                type="datetime-local"
                bind:value={form.due_datetime}
                required={form.priority === 'frog'} />
        </div>
        <fieldset class="pill-group">
            <legend>Pillars</legend>
            {#each pillars as pillar (pillar.id)}
                <label class="pill">
                    <input type="checkbox" value={pillar.id} bind:group={form.pillar_ids} />
                    <span>{pillar.name}</span>
                </label>
            {/each}
        </fieldset>

        <div class="subtask-chips">
            {#each selectedTasks as t (t.id)}
                <div class="subtask-chip">
                    <button
                        type="button"
                        class="btn-icon btn-round subtask-chip-remove"
                        aria-label="Remove subtask"
                        onclick={() =>
                            (form.subtask_ids = form.subtask_ids.filter((id) => id !== t.id))}
                        >✕</button>
                    <span>{t.name}</span>
                </div>
            {/each}
        </div>
        <div
            class="search-wrapper"
            class:open={dropdownOpen}
            onfocusout={(e) => {
                if (!e.currentTarget.contains(e.relatedTarget as Node)) dropdownOpen = false;
            }}>
            <label for="task-search">Search for subtasks:</label>
            <input
                id="task-search"
                type="search"
                placeholder="Search tasks"
                bind:value={search}
                onfocus={openDropdown}
                onclick={openDropdown} />
            <div class="subtask-dropdown" popover="auto" bind:this={dropdownEl}>
                {#each visibleTasks as t (t.id)}
                    <button
                        type="button"
                        class="subtask-option"
                        onclick={() => form.subtask_ids.push(t.id)}>
                        <div>{t.name}</div>
                        <svg class="icon" data-priority={t.priority}
                            ><use href="#badge-priority-{t.priority}"></use></svg>
                    </button>
                {/each}
            </div>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </form>
</FormModal>

<style>
    #task-search {
        anchor-name: --subtask-search;
    }

    .search-wrapper {
        position: relative;
    }

    .subtask-dropdown {
        position: fixed;
        position-anchor: --subtask-search;
        z-index: 50;
        top: calc(anchor(bottom) + 6px);
        left: anchor(left);
        width: anchor-size(width);
        max-height: min(300px, 40vh);
        overflow-y: auto;
        scrollbar-width: thin;
        background: var(--surface-2);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--line-strong);
        border-radius: 0 0 var(--border-radius) var(--border-radius);

        &:popover-open {
            display: flex;
            flex-direction: column;
        }
    }
    .subtask-option {
        display: grid;
        grid-template-columns: 1fr auto;
        align-items: center;
        background: var(--surface-2);
        padding: var(--space-sm) var(--space-md);

        &:hover {
            background: var(--surface-3);
        }
    }
    .subtask-option + .subtask-option {
        border-top: 1px solid var(--line-strong);
    }

    /* wraps all pills */
    .subtask-chips {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: var(--space-sm);
    }
    /* each pill as a whole (x_svg + name) */
    .subtask-chip {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        background: var(--surface-1);
        color: var(--accent-strong);
        border: 1px solid var(--accent-strong);
        border-radius: var(--border-radius);
        font-size: var(--font-size-sm);
    }
    .subtask-chip-remove {
        opacity: 0.7;
        cursor: pointer;

        &:hover {
            opacity: 1;
            color: var(--clr-error);
        }
    }
    /* wraps label + search input + dropdown */
    /* .search-wrapper:has(.subtask-dropdown:not(.hide)) input {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
    } */
    .search-wrapper.open {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
        border-bottom-color: transparent;
    }

    .search-wrapper.open {
        border-top-left-radius: 0;
        border-top-right-radius: 0;
        border-top: none;
    }
</style>
