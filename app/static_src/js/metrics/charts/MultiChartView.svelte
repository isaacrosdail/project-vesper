<script lang="ts">
    import { MultiChart } from "./multichart";
    import { getMultiData, metricsState } from "./../metricsState.svelte";

    let { hiddenLines }: {
        hiddenLines: any;
    } = $props();

    let el: HTMLDivElement;
    let chart: MultiChart | undefined;
    $effect(() => {
        chart ??= new MultiChart(el);
        chart.update(getMultiData(), metricsState.range);
    });
    $effect(() => {
        chart?.setHidden(Object.keys(hiddenLines).filter(m => hiddenLines[m]));
    });
</script>
<div bind:this={el} id="multi-chart-container"></div>
