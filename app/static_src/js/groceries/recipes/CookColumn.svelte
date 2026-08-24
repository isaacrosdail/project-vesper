
<script lang="ts">
    import type { MealEnum, RecipeSlotRead } from '../../apiTypes';
    import { nowISO } from '../../shared/datetime';
    import { api } from '../../shared/services/api';
    import { addToast } from '../../shared/components/Toaster.svelte';
    import { refreshShoppingList, refreshSlots, kitchen, openRecipeForm } from '../groceriesState.svelte';
    import { openContextMenu } from '../../shared/components/ContextMenu.svelte';
    import { askConfirm } from '../../shared/components/ConfirmDialog.svelte';
    import { MEAL_LABELS } from '../../enumLabels';

    // const MEALS: { value: MealEnum; label: string }[] = [
    //     { value: 'breakfast', label: 'Breakfast' },
    //     { value: 'morning_snack', label: 'Morning Snack' },
    //     { value: 'lunch', label: 'Lunch' },
    //     { value: 'afternoon_snack', label: 'Afternoon Snack' },
    //     { value: 'supper', label: 'Supper' },
    //     { value: 'pm_snack', label: 'PM Snack' },
    // ];

    const MEALS = Object.entries(MEAL_LABELS) as [MealEnum, string][];

    let pendingSlot = $state<RecipeSlotRead | null>(null);
    let mealPopoverEl: HTMLDivElement;

    async function addShortFalls(slot: RecipeSlotRead) {
        const { message } = await api.shopping_list.addShortfalls(String(slot.id));
        await refreshShoppingList();
        addToast(message, '', 'success');
    }
    async function cook(meal: MealEnum) {
        if (!pendingSlot) return;
        try {
            const { message } = await api.recipes.cook(String(pendingSlot.id), meal, nowISO());
            addToast(message, '', 'success');
            await refreshSlots();
        } finally {
            mealPopoverEl.hidePopover();
            pendingSlot = null;
        }
    }

    async function deleteRecipe(slot: RecipeSlotRead) {
        const confirmed = await askConfirm("Delete this recipe?");
        if (!confirmed) return;
        await api.recipes.delete(String(slot.id));
        await refreshSlots();
    }

    // For each slot, add 1 to total if missing.length === 0
    const readyCount = $derived(kitchen.slots.reduce((acc, s) => s.missing.length === 0 ? acc + 1 : acc, 0));
    const notReadyCount = $derived(kitchen.slots.length - readyCount);
</script>

<div class="cook-left">
    <div class="top-part">
        <span class="colored">Outflow - Cook</span>
        <!-- <span class="secondary">69 ready, 420 need shopping</span> -->
         <!-- Should "need shopping" mean number of recipes OR number of distinct items missing total? -->
        <span class="secondary">{readyCount} ready, {notReadyCount} need shopping</span>
    </div>
    <h2>Recipes</h2>
    <button class="btn-icon btn-round btn-primary"
        aria-label="TODO"
        onclick={() => openRecipeForm()}>
        <svg class="icon"><use href="#icon-plus"></use></svg>
    </button>

    {#each kitchen.slots as slot (slot.id)}
        <div class="recipe-slot surface" data-recipe-id={slot.id} data-state={slot.missing.length === 0 ? 'ready' : 'missing'}
            oncontextmenu={(e) => {
                e.preventDefault();
                openContextMenu(e.clientX, e.clientY, [
                    { label: 'Edit', action: () => { console.log("implement me") } },
                    { label: 'Delete', action: () => { deleteRecipe(slot) } },
                ]);
            }}>
            <div class="recipe-dot"></div>
            <div class="name">
                {slot.name}
                <span class="status-chip">
                    {slot.missing.length === 0 ? 'Ready' : `Missing ${slot.missing.length}`}
                </span>
            </div>
            <ul class="missing-ing">
                {#each slot.missing as ing (ing.product_id)}
                    <li>{ing.product_name} - {Math.round(ing.deficit_value)}{ing.unit}</li>
                {/each}
            </ul>
            {#if slot.missing.length}
                <button class="action btn btn-secondary" onclick={() => addShortFalls(slot)}>
                    Add {slot.missing.length} to list
                </button>
            {:else}
                <button class="action btn btn-secondary"
                    popovertarget="meal-select-popover"
                    onclick={() => pendingSlot = slot}>
                    Cook
                </button>
            {/if}
            <div class="meta secondary">Serves {slot.yields} - ~10min - 999kcal</div>
        </div>
    {/each}

</div>

<div popover id="meal-select-popover" class="popover-overlay" bind:this={mealPopoverEl}>
    {#each MEALS as [value, label] (label)}
        <button class="btn btn-secondary" onclick={() => cook(value)}>{label}</button>
    {/each}
</div>


<style>
    .cook-left {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
    }

    .recipe-dot {
        width: 0.5rem;
        aspect-ratio: 1;
        border-radius: 50%;
        background: red;
    }
    .recipe-slot {
        --slot-clr: var(--clr-success);

        display: grid;
        grid-template-columns: auto 1fr auto;
        grid-template-areas:
        "recipe-dot name    action"
        ".          meta    action"
        ".          missing action";
        column-gap: var(--space-md);
        align-items: center;
        padding: var(--space-md);

        &[data-state="missing"] {
        --slot-clr: var(--clr-warning);

        & .action {
            color: var(--slot-clr);
            border-color: color-mix(in oklab, var(--slot-clr) 50%, transparent);
        }
        }

        & .recipe-dot {
        grid-area: recipe-dot;
        width: 0.5rem;
        aspect-ratio: 1;
        border-radius: 50%;
        background-color: var(--slot-clr);
        }

        & .name {
        grid-area: name;
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        }

        & .meta {
        grid-area: meta;
        align-self: start;
        }

        & .missing-ing {
            grid-area: missing;
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-sm);
            margin-top: var(--space-sm);
            padding: 0;
            list-style: none;

            & li {
                padding: 0.1rem var(--space-sm);
                font-size: 0.7em;
                color: var(--slot-clr);
                border: 1px solid color-mix(in oklab, var(--slot-clr) 40%, transparent);
                background: color-mix(in oklab, var(--slot-clr) 7%, transparent);
                border-radius: var(--border-radius);
            }
        }

        & .status-chip {
        padding: 0.1rem var(--space-sm);
        font-size: 0.7em;
        color: var(--slot-clr);
        border: 1px solid color-mix(in oklab, var(--slot-clr) 40%, transparent);
        background: color-mix(in oklab, var(--slot-clr) 7%, transparent);
        border-radius: 999px;
        }

        & .action {
        grid-area: action;
        align-self: center;
        }
    }
</style>