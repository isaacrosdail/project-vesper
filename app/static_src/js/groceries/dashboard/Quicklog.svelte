

<script lang="ts">
    import type { GroceriesDashboardPayload, MealEnum, ProductRead } from "../../apiTypes";
    import FormModal from "../../shared/components/FormModal.svelte";
    import { addToast } from "../../shared/components/Toaster.svelte";
    import { nowISO } from "../../shared/datetime";
    import { api } from "../../shared/services/api";
    import SearchSelect from '../../shared/components/SearchSelect.svelte';
    import { MEAL_LABELS } from "../../enumLabels";

    let { meals, timeframe, onLogged }: {
        meals: GroceriesDashboardPayload['intake']['meals_today'];
        timeframe: number;
        onLogged?: () => void;
    } = $props();

    type LogForm = {
        product_id: string;
        grams: string;
        meal: MealEnum | '';
        entry_datetime: string;
    };

    function blankForm(): LogForm {
        return { product_id: '', grams: '', meal: '', entry_datetime: nowISO() };
    }

    let logOpen = $state(false);
    let submitting = $state(false);
    let products = $state<ProductRead[]>([]);
    let form = $state<LogForm>(blankForm());

    const selected = $derived(products.find(p => String(p.id) === form.product_id));

    async function openLog() {
        form = blankForm();
        logOpen = true;
        products = (await api.products.getAll()).data;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        if (!form.meal) return;   // narrows MealEnum | '' -> MealEnum; <select required> covers the UI
        submitting = true;
        try {
            const { message } = await api.nutrition_log.logProduct({
                product_id: Number(form.product_id),
                grams: Number(form.grams),
                meal: form.meal,
                entry_datetime: form.entry_datetime,
            })
            addToast(message, '', 'success');
            logOpen = false;
            onLogged?.();
        } finally {
            submitting = false;
        }
    }

    // Duped in cookcolumn.svelte too
    // const MEALS: { value: MealEnum; label: string }[] = [
    //     { value: 'breakfast', label: 'Breakfast' },
    //     { value: 'morning_snack', label: 'Morning Snack' },
    //     { value: 'lunch', label: 'Lunch' },
    //     { value: 'afternoon_snack', label: 'Afternoon Snack' },
    //     { value: 'supper', label: 'Supper' },
    //     { value: 'pm_snack', label: 'PM Snack' },
    // ];

</script>



<div class="card-dashboard surface">
    <div class="card-header">
        <div>Quick Log</div>
        <a class="tertiary card-link" href="/groceries/recipes">all recipes</a>
    </div>
    <!-- Quicklog container -->
    <div>
        {#each Object.entries(MEAL_LABELS) as [value, label] (value)}
            {#if meals[value]}
                <div class="logentry list-row secondary" data-meal={value}>
                    <div class="dot-time">
                        <div class="ddot"></div>
                    </div>
                    <div class="logentry-name">{label}</div>
                    <div class="logentry-cals">{meals[value]}kcal</div>
                </div>
            {/if}
        {/each}
        <div class="list-row secondary">
            <div>Log a single item</div>
            <button class="btn" onclick={openLog}>Log</button>
        </div>
    </div>
</div>

<FormModal title="Log Entry" bind:open={logOpen}>
    <form class="form-column" onsubmit={submit}>
        <div>
            <label for="log-product">Product:</label>
            <SearchSelect items={products} bind:value={form.product_id}
                toLabel={p => p.name} toValue={p => String(p.id)} />
            <!-- <select id="log-product" bind:value={form.product_id} required>
                <option value="">--</option>
                {#each products as p (p.id)}
                    <option value={String(p.id)}>{p.name}</option>
                {/each}
            </select> -->
        </div>
        <div>
            <label for="log-grams">Grams:</label>
            <input id="log-grams" type="text" inputmode="decimal" bind:value={form.grams} required>
        </div>
        <div>
            <label for="log-meal">Meal:</label>
            <select id="log-meal" bind:value={form.meal} required>
                <option value="">--</option>
                {#each Object.entries(MEAL_LABELS) as [value, label] (value)}
                    <option value={value}>{label}</option>
                {/each}
            </select>
        </div>
        <div class="form-actions">
            <button type="submit" class="btn btn-primary" disabled={submitting}>Log</button>
        </div>
    </form>
</FormModal>

<style>
    .logentry {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;

  & > .dot-time {
    display: flex;
    place-items: center;
    gap: var(--space-xs);
  }
  & .ddot { width: 0.5rem; height: 0.5rem; background: var(--meal-color); border-radius: 50%; }
}

/* Meal colors */
[data-meal="breakfast"] { --meal-color: #e0975a; }
[data-meal="lunch"]     { --meal-color: #7cb98c; }
[data-meal="snack"]     { --meal-color: #a48fce; }
.list-row {
  display: flex;
  justify-content: space-between;
  border: var(--border-default);
  border-radius: var(--border-radius);
  padding: var(--space-xs) var(--space-sm);
}
</style>