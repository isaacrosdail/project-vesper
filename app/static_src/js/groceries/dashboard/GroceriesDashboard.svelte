
<script lang="ts">
    import type { GroceriesDashboardPayload } from '../../apiTypes';
    import { api } from '../../shared/services/api';
    import IntakeCard from './IntakeCard.svelte';
    import MacroNutrientsCard from './MacroNutrientsCard.svelte';
    import PurchaseInsightsCard from './PurchaseInsightsCard.svelte';
    import ShoppingListDashboard from './ShoppingListDashboard.svelte';
    import Quicklog from './Quicklog.svelte';
    import PeriodMidsection from './PeriodMidsection.svelte';
    import { SvelteMap } from 'svelte/reactivity';
    import { fmtDate, rangeLabel } from '../../shared/datetime';
    import TransactionForm from '../data/TransactionForm.svelte';
    import ProductForm from '../data/ProductForm.svelte';

    // type MacroLine = {
    //     actual: number;
    //     target: number;
    //     pct: number;
    // }

    const TIMEFRAMES = [
        { label: 'Today', value: 1 },
        { label: 'Week', value: 7 },
        { label: 'Month', value: 30 },
    ];

    let transactionForm = $state<TransactionForm>();
    let productForm = $state<ProductForm>();

    let timeframe = $state(1);
    let data = $state<GroceriesDashboardPayload | null>(null);
    const cache = new SvelteMap<number, GroceriesDashboardPayload>();

    async function setTimeframe(tf: number) {
        timeframe = tf;
        if (!cache.has(tf)) {
            const resp = await api.groceries_dashboard.get(new URLSearchParams({ timeframe: String(tf) }));
            cache.set(tf, resp.data);
        }
        data = cache.get(tf) ?? null;
    }
    setTimeframe(1);

    // A write invalidates every timeframe, not just the visible one.
    async function refresh() {
        cache.clear();
        await setTimeframe(timeframe);
    }
</script>

<div class="page-header">
    <div>
        <h2 class="page-h2">{timeframe === 1 ? 'Today' : 'Period:'}</h2>
        <div class="timeframe-label secondary">{rangeLabel(timeframe)}</div>
    </div>
    <div class="timeframe-selector surface" data-timeframe="stuff">
        {#each TIMEFRAMES as tf (tf.label)}
            <button type="button" class:active={timeframe === tf.value}
                onclick={() => setTimeframe(tf.value)}>{tf.label}
            </button>
        {/each}
    </div>
</div>

<TransactionForm bind:this={transactionForm} onSuccess={refresh}/>
<button onclick={() => transactionForm?.open()}>Add TXN</button>

{#if data}
<section id="intake" data-view={timeframe === 1 ? 'today' : 'period'}>
    <IntakeCard intake={data.intake} {timeframe} />
    <MacroNutrientsCard intake={data.intake} {timeframe} />
</section>
{#if timeframe === 1}
<section id="quicklog-shoppinglist" class="mid-section">
    <Quicklog meals={data.intake.meals_today} {timeframe} onLogged={refresh}/>
    <ShoppingListDashboard shopping_list_items={data.midsection.shopping_list_items} {timeframe}/>
</section>
{:else}
    <PeriodMidsection midsection={data.midsection} {timeframe} />
{/if}
    <PurchaseInsightsCard insights={data.purchase_insights} {timeframe} />
{/if}


<style>

    .page-header {
        display: flex;
        justify-content: space-between;
    }

#intake {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-sm);
}
/* right card: macro-bar orientation */
#intake[data-view="today"]  .macro-bars { flex-direction: column; }
#intake[data-view="period"] .macro-bars { flex-direction: row; }

    #quicklog-shoppinglist {
    display: grid;
    grid-template-columns: 1fr 1fr;
    }
</style>