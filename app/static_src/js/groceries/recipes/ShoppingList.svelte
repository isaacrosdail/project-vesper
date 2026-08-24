<script lang="ts">
    import { api } from '../../shared/services/api';
    import { shoppingList, refreshShoppingList } from '../groceriesState.svelte';
    import type { ShoppingListItemRead } from '../../apiTypes';
    import { askConfirm } from '../../shared/components/ConfirmDialog.svelte';
    import QuantityStepper from '../../shared/components/QuantityStepper.svelte';
    import SearchSelect from '../../shared/components/SearchSelect.svelte';
    import { PRODUCT_CATEGORY_LABELS } from '../../enumLabels';
    import { money } from '../../shared/formatters';

    const perCat = $derived(Map.groupBy(shoppingList.items, (d) => d.category));

    const products = api.products.getAll();

    async function deleteItem(item: ShoppingListItemRead) {
        const confirmed = await askConfirm('Are you sure you want to delete this item?');
        if (!confirmed) return;
        await api.shopping_list.deleteItem(String(item.id));
        await refreshShoppingList();
    }
    async function addItem(productId: number, quantity_wanted: number) {
        await api.shopping_list.addItem(String(productId), quantity_wanted);
        await refreshShoppingList();
    }
    async function patchQuantity(item: ShoppingListItemRead, raw: string) {
        const quantity = Number(raw);
        if (!Number.isInteger(quantity) || quantity < 1) {
            await refreshShoppingList();
            return;
        }
        await api.shopping_list.patchItem(String(item.id), { quantity_wanted: quantity });
        await refreshShoppingList();
    }
</script>

<div class="card-dashboard surface">
    {#if shoppingList.items.length}
        <p>
            {shoppingList.items.length} items, {shoppingList.items.reduce(
                (sum, i) => sum + i.quantity_wanted,
                0,
            )} packages
        </p>
        {#each Object.entries(PRODUCT_CATEGORY_LABELS) as [category, label] (category)}
            {@const items = perCat.get(category)}
            {#if items}
                <div class="category-header">
                    <h3>{label}</h3>
                    <span class="category-count">{items.length}</span>
                </div>
                <ul>
                    {#each items as item (item.id)}
                        <li
                            class="shopping-list-item"
                            data-product-id={item.product_id}
                            data-item-id={item.id}>
                            <div class="left">
                                <span>{item.product_name}</span>
                                <span class="secondary">{item.net_weight}{item.unit_type}</span>
                            </div>
                            <div class="right">
                                <QuantityStepper
                                    value={item.quantity_wanted}
                                    label={item.product_name}
                                    onCommit={(n) => patchQuantity(item, String(n))} />
                                <span class="secondary"
                                    >{item.last_price
                                        ? `≈${money.format(item.last_price * item.quantity_wanted)}`
                                        : 'no history'}</span>
                                <button class="secondary" onclick={() => deleteItem(item)} aria-label="Remove item">
                                    <svg class="icon remove-item"><use href="#icon-x"></use></svg>
                                </button>
                            </div>
                        </li>
                    {/each}
                </ul>
            {/if}
        {/each}
    {:else}
        <span class="secondary">Nothing to buy</span>
    {/if}
    {#await products then { data }}
        <SearchSelect
            label="Search products"
            items={data}
            toLabel={(p) => p.name}
            toValue={(p) => String(p.id)}
            placeholder="Add an item"
            onSelect={(p) => addItem(p.id, 1)} />
    {/await}
</div>

<style>
    .remove-item {
        opacity: 0;
        color: var(--clr-error);
        transition: opacity 120ms ease;
    }
    .shopping-list-item:hover .remove-item,
    .shopping-list-item:focus-within .remove-item {
        opacity: 1;
    }
    .category-header {
        display: flex;
        justify-content: space-between;
        background: var(--surface-3);
    }
    .category-count {
        color: var(--text-muted);
    }

    li {
        border-top: var(--border-default);
        border-bottom: var(--border-default);
    }
    /* NEW: */
    .shopping-list-item {
        position: relative;
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: center;
        gap: var(--space-sm);

        /* stepper | price | remove — fixed price track keeps rows aligned */
        & .right {
            display: grid;
            grid-template-columns: auto 6.5rem auto;
            align-items: center;
            gap: var(--space-sm);

            & > span {
                text-align: right;
                font-variant-numeric: tabular-nums;
            }
        }

        & span {
            font-weight: 400;
        }
    }
</style>
