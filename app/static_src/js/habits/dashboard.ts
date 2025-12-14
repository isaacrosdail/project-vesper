import * as d3 from 'd3';

import { apiRequest } from '../shared/services/api';
import { showToolTip, hideToolTip } from '../shared/ui/tooltip';

type BarData = {
    name: string;
    count: number;
}

const chartState = {
    range: 7,
}

// Dimensions
const margin = { top: 20, right: 30, bottom: 40, left: 90 };
const width = 400;
const height = 300;
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

// Set up chart svg as a whole
const svg = d3.select("#habits-chart-container")
    .append("svg")
        .attr("width", width)
        .attr("height", height)

const gRoot = svg.append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)

const _title = svg.append("text")
    .attr("x", innerWidth/2)
    .attr("y", margin.top/2)
    .attr("font-size", "var(--font-size-l)")
    .attr("fill", "var(--text)")
    .text("Completions by Habit")

const gXAxis = gRoot.append("g")
    .attr("class", "axis-x")
    .attr("transform", `translate(0, ${innerHeight})`);
const gYAxis = gRoot.append("g")
    .attr("class", "axis-y");
const gChart = gRoot.append("g")
    .attr("class", "chart");

const xScale = d3.scaleLinear().range([0, innerWidth]);
const yScale = d3.scaleBand().range([0, innerHeight]).padding(0.2);

function updateBarChart(data: BarData[]) {

    gChart.selectAll(".empty-message").remove();

    // Update axes
    xScale.domain([0, d3.max(data, (d: BarData) => d.count)!])
    yScale.domain(data.map(d => d.name))

    gXAxis.call(
        d3.axisBottom(xScale)
            .tickValues(d3.range(0, d3.max(data, (d: BarData) => d.count)! + 1, 1))
        )
    gYAxis.call(d3.axisLeft(yScale));

    const bars = gChart.selectAll("rect.bar")
    .data(data)
    .join(
        enter => {
            const rects = enter.append("rect")
                .attr("x", 0)
                .attr("y", (d: BarData) => yScale(d.name)!)
                .attr("width", 0)
                .attr("height", yScale.bandwidth())
                .attr("fill", "var(--accent-strong)")
                .attr("class", "bar")
            
            rects.transition()
                .duration(200)
                .attr("width", (d: BarData) => xScale(d.count))

            return rects
        },
        update => update
            .transition()
            .duration(200)
            .attr("width", (d: BarData) => xScale(d.count))
            .attr("height", yScale.bandwidth()),
        exit => exit.remove()
    );

    bars.on('mouseenter', function(this: d3.BaseType, _event: Event, d: BarData) {
        showToolTip(this as SVGRectElement, `${d.name}: ${d.count}`);
    }).on('mouseleave', hideToolTip);
}

function showEmptyChart() {
    gChart.selectAll('rect.bar').remove();

    // Clear axes
    yScale.domain([]); // empty domain = no tick labels
    gYAxis.call(d3.axisLeft(yScale));

    xScale.domain([]);
    gXAxis.call(d3.axisBottom(xScale));

    const _emptyMessage = gChart.selectAll('text.empty-message')
        .data([1])
        .join("text")
        .attr("class", "empty-message")
        .attr("x", innerWidth/2)
        .attr("y", innerHeight/2)
        .attr("text-anchor", "middle")
        .attr("fill", "grey")
        .text("No completion data for this period.")
}

async function refreshBarChart() {
    const data = await getHabitsData(chartState.range);
    console.log(data)
    if (data.length === 0) {
        showEmptyChart();
        return;
    }
    updateBarChart(data);
}

export async function init() {
    await refreshBarChart();

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        
        if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!, 10);
            await refreshBarChart();
        }
        else if (target.matches('.table-range')) {
            const range = target.dataset['range']!;
            window.location.href = `/habits/dashboard?range=${range}`;
        }
    });
}

function getHabitsData(lastNDays: number): Promise<BarData[]> {
    return new Promise((resolve, reject) => {
        const url = `/habits/completions/summary?lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            const entries = responseData.data;
            resolve(entries);
        }, reject);
    });
}