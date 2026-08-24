import { D3_GRIDLINES_DASHARR_VALS, D3_GRIDLINES_OPACITY, getDims } from "../../shared/charts";

import * as d3 from 'd3';

// TODO: cleaner handling of these "reference lines" setups? so they're sorta pipelined and
//  properly organized

export class MacrosBarChart {
    dims;
    svg; gRoot; gXAxis; xScale; yScale;gYAxis;


    constructor(containerSelector: string | HTMLElement, calsTarget: any) {

        this.calsTarget = calsTarget;

        this.dims = getDims(50, 400, { top: 5, bottom: 20, left: 50, right: 5 });

        this.svg = d3.select(containerSelector).append("svg")
            .attr("viewBox", `0 0 ${this.dims.width} ${this.dims.height}`);

        this.gRoot = this.svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        // Create scales
        this.gXAxis = this.gRoot.append("g")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`);

        this.gYAxis = this.gRoot.append("g");

        this.xScale = d3.scaleBand().range([0, this.dims.innerWidth]).padding(0.2);
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0]);
    }

    update(data: any[]) {
        // Update .domains according to data
        this.xScale.domain(data.map(d => d.date));
        this.yScale.domain([0, d3.max(data, d => d.calories) * 1.2]); // +.2 for padding

        // Find avg
        const avgCals = d3.mean(data, d => d.calories);

        // Conditionally add either both target AND avg lines or just target
        const tickVals = this.calsTarget
            ? [this.calsTarget, avgCals]
            : [avgCals];

        // Render axes
        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickFormat(d => d3.timeFormat("%a")(new Date(d.split('T')[0] + 'T00:00:00')))
        ).call(g => g.select(".domain").remove()); // remove line from bottom axis

        this.gYAxis
            .call(d3.axisLeft(this.yScale).tickValues(tickVals))
            .call(
            g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick line")
                .attr("x2", this.dims.innerWidth) // stretch tick line across chart for goal line
                .attr("stroke-dasharray", D3_GRIDLINES_DASHARR_VALS)
                .attr("opacity", D3_GRIDLINES_OPACITY)
            )
            // Ensure our two label texts don't overlap
            .call(g => g.select(".tick text")
                .attr("dy", d => d === Math.max(this.calsTarget, avgCals) ? "-0.4em" : "1em")
            );


        // Draw bars
        this.gRoot.selectAll("rect")
            .data(data, d => d.date)
            .join('rect')
            .attr("x", d => this.xScale(d.date))
            .attr("y", d => this.yScale(d.calories))
            .attr("width", this.xScale.bandwidth())
            .attr("height", d => this.dims.innerHeight - this.yScale(d.calories))
            .attr("class", "bar")
    }
}
