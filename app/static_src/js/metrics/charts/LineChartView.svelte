<script lang="ts">
    import { MetricsLineChart } from "./linechart";
    import { metricsData, metricsState } from "./../metricsState.svelte";

    let { referenceLines, targets }: {
        referenceLines: any;
        targets: any;
    } = $props();

    let el: HTMLDivElement;
    let chart: MetricsLineChart | undefined;
    $effect(() => {
        chart ??= new MetricsLineChart(el, referenceLines, targets);
        chart.update(metricsData.series, metricsState.selected, metricsState.range);
    });
</script>
<div bind:this={el} id="metrics-line-chart-container"></div>


<style>
    /* Gradient for metrics (weight) line chart */
    :global(.area-stop-top) {
        stop-color: var(--metric-color, var(--accent-strong));
        stop-opacity: 0.30;
    }
    :global(.area-stop-bottom) {
        stop-color: var(--metric-color, var(--accent-strong));
        stop-opacity: 0;
    }
</style>