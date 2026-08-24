<script lang="ts">
    import type { GroceriesDashboardPayload } from "../../apiTypes";
    import { PRODUCT_CATEGORY_LABELS } from "../../enumLabels";

    type CategorySpend = { category: string; pct: number; spent: number };
    type RecipeCooked = { id: number; name: string; count: number };

    let { midsection }: {
        midsection: GroceriesDashboardPayload['midsection'];
    } = $props();

    // --- Spend by category: REAL data from the backend (already populated) ---
    const categories = midsection.category_spends;
    const totalSpent = midsection.total_spent;

    // --- Top recipes: TEMPORARY placeholder ---------------------------------
    // The backend currently sends a bare number for `top_five_recipes_cooked`.
    // Once it returns an array of { id, name, count }, delete this block and use:
    const recipes = midsection.top_five_recipes_cooked;
    // const recipes: RecipeCooked[] = [
    //     { id: 1, name: 'Morning Oatmeal Bowl', count: 18 },
    //     { id: 2, name: 'Simple Spinach Salad', count: 12 },
    //     { id: 3, name: 'Chicken Stir Fry', count: 9 },
    //     { id: 4, name: 'Beef Rice Bowl', count: 6 },
    //     { id: 5, name: 'Scrambled Eggs', count: 5 },
    // ];
    // ------------------------------------------------------------------------

    const totalMeals = recipes.reduce((sum, r) => sum + r.count, 0);
    const maxCount = Math.max(...recipes.map((r) => r.count), 1);

    // Distinct colors assigned by index (purple / green / blue / orange / …)
    const PALETTE = [
        'oklch(0.70 0.13 300)',
        'oklch(0.72 0.14 150)',
        'oklch(0.68 0.13 240)',
        'oklch(0.76 0.14 60)',
        'oklch(0.72 0.10 195)',
        'oklch(0.68 0.16 20)',
        'oklch(0.82 0.13 95)',
    ];
    const colorFor = (i: number): string => PALETTE[i % PALETTE.length];

    // TODO(formatters): move to formatters.ts?
    const money = (n: number): string =>
        n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
</script>


<div class="period-mid" data-view="period">
    <!-- Top recipes cooked -->
    <section class="dashboard-card surface">
        <div class="card-head">
            <h2>Top recipes cooked</h2>
            <span class="secondary">{totalMeals} meals total</span>
        </div>

        {#each recipes as r (r.id)}
            <div class="recipe">
                <div class="recipe__top">
                    <span class="recipe__name">{r.name}</span>
                    <span class="recipe__count">×{r.count}</span>
                </div>
                <div class="recipe__track">
                    <div class="recipe__fill" style="width: {(r.count / maxCount) * 100}%"></div>
                </div>
            </div>
            {:else}
            <span>No recipes cooked this period.</span>
        {/each}
    </section>

    <!-- Spend by category -->
    <section class="dashboard-card surface">
        <div class="card-head">
            <h2>Spend by category</h2>
            <span class="total">{money(totalSpent)}</span>
        </div>

        <div class="stacked">
            {#each categories as entry, i (entry.category)}
                <div class="stacked__seg" style="width: {entry.pct}%; background: {colorFor(i)}"></div>
            {/each}
        </div>

        <div class="legend">
            {#each categories as entry, i (entry.category)}
                <div class="legend-row">
                    <span class="dot" style="background: {colorFor(i)}"></span>
                    <span class="legend__label">{PRODUCT_CATEGORY_LABELS[entry.category]}</span>
                    <span class="legend__pct">{Math.round(entry.pct)}%</span>
                    <span class="legend__amt">{money(entry.spent)}</span>
                </div>
            {/each}
        </div>
    </section>
</div>


<style>
    .period-mid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-md);

        & > * { padding: var(--space-sm); }
    }

    @media (max-width: 720px) {
        .period-mid {
            grid-template-columns: 1fr;
        }
    }

    .card-head {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: var(--space-md);
    }

    .card-head h2 {
        margin: 0;
        font-size: var(--font-size-lg);
        font-weight: var(--font-weight-semibold);
    }
    .card-head .total {
        font-weight: var(--font-weight-semibold);
        font-variant-numeric: tabular-nums;
    }

    /* --- Recipes --- */
    .recipe {
        margin-bottom: var(--space-md);
    }
    .recipe:last-child {
        margin-bottom: 0;
    }
    .recipe__top {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: var(--space-xs);
    }

    .recipe__name {
        font-size: var(--font-size-sm);
    }

    .recipe__count {
        color: var(--text-muted);
        font-size: var(--font-size-sm);
        font-variant-numeric: tabular-nums;
    }

    .recipe__track {
        height: 6px;
        background: var(--bg);
        border-radius: 99px;
        overflow: hidden;
    }

    .recipe__fill {
        height: 100%;
        background: var(--clr-success);
        border-radius: 99px;
    }

    /* --- Spend --- */
    .stacked {
        display: flex;
        height: 10px;
        border-radius: 99px;
        overflow: hidden;
        margin-bottom: var(--space-md);
    }

    .stacked__seg {
        height: 100%;
    }

    .legend-row {
        display: grid;
        grid-template-columns: auto 1fr auto auto;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-xs) 0;
        font-size: var(--font-size-sm);
    }

    .dot {
        width: 0.6rem;
        height: 0.6rem;
        border-radius: 50%;
    }

    .legend__pct {
        color: var(--text-muted);
        font-variant-numeric: tabular-nums;
    }

    .legend__amt {
        text-align: right;
        min-width: 5ch;
        font-variant-numeric: tabular-nums;
    }
</style>
