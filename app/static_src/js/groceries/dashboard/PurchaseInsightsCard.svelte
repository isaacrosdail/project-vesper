
<script lang="ts">
    import type { GroceriesDashboardPayload } from "../../apiTypes";
    import { fmtDate } from "../../shared/datetime";

    let { insights, timeframe }: {
        insights: GroceriesDashboardPayload['purchase_insights'];
        timeframe: number;
    } = $props();

</script>

<section id="purchase-transactions-highlights" class="card-dashboard surface">
    <div>
        <h2>Purchase insights</h2>
        <p class="secondary insights__most-purchased-this-period">{timeframe <= 7 ? 'MOST PURCHASED THIS WEEK' : 'MOST PURCHASED THIS MONTH'}</p>
        <div class="ingredients-chips secondary">
            {#each insights.top_products as [name, count] (name)}
                <div class="insight-chip">
                    <span>{name}</span>
                    <span class="secondary">{count}x</span>
                </div>
            {/each}
        </div>
    </div>
    <div>
        <span class="insights__num-transactions">{insights.num_transactions}</span>
        <span class="secondary"> transactions</span><br>
        <span class="secondary subtext">{`$${insights.total_spent}`} - </span>
        <span class="secondary insights__across-n-products">{`across ${insights.num_products} products`}</span>
        {#if insights.last_shopping_trip}
        <div>
            <span class="last_shopping_trip">{`Last shopping trip: ${insights.last_shopping_trip.store_name} · ${fmtDate(insights.last_shopping_trip.entry_datetime)}`}</span>
            <span>{insights.last_shopping_trip.num_transactions}</span>
        </div>
        {/if}
        <p>Products + CSV -></p>
        <p>Transactions -></p>
    </div>
</section>


<style>
    /* TODO: For the purchase insights "Most purchased this.." products */
    .ingredients-chips {
        display: flex;
        & > .insight-chip {
            display: flex;
            gap: var(--space-xs);
            padding: var(--space-xs) var(--space-xs);
            color: var(--text);
            border: var(--border-default);
            border-radius: 999px;
        }
    }

    #purchase-transactions-highlights {
        display: flex;
        flex-direction: row;
    }

</style>