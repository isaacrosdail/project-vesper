import * as d3 from 'd3';

import { hideToolTip, showToolTip } from '../shared/ui/tooltip';
import { apiRequest } from '../shared/services/api';

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

// Set up dimensions
const width = 300;
const height = 300;
const radius = Math.min(width, height) / 2;
const margin = { top: 20, right: 20, bottom: 20, left: 20 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

// Pie chart
const svg = d3.select('#time_tracking-chart-container')
    .append("svg")
    .attr("width", width)
    .attr("height", height)

const gRoot = svg.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

const gChart = gRoot.append("g")
    .attr("transform", `translate(${innerWidth/2}, ${innerHeight/2})`);

const gLegend = gRoot.append("g")
    .attr("class", "legend")
    .attr("transform", `translate(300, 0)`);

// d3.pie() takes our array data and calculates angles
const pie = d3.pie<PieDatum>().value(d => d.value);
// d3.arc() draws the curved slice shapes based on those angles
const arc = d3.arc<d3.PieArcDatum<PieDatum>>()
    .innerRadius(0)
    .outerRadius(radius);
// Color Scale maps indexes to colors
const color = d3.scaleOrdinal(d3.schemeCategory10);

async function refreshPieChart() {
    const data = await getData(chartState.range);
    console.log(data)

    if (data.length === 0) {
        showEmptyChart();
        return;
    }

    updatePieChart(data);
}

function showEmptyChart() {
    gLegend.selectAll('g.legend-item').remove();
    gLegend.selectAll('.debug').remove();
    gChart.selectAll('g.slice').remove();

    const emptyMessage = gChart.selectAll('text.empty-message')
        .data([1])
        .join("text")
        .attr("class", "empty-message")
        .attr("x", 0)
        .attr("y", 0)
        .attr("text-anchor", "middle")
        .attr("fill", "grey")
        .text(`No time entry data for this period.`)
}

function updatePieChart(data: PieDatum[]) {

    gRoot.selectAll('.empty-message').remove();

    const pieData = pie(data);

    const groups = gChart.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.slice")
        // .data(data, keyFn)
        .data(pieData, d => d.data.category) // key function = stable matching?
        .join(
            enter => {
                const g = enter.append("g").attr("class", "slice");

                // path (slice)
                g.append('path')
                    .attr("class", "pie")
                    .attr("fill", d => color(d.data.category))
                    .each(
                        function(this: ArcPathElement, d) {
                            this._current = d; // store start?
                        })
                    .attr("d", arc);

                return g;
            },
            update => {
                update.select("path")
                    .transition().duration(500)
                    .attrTween("d", function(d) {
                        const el = this as ArcPathElement;
                        const i = d3.interpolate(el._current, d);
                        el._current = i(1);
                        return t => arc(i(t)) ?? ""; // ?? "" here since arc can return null, which TS doesn't like
                    });

                return update;
            },
            exit => exit.remove()
        );

    const legendItems = gLegend.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.legend-item")
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
                    .attr("fill", d => color(d.data.category));

                // text alongside
                g.append('text')
                    .attr("x", 18)
                    .attr("y", 14)
                    .attr("class", "chart-legend-text")
                    .text(d => `${d.data.category} - ${d.data.value} min`)

                return g;
            },
            update => {
                // Update transform to update positions
                update.attr("transform", (_d, i) => {
                    return `translate(0, ${i * 22})`;
                });
                return update;
            },
            exit => exit.remove()
        )

    // Enable tooltip on hover to see data
    groups.on('mouseenter', function(_event, d) {
        showToolTip(this, `${d.data.category}: ${d.data.value}`);

        // Calc midpoint (angle)
        const rawMidpoint = (d.startAngle + d.endAngle) / 2;
        const midpoint = rawMidpoint - (Math.PI / 2);
        const dist = radius / 10;

        // Calc x, y offsets for transform
        const x = Math.cos(midpoint) * dist;
        const y = Math.sin(midpoint) * dist;

        // Transform
        d3.select(this)
            .transition().duration(200)
            .attr("transform", `translate(${x}, ${y})`);
    });
    groups.on('mouseleave', function() {
        hideToolTip();
        d3.select(this)
            .transition().duration(200)
            .attr("transform", "translate(0, 0)");
    });
}

export async function init() {
    await refreshPieChart();

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!, 10);
            await refreshPieChart();
        }
        else if (target.matches('.table-range')) {
            const range = parseInt(target.dataset['range']!);
            window.location.href = `/time_tracking/dashboard?range=${range}`;
        }
    });
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