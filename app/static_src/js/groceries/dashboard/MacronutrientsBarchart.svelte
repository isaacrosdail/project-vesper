
<script lang="ts">
    import { MacrosBarChart } from './maconutrientsBarchart';

    let el: HTMLDivElement;
    let chart: MacrosBarChart | undefined;
    $effect(() => {
        chart ??= new MacrosBarChart(el, 2200);
        chart.update(dummyData);
    });

    const dummyData = [
        { date: '2026-07-27', calories: 2340 },
        { date: '2026-07-28', calories: 2150 },
        { date: '2026-07-29', calories: 1780 },
        { date: '2026-07-30', calories: 2600 },
        { date: '2026-07-31', calories: 1950 },
        { date: '2026-08-01', calories: 0 },
        { date: '2026-08-02', calories: 2210 },
    ];
</script>

<div bind:this={el}></div>

<style>
    :global(.bar) {
        fill: var(--macro-color);
    }
</style>