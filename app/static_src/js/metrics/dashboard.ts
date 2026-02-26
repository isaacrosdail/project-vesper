import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getChartDimensions, getTickValues, applyXAxisRotation, showEmptyChartMessage } from '../shared/charts';
import { apiRequest, routes } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager.js';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { initValidation, makeValidator } from '../shared/validators';


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
    metricType: MetricType;
    view: 'overview' | MetricType;
    range: number;
}
const chartState: ChartState = {
    metricType: 'weight',
    view: 'overview',
    range: 7,
}

type BarMetricType = 'steps' | 'calories';
type LineMetricType = 'weight' | 'sleep_duration_minutes';
type MetricType = BarMetricType | LineMetricType;
type StaticLineMetric = 'calories' | 'sleep_duration_minutes';

const BAR_METRICS: BarMetricType[] = ['steps', 'calories'];
const LINE_METRICS: LineMetricType[] = ['weight', 'sleep_duration_minutes'];
const ticks = 7; // Graph formatting

// TODO: Pull from db? Hardcoding BMR for calories, target duration for sleep
// Calc bmr from current weight periodically & re-store?
// Also: Store height in db and use that to calculate stride distance? That way we could convert: "5000 steps at 6'2" = 6.5 miles! nice!"
const bmrValue = 2000;
const targetSleepDuration = 7 * 60; // 7 hr
const STATIC_LINE_CONFIG = {
    'calories': {
        class: "bmr-target-line",
        targetValue: bmrValue
    },
    'sleep_duration_minutes': {
        class: "sleep-target-line",
        targetValue: targetSleepDuration
    }
}

const TYPE_LABELS: Record<MetricType, string> = {
    weight: "Weight",
    steps: "Steps",
    calories: "Calories",
    sleep_duration_minutes: "Sleep Duration (m)"
}




// For each date, produce an array where each metric is expressed as value / target -- a num where 1.0 = exactly on target, 0.8 = 80% of goal, etc.
class MultiChart {
    private dims;
    private gLines; gLegend;
    private gXAxis; gYAxis;
    private xScale; yScale;
    private line;
    private color;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 50, bottom: 30, left: 30, right: 40 });

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height)

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`)
            .attr("class", "gRoot")

        this.gXAxis = gRoot.append("g")
            .attr("class", "gXAxis")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)

        this.gYAxis = gRoot.append("g")
            .attr("class", "gYAxis")
        this.gLines = gRoot.append("g")
            .attr("class", "gLines")

        this.gLegend = gRoot.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(0, -${this.dims.margin.top / 2})`)


        // Create scales
        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth])
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0])

        // Line generator
        this.line = d3.line<LineDataPoint>()
            .x(d => this.xScale(d.date))
            .y(d => this.yScale(d.value))

        this.color = d3.scaleOrdinal(d3.schemeTableau10)
    }

    updateLineChart(data: LineData[]) {
        // 1. set domains on both scales based on data
        const flatArr = data.flatMap(d => d.values) // gives us all date/val points in one flat array
        this.xScale.domain(d3.extent(flatArr, d => d.date))

        const max = d3.max(flatArr, d => d.value);
        const upper = max ? max * 1.2 : 1.5;
        this.yScale.domain([0, upper]);

        // 2. set up ticks? // 3. profit?
        this.gXAxis.call(d3.axisBottom(this.xScale))
        this.gYAxis.call(
            d3.axisLeft(this.yScale)
            .ticks(5)
        )
        applyXAxisRotation(this.gXAxis)

        // TODO: fix up; trying to cleanly "highlight" the "1" tick
        const thing = this.gYAxis.call(
            d3.axisLeft(this.yScale).ticks(5)
        )
        thing.selectAll(".tick").filter(d => d === 1)
            .select("text")
            .attr("class", "thing")

        // color needs a domain - list of metric ids?
        // this.color.domain(data.map(d => d.id))
        this.gLines.selectAll("path.multi-line")
            .data(data, d => d.id) // 'weight', 'steps', etc here
            .join(
                enter => {
                    return enter.append("path")
                        .attr("d", d => this.line(d.values))
                        .attr("stroke", d => this.color(d.id))
                        .attr("class", "multi-line")
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
        this.gLegend.selectAll("multi-chart-legend")
            .data(data, d => d.id)
            .join(
                enter => {
                    const g = enter.append("g")
                        .attr("class", "legend-item")
                        .attr("transform", (_d, i) => `translate(${i * 100}, 0)`) //shift right for each entry

                    g.append("rect")
                        .attr("y", 5)
                        .attr("width", 20)
                        .attr("height", 2)
                        .attr("fill", d => this.color(d.id))

                    g.append("text")
                        .attr("x", 20)
                        .attr("y", 14)
                        .attr("class", "chart-legend-text")
                        .text(d => `${TYPE_LABELS[d.id]}`)

                    return g;
                },
            )
    }

    async refreshLineChart() {
        // dummy for now
        const targets = { weight: 170, steps: 10_000, sleep_duration_minutes: 480, calories: 2000 };

        // Get our data, NO metric_type query param
        const params = new URLSearchParams({ lastNDays: chartState.range.toString() })
        const url = routes.metrics.daily_metrics.query(params);
        const response = await apiRequest('GET', url, null);

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


async function getMetricData(metric_type: MetricType, lastNDays: number): Promise<LineDataPoint[]> {
    const params = new URLSearchParams({
        metric_type,
        lastNDays: lastNDays.toString()
    });
    const url = routes.metrics.daily_metrics.query(params);
    const response = await apiRequest('GET', url, null);

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

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 20, bottom: 30, left: 30, right: 40 });

        const svg = d3.select(containerSelector).append("svg")
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
        const config = STATIC_LINE_CONFIG[metricType as StaticLineMetric];
        if (!config) return;

        // TODO: update/fix
        const staticLine = this.gLines.selectAll(`rect.${config.class.split(" ")[0]}`)
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
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("y1", (d: number) => this.yScale(d))
                    .attr("y2", (d: number) => this.yScale(d)),

            );
    }

    updateLineChart(data: LineDataPoint[], metricType: LineMetricType) {
        // Clear static lines
        this.gLines.selectAll(".bmr-target-line, .sleep-target-line").remove();
        this.gLines.selectAll(".empty-message").remove();

        this.xScale.domain(d3.extent(data, d => d.date) as [Date, Date]);

        const dataValues = data.map(d => d.value);
        let combinedValues = dataValues;
        const config = STATIC_LINE_CONFIG[metricType as StaticLineMetric];
        if (config) {
            combinedValues = [...dataValues, config.targetValue];
        }
        const [min, max] = d3.extent(combinedValues);

        // Give a more reasonable "window" for min-max range
        const spread = max - min;
        const padding = spread === 0 ? 1 : spread * 0.2;
        this.yScale.domain([Math.floor(min - padding), max + padding]);

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
                console.log("ye")
                const [mouseX, mouseY] = d3.pointer(event);
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
                const config = STATIC_LINE_CONFIG[chartState.metricType as StaticLineMetric]
                const target = config?.targetValue
                let label = interpolated.toFixed(1);
                if (target) {
                    const percent = ((interpolated - target) / target * 100);
                    const sign = percent > 0 ? '+' : '';
                    label += ` (${sign}${percent.toFixed(1)}% vs target)`;
                }

                // const x = this.xScale(d.date); const y = this.yScale(d.value);
                const x = mouseX; // const y = mouseY;

                this.bisectLine
                    .attr("opacity", 1)
                    .attr("transform", `translate(${x}, 0)`);
                this.focusLabel
                    .attr("opacity", 1)
                    .attr("x", mouseX + 8) // appear to right of bisect line?
                    .attr("y", 12)
                    .text(`${label} - ${d3.timeFormat("%b %d")(date)}`)
            })
            // TODO: This fades away while we're sitting still, how to keep it?
            .on('mouseleave', () => {
                this.bisectLine.attr("opacity", 0)
                this.focusLabel.attr("opacity", 0)
            })

        // make sleep vals more readable
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
            this.gYAxis.call(d3.axisLeft(this.yScale).ticks(ticks));
        }

        const _metricLine = this.gLines.selectAll<SVGPathElement, LineData>("path.line")
            .data([{ id: metricType, values: data }], d => d.id) // makes each metric a datum
            .join(
                enter => {
                    return enter.append("path")
                        .attr("class", "line")
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

class MetricsBarChart {
    private dims;
    private gChart; gXAxis; gYAxis;
    private xScale; yScale;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 20, bottom: 30, left: 30, right: 40 })

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height);

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        const _title = svg.append("text")
            .attr("id", "bar-chart-title")
            .attr("class", "chart-title")
            .attr("x", this.dims.innerWidth/2)
            .attr("y", this.dims.margin.top/2)
            .text("Initial title") // TODO: fix!

        // Groups inside svg
        this.gXAxis = gRoot.append("g")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)
            .attr("class", "axis-x");
        this.gYAxis = gRoot.append("g")
            .attr("class", "axis-y");
        this.gChart = gRoot.append("g")
            .attr("class", "chart");

        // Create scales. Define only range/pixel values since data is dynamic
        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth]);
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0]);
    }


    updateBarChart(data: LineDataPoint[], metricType: BarMetricType) {

        // Stuff for getting vertical bars to not overlap axis lines
        const [minDate, maxDate] = d3.extent(data, d => d.date);
        if (!minDate || !maxDate) {
            console.warn("Error in updateBarChart: minDate/maxDate undefined/missing")
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
        const tickValues = getTickValues(data, chartState.range, this.xScale);

        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat("%b %d")(d as Date))
        );
        applyXAxisRotation(this.gXAxis)

        this.gYAxis.call(d3.axisLeft(this.yScale).ticks(ticks));


        // difference between valB - valA?
        const barWidth = this.dims.innerWidth / chartState.range * 0.8;
        const _metricBars = this.gChart.selectAll("rect.bar")
            .data(data)
            .join(
                enter => {
                    const rects = enter.append("rect")
                        .attr("class", "bar")
                        .attr("x", d => this.xScale(d.date) - barWidth / 2)
                        .attr("y", d => this.yScale(d.value))
                        .attr("width", barWidth)
                        .attr("height", d => this.dims.innerHeight - this.yScale(d.value))

                    return rects
                },
                update => update
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.xScale(d.date) - barWidth / 2)
                    .attr("y", d => this.yScale(d.value))
                    .attr("width", barWidth)
                    .attr("height", d => this.dims.innerHeight - this.yScale(d.value)),
                exit => exit.remove()
            );

        d3.select("#bar-chart-title")
            .text(TYPE_LABELS[metricType]);

    }

    showEmptyChart() {
        this.gChart.selectAll('rect.bar').remove();

        // Clear axes
        this.yScale.domain([]);
        this.gYAxis.call(d3.axisLeft(this.yScale));

        this.xScale.domain([]);
        this.gXAxis.call(d3.axisBottom(this.xScale));

        showEmptyChartMessage(
            this.gChart,
            TYPE_LABELS[chartState.metricType],
            this.dims.innerWidth,
            this.dims.innerHeight
        )
        // const _emptyMessage = this.gChart.selectAll('text.empty-message')
        //     .data([1])
        //     .join("text")
        //     .attr("class", "empty-message")
        //     .attr("text-anchor", "middle")
        //     .attr("x", this.dims.innerWidth/2)
        //     .attr("y", this.dims.innerHeight/2)
        //     .text(`No ${TYPE_LABELS[chartState.metricType]} data for this period.`)
    }

    async refreshBarChart() {
        const data = await getMetricData(chartState.metricType, chartState.range);
        if (data.length === 0) {
            this.showEmptyChart();
            return;
        }
        this.updateBarChart(data, chartState.metricType);
    }

}


export async function init() {
    const lineContainer = document.querySelector('#metrics-line-chart-container');
    const barContainer = document.querySelector('#metrics-bar-chart-container');
    const multiContainer = document.querySelector('#metrics-multi-chart-container');
    // if any of these are null/undefined?

    const metricsLineChart = new MetricsLineChart('#metrics-line-chart-container');
    await metricsLineChart.refreshLineChart();

    const metricsBarChart = new MetricsBarChart('#metrics-bar-chart-container');
    await metricsBarChart.refreshBarChart();

    const metricsMultiChart = new MultiChart('#metrics-multi-chart-container');
    await metricsMultiChart.refreshLineChart();


    const rangePills = document.querySelectorAll('.chart-range');

    // set default chart range button's active class
    const btn = document.querySelector('[data-range="7"]');
    btn.classList.add('active');
    const btnType = document.querySelector('[data-type="all"]');
    btnType.classList.add('active');
    // Set "other" chart type to hidden:
    barContainer.classList.add('hide');
    lineContainer.classList.add('hide');

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.chart-type')) {

            const chartType = target.dataset['type']!;
            chartState.view = chartType as typeof chartState.view;
            if (chartType !== 'overview') {
                chartState.metricType = chartType as MetricType;
            }

            document.querySelectorAll('.chart-type').forEach(btn => {
                btn.classList.remove('active');
            })
            target.classList.add('active');

            const showChart = (container: Element) => {
                [lineContainer, barContainer, multiContainer].forEach(c => {
                    c.classList.add('hide');
                    container.classList.remove('hide');
                })
            }

            if (BAR_METRICS.includes(chartState.metricType)) {
                showChart(barContainer)
                await metricsBarChart.refreshBarChart();
            } else if (LINE_METRICS.includes(chartState.metricType)){
                showChart(lineContainer)
                await metricsLineChart.refreshLineChart();
            } else {
                showChart(multiContainer)
                await metricsMultiChart.refreshLineChart();
            }
        }
        else if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!, 10);
            rangePills.forEach(btn => {
                btn.classList.remove('active');
            })
            target.classList.add('active');

            if(BAR_METRICS.includes(chartState.metricType)) {
                await metricsBarChart.refreshBarChart();
            } else {
                await metricsLineChart.refreshLineChart();
            }
            await metricsMultiChart.refreshLineChart();

        }
        else if (target.matches('.table-range')) {
            const range = target.dataset['range']!;
            const table = target.dataset['table']!;

            const url = new URL(window.location.href);
            url.searchParams.set(`${table}_range`, range);
            window.location.href = url.toString();
        }

        // table context menu
        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const row = target.closest('.table-row')!;
            const { itemId } = row.dataset;
            const url = routes.metrics.daily_metrics.item(itemId);
            const modal = document.querySelector('#daily_metrics-entry-dashboard-modal');
            const rect = button.getBoundingClientRect();

            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => openModalForEdit(itemId, url, modal, 'Daily Entry')
                    },
                    {
                        label: 'Delete',
                        action: () => handleDelete(itemId, url)
                    }
                ]
            })
        }
    });

    const validateSteps = makeValidator('steps', {
        isInt: true,
        min: 1,
        max: 40_000,
        pattern: /^\d+$/
    })
    const validateCalories = makeValidator('calories', {
        isInt: true,
        min: 0,
        max: 10_000
    })
    const validateWeight = makeValidator('weight', {
        isFloat: true,
        min: 0,
        max: 300
    })
    // Validation
    const metricsForm = document.querySelector<HTMLFormElement>('#daily_metrics-form')!;
    initValidation(
        metricsForm,
        {
            steps: validateSteps,
            calories: validateCalories,
            weight: validateWeight,

        }
    )

}