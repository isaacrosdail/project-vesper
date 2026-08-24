


<script lang="ts">
    import type { GroceriesDashboardPayload } from "../../apiTypes";
    import { api } from "../../shared/services/api";


    let { shopping_list_items, timeframe }: {
        shopping_list_items: GroceriesDashboardPayload['midsection']['shopping_list_items'];
        timeframe: number;
    } = $props();

</script>

<div class="shoppinglist card-dashboard surface">
    <div class="card-header">
        <div>Shopping List</div>
        <div class="tertiary another-pill">ITEMS NEEDED TODO</div>
        <a class="tertiary card-link" href="/groceries/recipes">full list</a>
    </div>
    <div class="listitems">
        {#each shopping_list_items as i (i.id)}
            <div class="listitem secondary">
                <div class="left">
                    <!-- TODO: get checkbox working -->
                    <input type="checkbox" bind:checked={i.is_checked} onchange={() => api.shopping_list.patchItem(i.id, { is_checked: !i.is_checked })}>
                    <span class="item-product_name">{i.product_name}</span>
                </div>
                <div class="right">
                    <span class="amount-needed">{i.net_weight * i.quantity_wanted}</span>
                    <span class="amount-units">{i.unit_type}</span>
                </div>
            </div>
        {/each}
    </div>
    <div class="cta">
        <div class="generate btn-soft">Generate from recipes</div>
        <div class="additem btn-soft">+ Add item</div>
    </div>
</div>

<style>
    /* TODO: For each entry in shopping list? */
    .listitem {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>