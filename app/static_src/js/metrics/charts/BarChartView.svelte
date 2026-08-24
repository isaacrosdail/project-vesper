<script lang="ts">
  import { MetricsBarChart } from "./barchart";
  import { metricsState, metricsData } from "./../metricsState.svelte";

  let {
    referenceLines,
    targets,
  }: {
    referenceLines: any;
    targets: any;
  } = $props();

  let el: HTMLDivElement;
  let chart: MetricsBarChart | undefined;
  $effect(() => {
    chart ??= new MetricsBarChart(el, referenceLines, targets);
    chart.update(metricsData.series, metricsState.selected, metricsState.range);
  });
</script>

<div bind:this={el} id="metrics-bar-chart-container"></div>

<style>
  /* For diff shading for bars that are under target val: */
  div :global(.bar) {
    fill: var(--metric-color);
  }
  div :global(.bar.under-target) {
    fill: color-mix(in srgb, var(--metric-color) 35%, var(--bg));
  }
</style>
