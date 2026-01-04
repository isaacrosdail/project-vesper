import * as d3 from 'd3';

import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { apiRequest } from '../shared/services/api';
import { getChartDimensions, D3_TRANSITION_DURATION_MS } from '../shared/charts';

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

const chartState = {
    metricType: 'weight' as MetricType,
    range: 7,
}

// Hardcoding BMR for calories, target duration for sleep
const bmrValue = 2000;
const targetSleepDuration = 7 * 60; // 7 hr

// Graph formatting
const ticks = 7;

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

const TYPE_LABELS: Record<MetricType, string> = {
    weight: "Weight",
    steps: "Steps",
    calories: "Calories",
    sleep_duration_minutes: "Sleep Duration (mins)"
}

async function getMetricData(metric_type: MetricType, lastNDays: number): Promise<LineDataPoint[]> {
    const params = new URLSearchParams({
        metric_type,
        lastNDays: lastNDays.toString()
    });
    const url = `/metrics/daily_metrics/timeseries?${params}`;
    const response = await apiRequest('GET', url, null);

    const chartData = response.data.map((d: ApiMetricData) => ({
        date: new Date(d.date),
        value: parseFloat(d.value),
    }));
    return chartData;
}

class MetricsChart {
    private gLines;
    private xScale;
    private yScale;
    private gXAxis;
    private gYAxis;
    private dims;
    private line;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 20, bottom: 20, left: 30, right: 40 });

        const svg = d3.select(containerSelector)
            .append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height);

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);
        
            // Title for lineChart
        const _title = svg.append("text")
            .attr("id", "line-chart-title")
            .attr("class", "chart-title")
            .attr("x", this.dims.width/2)
            .attr("y", this.dims.margin.top/2)
            .attr("text-anchor", "middle")
            .attr("font-size", "var(--font-size-lg)")
            .attr("font-weight", "var(--font-weight-semibold)")
            .text("Initial Title");

        // Groups inside svg
        this.gXAxis = gRoot.append("g")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)
            .attr("class", "axis-x");
        this.gYAxis = gRoot.append("g")
            .attr("class", "axis-y");
        this.gLines = gRoot.append("g")
            .attr("class", "chart");

        // Create scales. Define only range/pixel values since data is dynamic
        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth]);
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0]);

        this.line = d3.line<LineDataPoint>()
            .x(d => this.xScale(d.date))
            .y(d => this.yScale(d.value))
    }

    drawStaticLines(metricType: MetricType) {
        const config = STATIC_LINE_CONFIG[metricType as StaticLineMetric];
        if (!config) return;

        const staticLine = this.gLines.selectAll(`rect.${config.class.split(" ")[0]}`)
            .data(config.data())
            .join(
                enter => enter.append("rect")
                    .attr("class", config.class)
                    .attr("x", 0)
                    .attr("y", (d: number) => this.yScale(d) - 1)
                    .attr("width", this.dims.innerWidth)
                    .attr("height", 2)
                    .attr("fill", config.color)
                    .attr("opacity", 0.6),
                update => update
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("y1", (d: number) => this.yScale(d))
                    .attr("y2", (d: number) => this.yScale(d)),

            );
        staticLine.on('mouseenter', function(this: d3.BaseType, _event: Event, d: number) {
            const el = this as SVGRectElement;
            createTooltip(el, config.label(d));
        }).on('mouseleave', removeTooltip);
    }

    updateLineChart(data: LineDataPoint[], metricType: MetricType) {
        // Clear static lines
        this.gLines.selectAll(".bmr-line, .sleep-line").remove();
        this.gLines.selectAll(".empty-message").remove();

        this.xScale.domain(d3.extent(data, d => d.date) as [Date, Date]);

        const dataValues = data.map(d => d.value);
        let combinedValues = dataValues;
        const config = STATIC_LINE_CONFIG[metricType as StaticLineMetric];
        if (config) {
            // grab vals
            const staticLineValues = config.data();
            combinedValues = [...dataValues, ...staticLineValues]; // spread both arrays
        }
        const [min, max] = d3.extent(combinedValues) as [number, number];
        this.yScale.domain([Math.floor(min * 0.7), max * 1.1]);

        this.gXAxis.call(d3.axisBottom(this.xScale).tickFormat((d) => d3.timeFormat("%m/%d")(d as Date)));
        this.gYAxis.call(d3.axisLeft(this.yScale).ticks(ticks));

        const _metricLine = this.gLines.selectAll<SVGPathElement, LineData>("path.line")
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
                        .attr("stroke", "var(--accent-strong)")
                        .attr("stroke-width", 2)
                        .attr("d", (d: LineData) => this.line(d.values));
                },
                update => update
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("d", (d: LineData) => this.line(d.values)),
                exit => exit.remove()
            );

        const circles = this.gLines.selectAll<SVGCircleElement, LineDataPoint>("circle")
            .data(data, d => d.date.getTime()) // .getTime() -> more stable than Date objects
            .join(
                enter => {
                    return enter.append("circle")
                        .attr("r", 0)
                        .attr("fill", "var(--accent-strong)")
                        .attr("cx", d => this.xScale(d.date))
                        .attr("cy", d => this.yScale(d.value))
                        .transition()
                        .duration(D3_TRANSITION_DURATION_MS)
                        .attr("r", 4);
                },
                update => update
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("cx", d => this.xScale(d.date))
                    .attr("cy", d => this.yScale(d.value)),
                exit => exit.remove()
            );

        d3.select("#line-chart-title")
            .text(TYPE_LABELS[metricType]);

        circles.on('mouseenter', function(this: d3.BaseType, _event: Event, d: LineDataPoint) {
            const el = this as SVGRectElement;
            createTooltip(el, `${metricType}: ${d.value}`)
        });
        circles.on('mouseleave', () => {
            removeTooltip();
        })
    }

    showEmptyChart(metricType: MetricType) {
        this.gLines.selectAll("path.line").remove();
        this.gLines.selectAll("circle").remove();
        this.gLines.selectAll(".bmr-line, .sleep-line").remove();

        const _emptyMessage = this.gLines.selectAll("text.empty-message")
            .data([metricType])
            .join("text")
            .attr("class", "empty-message")
            .attr("x", this.dims.innerWidth / 2)
            .attr("y", this.dims.innerHeight / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "grey")
            .text(`No ${TYPE_LABELS[metricType]} data for this period.`)

        d3.select("#line-chart-title")
            .text(TYPE_LABELS[metricType])
    }

    async refreshLineChart() {
        const data = await getMetricData(chartState.metricType, chartState.range);
        if (data.length === 0) {
            this.showEmptyChart(chartState.metricType);
            return;
        }
        this.updateLineChart(data, chartState.metricType);
        this.drawStaticLines(chartState.metricType);
    }
}

export async function init() {
    const metricsChart = new MetricsChart('#metrics-chart-container');
    await metricsChart.refreshLineChart();

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.chart-type')) {
            chartState.metricType = target.dataset['type']! as MetricType;
            await metricsChart.refreshLineChart();
        }
        else if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!);
            await metricsChart.refreshLineChart();
        }
        else if (target.matches('.table-range')) {
            const range = target.dataset['range']!;
            const table = target.dataset['table']!;

            const url = new URL(window.location.href);
            url.searchParams.set(`${table}_range`, range);
            window.location.href = url.toString();
        }
    });
}