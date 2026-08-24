
<script lang="ts">
    import FormModal from '../shared/components/FormModal.svelte';
    import { api } from '../shared/services/api';
    import { addToast } from '../shared/components/Toaster.svelte';
    import { toTypeTimeInputValue, userDay, todayUser } from '../shared/datetime';
    import type { TimeEntryRead, PillarRead } from '../apiTypes';

    let { onSuccess } = $props<{ onSuccess?: (entry: TimeEntryRead, isEdit: boolean) => void }>();

    let isOpen = $state(false);
    let editingId = $state<number | null>(null);
    let pillars = $state<PillarRead[]>([]);

    function blankForm() {
        return {
            entry_date: todayUser().toString(),
            started_at: '',
            ended_at: '',
            category: '',
            description: '',
            pillar_ids: [] as number[],
        }
    }
    let form = $state(blankForm());

    const timeError = $derived(
        form.started_at && form.ended_at && form.started_at >= form.ended_at
            ? 'End time must be after start time' : null
    );

    export async function open(opts: { editId?: number } = {}) {
        editingId = opts.editId ?? null;
        if (!pillars.length) api.pillars.getAll().then(({ data }) => pillars = data);
        if (editingId !== null) {
            const { data } = await api.time_entries.getById(String(editingId));
            form.entry_date = userDay(data.started_at).toString();
            form.started_at = toTypeTimeInputValue(data.started_at);
            form.ended_at = toTypeTimeInputValue(data.ended_at);
            form.category = data.category;
            form.description = data.description ?? '';
            form.pillar_ids = data.pillars?.map(p => p.id) ?? [];
        } else {
            form = blankForm();
        }
        isOpen = true;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        if (timeError) return;
        const payload = {
            entry_date: form.entry_date,
            started_at: form.started_at,
            ended_at: form.ended_at,
            category: form.category.trim(),
            description: form.description.trim() || null,
            pillar_ids: form.pillar_ids,
        };
        const isEdit = editingId !== null;
        const { data, message } = isEdit
            ? await api.time_entries.patch(String(editingId), payload)
            : await api.time_entries.post(payload);
        addToast(message, '', 'success');
        isOpen = false;
        onSuccess?.(data, isEdit);
    }
</script>

<FormModal title={editingId !== null ? 'Edit Time Entry' : 'Add Time Entry'} bind:open={isOpen}>
    <form class="form-column" onsubmit={submit}>
        <div>
            <label for="te-date">Date:</label>
            <input id="te-date" type="date" bind:value={form.entry_date} required>
        </div>
        <div class="field-pair">
            <div>
                <label for="te-start">Start:</label>
                <input id="te-start" type="time" bind:value={form.started_at} required>
            </div>
            <div>
                <label for="te-end">End:</label>
                <input id="te-end" type="time" bind:value={form.ended_at} required>
            </div>
        </div>
        {#if timeError}<small class="error-inline">{timeError}</small>{/if}
        <div>
            <label for="te-category">Category:</label>
            <input id="te-category" type="text" placeholder="Project Work" bind:value={form.category} required>
        </div>
        <fieldset class="pill-group">
            <legend>Pillars:</legend>
            {#each pillars as pillar (pillar.id)}
                <label class="pill">
                    <input type="checkbox" value={pillar.id} bind:group={form.pillar_ids}>
                    <span>{pillar.name}</span>
                </label>
            {/each}
        </fieldset>
        <div>
            <label for="te-desc">Description (Optional):</label>
            <textarea id="te-desc" rows="5" bind:value={form.description}></textarea>
        </div>
        <div class="form-actions">
            <button type="submit" class="btn btn-primary" disabled={!!timeError}>Save</button>
        </div>
    </form>
</FormModal>