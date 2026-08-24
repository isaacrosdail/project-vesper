<script lang="ts">
    import { api } from '../shared/services/api';
    import { addToast } from '../shared/components/Toaster.svelte';
    import { toDateTimeLocalValue, todayUser } from '../shared/datetime';
    import type { DailyMetricsRead } from '../apiTypes';
    import FormModal from '../shared/components/FormModal.svelte';
    import { userState } from '../shared/services/userState.svelte';

    // TODO: remove calories input? Should be either derived entirely OR manually entered more with groceries?
    const TABS = ['steps', 'weight', 'sleep', 'calories'] as const;
    type Tab = (typeof TABS)[number];

    const ICON_HREFS: Record<Tab, string> = {
        steps: '#icon-steps',
        weight: '#icon-scale',
        sleep: '#icon-sleep',
        calories: '#icon-flame',
    };

    let { onSuccess }: {
        onSuccess?: (metrics: DailyMetricsRead, isEdit: boolean) => void;
    } = $props();

    let isOpen = $state(false);
    let editingId = $state<number | null>(null);
    let activeTab = $state<Tab>('steps');

    const defaultUnits = () =>
        userState.me?.profile.unit_system === 'imperial' ? 'lbs' : 'kg';

    let form = $state({
        entry_date: '',
        steps: '',
        weight: '',
        weight_units: 'kg',
        calories: '',
        wake_datetime: '',
        sleep_datetime: '',
    });

    const title = $derived(editingId !== null ? 'Edit Metric' : 'Add Metric');
    const hasAnyMetric = $derived(
        [form.steps, form.weight, form.calories, form.wake_datetime, form.sleep_datetime]
            .some(v => v !== '')
    );
    const isValid = $derived(form.entry_date !== '' && hasAnyMetric);

    // ISO w/ offset -> "YYYY-MM-DDTHH:MM" in browser-local time, for datetime-local inputs
    function isoToLocalInput(iso: string): string {
        const d = new Date(iso);
        const pad = (n: number) => String(n).padStart(2, '0');
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
    }

    function reset() {
        form.entry_date = todayUser().toString();
        form.steps = '';
        form.weight = '';
        form.weight_units = defaultUnits();
        form.calories = '';
        form.wake_datetime = '';
        form.sleep_datetime = '';
        activeTab = 'steps';
    }

    export async function open(opts: { editId?: number } = {}) {
        editingId = opts.editId ?? null;
        if (editingId !== null) {
            const { data } = await api.daily_metrics.getById(String(editingId));
            form.entry_date = toDateTimeLocalValue(data.entry_datetime);
            form.steps = data.steps !== null ? String(data.steps) : '';
            form.weight = data.weight !== null ? String(data.weight) : '';
            form.weight_units = defaultUnits();
            form.calories = data.calories !== null ? String(data.calories) : '';
            form.wake_datetime = data.wake_datetime ? isoToLocalInput(data.wake_datetime) : '';
            form.sleep_datetime = data.sleep_datetime ? isoToLocalInput(data.sleep_datetime) : '';
        } else {
            reset();
        }
        isOpen = true;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        const payload = {
            entry_date: form.entry_date,
            steps: form.steps ? Number(form.steps) : null,
            weight: form.weight ? Number(form.weight) : null,
            weight_units: form.weight ? form.weight_units : null,
            calories: form.calories ? Number(form.calories) : null,
            wake_datetime: form.wake_datetime ? new Date(form.wake_datetime).toISOString() : null,
            sleep_datetime: form.sleep_datetime ? new Date(form.sleep_datetime).toISOString() : null,
        };
        const isEdit = editingId !== null;
        const { data, message } = isEdit
            ? await api.daily_metrics.patch(String(editingId), payload)
            : await api.daily_metrics.post(payload);
        addToast(message, '', 'success');
        isOpen = false;
        onSuccess?.(data, isEdit);
    }

</script>

<FormModal {title} bind:open={isOpen}>
    <form class="form-column" onsubmit={submit}>
        <div class="form-group entry-date-field">
            <label for="metrics-entry-date">Entry Date:</label>
            <input id="metrics-entry-date" type="date" bind:value={form.entry_date} required>
        </div>

        <div class="tab-group" role="tablist">
            {#each TABS as tab (tab)}
                <button type="button" role="tab" class="tab" aria-selected={activeTab === tab}
                    onclick={() => activeTab = tab}>
                    <svg class="icon">
                        <use href={ICON_HREFS[tab]} />
                    </svg>
                    {tab}
                </button>
            {/each}
        </div>

        <div role="tabpanel" class="tab-content" hidden={activeTab !== 'steps'}>
            <label for="metrics-steps">Steps:</label>
            <input id="metrics-steps" type="text" inputmode="numeric" bind:value={form.steps}>
        </div>
        <div role="tabpanel" class="tab-content field-pair field-pair--weighted" hidden={activeTab !== 'weight'}>
            <div>
                <label for="metrics-weight">Weight:</label>
                <input id="metrics-weight" type="text" inputmode="decimal" bind:value={form.weight}>
            </div>
            <div>
                <label for="metrics-weight-units">Units:</label>
                <select id="metrics-weight-units" bind:value={form.weight_units}>
                    <option value="kg">kg</option>
                    <option value="lbs">lbs</option>
                </select>
            </div>
        </div>
        <div role="tabpanel" class="tab-content" hidden={activeTab !== 'sleep'}>
            <div>
                <label for="metrics-wake">Wake Time:</label>
                <input id="metrics-wake" type="datetime-local" bind:value={form.wake_datetime}>
            </div>
            <div>
                <label for="metrics-sleep">Sleep Time:</label>
                <input id="metrics-sleep" type="datetime-local" bind:value={form.sleep_datetime}>
            </div>
        </div>
        <div role="tabpanel" class="tab-content" hidden={activeTab !== 'calories'}>
            <label for="metrics-calories">Calories:</label>
            <input id="metrics-calories" type="text" inputmode="numeric" bind:value={form.calories}>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary" disabled={!isValid}>Save</button>
        </div>
    </form>
</FormModal>
