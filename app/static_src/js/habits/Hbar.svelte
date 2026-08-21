<script lang="ts">
    import { HabitsChart } from './barchart';
    import { habitsState } from './habitsState.svelte';

    let el: HTMLDivElement;
    let hbarChart: HabitsChart | undefined;
    $effect(() => {
        if (!habitsState.barData) return;
        hbarChart ??= new HabitsChart(el);
        hbarChart.updateBarChart(habitsState.barData);
    });
</script>

{#if habitsState.barData?.length}
    <div bind:this={el} id="hbar-chart-container"></div>
{:else}
    <div>no data</div>
{/if}
