import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getChartDimensions, hourMinsDisplay, initChartRangeButtons } from '../shared/charts';
import { isoToUserDate } from '../shared/datetime';
import { initTimeEntryForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { FormDialog, TimeEntry } from '../types';

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
    const response = await api.time_entries.summary(params)
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
    private gRoot; gChart; gLegend;
    private centerLabel; totalMins; highest; countOther; idleTimeout;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 20, right: 20, bottom: 20, left: 20 });

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

    private showIdleSummary() {
        this.centerLabel.selectAll("tspan").remove();
        // const highest = data.reduce((a, b) => a.value > b.value ? a : b)
        // const totalMins = data.reduce((a, b) => a + b.value, 0)
        this.centerLabel.selectAll("tspan").remove();
        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "0em")
            .text(`Total: ${hourMinsDisplay(this.totalMins)}`)

        this.centerLabel
            .append("tspan")
            .attr("x", 0)
            .attr("dy", "1.6em")
            .attr("font-size", "0.8rem")
            .text(`Top: ${this.highest.category}`)

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
        this.highest = data.reduce((a, b) => a.value > b.value ? a : b);
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

                    // g.append("text") // thing?
                    //     .attr("transform", d => this.labelTransform(d))
                    //     .attr("class", "slice-label")
                    //     .attr("opacity", 1) // TODO: RETURN TO 0 WHEN DONE DEBUGGING
                    //     .attr("pointer-events", "none")
                    //     .attr("stroke", d => this.color(d.data.category))
                    //     .attr("text-anchor", d => {
                    //         const mid = (d.startAngle + d.endAngle) / 2;
                    //         const isRight = mid < Math.PI;
                    //         return isRight ? "start" : "end"
                    //     })
                    //     .text(d => {
                    //         return `${hourMinsDisplay(d.data.value)} - 50%` // TODO fix
                    //     })

                    return g;
                },
                update => {
                    const arc = this.arc; // Capture TimeEntriesChart's arc before .attrTween hijacks 'this'

                    update.select("path")
                        .transition().duration(500)
                        // D3 needs prev state to interpolate from, and we need to store
                        // it ourselves bc join() is stateless?
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
            // this.showIdleSummary();
        })
        const radius = this.radius; // Capture outside callback
    }
}

export async function init() {
    const dialog = document.querySelector<FormDialog>('#time_entries-entry-dashboard-modal')
    if (!dialog) {
        console.warn('time_tracking dashboard: #time_entries-entry-dashboard-modal not found')
        return
    }
    initTimeEntryForm(dialog)

    const timeEntriesChart = new TimeEntriesChart('#time_tracking-chart-container');
    await timeEntriesChart.refreshPieChart();

    const btn = document.querySelector('[data-range="7"]');
    btn.classList.add('active');

    initChartRangeButtons(chartState, () => timeEntriesChart.refreshPieChart())
    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        // Handle table ellipsis options click
        if (!(target.matches('.js-table-options'))) {
            return
        }
        const button = target.closest('.row-actions')!;
        const row = target.closest<HTMLTableRowElement>('tr')!;
        const { itemId, subtype } = row.dataset;
        const modal = document.querySelector<FormDialog>('#time_entries-entry-dashboard-modal');
        const rect = button.getBoundingClientRect();

        contextMenu.create({
            position: { x: rect.left, y: rect.bottom },
            items: [
                {
                    label: 'Edit',
                    action: () => openModalForEdit<TimeEntry>(itemId, modal, 'Time Entry', (data) => {
                        const entryDateInput = modal.querySelector<HTMLInputElement>('#entry_date');
                        if (entryDateInput) {
                            entryDateInput.value = isoToUserDate(data.started_at);
                        }
                        // TODO: sync checkboxes for Pillars
                        data.pillars.forEach((p: {id: number}) => {
                            const cb = modal.querySelector(`input[value="${p.id}"]`);
                            if (cb) cb.checked = true;
                        })
                        // also sync the hidden input
                        modal.querySelector('#pillar_ids_hidden').value = data.pillars.map(p => p.id).join(',') ?? '';
                    })
                },
                {
                    label: 'Delete',
                    action: () => handleDelete(itemId, subtype)
                }
            ]
        })
    });
}

