<script lang="ts">
    import QuantityStepper from '../../shared/components/QuantityStepper.svelte';
    import { toAwareISO, todayUser } from '../../shared/datetime';
    import { api } from '../../shared/services/api';
    import CurrencyInput from '../../shared/components/CurrencyInput.svelte';
    import { formatCents } from '../../shared/formatters';
    import ShoppingList from '../recipes/ShoppingList.svelte';
    import { refreshShoppingList, shoppingList } from '../groceriesState.svelte';

    let view: 'plan' | 'log' = $state('plan');

    await refreshShoppingList();

    let storeName = $state('');
    let entryDate = $state(todayUser());
    const draft = $state(
        shoppingList.items.map((i) => ({
            product_id: i.product_id,
            product_name: i.product_name,
            net_weight: i.net_weight,
            packages: i.quantity_wanted,
            unit_type: i.unit_type,
            unitPrice: Math.round((i.last_price ?? 0) * 100),
            checked: true,
        })),
    );

    const bought = $derived(draft.filter((x) => x.checked));
    const packages = $derived(bought.reduce((acc, x) => acc + x.packages, 0));
    const totalPrice = $derived(
        bought.reduce((acc, x) => acc + x.packages * Number(x.unitPrice), 0),
    );

    async function submit() {
        if (!isValid) {
            showErrors = true;
            return;
        }
        await logTrip();
    }
    async function logTrip() {
        await api.shopping_trip.post({
            store_name: storeName,
            entry_datetime: toAwareISO(entryDate + 'T12:00'),
            lines: bought.map((r) => ({
                product_id: r.product_id,
                price_at_scan: r.unitPrice / 100,
                quantity: r.packages,
            })),
        });
    }

    let showErrors = $state(false);
    const isValid = $derived(
        storeName.trim().length > 0 &&
            bought.length > 0 &&
            bought.every((r) => Number(r.unitPrice) > 0) &&
            Boolean(entryDate),
    );
</script>

<div>
    <button onclick={() => (view = 'plan')}>Plan & Buy</button>
    <button onclick={() => (view = 'log')}>Log a Shop</button>
</div>

{#if view === 'plan'}
    <button onclick={() => console.log('TODO')}>Print/take to the store</button>
    <div class="plan-grid-container surface card-dashboard">
        <div class="plan-grid">
            <div class="plan-total">
                <span class="secondary">Estimated Total</span>
                <span>≈ {formatCents(totalPrice)}</span>
                <span class="tertiary">** Items never bought before are not given an estimate</span>
            </div>
            <div>
                <span class="secondary">Last Shop</span>
                <span>Mar 13</span>
            </div>
            <div>
                <span class="secondary">Avg Weekly</span>
                <span>648.20</span>
            </div>
            <div>
                <span class="secondary">This month</span>
                <span>1,894.00 (3 shops)</span>
            </div>
        </div>
    </div>

    <ShoppingList />
{:else if view === 'log'}
    <div class="log">
        <section class="log-left card-dashboard surface">
            <strong>What came home</strong>
            <p class="secondary">
                Everything on the list is pre-checked. Un-check what you didn't buy. Unit prices are
                pre-filled from last transaction price, if available.
            </p>
            <table>
                <colgroup>
                    <col class="c-check" />
                    <col class="c-item" />
                    <col class="c-pkg" />
                    <col class="c-price" />
                    <col class="c-line" />
                </colgroup>
                <thead>
                    <tr>
                        <th></th>
                        <th>Item</th>
                        <th>Packages</th>
                        <th>Unit Price</th>
                        <th>Line</th>
                    </tr>
                </thead>
                <tbody>
                    {#each draft as item}
                        <tr class:unchecked={!item.checked}>
                            <td
                                ><input
                                    type="checkbox"
                                    id="chk-{item.product_id}"
                                    bind:checked={item.checked} /></td>
                            <td><label for="chk-{item.product_id}">{item.product_name}</label></td>
                            <td>
                                <QuantityStepper
                                    bind:value={item.packages}
                                    label={item.product_name} />
                            </td>
                            <td
                                ><CurrencyInput
                                    label="Unit price of {item.product_name}"
                                    bind:value={item.unitPrice}
                                    invalid={showErrors &&
                                        item.checked &&
                                        item.unitPrice <= 0} /></td>
                            <td>{formatCents(item.packages * item.unitPrice)}</td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </section>

        <section class="card-dashboard surface">
            <strong>The trip</strong>
            <label>
                <span class="secondary">Store</span>
                <input
                    type="text"
                    bind:value={storeName}
                    maxlength="50"
                    aria-invalid={showErrors && storeName.trim().length === 0} />
            </label>
            <label>
                <span class="secondary">Date</span>
                <input type="date" bind:value={entryDate} aria-invalid={showErrors && !entryDate} />
            </label>

            <dl class="secondary">
                <dt>Items bought:</dt>
                <dd>{bought.length}</dd>
                <dt>Packages:</dt>
                <dd>{packages}</dd>
                <dt>Trip total:</dt>
                <dd>{formatCents(totalPrice)}</dd>
            </dl>
            <button class="btn btn-primary" onclick={submit}>Log the trip</button>
            {#if isValid}
                <p class="secondary">
                    One submit writes {bought.length} transactions,
                    {bought.length} PURCHASE ledger rows and one trip of {formatCents(totalPrice)}.
                </p>
            {:else if showErrors}
                <p class="secondary">
                    Add a store name and a price for every checked off / included row.
                </p>
            {/if}
        </section>
    </div>
{/if}

<style>
    input[aria-invalid='true'] {
        border-color: var(--clr-error);
    }
    .plan-grid-container {
        container-type: inline-size;
    }

    .plan-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: var(--space-sm);

        & > * {
            display: flex;
            flex-direction: column;
        }
    }
    @container (width <= 40rem) {
        .plan-grid {
            grid-template-columns: repeat(3, 1fr);
        }
        .plan-total {
            grid-column: 1 / -1;
        }
    }

    .unchecked {
        opacity: 0.5;
    }

    table {
        table-layout: fixed;
        width: 100%;
    }
    .c-check {
        width: 2.5rem;
    }
    .c-item {
        width: auto;
    }
    .c-pkg {
        width: 8rem;
    }
    .c-price {
        width: 8rem;
    }
    .c-line {
        width: 6rem;
    }
    th {
        text-align: left;
        white-space: nowrap;
    }
    th:last-child,
    td:last-child {
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
    th {
        border-bottom: var(--border-default);
    }

    dl {
        display: grid;
        grid-template-columns: 1fr auto;
    }
    dd {
        color: var(--text);
        font-variant-numeric: tabular-nums;
        text-align: end;
    }
    dt:last-of-type,
    dd:last-of-type {
        padding-top: var(--space-sm);
        border-top: var(--border-default);
        font-size: var(--font-size-lg);
    }
    /* Log a shop "view" */
    .log {
        display: grid;
        grid-template-columns: 2fr 1fr;
    }

    @media (width <= 768px) {
        .log {
            grid-template-columns: 1fr;
        }
    }
</style>
