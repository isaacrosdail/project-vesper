import * as d3 from 'd3';

import { showToolTip, hideToolTip } from '../shared/ui/tooltip';
import { apiRequest } from '../shared/services/api';

// OVERALL FLOW FOR A LINE CHART:
// 1. Define scales (xScale, yScale)
// 2. Create the axes generators
// 3. Call them on groups inside gRoot

type MetricType = 'steps' | 'weight' | 'calories' | 'sleep_duration_minutes';
type StaticLineMetric = 'calories' | 'sleep_duration_minutes';

type ApiMetricData = {
    date: string;
    value: string;
}

type LineDataPoint = {
    date: Date;
    value: number;
}

type LineData = {
    id: MetricType;
    values: LineDataPoint[];
}

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
    .attr("class", "chart-title")
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
const line = d3.line<LineDataPoint>()
    .x(d => xScale(d.date))
    .y(d => yScale(d.value))

const STATIC_LINE_CONFIG = {
    'calories': {
        class: "bmr-line",
        label: (d: number) => `BMR: ${d}`,
        color: "red",
        data: () => [bmrValue]
    },
    'sleep_duration_minutes': {
        class: "sleep-line",
        label: (d: number) => `Target: ${d}`,
        color: "red",
        data: () => [targetSleepDuration]
    }
}

function drawStaticLines(metricType: MetricType) {
    const config = STATIC_LINE_CONFIG[metricType as StaticLineMetric];
    if (!config) return;

    const staticLine = gChart.selectAll(`rect.${config.class.split(" ")[0]}`)
        .data(config.data())
        .join(
            enter => enter.append("rect")
                .attr("class", config.class)
                .attr("x", 0)
                .attr("y", (d: number) => yScale(d) - 1)
                .attr("width", innerWidth)
                .attr("height", 2)
                .attr("fill", config.color)
                .attr("opacity", 0.6),
            update => update
                .transition()
                .duration(200)
                .attr("y1", (d: number) => yScale(d))
                .attr("y2", (d: number) => yScale(d)),

        );
    staticLine.on('mouseenter', function(this: d3.BaseType, _event: any, d: number) {
        const el = this as SVGRectElement;
        showToolTip(el, config.label(d));
    }).on('mouseleave', hideToolTip);
}

function updateLineChart(data: LineDataPoint[], metricType: MetricType) {
    if (data.length === 0){ // if dataset is empty, bail so we can safely coalesce for .domains below
        return;
    }
    // Clear static lines
    gChart.selectAll(".bmr-line, .sleep-line").remove();

    xScale.domain(d3.extent(data, d => d.date) as [Date, Date]);
    yScale.domain(d3.extent(data, d => d.value) as [number, number]);

    gXAxis.call(d3.axisBottom(xScale).tickFormat((d) => d3.timeFormat("%m/%d")(d as Date)));
    gYAxis.call(d3.axisLeft(yScale).ticks(ticks));

    const metricLine = gChart.selectAll<SVGPathElement, LineData>("path.line")
        // .data([data])
        // This makes each metric a datum
        .data([{
            id: metricType,
            values: data
        }], d => d.id) // use stable ID key
        .join(
            enter => {
                return enter.append("path")
                    .attr("class", "line")
                    .attr("fill", "none")
                    .attr("stroke", "steelblue")
                    .attr("stroke-width", 2)
                    .attr("d", (d: any) => line(d.values));
            },
            update => update
                .transition()
                .duration(200)
                .attr("d", (d: any) => line(d.values)), // re-draw on update
            exit => exit.remove()
        );

    const circles = gChart.selectAll<SVGCircleElement, LineDataPoint>("circle")
        .data(data, d => d.date.getTime()) // using .getTime(): more stable than raw Date objs?
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

    circles.on('mouseenter', function(this: d3.BaseType, _event: any, d: LineDataPoint) {
        const el = this as SVGRectElement;
        showToolTip(el, `${metricType}: ${d.value}`)
    });
    circles.on('mouseleave', () => {
        hideToolTip();
    })

    // update title text
    d3.select("#line-chart-title")
        .text(TYPE_LABELS[metricType]);

}

const TYPE_LABELS: Record<MetricType, string> = {
    weight: "Weight",
    steps: "Steps",
    calories: "Calories",
    sleep_duration_minutes: "Sleep Duration (mins)"
}

export async function init() {
    const initialData = await getMetricData('weight', 7);
    updateLineChart(initialData, 'weight');

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.type-selection')) {
            const metricType = target.dataset['type']! as MetricType;
            const data = await getMetricData(metricType, 7);
            updateLineChart(data, metricType);
            drawStaticLines(metricType);
        }
    });
}

function getMetricData(metric_type: MetricType, lastNDays: number): Promise<LineDataPoint[]> {
    return new Promise((resolve, reject) => {
        const url = `/metrics/daily_entries/timeseries?metric_type=${metric_type}&lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            // Coerce date strings to Date objects
            const chartData = responseData.data.map((d: ApiMetricData) => ({
                date: new Date(d.date),
                value: parseFloat(d.value),
            }));

            resolve(chartData);
        }, reject);
    });
}