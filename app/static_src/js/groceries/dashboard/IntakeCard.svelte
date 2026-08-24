<script lang="ts">
    import type { GroceriesDashboardPayload } from '../../apiTypes';
    let {
        intake,
        timeframe,
    }: {
        intake: GroceriesDashboardPayload['intake'];
        timeframe: number;
    } = $props();
</script>

<section>
    <div class="intake-card surface">
        <div class="intake-card__header" data-macro="Cals">
            <span class="intake-dot"></span>
            <span
                >{timeframe === 1 ? 'Today' : timeframe === 7 ? 'Weekly' : 'Monthly'} · Intake</span>
        </div>

        {#if timeframe === 1}
            {@const caloriesTarget = intake.targets.calories}
            <div class="goal-donut" style="--pct: {caloriesTarget?.pct ?? 69}" data-macro="Cals">
                <svg class="goal-donut__ring" viewBox="0 0 100 100">
                    <circle class="goal-donut__track" cx="50" cy="50" r="42" pathLength="100" />
                    <circle class="goal-donut__value" cx="50" cy="50" r="42" pathLength="100" />
                </svg>
                <div class="goal-donut__label" data-macro="Cals">
                    <span>{caloriesTarget?.actual ?? 1}</span>
                    <span class="secondary intake-kcal"
                        >of {caloriesTarget.target?.nominal ?? 'nah'} kcal</span>
                    <span class="intake-left"
                        >{caloriesTarget.target !== null
                            ? (
                                  caloriesTarget.target.nominal - caloriesTarget.actual
                              ).toLocaleString()
                            : '66'} left</span>
                </div>
            </div>
            <div class="intake-footer secondary">
                {caloriesTarget?.pct ?? 69}% of daily goal
            </div>
        {:else}
            <div class="intake-avg-block">
                <span class="intake-avg">{intake.cals_avg_daily.toLocaleString()}</span><span
                    class="secondary">
                    avg kcal / day</span>
            </div>
            <div data-status="good">-</div>
            <!-- prune data-status? -->
            <div class="intake-stats secondary">
                <div class="stat-row">
                    <span>Days on target</span><span
                        >{intake.days_on_target} of {intake.days_logged}</span>
                </div>
                <div class="stat-row">
                    <span>Total consumed</span><span>{intake.total_cals_over_period} kcal</span>
                </div>
                <div class="stat-row">
                    <span>Meals logged</span><span>{intake.num_meals_logged}</span>
                </div>
            </div>
        {/if}
    </div>
</section>

<style>
    .intake-stats {
        width: 100%;

        & > .stat-row {
            display: flex;
            justify-content: space-between;
        }
    }
    /* TODO: weekly/monthly views' stats rows */
    .stat-row {
        display: grid;
        grid-template-columns: 1fr auto;
        justify-content: space-between;
    }
    .intake-kcal {
        font-size: var(--font-size-2xl); /* the big 1,543 */
        font-weight: 700;
        line-height: 1.1;
    }
    .intake-dot {
        width: 0.5rem;
        aspect-ratio: 1;
        border-radius: 50%;
        background: var(--macro-color);
    }

    /* Colored areas: */
    .intake-left,
    .intake-card__header {
        color: var(--macro-color);
    }

    .intake-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-md);
        padding: var(--space-lg);
        width: max-content;
    }

    .intake-card__header {
        align-self: flex-start;
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .intake-card .goal-donut {
        width: 16rem;
    }
    .intake-left {
        color: var(--macro-color);
    } /* the orange "657 left" */

    .goal-donut {
        display: grid;
        aspect-ratio: 1;
    }
    /* stack ring + label in the same grid cell — no absolute positioning */
    .goal-donut > * {
        grid-area: 1 / 1;
    }
    .goal-donut__ring {
        width: 100%;
        transform: rotate(-90deg); /* move the arc's start to 12 o'clock */
    }
    .goal-donut__track,
    .goal-donut__value {
        fill: none;
        stroke-width: 8;
    }
    .goal-donut__track {
        stroke: var(--surface-3);
    }
    @property --pct {
        syntax: '<number>';
        inherits: true;
        initial-value: 0;
    }
    .goal-donut__value {
        stroke: var(--metric-color);
        stroke-linecap: round;
        stroke-dasharray: 100; /* full path = 100 units */
        /* visible arc length = --pct */
        /* 1% to append the % unit to the calc'ed number; */
        stroke-dashoffset: calc((100 - var(--pct)) * 1%);
        transition: stroke-dashoffset 300ms ease;
    }
    .goal-donut__label {
        place-self: center;
        text-align: center;
        display: flex;
        flex-direction: column;
    }
</style>
