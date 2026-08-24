

<script lang="ts">
    import type { GroceriesDashboardPayload } from "../../apiTypes";
    import MacrosBarChart from './MacronutrientsBarchart.svelte';

    // type MacroLine = {
    //     actual: number;
    //     target: number;
    //     pct: number;
    // }

    let { intake, timeframe }: {
        intake: GroceriesDashboardPayload['intake'];
        timeframe: number;
    } = $props();

    const macroLines = $derived(([['Protein','protein'], ['Carbs','carbs'], ['Fat','fat']] as const)
        .map(([label, key]) => ({ label, key, ...intake.targets[key] })));

    $inspect(intake);
</script>

<div class="macros-card surface" class:period={timeframe !== 1}>
    <div class="secondary macros-card__label">{timeframe === 1 ? 'Macronutrients' : 'Daily Calories'}</div>
    <div class="macro-bars" class:vertical={timeframe === 1}>
        {#each macroLines as m (m.label)}
            {@const valSuffix = timeframe === 1 ? 'g' : 'g avg'}
            <div class="macro-bar" data-macro={m.label}>
                <span class="macro-bar__label">{m.label}</span>
                <div class="macro-bar__track">
                    <div class="macro-bar__fill" style="--pct: {m.pct}"></div>
                </div>
                {#if m.target?.nominal}
                    <span class="macro-bar__val secondary">{m.actual}/{m.target?.nominal}{valSuffix}</span>
                {:else}
                    <span class="macro-bar__val secondary">{m.actual}{valSuffix}</span>
                {/if}
            </div>
        {/each}
    </div>
    <div class="intake-chart" id="intake-barchart">
        <MacrosBarChart />
    </div>
</div>

<style>
.macros-card {
    display: flex;
    flex-direction: column;
    padding: var(--space-sm);
}
.macros-card.period .macro-bars { order: 1; }

.macros-card:not(.period) .macro-bars {
    flex-direction: column;
}

/* For macros progress; now driven by --pct value? */
.macro-bars {

  display: flex;

  &:not(.vertical) > .macro-bar {
    flex: 1;
    min-width: 0;
  }
    gap: var(--space-sm);
    width: 100%;
}

.macros-card.period .macro-bar {
    grid-template-areas:
        "label"
        "value"
        "bar";
}
.macros-card.period .macro-bar__val { justify-self: start; }

.macro-bar {
    display: grid;
    /* grid-template-columns: 4rem 1fr auto; */
    grid-template-areas:
      "label value"
      "bar bar";
    align-items: center;
    gap: var(--space-xs);

}
.macro-bar__label { grid-area: label; }
.macro-bar__val { grid-area: value; justify-self: end; }

.macro-bar__track {
  grid-area: bar;
    height: 0.5rem;
    overflow: hidden;                        /* clips fill to rounded corners */
    background-color: var(--surface-3);
    border-radius: var(--border-radius);
}

.macro-bar__fill {
    height: 100%;
    /* background: var(--progress-bar-fill); */
    background: var(--macro-color);
    transform: scaleX(calc(var(--pct, 0) / 100));   /* 0–100 scale, same as the donut */
    transform-origin: left;
    transition: transform 0.2s ease-in-out;
}
</style>