import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getDims,
    D3_GRIDLINES_DASHARR_VALS, D3_GRIDLINES_OPACITY, D3_OTHER_DIM_OPACITY, D3_TICKS, 
    getTickValues} from "../../shared/charts";
import { hourMinsDisplay } from '../../shared/formatters';
import { drawReferenceLines, TYPE_LABELS, HERO_PANEL_CHART_CONFIG } from '../shared';
import type { BarMetricType, MetricType, ReferenceLine } from '../shared';

export class MetricsBarChart {
    private dims;
    private gChart; gXAxis; gYAxis;
    private xScale; yScale;
    private overlay; focusLabel;

    constructor(
        containerSelector: string | HTMLElement,
        private config: Record<MetricType, ReferenceLine[]>,
        private targets: Record<MetricType, number>,
    ) {
        this.dims = getDims(HERO_PANEL_CHART_CONFIG.height, HERO_PANEL_CHART_CONFIG.width, HERO_PANEL_CHART_CONFIG.margin);

        const svg = d3.select(containerSelector).append("svg")
            .attr("viewBox", `0 0 ${this.dims.width} ${this.dims.height}`);

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

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


    update(data: any[], metricType: BarMetricType, range: number) {
        drawReferenceLines(this.gChart, this.config[metricType], this.yScale, this.dims.innerWidth);

        // TODO: For shading bar:
        const target = this.targets[metricType];

        // Stuff for getting vertical bars to not overlap axis lines
        const [minDate, maxDate] = d3.extent(data, d => d.date);
        if (!minDate || !maxDate) {
            console.warn("Error in update: minDate/maxDate undefined/missing")
            return
        }
        // TODO(d3): this hack dies once we fix the densify/.defined() stuff
        const halfBar = (maxDate.getTime() - minDate.getTime()) / (data.length - 1) / 2;
        this.xScale.domain([
            new Date(minDate.getTime() - halfBar),
            new Date(maxDate.getTime() + halfBar)
        ]);

        // Padding on vertical max range
        const dataValues = data.map(d => d.value);
        // Remember: Scale domain must be the union of every series we render onto it - bars, ref lines, overlays, etc.
        const refValues = this.config[metricType].map(r => r.value);
        const [, max] = d3.extent([...dataValues, ...refValues]) as [number, number];
        const padding = max === 0 ? 1 : max * 0.2;
        this.yScale.domain([0, max + padding]);

        const tickValues = getTickValues(data, range, this.xScale)
        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat("%b %d")(d as Date))
        );
        // applyXAxisRotation(this.gXAxis)

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
                        // TODO: change hoursMinsDisplay to allow not showing mins val?
                        const hours = Math.floor(d / 60)
                        const mins = d % 60;
                        return mins === 0
                            ? `${hours}h`
                            : `${hours}h${mins}m`;
                    })
            )
        } else {
            this.gYAxis.call(d3.axisLeft(this.yScale).ticks(D3_TICKS))
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
        const barWidth = this.dims.innerWidth / range * 0.8;
        // Metric bars
        this.gChart.selectAll("rect.bar")
            .data(data)
            .join(
                enter => {
                    const rects = enter.append("rect")
                        .attr("class", "bar")
                        .classed("under-target", d => d.value < target)
                        .attr("x", d => this.xScale(d.date) - barWidth / 2)
                        .attr("width", barWidth)
                        .attr("y", this.dims.innerHeight)
                        .attr("height", 0)
                        .attr("rx", 2)
                        .transition().duration(D3_TRANSITION_DURATION_MS)
                        .attr("y", d => this.yScale(d.value))
                        .attr("height", d => this.dims.innerHeight - this.yScale(d.value))

                    return rects
                },
                update => update
                    .classed("under-target", d => d.value < target)
                    .transition().duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.xScale(d.date) - barWidth / 2)
                    .attr("y", d => this.yScale(d.value))
                    .attr("width", barWidth)
                    .attr("height", d => this.dims.innerHeight - this.yScale(d.value)),
                exit => exit.remove()
            );
    }
}