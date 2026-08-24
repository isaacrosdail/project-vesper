<script lang="ts">
    import { ConsistencyMap } from "./consistency";
    import { metricsData, metricsState } from "./../metricsState.svelte";

    let { targets } = $props();

    let el: HTMLDivElement;
    let map: ConsistencyMap | undefined;
    $effect(() => {
        map ??= new ConsistencyMap(el);
        map.renderGrid(metricsData.series, targets, metricsState.selected, metricsState.range);
    });
</script>
<div bind:this={el} id="consistency-map-chart-container" class="triple-row-chart"></div>
