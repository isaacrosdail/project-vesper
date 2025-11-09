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

// Set up dimensions
const width = 300;
const height = 300;
const radius = Math.min(width, height) / 2;

// Pie chart
const svg = d3.select('#time-chart')
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width/2}, ${height/2})`);

// d3.pie() takes our array data and calculates angles
const pie = d3.pie<PieDatum>().value(d => d.value);
// d3.arc() draws the curved slice shapes based on those angles
const arc = d3.arc<d3.PieArcDatum<PieDatum>>()
    .innerRadius(0)
    .outerRadius(radius);
// Color Scale maps indexes to colors
const color = d3.scaleOrdinal(d3.schemeCategory10);


function updatePieChart(data: PieDatum[]) {
    let disableHoverEffects = data.length === 0 || data.length === 1;

    if (data.length === 0) {
        data = [{ category: 'No data', value: 1}];
    }
    const pieData = pie(data);

    const groups = svg.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.slice")
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
                // update paths
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

    const legend = svg.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.legend")
        .data(pieData, d => d.data.category)
        .join(
            enter => {
                const g = enter.append("g").attr("class", "legend");

                // Position each below the last
                g.attr("transform", (_d, i) => {
                    return `translate(170, ${-130 + (i * 22)})`
                })
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
                    return `translate(170, ${-130 + (i * 22)})`;
                });
                return update;
            },
            exit => exit.remove()
        )

    // Enable tooltip on hover to see data
    groups.on('mouseenter', function(_event, d) {
        if (disableHoverEffects) return;

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
        if (disableHoverEffects) return;

        hideToolTip();
        d3.select(this)
            .transition().duration(200)
            .attr("transform", "translate(0, 0)");
    });
}

export async function init() {
    // Render initial pie chart
    const data = await getData(7);
    updatePieChart(data);


    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.timeframe-selection')) {
            const range = parseInt(target.dataset['range']!, 10);
            const data = await getData(range);
            updatePieChart(data);
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