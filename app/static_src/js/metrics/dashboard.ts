import * as d3 from 'd3';

import { applyXAxisRotation, D3_TRANSITION_DURATION_MS, getChartDimensions, getTickValues, hourMinsDisplay, initChartRangeButtons, showEmptyChartMessage } from '../shared/charts';
import { initMetricsForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { getNumPref } from '../shared/services/userStore';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager';
import { FormDialog } from '../types';


type ApiMetricData = {
    date: string;
    value: string;
}

type LineDataPoint = {
    date: Date;
    value: number;
}

type LineData = {
    id: LineMetricType;
    values: LineDataPoint[];
}

interface ChartState {
    selected: MetricType | 'all';
    range: number;
}
const chartState: ChartState = {
    selected: 'all',
    range: 7,
}

type BarMetricType = 'steps' | 'calories' | 'sleep_duration_minutes';
type LineMetricType = 'weight';
type MetricType = BarMetricType | LineMetricType;
type StaticLineMetric = 'calories' | 'sleep_duration_minutes';

const BAR_METRICS: BarMetricType[] = ['steps', 'calories', 'sleep_duration_minutes'] as const;
const LINE_METRICS: LineMetricType[] = ['weight'] as const;
const ticks = 7; // Graph formatting
const D3_GRIDLINES_OPACITY = 0.7;
const D3_GRIDLINES_DASHARR_VALS = "2,4"; // 2px dash, 4px gap
const D3_OTHER_DIM_OPACITY = 0.4;

// Pull BMR from db? Could calc bmr from current weight periodically & re-store?
// Also: Store height in db and use that to calculate stride distance? That way we could convert: "5000 steps at 6'2" = 6.5 miles! nice!"
const bmrValue = 2000;

const TYPE_LABELS: Record<MetricType, string> = {
    weight: "Weight",
    steps: "Steps",
    calories: "Calories",
    sleep_duration_minutes: "Sleep (hrs)"
} as const;

class MultiChart {
    private dims;
    private gLines; gLegend; gTitle;
    private gXAxis; gYAxis;
    private xScale; yScale;
    private line;
    private color;
    private hiddenLines = new Set<BarMetricType | LineMetricType>;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 50, bottom: 30, left: 30, right: 100 });

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height)

        const gRoot = svg.append("g")
            .attr("class", "gRoot")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`)

        this.gXAxis = gRoot.append("g")
            .attr("class", "axis-x")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)
        this.gYAxis = gRoot.append("g")
            .attr("class", "axis-y")

        this.gLines = gRoot.append("g")
            .attr("class", "gLines")

        this.gTitle = gRoot.append("text")
            .attr("class", "chart-title")
            .attr("x", this.dims.innerWidth / 2)
            .attr("y", -this.dims.margin.top / 2)
            .attr("text-anchor", "middle")
            .text("Normalized Metric Variance")

        this.gLegend = gRoot.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(${this.dims.innerWidth}, 0)`)

        // Create scales
        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth])
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0])

        // Line generator
        this.line = d3.line<LineDataPoint>().curve(d3.curveMonotoneX) // TODO: unsure
            .x(d => this.xScale(d.date))
            .y(d => this.yScale(d.value))

        this.color = d3.scaleOrdinal(d3.schemeTableau10)
    }

    private syncHiddenLines() {
        this.gLines.selectAll(".multi-line")
            .attr("opacity", d => this.hiddenLines.has(d.id) ? 0 : 1);

        this.gLegend.selectAll(".multi-chart-legend")
            .attr("opacity", d => this.hiddenLines.has(d.id) ? 0.3 : 1)
    }

    updateLineChart(data: LineData[]) {
        // 1. set domains on both scales based on data
        const flatArr = data.flatMap(d => d.values) // gives us all date/val points in one flat array
        this.xScale.domain(d3.extent(flatArr, d => d.date))

        const max = d3.max(flatArr, d => d.value);
        const upper = max ? max * 1.2 : 1.5;
        this.yScale.domain([0, upper]);

        // TODO: find better way
        const hiddenLines = this.hiddenLines;

        // 2. set up ticks? // 3. profit?
        const tickValues = getTickValues(flatArr, chartState.range, this.xScale)
        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat("%b %d")(d as Date))
        )
        applyXAxisRotation(this.gXAxis)

        // TODO: Trying to cleanly "highlight" the "1" tick
        this.gYAxis.call(d3.axisLeft(this.yScale).ticks(5))
            .selectAll(".tick").filter(d => d === 1)
            .select("text")
            .attr("class", "multi-line-one-tick")

        // color needs a domain - list of metric ids?
        this.gLines.selectAll("path.multi-line")
            .data(data, d => d.id) // 'weight', 'steps', etc here
            .join(
                enter => {
                    return enter.append("path")
                        .attr("d", d => this.line(d.values))
                        .attr("stroke", d => this.color(d.id))
                        .attr("stroke-width", 1.5)
                        .attr("class", "multi-line")
                        .attr("id", d => `line-${d.id}`)
                        .attr("fill", "none") // otherwise D3 will try to fill the path as a shape
                },
                update => {
                    return update
                        .transition()
                        .duration(D3_TRANSITION_DURATION_MS)
                        .attr("d", d => this.line(d.values))
                },
                exit => exit.remove()
            )

        // Legend?
        const legendItems = this.gLegend.selectAll(".multi-chart-legend")
            .data(data, d => d.id)
            .join(
                enter => {
                    const g = enter.append("g")
                        .attr("class", "multi-chart-legend")
                        .attr("cursor", "pointer")
                        .attr("transform", (_d, i) => `translate(0, ${i * 24})`) //shift right for each entry

                    g.append("rect")
                        .attr("y", 5)
                        .attr("width", 20)
                        .attr("height", 2)
                        .attr("fill", d => this.color(d.id))

                    g.append("text")
                        .attr("x", 20)
                        .attr("y", 14)
                        .attr("class", "multi-chart-legend-text")
                        .text(d => `${TYPE_LABELS[d.id]}`)

                    return g;
                },
            )

        legendItems.on('click', (_e, d) => {
            if (hiddenLines.has(d.id)) {
                hiddenLines.delete(d.id)
            } else{
                hiddenLines.add(d.id)
            }
            this.syncHiddenLines()
        });

        this.syncHiddenLines();
    }

    async refreshLineChart(range: number) {
        const targets = {
            weight: getNumPref('weight_target', 76),
            steps: getNumPref('steps_target', 10000),
            sleep_duration_minutes: getNumPref('sleep_target', 480),
            calories: getNumPref('calories_target', 2200),
        };
        // Get our data, NO metric_type query param
        const params = new URLSearchParams({ lastNDays: String(range) })
        const response = await api.daily_metrics.getAll(params);
        
        // ugly transform to chartData
        const interim = response.data.map(e => ({
            date: new Date(e.entry_datetime.split('T')[0] + 'T00:00:00'),
            ...Object.fromEntries(Object.keys(targets).map(key => [key, e[key] / targets[key]]))
        }))
        
        const chartData = Object.keys(targets).map(key => ({
            id: key,
            values: interim.map(e => ({ date: e.date, value: e[key] }))
        }))

        this.updateLineChart(chartData)
    }
}


async function getMetricData(lastNDays: number, metricType?: MetricType): Promise<LineDataPoint[]> {
    const params = new URLSearchParams({ lastNDays: lastNDays.toString() });
    if (metricType) params.set('metric_type', metricType)
    const response = await api.daily_metrics.getAll(params);

    const chartData = response.data.map((d: ApiMetricData) => ({
        date: new Date(d.date.split('T')[0] + 'T00:00:00'),
        value: parseFloat(d.value),
    }));
    return chartData;
}

class MetricsLineChart {
    private dims;
    private gLines; gXAxis; gYAxis;
    private overlay; bisectLine; focusLabel;
    private xScale; yScale;
    private line;

    constructor(containerSelector: string, private config: StaticLineConfig) {
        this.dims = getChartDimensions(containerSelector, { top: 50, bottom: 30, left: 30, right: 40 });

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height);

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);
        
        // Title for lineChart
        gRoot.append("text")
            .attr("id", "line-chart-title")
            .attr("class", "chart-title")
            .attr("x", this.dims.innerWidth/2)
            .attr("y", -this.dims.margin.top/2)
            .attr("text-anchor", "middle")
            .text("Initial Title"); // TODO: FIX!!!

        // Groups inside svg
        this.gXAxis = gRoot.append("g")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)
            .attr("class", "axis-x");
        this.gYAxis = gRoot.append("g").attr("class", "axis-y");
        this.gLines = gRoot.append("g").attr("class", "chart");

        // Overlay to capture mouseover event for bisect line
        this.overlay = gRoot.append("rect")
            .attr("width", this.dims.innerWidth)
            .attr("height", this.dims.innerHeight)
            .attr("fill", "none")
            .attr("pointer-events", "all");

        // vertical line + label for bisect display
        this.bisectLine = gRoot.append("line")
            .attr("class", "bisect-line")
            .attr("y1", 0)
            .attr("y2", this.dims.innerHeight)
            .attr("opacity", 0)
            .attr("pointer-events", "none") // prevent line hijacking mousemove from overlay

        this.focusLabel = gRoot.append("text")
            .attr("class", "bisect-label")
            .attr("opacity", 0)

        // Create scales. Define only range/pixel values since data is dynamic
        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth]);
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0]);

        this.line = d3.line<LineDataPoint>()
            .x(d => this.xScale(d.date))
            .y(d => this.yScale(d.value))
    }

    drawStaticLines(metricType: LineMetricType) {
        // TODO: rip out too?
        const config = this.config[metricType as StaticLineMetric];
        if (!config) return;

        // TODO: Static line
        this.gLines.selectAll(`rect.${config.class.split(" ")[0]}`)
            .data([config.targetValue])
            .join(
                enter => enter.append("rect")
                    .attr("class", config.class)
                    .attr("x", 0)
                    .attr("y", (d: number) => this.yScale(d) - 1)
                    .attr("width", this.dims.innerWidth)
                    .attr("height", 2)
                    .attr("opacity", 0.6),
                update => update
                    .transition().duration(D3_TRANSITION_DURATION_MS)
                    // .attr("y1", (d: number) => this.yScale(d)) TODO: ???
                    // .attr("y2", (d: number) => this.yScale(d)),
                    .attr("y", (d: number) => this.yScale(d) - 1)

            );
    }

    updateLineChart(data: LineDataPoint[], metricType: LineMetricType) {
        // Clear static lines
        this.gLines.selectAll(".bmr-target-line, .sleep-target-line").remove();
        this.gLines.selectAll(".empty-message").remove();

        this.xScale.domain(d3.extent(data, d => d.date) as [Date, Date]);

        const dataValues = data.map(d => d.value);
        let combinedValues = dataValues;
        const config = this.config[metricType as StaticLineMetric];
        if (config) {
            combinedValues = [...dataValues, config.targetValue];
        }
        const [min, max] = d3.extent(combinedValues);

        // Give a more reasonable "window" for min-max range
        const spread = max - min;
        const padding = spread === 0 ? 1 : spread * 0.2;
        this.yScale.domain([Math.max(0, Math.floor(min - padding)), max + padding]);

        // Consistent ticks for dates
        const tickValues = getTickValues(data, chartState.range, this.xScale)

        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat("%b %d")(d as Date))
        );
        applyXAxisRotation(this.gXAxis)

        // TODO: For bisect thing?
        // NOTE: bisect expects ASCENDING order (backend repo method does this, needs to stay that way)
        const bisect = d3.bisector((d: LineDataPoint) => d.date).left;
        this.overlay
            .on('mousemove', (event) => {
                const [mouseX] = d3.pointer(event);
                const date = this.xScale.invert(mouseX);
                const idx = bisect(data, date);
                const left = data[idx - 1];
                const right = data[idx];
                if (!left || !right) {
                    console.warn("Error: Bisect missing left or right data point")
                    return;
                };

                const [leftDate, rightDate] = [left.date.getTime(), right.date.getTime()]
                const t = (date.getTime() - leftDate) / (rightDate - leftDate)
                const interpolated = left.value + (right.value - left.value) * t;

                // For rendering a comparison to target/goal value, if applicable
                const config = this.config[metricType as StaticLineMetric]
                const target = config?.targetValue
                let label = interpolated.toFixed(1);
                if (target) {
                    const percent = ((interpolated - target) / target * 100);
                    const sign = percent > 0 ? '+' : '';
                    label += ` (${sign}${percent.toFixed(1)}% vs target)`;
                }

                this.bisectLine
                    .attr("opacity", 1)
                    .attr("transform", `translate(${mouseX}, 0)`);
                this.focusLabel
                    .attr("opacity", 1)
                    .attr("x", mouseX + 8) // appear to right of bisect line?
                    .attr("y", 12)
                    .text(`${label} - ${d3.timeFormat("%b %d")(date)}`)
            })
            .on('mouseleave', () => {
                this.bisectLine.attr("opacity", 0)
                this.focusLabel.attr("opacity", 0)
            })

        this.gYAxis.call(d3.axisLeft(this.yScale).ticks(ticks))
            .call(g => g.selectAll(".tick line")
                .attr("x2", this.dims.innerWidth)
                .attr("stroke-opacity", D3_GRIDLINES_OPACITY)
                .attr("stroke-dasharray", D3_GRIDLINES_DASHARR_VALS)
            )

        // Metric line?
        this.gLines.selectAll<SVGPathElement, LineData>("path.line")
            .data([{ id: metricType, values: data }], d => d.id) // makes each metric a datum
            .join(
                enter => {
                    return enter.append("path")
                        .attr("class", "line")
                        .attr("d", (d: LineData) => this.line(d.values))
                        .each(function() {
                            const len = this.getTotalLength();
                            d3.select(this)
                                .attr("stroke-dasharray", len)  // makes entire line one "dash"
                                .attr("stroke-dashoffset", len) // hides whole line
                                .transition().duration(800)
                                .attr("stroke-dashoffset", 0)   // reveals left to right
                        })
                },
                update => update
                    .attr("stroke-dasharray", "none") // so it doesn't interfere on updates
                    .transition().duration(D3_TRANSITION_DURATION_MS)
                    .attr("d", (d: LineData) => this.line(d.values)),
                exit => exit.remove()
            );

        const circles = this.gLines.selectAll<SVGCircleElement, LineDataPoint>("circle")
            .data(data, d => d.date.getTime()) // .getTime() -> more stable than Date objects
            .join(
                enter => {
                    return enter.append("circle")
                        .attr("r", 0)
                        .attr("fill", "var(--accent-subtle)")
                        .attr("cx", d => this.xScale(d.date))
                        .attr("cy", d => this.yScale(d.value))
                        .transition()
                        .duration(D3_TRANSITION_DURATION_MS)
                        .attr("r", 4);
                },
                update => update
                    .transition().duration(D3_TRANSITION_DURATION_MS)
                    .attr("cx", d => this.xScale(d.date))
                    .attr("cy", d => this.yScale(d.value)),
                exit => exit.remove()
            );

        d3.select("#line-chart-title").text(TYPE_LABELS[metricType]);
    }

    showEmptyChart(metricType: LineMetricType) {
        this.gLines.selectAll("path.line").remove();
        this.gLines.selectAll("circle").remove();
        this.gLines.selectAll(".bmr-target-line, .sleep-target-line").remove();

        showEmptyChartMessage(
            this.gLines,
            TYPE_LABELS[metricType],
            this.dims.innerWidth,
            this.dims.innerHeight
        )

        d3.select("#line-chart-title")
            .text(TYPE_LABELS[metricType])
    }

    async refreshLineChart(range: number, metricType: LineMetricType) {
        const data = await getMetricData(range, metricType);
        if (data.length === 0) {
            this.showEmptyChart(metricType);
            return;
        }
        this.updateLineChart(data, metricType);
        this.drawStaticLines(metricType);
    }
}

class MetricsBarChart {
    private dims;
    private gChart; gXAxis; gYAxis;
    private xScale; yScale;
    private overlay; focusLabel;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 50, bottom: 30, left: 30, right: 40 })

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height);

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        // Title
        gRoot.append("text")
            .attr("id", "bar-chart-title")
            .attr("class", "chart-title")
            .attr("x", this.dims.innerWidth/2)
            .attr("y", -this.dims.margin.top/2)
            .attr("text-anchor", "middle")
            .text("Initial title") // TODO: fix!

        // Groups inside svg
        this.gXAxis = gRoot.append("g")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)
            .attr("class", "axis-x");
        this.gYAxis = gRoot.append("g")
            .attr("class", "axis-y");
        this.gChart = gRoot.append("g")
            .attr("class", "chart");

        this.overlay = gRoot.append("rect")
            .attr("width", this.dims.innerWidth)
            .attr("height", this.dims.innerHeight)
            .attr("fill", "none")
            .attr("pointer-events", "all")

        this.focusLabel = gRoot.append("text")
            .attr("class", "bisect-label")
            .attr("opacity", 0)

        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth]);
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0]);
    }


    updateBarChart(data: LineDataPoint[], metricType: BarMetricType) {

        // Stuff for getting vertical bars to not overlap axis lines
        const [minDate, maxDate] = d3.extent(data, d => d.date);
        if (!minDate || !maxDate) {
            console.warn("Error in updateBarChart: minDate/maxDate undefined/missing")
            return
        }
        const halfBar = (maxDate.getTime() - minDate.getTime()) / (data.length - 1) / 2;
        this.xScale.domain([
            new Date(minDate.getTime() - halfBar),
            new Date(maxDate.getTime() + halfBar)
        ]);

        // Padding on vertical max range
        const dataValues = data.map(d => d.value);
        const [, max] = d3.extent(dataValues) as [number, number];
        const padding = max === 0 ? 1 : max * 0.2;
        this.yScale.domain([0, max + padding]);

        // Consistent ticks for dates
        const maxTicks = 7;
        const every = Math.ceil(data.length / maxTicks);
        const tickValues = data
            .filter((_, i) => i % every === 0)
            .map(d => d.date);

        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat("%b %d")(d as Date))
        );
        applyXAxisRotation(this.gXAxis)

        // Add grid lines
        if (metricType === 'sleep_duration_minutes') {
            const [yMin, yMax] = this.yScale.domain();
            const ySpread = yMax - yMin;
            const yInterval = ySpread > 600 ? 120 : 60;
            const sleepTickValues = d3.range(
                Math.floor(yMin / yInterval) * yInterval,
                Math.floor(yMax / yInterval) * yInterval + 1,
                yInterval
            );
            this.gYAxis.call(
                d3.axisLeft(this.yScale)
                    .tickValues(sleepTickValues)
                    .tickFormat((d: number) => {
                        const hours = Math.floor(d / 60)
                        const mins = d % 60;
                        return mins === 0
                            ? `${hours}h`
                            : `${hours}h${mins}m`;
                    })
            )
        } else {
            this.gYAxis.call(d3.axisLeft(this.yScale).ticks(ticks))
        }
        this.gYAxis.call(g => g.selectAll(".tick line")
                .attr("x2", this.dims.innerWidth)
                .attr("stroke-opacity", D3_GRIDLINES_OPACITY)
                .attr("stroke-dasharray", D3_GRIDLINES_DASHARR_VALS)
            )

        // Bisect stuff
        const bisect = d3.bisector(d => d.date).left;
        this.overlay
            .on('mousemove', (event) => {
                const [mouseX] = d3.pointer(event)
                const date = this.xScale.invert(mouseX)
                const idx = bisect(data, date)
                const left = data[idx - 1]
                const right = data[idx]

                let closest;
                if (!left) closest = right;
                else if (!right) closest = left;
                else closest = (date - left.date) < (right.date - date) ? left : right;

                // Dim all other bars
                this.gChart.selectAll("rect.bar").attr("opacity", d => {
                    return d.date === closest.date ? 1 : D3_OTHER_DIM_OPACITY
                })

                // Adjust for XhYm for sleep display vals
                const displayValue = metricType === 'sleep_duration_minutes'
                    ? hourMinsDisplay(closest.value)
                    : `${closest.value}`;

                this.focusLabel
                    .attr("opacity", 1)
                    .attr("x", this.xScale(closest.date))
                    .attr("y", this.yScale(closest.value) - 10)
                    .attr("text-anchor", "middle")
                    .text(displayValue)
            })
            .on('mouseleave', () => {
                this.focusLabel.attr("opacity", 0)
                this.gChart.selectAll("rect.bar").attr("opacity", 1)
            })

        // difference between valB - valA?
        const barWidth = this.dims.innerWidth / chartState.range * 0.8;
        // Metric bars
        this.gChart.selectAll("rect.bar")
            .data(data)
            .join(
                enter => {
                    const rects = enter.append("rect")
                        .attr("class", "bar")
                        .attr("x", d => this.xScale(d.date) - barWidth / 2)
                        .attr("width", barWidth)
                        .attr("y", this.dims.innerHeight)
                        .attr("height", 0)
                        .transition().duration(D3_TRANSITION_DURATION_MS)
                        .attr("y", d => this.yScale(d.value))
                        .attr("height", d => this.dims.innerHeight - this.yScale(d.value))

                    return rects
                },
                update => update
                    .transition().duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.xScale(d.date) - barWidth / 2)
                    .attr("y", d => this.yScale(d.value))
                    .attr("width", barWidth)
                    .attr("height", d => this.dims.innerHeight - this.yScale(d.value)),
                exit => exit.remove()
            );
        d3.select("#bar-chart-title").text(TYPE_LABELS[metricType]);
    }

    showEmptyChart(metricType: BarMetricType) {
        this.gChart.selectAll('rect.bar').remove();

        // Clear axes
        this.yScale.domain([]);
        this.gYAxis.call(d3.axisLeft(this.yScale));

        this.xScale.domain([]);
        this.gXAxis.call(d3.axisBottom(this.xScale));

        showEmptyChartMessage(
            this.gChart,
            TYPE_LABELS[metricType],
            this.dims.innerWidth,
            this.dims.innerHeight
        )
    }

    async refreshBarChart(range: number, metricType: BarMetricType) {
        const data = await getMetricData(range, metricType);
        if (data.length === 0) {
            this.showEmptyChart(metricType);
            return;
        }
        this.updateBarChart(data, metricType);
    }

}


export async function init() {
    const targetSleepDuration = getNumPref('sleep_duration_minutes_target', 999);
    const targetWeight = getNumPref('weight_target', 999);

    const STATIC_LINE_CONFIG = {
        'calories': {
            class: "bmr-target-line",
            targetValue: bmrValue
        },
        'sleep_duration_minutes': {
            class: "sleep-target-line",
            targetValue: targetSleepDuration
        },
        'weight': {
            class: "weight-target-line",
            targetValue: targetWeight
        }
    }

    const lineContainer = document.querySelector('#metrics-line-chart-container');
    const barContainer = document.querySelector('#metrics-bar-chart-container');
    const multiContainer = document.querySelector('#metrics-multi-chart-container');
    // if any of these are null/undefined?
    // Don't create all charts upfront:
    let metricsBarChart: MetricsBarChart | null = null;
    let metricsLineChart: MetricsLineChart | null = null;
    const metricsMultiChart = new MultiChart('#metrics-multi-chart-container');
    await metricsMultiChart.refreshLineChart(chartState.range);

    // For metrics chart timeframe pills
    const selector = document.querySelector('[data-timeframe="daily_metrics-chart"]');
    const btn = selector.querySelector('[data-range="7"]');
    btn.classList.add('active');

    const btnType = document.querySelector('[data-type="all"]');
    btnType.classList.add('active');
    // Set "other" chart type to hidden:
    barContainer.classList.add('hide');
    lineContainer.classList.add('hide');

    initChartRangeButtons(chartState, async () => {
        if (chartState.selected === 'all') {
            await metricsMultiChart.refreshLineChart(chartState.range);
        } else if (BAR_METRICS.includes(chartState.selected)) {
            await metricsBarChart.refreshBarChart(chartState.range, chartState.selected);
        } else {
            await metricsLineChart.refreshLineChart(chartState.range, chartState.selected);
        }
    });
    
    const showChart = (container: Element) => {
        [lineContainer, barContainer, multiContainer].forEach(c => {
            c!.classList.add('hide');
        })
        container.classList.remove('hide');
    }

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.chart-type')) {

            
            const chartType = target.dataset['type']!;
            chartState.selected = chartType;
            
            document.querySelectorAll('.chart-type').forEach(btn => btn.classList.remove('active'));
            target.classList.add('active');
            

            if (BAR_METRICS.includes(chartState.selected)) {
                showChart(barContainer)
                if (!metricsBarChart) {
                    metricsBarChart = new MetricsBarChart('#metrics-bar-chart-container');
                }
                await metricsBarChart.refreshBarChart(chartState.range, chartState.selected);
            } else if (LINE_METRICS.includes(chartState.selected)){
                showChart(lineContainer)
                if (!metricsLineChart) {
                    metricsLineChart = new MetricsLineChart(
                        '#metrics-line-chart-container',
                        STATIC_LINE_CONFIG
                    );
                }
                await metricsLineChart.refreshLineChart(chartState.range, chartState.selected);
            } else {
                showChart(multiContainer)
                await metricsMultiChart.refreshLineChart(chartState.range);
            }
        }

        // table context menu
        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const row = target.closest('tr')!;
            const { itemId, subtype } = row.dataset;
            const modal = document.querySelector('#daily_metrics-entry-dashboard-modal');
            const rect = button.getBoundingClientRect();

            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => openModalForEdit(itemId, modal, 'Daily Entry', (data) => {
                            const dateField = modal.querySelector('#entry_date')
                            dateField.value = data.entry_datetime.slice(0, 10)
                        })
                    },
                    { label: 'Delete', action: () => handleDelete(itemId, subtype) }
                ]
            })
        }
    });

    const dialog = document.querySelector<FormDialog>('#daily_metrics-entry-dashboard-modal');
    if (!dialog) {
        console.warn('metrics dashboard: #daily_metrics-entry-dashboard-modal not found')
        return
    }
    initMetricsForm(dialog)
}