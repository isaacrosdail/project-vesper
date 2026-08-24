<script lang="ts">
    import CookColumn from './CookColumn.svelte';
    import RecipeForm from './RecipeForm.svelte';
    import { kitchen, refreshMacros, refreshSlots } from '../groceriesState.svelte';
    import type { MacroLineRead } from '../../apiTypes';

    refreshSlots();
    refreshMacros();

    const fmt = (m: MacroLineRead, unit: string) =>
        m.target == null ? `${m.actual}${unit}` : `${m.actual}/${m.target.nominal}${unit}`;
</script>

<section id="top-section">
    <h2 class="header">Kitchen</h2>
    {#if kitchen.macros}
        {@const { calories, ...macros } = kitchen.macros}
        <div class="nutrition-info-row surface">
            <div class="kcal">
                {#if calories.target !== null}
                    <strong>{calories.target.nominal - calories.actual} left</strong>
                {/if}
                <span>{fmt(calories, 'kcal')}</span>
            </div>
            <div class="macros-row">
                {#each Object.entries(macros) as [name, line] (name)}
                    <div class="macro" data-macro={name}>
                        <div class="macros-dot"></div>
                        <span>{name}</span>
                        <span class="secondary">{fmt(line, 'g')}</span>
                    </div>
                {/each}
            </div>
        </div>
    {/if}

    <div class="info">Cook drains stock -> Shortfalls fill the queue -> Buy refills stock</div>
</section>

<section id="main">
    <CookColumn />
</section>

<RecipeForm />

<style>
    :global(.top-part) {
        display: flex;
        justify-content: space-between;

        :global(& .colored) {
            color: green;
        }
    }

    #top-section,
    #main {
        --clr-calories: #e0975a;
        --clr-protein: #e0975a;
        --clr-carbs: #7cb98c;
        --clr-fat: #a48fce;
    }

    .nutrition-info-row {
        display: flex;
        align-items: center;
        gap: var(--space-sm);

        & > .kcal {
            display: flex;
            gap: var(--space-sm);
            padding-right: var(--space-md);
            border-right: var(--border-default);
        }
    }

    #top-section {
        display: grid;
        grid-template-areas:
            'header nutrition'
            'info info';

        & > .header {
            grid-area: header;
        }
        & > .nutrition-info-row {
            grid-area: nutrition;
        }
        & > .info {
            grid-area: info;
        }
    }

    .macro[data-macro='protein'] .macros-dot {
        background: var(--clr-protein);
    }
    .macro[data-macro='carbs'] .macros-dot {
        background: var(--clr-carbs);
    }
    .macro[data-macro='fat'] .macros-dot {
        background: var(--clr-fat);
    }

    .macros-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 50%;
        background-color: var(--macro-color);
    }
    .macros-row {
        display: flex;
        gap: var(--space-md);

        & .macro {
            display: flex;
            place-items: center;
            gap: var(--space-sm);
        }
    }
    #main {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-lg);
    }

    @media (width <= 768px) {
        #main {
            grid-template-columns: 1fr;
        }
    }
</style>
