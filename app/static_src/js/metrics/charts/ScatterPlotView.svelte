<script lang="ts">
    import { ScatterPlot } from "./scatterplot";
    import { getPairs, metricsData } from "./../metricsState.svelte";

    let { regressionSlope, regressionIntercept } = $props();
    let el: HTMLDivElement;
    let scatterPlot: ScatterPlot | undefined;
    $effect(() => {
        scatterPlot ??= new ScatterPlot(el);
        scatterPlot.update(getPairs(), regressionSlope, regressionIntercept);
    });
</script>
<div bind:this={el} id="scatter-plot-chart-container" class="triple-row-chart"></div>


<style>
        /* For metrics scatterplot correlation chart */
    :global(.regression-line) {
    stroke: var(--metric-color);
    stroke-width: 2;
    stroke-dasharray: 2,4;
    }
</style>