import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getDims, getTickValues } from '../../shared/charts';
import type { BarMetricType, LineData, LineDataPoint, LineMetricType, MetricType } from './../shared';
import { HERO_PANEL_CHART_CONFIG } from './../shared';


export class MultiChart {
    private dims;
    private gLines; gLegend;
    private gXAxis; gYAxis;
    private xScale; yScale;
    private line;
    private color;
    private hiddenLines = new Set<BarMetricType | LineMetricType>;

    constructor(containerSelector: string | HTMLElement) {
        this.dims = getDims(HERO_PANEL_CHART_CONFIG.height, HERO_PANEL_CHART_CONFIG.width, HERO_PANEL_CHART_CONFIG.margin);

        const svg = d3.select(containerSelector).append("svg")
            .attr("viewBox", `0 0 ${this.dims.width} ${this.dims.height}`);

        const gRoot = svg.append("g")
            .attr("class", "gRoot")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        this.gXAxis = gRoot.append("g")
            .attr("class", "axis-x")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`)
        this.gYAxis = gRoot.append("g")
            .attr("class", "axis-y")

        this.gLines = gRoot.append("g")
            .attr("class", "gLines")

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

    update(data: LineData[], range: number) {
        // 1. set domains on both scales based on data
        const flatArr = data.flatMap(d => d.values) // gives us all date/val points in one flat array
        this.xScale.domain(d3.extent(flatArr, d => d.date))

        const max = d3.max(flatArr, d => d.value);
        const upper = max ? max * 1.2 : 1.5;
        this.yScale.domain([0, upper]);

        // TODO: find better way
        // const hiddenLines = this.hiddenLines;

        // 2. set up ticks? // 3. profit?
        const tickValues = getTickValues(flatArr, range, this.xScale)
        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat("%b %d")(d as Date))
        )
        // applyXAxisRotation(this.gXAxis)

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
        this.syncHiddenLines();
    }

    setHidden(ids: MetricType[]) {
        this.hiddenLines = new Set(ids);
        this.syncHiddenLines();
    }
}