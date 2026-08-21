<script lang="ts">
    import FormModal from '../shared/components/FormModal.svelte';
    import { addToast } from '../shared/components/Toaster.svelte';
    import { HABIT_TYPE_LABELS } from '../enumLabels';
    import type { HabitRead, HabitTypeEnum, PillarRead } from '../apiTypes';
    import { api } from '../shared/services/api';
    import { slide } from 'svelte/transition';
    import { prefersReducedMotion } from 'svelte/motion';

    // Note:
    // Tolerance comes from backend as low/high values. Converted here to tolerance for display, and converted on backend to high/low?

    let isOpen = $state(false);
    let formStep: 1 | 2 | 3 = $state(1);
    let editingId = $state<number | null>(null);
    let pillars = $state<PillarRead[]>([]);

    let { onSuccess } = $props<{ onSuccess?: (task: HabitRead, isEdit: boolean) => void }>();

    function blankForm() {
        return {
            name: '',
            weekly_frequency: '',
            pillar_ids: [] as number[],
            type: 'binary' as HabitTypeEnum,
            target_kind: 'at_least',
            target_value: '',
            target_tolerance: '',
            units: '',
            // NEW:
            schedule_type: 'frequency' as ScheduleType,
            scheduled_days: [] as number[],
            monthly_days: [] as number[],
            interval_days: '',
        };
    }
    let form = $state(blankForm());
    let formEl: HTMLFormElement;
    type ScheduleType = 'frequency' | 'everyday' | 'weekly' | 'monthly' | 'interval';
    const SCHEDULE_TYPE_LABELS: Record<ScheduleType, string> = {
        frequency: 'Days per week',
        everyday: 'Every day',
        weekly: 'Weekdays',
        monthly: 'Days of month',
        interval: 'Every N days',
    };
    // ISO weekday numbering (Mon=1), matching Temporal dayOfWeek
    const WEEKDAYS: [number, string][] = [
        [1, 'Mon'],
        [2, 'Tue'],
        [3, 'Wed'],
        [4, 'Thu'],
        [5, 'Fri'],
        [6, 'Sat'],
        [7, 'Sun'],
    ];
    // 1-28 + Last (-1); 29-31 deliberately not offered so every rule fires every month
    const MONTH_DAYS = [...Array.from({ length: 28 }, (_, i) => i + 1), -1];

    // 'everyday' option is a form convenience, not a schedule_type -> submits as weekly with all days
    function buildSchedule() {
        switch (form.schedule_type) {
            case 'frequency':
                return {
                    schedule_type: 'frequency',
                    weekly_frequency: Number(form.weekly_frequency),
                };
            case 'everyday':
                return { schedule_type: 'weekly', scheduled_days: [1, 2, 3, 4, 5, 6, 7] };
            case 'weekly':
                return {
                    schedule_type: 'weekly',
                    scheduled_days: form.scheduled_days.toSorted((a, b) => a - b),
                };
            case 'monthly':
                return {
                    schedule_type: 'monthly',
                    monthly_days: form.monthly_days.toSorted((a, b) => a - b),
                };
            case 'interval':
                return { schedule_type: 'interval', interval_days: Number(form.interval_days) };
        }
    }

    function next() {
        if (!formEl.reportValidity()) return;
        formStep++;
    }

    export async function open(opts: { editId?: number } = {}) {
        editingId = opts.editId ?? null;
        formStep = editingId === null ? 1 : 2;
        if (!pillars.length) api.pillars.getAll().then(({ data }) => (pillars = data));
        const { data } = await api.habits.getAll();
        if (editingId !== null) {
            const h = data.find((h) => h.id === editingId)!;
            form = {
                ...blankForm(),
                name: h.name,
                pillar_ids: h.pillars.map((p) => p.id),
                type: h.type,
                units: h.units ?? '',
                target_kind: h.target?.kind ?? 'anyval',
                target_value: h.target ? String(h.target.nominal) : '',
                target_tolerance:
                    h.target?.kind === 'within' ? String((h.target.high - h.target.low) / 2) : '',
                schedule_type: h.scheduled_days?.length === 7 ? 'everyday' : h.schedule_type,
                weekly_frequency: h.weekly_frequency != null ? String(h.weekly_frequency) : '',
                scheduled_days: h.scheduled_days ?? [],
                monthly_days: h.monthly_days ?? [],
                interval_days: h.interval_days != null ? String(h.interval_days) : '',
            };
        } else {
            form = blankForm();
        }
        isOpen = true;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        if (
            (form.schedule_type === 'weekly' && form.scheduled_days.length === 0) ||
            (form.schedule_type === 'monthly' && form.monthly_days.length === 0)
        ) {
            addToast('Pick at least one day', '', 'error');
            return;
        }
        const target =
            form.target_kind === 'anyval'
                ? null
                : {
                      kind: form.target_kind,
                      value: Number(form.target_value),
                      ...(form.target_kind === 'within' && {
                          tolerance: Number(form.target_tolerance),
                      }),
                  };
        const base = {
            name: form.name.trim(),
            pillar_ids: form.pillar_ids,
            ...buildSchedule(),
        };
        const payload =
            form.type === 'binary'
                ? base
                : form.type === 'duration'
                  ? { ...base, target }
                  : { ...base, target, units: form.units.trim() || null };

        const isEdit = editingId !== null;
        const { data, message } = isEdit
            ? await api.habits.patch(String(editingId), payload) // cannot edit type
            : await api.habits.post({ ...payload, type: form.type });
        addToast(message, '', 'success');
        isOpen = false;
        onSuccess?.(data, isEdit);
    }
</script>

<FormModal title={editingId !== null ? 'Edit Habit' : 'Add Habit'} bind:open={isOpen}>
    <form bind:this={formEl} class="form-column" onsubmit={submit}>
        {#if formStep === 1}
            <div class="form-column">
                {#each Object.entries(HABIT_TYPE_LABELS) as [value, label] (value)}
                    <button
                        type="button"
                        class="btn btn-secondary"
                        onclick={() => {
                            form.type = value as HabitTypeEnum;
                            formStep++;
                        }}>{label}</button>
                {/each}
            </div>
        {/if}
        {#if formStep === 2}
            <div>
                <label for="name">Name</label>
                <input type="text" id="name" bind:value={form.name} required />
            </div>
            {#if form.type !== 'binary'}
                <fieldset transition:slide={{ duration: prefersReducedMotion.current ? 0 : 200 }}>
                    <legend>Goal</legend>
                    <div>
                        <label for="target_kind">Target kind</label>
                        <select id="target_kind" bind:value={form.target_kind}>
                            <option value="at_least">At least</option>
                            <option value="at_most">At most</option>
                            <option value="within">Within</option>
                            <option value="anyval">Any value</option>
                        </select>
                    </div>

                    {#if form.target_kind !== 'anyval'}
                        <div>
                            <label for="target_value">Target</label>
                            <input
                                type="text"
                                id="target_value"
                                bind:value={form.target_value}
                                inputmode="numeric"
                                required />
                            {#if form.type === 'duration'}
                                <span class="secondary">min</span>
                            {/if}
                        </div>
                        {#if form.target_kind === 'within'}
                            <div>
                                <label for="target_tolerance">Tolerance (±)</label>
                                <input
                                    type="text"
                                    id="target_tolerance"
                                    bind:value={form.target_tolerance}
                                    inputmode="numeric"
                                    required />
                            </div>
                        {/if}
                    {/if}
                    {#if form.type === 'numeric_value'}
                        <div>
                            <label for="units">Units</label>
                            <input
                                type="text"
                                id="units"
                                bind:value={form.units}
                                placeholder="km, reps, glasses…" />
                        </div>
                    {/if}
                </fieldset>
            {/if}

            <fieldset class="pill-group" id="pillar-fieldset">
                <legend>Pillars</legend>
                {#each pillars as pillar (pillar.id)}
                    <label class="pill">
                        <input type="checkbox" value={pillar.id} bind:group={form.pillar_ids} />
                        <span>{pillar.name}</span>
                    </label>
                {/each}
            </fieldset>
        {/if}
        {#if formStep === 3}
            <h2>How often?</h2>
            <fieldset class="form-column">
                {#each Object.entries(SCHEDULE_TYPE_LABELS) as [st, label] (st)}
                    <label>
                        <input type="radio" value={st} bind:group={form.schedule_type} />
                        {label}
                    </label>
                {/each}
            </fieldset>
            {#if form.schedule_type === 'frequency'}
                <div>
                    <label for="weekly_frequency">Days per week</label>
                    <input
                        type="text"
                        id="weekly_frequency"
                        bind:value={form.weekly_frequency}
                        required
                        pattern="[1-7]"
                        title="1-7"
                        inputmode="numeric" />
                </div>
            {/if}
            {#if form.schedule_type === 'weekly'}
                <fieldset class="pill-group">
                    <legend>Days</legend>
                    {#each WEEKDAYS as [val, label] (val)}
                        <label class="pill">
                            <input type="checkbox" value={val} bind:group={form.scheduled_days} />
                            <span>{label}</span>
                        </label>
                    {/each}
                </fieldset>
            {/if}
            {#if form.schedule_type === 'monthly'}
                <fieldset class="pill-group">
                    <legend>Days</legend>
                    {#each MONTH_DAYS as d (d)}
                        <label class="pill">
                            <input type="checkbox" value={d} bind:group={form.monthly_days} />
                            <span>{d === -1 ? 'Last' : d}</span>
                        </label>
                    {/each}
                </fieldset>
            {/if}
            {#if form.schedule_type === 'interval'}
                <div>
                    <label for="interval_days">Every N days</label>
                    <input
                        type="text"
                        id="interval_days"
                        bind:value={form.interval_days}
                        pattern="[1-9][0-9]*"
                        title="Positive numbers only"
                        required
                        inputmode="numeric" />
                </div>
            {/if}
        {/if}

        <div class="form-actions">
            {#if formStep > (editingId === null ? 1 : 2)}
                <button
                    type="button"
                    class="btn btn-secondary"
                    aria-label="Back to type selection"
                    onclick={() => formStep--}>
                    <svg class="icon"><use href="#icon-arrow-left"></use></svg></button>
            {/if}
            {#if formStep === 2}
                <button type="button" onclick={next}>next</button>
            {/if}
            {#if formStep === 3}
                <button type="submit" class="btn btn-primary">Save</button>
            {/if}
        </div>
    </form>
</FormModal>
