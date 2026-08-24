
import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getDims } from '../shared/charts';
import { hourMinsDisplay } from '../shared/formatters';

export type PieDatum = {
    category: string;
    value: number;
};

interface ArcPathElement extends SVGPathElement {
    _current?: d3.PieArcDatum<PieDatum>;
}


export class TimeEntriesChart {
    private dims; radius;
    private pie; arc;
    private color;
    private gRoot; gChart; gLegend;
    private centerLabel;
    private totalMins!: number;
    private highest!: PieDatum;
    countOther!: number | null;
    idleTimeout!: number;

    constructor(containerSelector: string) {
        this.dims = getDims(300, 400, { top: 40, right: 20, bottom: 10, left: 20 });

        this.radius = Math.min(this.dims.innerWidth, this.dims.innerHeight) / 2;

        const legendHeight = 40;
        const gap = 12;
        const chartAreaHeight = this.dims.innerHeight - legendHeight - gap;

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height);

        this.gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        this.gChart = this.gRoot.append("g")
                .attr("transform", `translate(${this.dims.innerWidth/2}, ${chartAreaHeight / 2})`)

        this.centerLabel = this.gChart.append("text")
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle")
            .attr("class", "donut-center-label")

        this.gLegend = this.gRoot.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(0, ${chartAreaHeight + gap + legendHeight})`) // moving legend to bottom "row"

        this.pie = d3.pie<PieDatum>().value(d => d.value); // calc angles from array
        this.arc = d3.arc<d3.PieArcDatum<PieDatum>>() // draw curved slice shapes from angles
            .innerRadius(this.radius * 0.7) // prime real estate
            .outerRadius(this.radius);

        this.color = d3.scaleOrdinal(d3.schemeTableau10);
    }

    // Adjust text label positions for each slice to show at appropriate locations
    private labelTransform(d): string {
        const mid = (d.startAngle + d.endAngle) / 2;
        const [x, y] = this.arc.centroid(d);
        const xOffset = mid < Math.PI ? 15 : -15;
        const yOffsetSign = Math.sign(Math.sin(mid - Math.PI / 2));
        const yOffset = yOffsetSign * 20;
        return `translate(${x + xOffset}, ${y + yOffset})`
    }

    private showIdleSummary() {
        this.centerLabel.selectAll("tspan").remove();
        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "-2em")
            .text(`${hourMinsDisplay(this.totalMins)}`)

        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "1.6em")
            .attr("font-size", "0.8rem")
            .text(this.highest ? `Top: ${this.highest.category}` : '')

        // find count of "other":
        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "3em")
            .attr("font-size", "0.8rem")
            .text(`+${this.countOther} more`)
    }

    private showSliceDetail(datum: PieDatum) {
        this.centerLabel.selectAll("tspan").remove();

        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "0em")
            .text(`${datum.category}`)

        const percentTotal = (datum.value / this.totalMins) * 100;
        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "1.6em")
            .attr("font-size", "0.8rem")
            .text(`${hourMinsDisplay(datum.value)} (${percentTotal.toFixed(0)}%)`)
    }

    updatePieChart(data: PieDatum[]) {
        this.gRoot.selectAll('.empty-message').remove();

        const sorted = [...data].toSorted((a, b) => b.value - a.value);
        const pieData = this.pie(sorted);

        // Re-calc totalMins and highest for center label
        this.totalMins = data.reduce((a, b) => a + b.value, 0);
        // this.highest = data.reduce((a, b) => a.value > b.value ? a : b);
        this.highest = sorted[0] ?? null;
        this.countOther = data.length > 1 ? data.length - 1 : null;

        const groups = this.gChart.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.slice")
            .data(pieData, d => d.data.category)
            .join(
                enter => {
                    const g = enter.append("g")
                        .attr("class", "slice");

                    g.append('path') // slice
                        .attr("class", "pie")
                        .attr("fill", d => this.color(d.data.category))
                        .each(function(this: ArcPathElement, d) {
                            this._current = d;
                        })
                        .attr("d", this.arc);

                    return g;
                },
                update => {
                    const arc = this.arc; // Capture TimeEntriesChart's arc before .attrTween hijacks 'this'

                    update.select("path")
                        .transition().duration(500)
                        // D3 needs prev state to interpolate from, and we need to store
                        // it ourselves bc join() is stateless
                        .attrTween("d", function(d) {
                            const el = this as ArcPathElement;        // 'this' = DOM element
                            const i = d3.interpolate(el._current, d);
                            el._current = i(1);
                            return t => arc(i(t)) ?? "";
                        });

                    return update;
                },
                exit => exit.remove()
            );

        this.showIdleSummary()

        groups.on('mouseenter', (_event, d) => {
            // Skip hover effect if slice is > 75% of circle (since 2pi is full circle, so here we do 1.5pi)
            const sliceAngle = (d.endAngle - d.startAngle);
            if (sliceAngle > Math.PI * 1.5) {
                return;
            }
            // Calc midpoint (angle)
            const rawMidpoint = (d.startAngle + d.endAngle) / 2;
            const midpoint = rawMidpoint - (Math.PI / 2);
            const dist = radius / 10;

            // Calc x, y offsets for transform
            const x = Math.cos(midpoint) * dist;
            const y = Math.sin(midpoint) * dist;

            // Transform slice
            d3.select(_event.currentTarget)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", `translate(${x}, ${y})`);

            // Show slice label
            clearTimeout(this.idleTimeout)
            this.showSliceDetail(d.data)
        })
        .on('mouseleave', (event) => {
            d3.select(event.currentTarget)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", "translate(0, 0)");

            this.idleTimeout = setTimeout(() => this.showIdleSummary(), 120);
        })
        const radius = this.radius; // Capture outside callback
    }
}