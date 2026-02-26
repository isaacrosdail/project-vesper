import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, hourMinsDisplay, getChartDimensions } from '../shared/charts';
import { apiRequest, routes } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager.js';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { initValidation, makeValidator } from '../shared/validators';

/**
 * Thoughts:
 * - Am I spending time on the right things?
 * - Balance: Am I over-indexing on one category and neglecting others?
 * - Work vs rest ratio: Burning out? Coasting?
 * - Trends: Is activity A going up or down over the given window?
 */



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

async function getData(lastNDays: number): Promise<PieDatum[]> {
    const params = new URLSearchParams({ lastNDays: lastNDays.toString() })
    const url = routes.time_tracking.time_entries.summary(params);
    const response = await apiRequest('GET', url, null);
    const entries: ApiPieData[] = response.data;
    
    if(Array.isArray(entries) && entries.length === 0) {
        return [];
    }
    // const rollup = d3.rollup(data, reducerFn, keyFn);
    const rollupMap = d3.rollup(
        entries,
        v => d3.sum(v, d => d.duration_minutes),
        d => d.category
    );
    const arr: PieDatum[] = [...rollupMap].map(([k, v]) => ({category: k, value: v}));
    return arr;
}


class TimeEntriesChart {
    private dims; radius;
    private pie; arc;
    private color;
    private gRoot; gChart; gLegend; centerLabel;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector);

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

    showEmptyChart() {
        this.gLegend.selectAll('g.legend-item').remove();
        this.gChart.selectAll('g.slice').remove();

        const _emptyMessage = this.gChart.selectAll('text.empty-message')
            .data([1])
            .join("text")
            .attr("class", "empty-message")
            .attr("text-anchor", "middle")
            .attr("x", 0)
            .attr("y", 0)
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

    // Adjust text label positions for each slice to show at appropriate locations
    private labelTransform(d): string {
        const mid = (d.startAngle + d.endAngle) / 2;
        const [x, y] = this.arc.centroid(d);
        const xOffset = mid < Math.PI ? 15 : -15;
        const yOffsetSign = Math.sign(Math.sin(mid - Math.PI / 2));
        const yOffset = yOffsetSign * 20;
        return `translate(${x + xOffset}, ${y + yOffset})`
    }

    updatePieChart(data: PieDatum[]) {
        this.gRoot.selectAll('.empty-message').remove();

        const sorted = [...data].toSorted((a, b) => b.value - a.value);
        const pieData = this.pie(sorted);

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

                    g.append("text") // thing?
                        .attr("transform", d => this.labelTransform(d))
                        .attr("class", "slice-label")
                        .attr("opacity", 1) // TODO: RETURN TO 0 WHEN DONE DEBUGGING
                        .attr("pointer-events", "none")
                        .attr("stroke", d => this.color(d.data.category))
                        .attr("text-anchor", d => {
                            const mid = (d.startAngle + d.endAngle) / 2;
                            const isRight = mid < Math.PI;
                            return isRight ? "start" : "end"
                        })
                        .text(d => {
                            return `${hourMinsDisplay(d.data.value)} - 50%` // TODO fix
                        })

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

                    update.select(".slice-label")
                        .attr("transform", d => this.labelTransform(d))
                        .attr("text-anchor", d => {
                            const mid = (d.startAngle + d.endAngle) / 2;
                            const isRight = mid < Math.PI;
                            return isRight ? "start" : "end"
                        })

                    return update;
                },
                exit => exit.remove()
            );

        // Text in the center of donut
        const highest = data.reduce((a, b) => a.value > b.value ? a : b)
        const totalMins = data.reduce((a, b) => a + b.value, 0)
        this.centerLabel.selectAll("tspan").remove();
        this.centerLabel
        .append("tspan")
        .attr("x", 0)
        .attr("dy", "0em")
        .text(`Total: ${hourMinsDisplay(totalMins)}`)
        
        this.centerLabel
        .append("tspan")
        .attr("x", 0)
        .attr("dy", "1.6em")
        .attr("font-size", "0.8rem")
        .text(`Top: ${highest.category}`)
        // ==============================

        const _legendItems = this.gLegend.selectAll<SVGGElement, d3.PieArcDatum<PieDatum>>("g.legend-item")
            .data(pieData, d => d.data.category)
            .join(
                enter => {
                    const g = enter.append("g")
                        .attr("class", "legend-item")
                        .attr("transform", (_d, i, nodes) => {
                            const x = (i + 0.5) / nodes.length * this.dims.innerWidth;
                            return `translate(${x}, 0)`
                        })

                    // legend circle
                    // g.append('circle')
                    //     .attr("cx", 0)
                    //     .attr("cy", 0)
                    //     .attr("r", 6)
                    //     .attr("class", "pie legend-dot")
                    //     .attr("fill", d => this.color(d.data.category));

                    // text alongside
                    g.append('text')
                        .attr("x", 18)
                        .attr("y", 14)
                        .attr("class", "chart-legend-text")
                        .attr("text-anchor", "middle")
                        .attr("stroke", d => this.color(d.data.category))
                        // .text(d => `${d.data.category} - ${hourMinsDisplay(d.data.value)}`)
                        .text(d => `${d.data.category}`)
                    return g;
                },
                update => {
                    update.attr("transform", (_d, i, nodes) => {
                        const x = (i + 0.5) / nodes.length * this.dims.innerWidth;
                        return `translate(${x}, 0)`;
                    });
                    update.select('circle')
                        .attr("fill", d => this.color(d.data.category))
                    update.select('text')
                        .text(d => `${d.data.category} - ${hourMinsDisplay(d.data.value)}`)

                    return update;
                },
                exit => exit.remove()
            )

        // Enable tooltip on hover to see data
        const radius = this.radius; // Capture outside callback
        _legendItems.on('mouseenter', (_event, d) =>  {
            const match = this.gChart.selectAll("g.slice")
                .filter(sd => sd.data.category === d.data.category);

            match.select("text")
                .attr("opacity", 1)
            const sd = match.datum();
            const mid = (sd.startAngle + sd.endAngle) / 2 - Math.PI / 2;
            const dist = this.radius / 10;

            match.transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", `translate(${Math.cos(mid) * dist}, ${Math.sin(mid) * dist})`)
                // .attr("opacity", 1)
        })
        .on('mouseleave', (_event, d) => {
            const match = this.gChart.selectAll("g.slice")
                .filter(sd => sd.data.category === d.data.category)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", "translate(0, 0)")
            match.select("text")
                .attr("opacity", 0)
        })
        groups.on('mouseenter', function(_event, d) {
            createTooltip(this, `${d.data.category}: ${hourMinsDisplay(d.data.value)}`);

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
            d3.select(this)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", `translate(${x}, ${y})`);
        });
        groups.on('mouseleave', function() {
            removeTooltip();
            d3.select(this)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("transform", "translate(0, 0)");
        });
    }
}

export async function init() {
    const timeEntriesChart = new TimeEntriesChart('#time_tracking-chart-container');
    await timeEntriesChart.refreshPieChart();
    const btn = document.querySelector('[data-range="7"]');
    btn.classList.add('active');

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!, 10);
            document.querySelectorAll('.chart-range').forEach(btn => {
                btn.classList.remove('active');
            })
            target.classList.add('active');

            await timeEntriesChart.refreshPieChart();
        }
        else if (target.matches('.table-range')) {
            const range = target.dataset['range']!;
            const table = target.dataset['table']!;

            const url = new URL(window.location.href);
            url.searchParams.set(`${table}_range`, range);
            window.location.href = url.toString();
        }

        // Handle table ellipsis options click
        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const row = target.closest('.table-row')!;
            const { itemId } = row.dataset;
            const url = routes.time_tracking.time_entries.item(itemId);
            const modal = document.querySelector('#time_entries-entry-dashboard-modal');
            const rect = button.getBoundingClientRect();

            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => openModalForEdit(itemId, url, modal, 'Time Entry')
                    },
                    {
                        label: 'Delete',
                        action: () => handleDelete(itemId, url)
                    }
                ]
            })
        }
    });

    const validateCategory = makeValidator('category', {
        maxLength: 50,
    });

    const validateDescription = makeValidator('description', {
        maxLength: 200,
    })

    // Validation
    const timeTrackingForm = document.querySelector<HTMLFormElement>('#time_entries-form')!;

    initValidation(timeTrackingForm, {
        category: validateCategory,
        description: validateDescription,
    });
}

