import * as d3 from 'd3';

import { apiRequest } from '../shared/services/api';

// OVERALL FLOW FOR A LINE CHART:
// 1. Define scales (xScale, yScale)
// 2. Create the axes generators
// 3. Call them on groups inside gRoot


// Dimensions
const height = 300;
const width = 500;
const margin = { top: 20, right: 20, bottom: 30, left: 40 };

const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

// Dummy dataset
const dataDate = [
    { date: new Date(2025, 9, 22), value: 200 },
    { date: new Date(2025, 9, 23), value: 205 },
    { date: new Date(2025, 9, 24), value: 196 },
    { date: new Date(2025, 9, 27), value: 220 },
];
const data = [
    { day: 1, weight: 200 },
    { day: 2, weight: 205 },
    { day: 3, weight: 196 },
    { day: 4, weight: 220 },
];
const data2 = [
    { day: 1, weight: 200 },
    { day: 2, weight: 205 },
    { day: 3, weight: 196 },
    { day: 4, weight: 220 },
    { day: 5, weight: 234 },
    { day: 6, weight: 220 },
    { day: 7, weight: 213 },
];
// Create the SVG itself
const svg = d3.select('#line-chart')
    .append("svg")
    .attr("width", width)
    .attr("height", height);

// Create the <g> that acts as the inner drawing area
// Inside this, we later put stuff like g.axis-x, g.axis-y, g.legend, etc?
const gRoot = svg.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

// Groups inside svg
const gXAxis = gRoot.append("g").attr("class", "axis-x");
const gYAxis = gRoot.append("g").attr("class", "axis-y");
const gChart = gRoot.append("g").attr("class", "chart");

// Create scales
const xScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.day))
    .range([0, innerWidth])

const yScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.weight))
    .range([innerHeight, 0]) // Remember: pixel space flipped vertically

// Line generator
const line = d3.line()
    .x(d => xScale(d.day))
    .y(d => yScale(d.weight));


// Create second line chart (using dates now)
const svg2 = d3.select('#line-chart')
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const gRoot2 = svg2.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

// Title for line2Chart
const title = svg2.append("text")
    .attr("id", "line-chart-title")
    .attr("x", width/2)
    .attr("y", margin.top/2)
    .attr("text-anchor", "middle")
    .attr("font-size", "16px")
    .attr("font-weight", "bold")
    .text("Initial Title");

// Groups inside svg
const g2XAxis = gRoot2.append("g").attr("class", "axis-x");
const g2YAxis = gRoot2.append("g").attr("class", "axis-y");
const g2Chart = gRoot2.append("g").attr("class", "chart");

// Create scales
const x2Scale = d3.scaleTime()
    .domain(d3.extent(dataDate, d => d.date))
    .range([0, innerWidth])

const y2Scale = d3.scaleLinear()
    .domain(d3.extent(dataDate, d => d.value))
    .range([innerHeight, 0])

// Line generator
const line2 = d3.line()
    .x(d => x2Scale(d.date))
    .y(d => y2Scale(d.value))

function updateLine2Chart(dataDate, metricType) {

    x2Scale.domain(d3.extent(dataDate, d => d.date))
    y2Scale.domain(d3.extent(dataDate, d => d.value))

    g2XAxis.attr("transform", `translate(0, ${innerHeight})`)
           .call(d3.axisBottom(x2Scale));
    g2YAxis.call(d3.axisLeft(y2Scale));

    const thing = g2Chart.selectAll("path.line")
        // .data([dataDate])
        // This makes each metric a datum
        .data([{
            id: metricType,
            values: dataDate
        }], d => d.id) // use stable ID key
        .join(
            enter => {
                return enter.append("path")
                    .attr("class", "line tooltip")
                    .attr("fill", "none")
                    .attr("stroke", "steelblue")
                    .attr("stroke-width", 2)
                    .attr("d", d => line2(d.values));
            },
            update => update
                .transition()
                .duration(200)
                .attr("d", d => line2(d.values)), // re-draw on update
            exit => exit.remove()
        );


    const circles = g2Chart.selectAll("circle")
        .data(dataDate, d => d.date)
        .join(
            enter => {
                return enter.append("circle")
                // Instead of this:
                    // .attr("r", 4)
                    // .attr("fill", "steelblue")
                    // .attr("cx", d => x2Scale(d.date))
                    // .attr("cy", d => y2Scale(d.value));
                // We can have r start at 0 and add a transition in the enter to make them animate in
                    .attr("r", 0)
                    .attr("fill", "steelblue")
                    .attr("cx", d => x2Scale(d.date))
                    .attr("cy", d => y2Scale(d.value))
                    .transition()
                    .duration(200)
                    .attr("r", 4);
            },
            update => update
                .transition()
                .duration(200)
                .attr("cx", d => x2Scale(d.date))
                .attr("cy", d => y2Scale(d.value)),
            exit => exit.remove()
        );

    // update title text
    d3.select("#line-chart-title")
        .text(metricType.charAt(0).toUpperCase() + metricType.slice(1));

}

function updateLineChart(data) {
    // 1. Update scales
    xScale.domain(d3.extent(data, d => d.day));
    yScale.domain(d3.extent(data, d => d.weight));

    // 2. Draw/update axes
    gXAxis.attr("transform", `translate(0, ${innerHeight})`)
          .call(d3.axisBottom(xScale));
    gYAxis.call(d3.axisLeft(yScale));

    // 3. Draw/update the line
    gChart.selectAll("path.line")
    // Since we want one line per data SET, not data point, we either use .data([data]) to pass an array containing our dataset as one item OR use .datum(data)
    // Note if we want enter/update behavior, we need to use .data([data])
        .data([data]) // one path per dataset
        .join("path")
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2)
        .attr("d", line);
}

export function init() {

    updateLineChart(data);
    updateLine2Chart(dataDate, 'Dummy Data');

    document.addEventListener('click', async (e) => {
        if (e.target.matches('.type-selection')) {
            const type = e.target.dataset.type;
            if (type === '1') {
                updateLineChart(data);
            } else if (type === '2') {
                console.log(data2);
                updateLineChart(data2);
            } else if (type === 'real2') {
                const realData2 = await getMetricData('weight', 7);
                updateLine2Chart(realData2, 'weight');
            } else if (type === 'steps7') {
                const realData3 = await getMetricData('steps', 7);
                updateLine2Chart(realData3, 'steps');
            }
        }
    });
}

function getMetricData(type, lastNDays) {
    return new Promise((resolve, reject) => {
        const url = `/metrics/daily_entries/linechart?type=${type}&lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            const entries = responseData.data;
            console.log(entries);

            // Coerce date strings to Date objects
            const chartData = responseData.data.map(d => ({
                date: new Date(d.date),
                value: parseFloat(d.value),
            }));

            resolve(chartData);
        }, reject);
    });
}