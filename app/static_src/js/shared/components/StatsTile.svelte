<script lang="ts">
    let {
        label,
        value,
        detail,
        progress,
        tone = 'neutral',
    }: {
        label: string;
        value: string | number;
        detail?: string;
        progress?: number;
        tone?: 'neutral' | 'good' | 'bad';
    } = $props();
</script>

<div class={['card-stats', 'surface', tone]}>
    <span class="stats-label secondary">{label}</span>
    <span class="stats-value">{value}</span>
    {#if detail}<span class="stats-detail secondary">{detail}</span>{/if}
    {#if progress !== undefined}
        <div class="stat-progress" style:--p={progress}>
            <div class="stat-progress__fill"></div>
        </div>
    {/if}
</div>

<style>
    .stats-value {
        color: var(--tile-clr);
    }

    .card-stats {
        --tile-clr: var(--accent-strong);

        position: relative; /* so stat-progress bar takes full width */
        /* Pct bar across bottom of card */
        display: grid;
        grid-template-columns: 1fr auto;
        grid-template-areas:
            'label detail'
            'value value';
        gap: var(--space-sm);
        padding: var(--space-sm);
        &.good {
            --tile-clr: var(--clr-success);
        }
        &.bad {
            --tile-clr: var(--clr-error);
        }
    }
    .stats-label {
        grid-area: label;
    }
    .stats-detail {
        grid-area: detail;
    }
    .stats-value {
        grid-area: value;
    }

    .stat-progress {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 4px;
        background: rgba(255, 255, 255, 0.07);
        overflow: hidden;
        --p: 0;

        & .stat-progress__fill {
            height: 100%;
            width: 100%;
            transform: scaleX(calc(var(--p) / 100));
            transform-origin: left center;
            background: var(--tile-clr);
            transition: transform 0.2s cubic-bezier(0.22, 0.61, 0.36, 1);
        }
    }
</style>
