import * as d3 from 'd3';

import { hideTooltip, showTooltip } from '../shared/ui/tooltip';
import { apiRequest } from '../shared/services/api';
import { getChartDimensions, D3_TRANSITION_DURATION_MS } from '../shared/charts';

type PieDatum = {
    category: string;
    value: number;
};

type ApiPieData = {
    category: string;
    duration_minutes: number;
};

interface ArcPathElement extends SVGPathElement {
    _current?: d3.PieArcDatum<PieDatum>;
}

const chartState = {
    range: 7,
}

function getData(lastNDays: number): Promise<PieDatum[]> {
    return new Promise((resolve, reject) => {
        const url = `/time_tracking/time_entries/summary?lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            const entries: ApiPieData[] = responseData.data;
            
            if(Array.isArray(entries) && entries.length === 0) {
                return resolve([]);
            }
            // const rollup = d3.rollup(data, reducerFn, keyFn);
            const rollupMap = d3.rollup(
                entries,
                v => d3.sum(v, d => d.duration_minutes),
                d => d.category
            );
            const arr: PieDatum[] = [...rollupMap].map(([k, v]) => ({category: k, value: v}));
            resolve(arr);
        }, reject);
    });
}

class TimeEntriesChart {
    private dims;
    private pie;
    private arc;
    private color;
    private radius;
    private gLegend;
    private gChart;
    private gRoot;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector);

        this.radius = Math.min(this.dims.innerWidth, this.dims.innerHeight) / 2;

        const svg = d3.select(containerSelector)
            .append("svg")
            .attr("width", this.dims.width)
            .attr("height", this.dims.height);

        this.gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        this.gChart = this.gRoot.append("g")
        .attr("transform", `translate(${this.dims.innerWidth/2}, ${this.dims.innerHeight/2})`);

        const pad = 20;
        const legendXOffset = (this.dims.innerWidth / 2) + this.radius + pad;
        this.gLegend = this.gRoot.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(${legendXOffset}, 0)`);

        // d3.pie() takes our array data and calculates angles
        this.pie = d3.pie<PieDatum>().value(d => d.value);
        // d3.arc() draws the curved slice shapes based on those angles
        this.arc = d3.arc<d3.PieArcDatum<PieDatum>>()
            .innerRadius(0)
            .outerRadius(this.radius);
        this.color = d3.scaleOrdinal(d3.schemeCategory10);
    }

    showEmptyChart() {
        this.gLegend.selectAll('g.legend-item').remove();
        this.gLegend.selectAll('.debug').remove();
        this.gChart.selectAll('g.slice').remove();

        const _emptyMessage = this.gChart.selectAll('text.empty-message')
            .data([1])
            .join("text")
            .attr("class", "empty-message")
            .attr("x", 0)
            .attr("y", 0)
            .attr("text-anchor", "middle")
            .attr("fill", "grey")
            .text(`No time entry data for this period.`)
    }

    async refreshPieChart() {
        const data = await getData(chartState.range);
        if (data.length === 0) {
            this.showEmptyChart();
            return;
        }
        this.updatePieChart(data);
    }

    updatePieChart(data: PieDatum[]) {
        this.gRoot.selectAll('.empty-message').remove();

        const pieData = this.pie(data);

        const groups = this.gChart.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.slice")
            // .data(data, keyFn)
            .data(pieData, d => d.data.category)
            .join(
                enter => {
                    const g = enter.append("g").attr("class", "slice");

                    // path (slice)
                    g.append('path')
                        .attr("class", "pie")
                        .attr("fill", d => this.color(d.data.category))
                        .each(
                            function(this: ArcPathElement, d) {
                                this._current = d;
                            })
                        .attr("d", this.arc);

                    return g;
                },
                update => {
                    const arc = this.arc; // Capture TimeEntriesChart's arc before .attrTween hijacks 'this'

                    update.select("path")
                        .transition().duration(500)
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

        const _legendItems = this.gLegend.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.legend-item")
            .data(pieData, d => d.data.category)
            .join(
                enter => {
                    const g = enter.append("g")
                        .attr("class", "legend-item")
                        .attr("transform", (_d, i) => `translate(0, ${i * 22})`);

                    // legend circle
                    g.append('circle')
                        .attr("cx", 10)
                        .attr("cy", 10)
                        .attr("r", 6)
                        .attr("class", "pie legend-dot")
                        .attr("fill", d => this.color(d.data.category));

                    // text alongside
                    g.append('text')
                        .attr("x", 18)
                        .attr("y", 14)
                        .attr("class", "chart-legend-text")
                        .text(d => `${d.data.category} - ${d.data.value} min`)

                    return g;
                },
                update => {
                    update.attr("transform", (_d, i) => {
                        return `translate(0, ${i * 22})`;
                    });
                    update.select('circle')
                        .attr("fill", d => this.color(d.data.category))
                    update.select('text')
                        .text(d => `${d.data.category} - ${d.data.value} min`)

                    return update;
                },
                exit => exit.remove()
            )

        // Enable tooltip on hover to see data
        const radius = this.radius; // Capture outside callback
        groups.on('mouseenter', function(_event, d) {
            showTooltip(this, `${d.data.category}: ${d.data.value}`);

            // Don't trigger hover effect if slice is > 75% of circle (since 2pi is full circle, so here we do 1.5pi)
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
            d3.select(this)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", `translate(${x}, ${y})`);
        });
        groups.on('mouseleave', function() {
            hideTooltip();
            d3.select(this)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", "translate(0, 0)");
        });
    }
}

export async function init() {
    const time_entriesChart = new TimeEntriesChart('#time_tracking-chart-container');
    await time_entriesChart.refreshPieChart();

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!, 10);
            time_entriesChart.refreshPieChart();
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

