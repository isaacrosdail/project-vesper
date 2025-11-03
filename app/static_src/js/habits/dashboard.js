import * as d3 from 'd3';

import { apiRequest } from '../shared/services/api';

// Arr of objs, each w/ date & count
const dummyData = [
    {date: new Date(2025, 9, 10), count: 3},
    {date: new Date(2025, 9, 10), count: 2},
    {date: new Date(2025, 9, 10), count: 4},
    {date: new Date(2025, 9, 10), count: 2},
    {date: new Date(2025, 9, 10), count: 5},
    {date: new Date(2025, 9, 10), count: 3},
]
const hbarData = [
    { category: "A", count: 6},
    { category: "B", count: 12},
    { category: "C", count: 3},
    { category: "D", count: 8},
]

// Dimensions
const margin = { top: 20, right: 30, bottom: 40, left: 90 };
const width = 400 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

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
    .attr("font-size", "var(--font-size-xl)")
    .text("hey")

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

    gXAxis.call(d3.axisBottom(xScale))
        // Then rotates the text for x-axis info to fit slightly better
        .selectAll("text")
            .attr("transform", "translate(-10,0)rotate(-45)")
            .attr("text-anchor", "end");
    gYAxis.call(d3.axisLeft(yScale));

    const graph = svg.selectAll("rect")
    .data(data)
    .join(
        enter => {
            return enter.append("rect")
                .attr("x", 0) // start at same horizontal point
                .attr("y", d => yScale(d.name)) // 
                .attr("width", 0)
                .attr("height", yScale.bandwidth())
                .attr("fill", "var(--accent-strong)")
                .transition()
                .duration(500)
                .attr("width", d => xScale(d.count)) // Start at 0 width above & transition to full
        },
        update => update
            .transition()
            .duration(200)
            .attr("width", d => xScale(d.count)),
        exit => exit.remove()
    );
}

export async function init() {
    const data = await getHabitsData(5);
    updateBarChart(data);
}

function getHabitsData(lastNDays) {
    return new Promise((resolve, reject) => {
        const url = `/habits/completions/hbarchart?lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            const entries = responseData.data;
            console.log(entries)
            resolve(entries);
        }, reject);
    });
}