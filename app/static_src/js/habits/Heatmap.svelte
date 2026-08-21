<script lang="ts">
    import type { HeatmapApiEntry } from './heatmap';
    import { HabitsHeatmap } from './heatmap';

    let {
        data,
    }: {
        data: HeatmapApiEntry[] | null;
    } = $props();

    let el: HTMLDivElement;
    let heatmap: HabitsHeatmap | undefined;
    $effect(() => {
        if (!data) return;
        heatmap ??= new HabitsHeatmap(el);
        heatmap.render(data);
    });
</script>

<div bind:this={el} id="heatmap-chart-container"></div>
