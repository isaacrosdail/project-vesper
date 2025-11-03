import * as d3 from 'd3';

import { apiRequest } from '../shared/services/api';
import { showToolTip, hideToolTip } from '../shared/ui/tooltip';

// Dimensions
const margin = { top: 20, right: 30, bottom: 40, left: 90 };
const width = 350 - margin.left - margin.right;
const height = 350 - margin.top - margin.bottom;

// Set up chart svg as a whole
const svg = d3.select(".chart-container")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)

const title = svg.append("text")
    .attr("x", (width/2))
    .attr("y", -margin.top/2)
    .attr("font-size", "var(--font-size-l)")
    .text("Completions by Habit")

const gXAxis = svg.append("g")
    .attr("class", "axis-x")
    .attr("transform", `translate(0, ${height})`);
const gYAxis = svg.append("g")
    .attr("class", "axis-y");

const xScale = d3.scaleLinear().range([0, width]);
const yScale = d3.scaleBand().range([0, height]).padding(0.2);

function updateBarChart(data) {
    // Update axes
    xScale.domain([0, d3.max(data, d => d.count)])
    yScale.domain(data.map(d => d.name))

    gXAxis.call(
        d3.axisBottom(xScale)
            .tickValues(d3.range(0, d3.max(data, d => d.count) + 1, 1))
        )
    gYAxis.call(d3.axisLeft(yScale));

    const bars = svg.selectAll("rect")
    .data(data)
    .join(
        enter => {
            return enter.append("rect")
                .attr("x", 0)
                .attr("y", d => yScale(d.name))
                .attr("width", 0)
                .attr("height", yScale.bandwidth())
                .attr("fill", "var(--accent-strong)")
                .attr("class", "line")
                .transition()
                .duration(500)
                .attr("width", d => xScale(d.count))
        },
        update => update
            .transition()
            .duration(200)
            .attr("width", d => xScale(d.count)),
        exit => exit.remove()
    );

    bars.on('mouseenter', function(event, d) {
        showToolTip(this, `${d.name}: ${d.count}`);
    })
    .on('mouseleave', function() {
        hideToolTip();
    });
}

export async function init() {
    const data = await getHabitsData(1);
    updateBarChart(data);

    document.addEventListener('click', async (e) => {
        if (e.target.matches('.timeframe-selection')) {
            const range = parseInt(e.target.dataset.range, 10);
            const newData = await getHabitsData(range);
            updateBarChart(newData);
        }
    });
}

function getHabitsData(lastNDays) {
    return new Promise((resolve, reject) => {
        const url = `/habits/completions/summary?lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            const entries = responseData.data;
            resolve(entries);
        }, reject);
    });
}