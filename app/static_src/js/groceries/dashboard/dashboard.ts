import * as d3 from 'd3';
import { mount } from 'svelte';

import { api } from '../../shared/services/api';
import { required } from '../../shared/dom';
import GroceriesDashboard from './GroceriesDashboard.svelte';

// Should become discrete bar chart prob? Days ARE distinct.
async function renderSparkline() {
    const response = await api.nutrition_log.summary(new URLSearchParams({ lastNDays: '10' }));
    const data = response.data.map(d => ({
        date: new Date(d.date),
        value: d.value
    }));
    const sparkline = d3.select('.sparkline-chart');
    const container = document.querySelector('.sparkline-chart')
    const width = container.clientWidth;
    const height = 40; // tiny

    const padding = 4;
    const x = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)])
        .range([height - padding, 0]);

    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.value));

    sparkline.append('svg')
        .attr('width', '100%')
        .attr('height', height)
        .append('path')
        .datum(data)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', 'var(--accent-strong)')
        .attr('stroke-width', 1.5);

    // TODO: clean this up, but also swap days and avg texts:
    const daysSpan = document.querySelector('.days');
    const avgSpan = document.querySelector('.avg');
    const avg = data.reduce((sum, curr) => sum + curr.value, 0) / data.length;
    daysSpan.textContent = `${data.length} days`;
    avgSpan.textContent = `avg: ${avg.toFixed(0)}kcal`;

    // remove "loading" effect w shimmer:
    [daysSpan, avgSpan]?.forEach(el => el.classList.remove('loading'))
}

export async function init() {

    mount(GroceriesDashboard, {
        target: required(document.querySelector('#groceries-dashboard-root'), '#groceries-dashboard-root')
    });
    // await renderSparkline(); // TODO(svelte): D3-wrap component lesson
}
