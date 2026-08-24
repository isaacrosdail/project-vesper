import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getDims, withTooltip } from '../../shared/charts';
import { fmtDate } from '../../shared/datetime';
import { Pairs } from './../metricsState.svelte';

// TODO: We can use d3.drag to "lasso" a group of points in the scatterplot
// Sounds sick, should try implementing that

export class ScatterPlot {
    gXAxis;
    gYAxis;
    xScale;
    yScale;
    gDots;
    regressionLine;

    constructor(containerSelector: string) {

        const dims = getDims(150, 150, { top: 20, left: 20, bottom: 10, right: 10 });
        const svg = d3.select(containerSelector).append("svg")
            .attr("viewBox", `0 0 ${dims.width} ${dims.height}`)
            .attr("height", "100%")
        
        const gRoot = svg.append("g")
            .attr("transform", `translate(${dims.margin.left}, ${dims.margin.top})`);

        this.gXAxis = gRoot.append("g").attr("class", "x-axis")
            .attr("transform", `translate(0, ${dims.innerHeight})`);
        this.gYAxis = gRoot.append("g").attr("class", "y-axis");

        this.gDots = gRoot.append("g").attr("class", "g-dots");
        // Axes: Each is one of the compared values we're using on the same date:
        // (valA, valB) <- date disappears as an axis, since it's what "binds" the points
        this.xScale = d3.scaleLinear().range([0, dims.innerWidth]);
        this.yScale = d3.scaleLinear().range([dims.innerHeight, 0]);
        
        this.regressionLine = gRoot.append("line").attr("class", "regression-line")
    }

    // m = slope
    // b = 
    update(pairs: Pairs, m: number, b: number) {
        // Set/update domains
        const [xMin, xMax] = d3.extent(pairs, d => d.valA);

        this.xScale.domain(d3.extent(pairs, d => d.valA));
        this.yScale.domain(d3.extent(pairs, d => d.valB));

        // Regression line
        const y1 = m * xMin + b;
        const y2 = m * xMax + b;
        this.regressionLine
            .attr("x1", this.xScale(xMin)).attr("y1", this.yScale(y1))
            .attr("x2", this.xScale(xMax)).attr("y2", this.yScale(y2));

        this.gDots.selectAll("circle.metrics-dot")
            .data(pairs, d => d.date)
            .join(
                enter => {
                    const circles = enter.append("circle")
                        .attr("cx", d => this.xScale(d.valA))
                        .attr("cy", d => this.yScale(d.valB))
                        .attr("r", 3)
                        .attr("fill", "var(--metric-color)")
                        .attr("class", "metrics-dot")
                        
                        circles.call(withTooltip(d => `${fmtDate(d.date)}: ${d.valA}|${d.valB}`))

                    return circles
                },
                update => {
                    return update
                        .transition().duration(D3_TRANSITION_DURATION_MS)
                        .attr("cx", d => this.xScale(d.valA))
                        .attr("cy", d => this.yScale(d.valB))
                },
                exit => exit.remove()
            )
    }
}