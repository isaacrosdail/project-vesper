import * as d3 from 'd3';

import { showToolTip, hideToolTip } from '../shared/ui/tooltip';
import { apiRequest } from '../shared/services/api';

// OVERALL FLOW FOR A LINE CHART:
// 1. Define scales (xScale, yScale)
// 2. Create the axes generators
// 3. Call them on groups inside gRoot

// Hardcoding BMR for calories, target duration for sleep
const bmrValue = 2000;
const targetSleepDuration = 7 * 60; // 7hrs in minutes

// Dimensions & margins
const height = 300;
const width = 500;
const margin = { top: 20, right: 20, bottom: 30, left: 40 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

// Graph formatting
const ticks = 7;

// Create second line chart (using dates now)
const svg = d3.select('#line-chart')
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const gRoot = svg.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

// Title for lineChart
const title = svg.append("text")
    .attr("id", "line-chart-title")
    .attr("x", width/2)
    .attr("y", margin.top/2)
    .attr("text-anchor", "middle")
    .attr("font-size", "16px")
    .attr("font-weight", "bold")
    .text("Initial Title");

// Groups inside svg
const gXAxis = gRoot.append("g")
    .attr("transform", `translate(0, ${innerHeight})`)
    .attr("class", "axis-x");
const gYAxis = gRoot.append("g")
    .attr("class", "axis-y");
const gChart = gRoot.append("g")
    .attr("class", "chart");

// Create scales
// Define only range/pixel values since data is dynamic
const xScale = d3.scaleTime().range([0, innerWidth]);
const yScale = d3.scaleLinear().range([innerHeight, 0]);

// Line generator: Turns [ {date,value}...] into a smooth path string
const line2 = d3.line()
    .x(d => xScale(d.date))
    .y(d => yScale(d.value))

const STATIC_LINE_CONFIG = {
    'calories': {
        class: "bmr-line tooltip",
        label: d => `BMR: ${d}`,
        color: "red",
        data: () => [bmrValue]
    },
    'sleep_duration_minutes': {
        class: "sleep-line tooltip",
        label: d => `Target: ${d}`,
        color: "red",
        data: () => [targetSleepDuration]
    }
}

function drawStaticLines(metricType) {
    const config = STATIC_LINE_CONFIG[metricType];
    if (!config) return;

    const line = gChart.selectAll(`rect.${config.class.split(" ")[0]}`)
        .data(config.data())
        .join(
            enter => enter.append("rect")
                .attr("class", config.class)
                .attr("x", 0)
                .attr("y", d => yScale(d) - 1)
                .attr("width", innerWidth)
                .attr("height", 2)
                .attr("fill", config.color)
                .attr("opacity", 0.6),
            update => update
                .transition()
                .duration(200)
                .attr("y1", d => yScale(d))
                .attr("y2", d => yScale(d)),
            exit => exit.remove()
        );
    line.on('mouseenter', function(event, d) {
        showToolTip(this, config.label(d));
    }).on('mouseleave', hideToolTip);
}

function updateLineChart(data, metricType) {

    // Clear static lines
    gChart.selectAll(".bmr-line, .sleep-line").remove();

    xScale.domain(d3.extent(data, d => d.date))
    yScale.domain(d3.extent(data, d => d.value))

    gXAxis.call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%m/%d")));
    gYAxis.call(d3.axisLeft(yScale).ticks(ticks));

    const thing = gChart.selectAll("path.line")
        // .data([data])
        // This makes each metric a datum
        .data([{
            id: metricType,
            values: data
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

    const circles = gChart.selectAll("circle")
        .data(data, d => d.date)
        .join(
            enter => {
                return enter.append("circle")
                // We can have r start at 0 and add a transition in the enter to make them animate in
                    .attr("r", 0)
                    .attr("fill", "var(--accent-strong")
                    .attr("cx", d => xScale(d.date))
                    .attr("cy", d => yScale(d.value))
                    .transition()
                    .duration(200)
                    .attr("r", 4);
            },
            update => update
                .transition()
                .duration(200)
                .attr("cx", d => xScale(d.date))
                .attr("cy", d => yScale(d.value)),
            exit => exit.remove()
        );

    circles.on('mouseenter', function(_event, d) {
        showToolTip(this, `${metricType}: ${d.value}`)
    });
    circles.on('mouseleave', () => {
        hideToolTip();
    })

    // update title text
    d3.select("#line-chart-title")
        .text(metricType.charAt(0).toUpperCase() + metricType.slice(1));

}

const TYPE_LABELS = {
    weight: "Weight",
    steps: "Steps",
    calories: "Calories",
    sleep_duration_minutes: "Sleep Duration (mins)"
}

export async function init() {
    const initialData = await getMetricData('weight', 7);
    updateLineChart(initialData, 'Weight');

    document.addEventListener('click', async (e) => {
        if (e.target.matches('.type-selection')) {
            const metric_type = e.target.dataset.type;
            const data = await getMetricData(metric_type, 7);
            updateLineChart(data, TYPE_LABELS[metric_type]);
            drawStaticLines(metric_type);
        }
    });
}

function getMetricData(metric_type, lastNDays) {
    return new Promise((resolve, reject) => {
        const url = `/metrics/daily_entries/timeseries?metric_type=${metric_type}&lastNDays=${lastNDays}`;
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