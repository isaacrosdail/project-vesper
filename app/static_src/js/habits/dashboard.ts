import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, enableStats, getChartDimensions, initChartRangeButtons, showEmptyChartMessage } from '../shared/charts';
import { formatToUserTimeString, getUserTodayDate } from '../shared/datetime';
import { initHabitForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { debounce } from '../shared/utils';
import { FormDialog } from '../types';


/**
 * What do we care about here?
 * 1. Which habits am I sticking to vs struggling with? - sorted hbar helps with that, maybe color code a bit on that curve?
 * 2. Is my consistency improving or declining over time for a given habit?
 * 3. Do I tend to cluster completions on certain days of the week? -> heatmap
 * 4. How long is my current streak vs best streak?
 * 
 * Correlation:
 * 1. Do I tend to complete more habits on the same days?
 * 2. Are there habits that almost always go together?
 * 
 * Motivation:
 * 1. Am I close to a milestone? (eg 80% this month)
 * 2. What's my "weakest" habit that I could realistically improve?
 */

type BarData = {
    name: string;
    count: number;
    target_frequency: number;
}
interface ChartState { range: number; }
const chartState: ChartState = { range: 7 }

type HeatmapApiEntry = {
    date: string;
    count: number;
}
type HeatmapCell = {
    date: Date;
    value: number;
    isFuture: boolean;
}

class HabitsHeatmap {
    private dims; gRoot; gLegend; color;

    private config = {
        cellSize: 14,
        gap: 2,
        numWeeks: 53
    };

    constructor(containerSelector: string) {
        // const gap = 2;
        // const numWeeks = 53;
        // const cellSize = 14;
        const step = this.config.cellSize + this.config.gap
        this.dims = getChartDimensions('.heatmap-group', { top: 20, right: 20, bottom: 20, left: 20 })

        const naturalWidth = this.config.numWeeks * step + this.dims.margin.left + this.dims.margin.right;
        const naturalHeight = 7 * step + 40 + this.dims.margin.top + this.dims.margin.bottom;

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", naturalWidth)
            .attr("height", naturalHeight)

        this.gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`)
    }

    async refresh() {
        const response = await api.habitCompletions.heatmap();
        const heatmapData: HeatmapApiEntry[] = response.data;
        if (!heatmapData.length) {
            console.warn('HabitsHeatmap refresh: heatmapData returned empty')
            return
        }
        this.render(heatmapData);
    }

    private render(heatmapData: HeatmapApiEntry[]) {
        // const gap = 2;
        // const numWeeks = 53;
        // const cellSize = 14;
        const step = this.config.cellSize + this.config.gap;

        const lookup = new Map(heatmapData.map(d => [d.date, d.count]))

        // TODO: Fix - need to ensure we get a date matching current_user.timezone, not browser
        const todayStr = getUserTodayDate();
        const todayDate = getUserTodayDate();
        const year = Number(todayStr.slice(0, 4));
        const start = new Date(year, 0, 1);
        const end = new Date(year + 1, 0, 1);

        const days = d3.timeDays(start, end); // generates one local-midnight Date per day in the range (zero-fills 'empty' dates)
        const data: HeatmapCell[] = days.map(d => {
            const dateStr = formatToUserTimeString(d, { year: 'numeric', month: '2-digit', day: '2-digit' });
            return {
                date: d,
                value: lookup.get(dateStr) ?? 0,
                isFuture: dateStr > todayStr
            };
        });

        this.color = d3.scaleSequential()
            // .domain([0, 4])
            .domain([0, d3.max(data, d => d.value) ?? 4]) // better? otherwise 4+ completions
            // just look the same - max blue. :/
            .interpolator(d3.interpolateBlues)

        // Cells
        this.gRoot.selectAll("rect.cell") // draw cells
            .data(data)
            .join("rect")
            .attr("class", "cell")
            .attr("width", this.config.cellSize)
            .attr("height", this.config.cellSize)
            // Anchor left side of date starts to first date in data?
            .attr("x", d => d3.timeWeek.count(d3.timeYear(d.date), d.date) * step)
            .attr("y", d => d.date.getDay() * step)
            .attr("fill", d => d.isFuture
                ? "var(--text-muted)" // TODO: Tune, looks jank
                : d.value === 0 ? "var(--bg-light)" : this.color(d.value)
            )
            .attr("rx", 2) // rounded corners
            .on('mouseover', function(_event, d) {
                const dateFormatted = formatToUserTimeString(d.date, { month: 'short', day: 'numeric', year: 'numeric'});
                const completions = d.value === 1 ? 'completion' : 'completions';
                createTooltip(this, `${d.value} ${completions} - ${dateFormatted}`)
            })
            .on('mouseleave', function() { removeTooltip(this) });

        this.renderLegend(step);
    }

    private renderLegend(step: number) {
        // Add legend
        const legendValues = [0, 1, 2, 3, 4];
        
        const [lessTextWidth, moreTextWidth] = [32, 32];
        const boxesWidth = legendValues.length * step;
        const legendTotalWidth = lessTextWidth + boxesWidth + moreTextWidth;

        const legendX = (this.dims.innerWidth - legendTotalWidth) / 2;
        const legendY = 7 * step + 16; // some padding

        const gLegend = this.gRoot.append("g")
            .attr("transform", `translate(${legendX}, ${legendY})`)

        // TODO: align this, gets cut off :(
        gLegend.append("text")
            .attr("class", "chart-legend-text")
            .attr("x", 0)
            .attr("y", this.config.cellSize / 2)
            .attr("dominant-baseline", "middle")
            .text("Less")

        gLegend.selectAll("rect.legend-cell")
            .data(legendValues)
            .join("rect")
            .attr("class", "legend-cell")
            .attr("x", (_v, i) => lessTextWidth + i * step)
            .attr("y", 0)
            .attr("width", this.config.cellSize)
            .attr("height", this.config.cellSize)
            .attr("fill", (v) => v === 0 ? "var(--bg-light)" : this.color(v))
            .attr("rx", 2)

        gLegend.append("text")
            .attr("class", "chart-legend-text")
            .attr("x", lessTextWidth + legendValues.length * step + 4) // TODO: un-magic number this
            .attr("y", this.config.cellSize / 2)
            .attr("dominant-baseline", "middle")
            .text("More");
    }
}


async function getHabitsData(lastNDays: number): Promise<BarData[]> {
    const params = new URLSearchParams({ lastNDays: lastNDays.toString()})
    const response = await api.habitCompletions.summary(params);
    return response.data;
}

class HabitsChart {
    private dims;
    private gChart; gXAxis; gYAxis;
    private xScale; yScale;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 20, right: 20, bottom: 20, left: 160 });
        
        const svg = d3.select(containerSelector).append("svg")
                .attr("width", this.dims.width)
                .attr("height", this.dims.height)

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`)

        // TODO: FIX! looks weird
        // gRoot.append("text")
        //     .attr("class", "chart-title")
        //     .attr("x", this.dims.innerWidth/2)
        //     .attr("y", -this.dims.margin.top/2)
        //     .attr("text-anchor", "middle")
        //     .text("Completions by Habit")

        this.gXAxis = gRoot.append("g")
            .attr("class", "axis-x")
            .attr("transform", `translate(0, ${this.dims.innerHeight})`);
        this.gYAxis = gRoot.append("g")
            .attr("class", "axis-y");
        this.gChart = gRoot.append("g")
            .attr("class", "chart");

        this.xScale = d3.scaleLinear().range([0, this.dims.innerWidth]);
        this.yScale = d3.scaleBand().range([0, this.dims.innerHeight]).padding(0.2);
    }

    private updateScales(data: BarData[]) {
        const maxVal = d3.max(
            data,
            d => Math.max(d.count, d.target_frequency * (chartState.range / 7))
        ) ?? 0;

        this.xScale.domain([0, maxVal]);
        this.yScale.domain(data.map(d => d.name));

        return maxVal;
    }

    updateBarChart(data: BarData[]) {
        this.gChart.selectAll(".empty-message").remove();

        const maxVal = this.updateScales(data);
        // TODO: dry this up, still have some repetitive copies of this sprinkled around
        // Rounds up to nearest 5
        const step = Math.max(1, Math.ceil(maxVal / 10 / 5) * 5);
        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(d3.range(0, maxVal! + 1, step))
                .tickFormat(d3.format("d")) // force integer display for bottom-axis ticks
            )
        this.gYAxis.call(d3.axisLeft(this.yScale));

        // Math for the "bar height vs track height" thing
        const bw = this.yScale.bandwidth();
        const barHeight = bw * 0.7;

        const bars = this.gChart.selectAll("g.habit-row")
        .data(data, d => d.name)
        .join(
            enter => {
                // Group for actual bar + target bar
                // This will get the y position for the both of them, then
                // each track and bar pairing will sit at y=0 relative to the group
                // since the group represents the pair of them
                const habitRow = enter.append("g")
                    .attr("class", "habit-row")
                    .attr("transform", d => `translate(0, ${this.yScale(d.name)})`)

                // For target frequency
                const habitTrack = habitRow.append("rect")
                    .attr("class", "track")
                    .attr("opacity", 0.3)
                    .attr("fill", "var(--accent-subtle)")
                    .attr("width", d => this.xScale(d.target_frequency * (chartState.range / 7)))
                    .attr("height", this.yScale.bandwidth())

                // For actual completion count
                const habitBar = habitRow.append("rect")
                    .attr("class", "bar")
                    .attr("fill", "var(--accent-strong)") // TODO: interpolate for "more intense = blue"? then low succes bars get red?
                    .attr("width", 0)
                    .attr("height", barHeight)
                    .attr("y", (bw - barHeight) / 2)

                habitBar.on('mouseenter', function(this: d3.BaseType, _event: Event, d: BarData) {
                    createTooltip(this as SVGRectElement, `${d.name}: ${d.count}`);
                }).on('mouseleave', function() { removeTooltip(this) });

                habitBar.transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("width", (d: BarData) => this.xScale(d.count))

                return habitRow
            },
            update =>  {
                update.attr("transform", d => `translate(0, ${this.yScale(d.name)})`)

                update.select("rect.track")
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("width", (d: BarData) => this.xScale(d.target_frequency * (chartState.range / 7)))
                    .attr("height", this.yScale.bandwidth())
                
                update.select("rect.bar")
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("width", d => this.xScale(d.count))
                    .attr("height", barHeight)
                    // want y = (track width - bar width) / 2
                    // track width is this.yScale.bandwidth()
                    // bar width is this.yScale.bandwidth() * 0.6, so:
                    .attr("y", (bw - barHeight) / 2)

                return update
            },
            exit => exit.remove()
        );

        const labels = this.gChart.selectAll("text.value")
        .data(data, d => d.name)
        .join(
            enter => enter.append("text")
                .attr("class", "value") // TODO: rename, this is the text on the right side of hbar bars for value
                .attr("dominant-baseline", "middle")
                .attr("x", 0)
                .attr("y", d => this.yScale(d.name)! + this.yScale.bandwidth() / 2)
                .text(d => d.count)
                .call(enter => enter.transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.xScale(d.count) + 6)
            ),
            update => update
                .text(d => d.count)
                .call(update => update.transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.xScale(d.count) + 6)
                    .attr("y", d => this.yScale(d.name)! + this.yScale.bandwidth() / 2)
            ),
            exit => exit.remove()
        )
    }

    showEmptyChart() {
        this.gChart.selectAll('rect.bar').remove();

        // Clear axes
        this.yScale.domain([]); // empty domain = no tick labels
        this.gYAxis.call(d3.axisLeft(this.yScale));

        this.xScale.domain([]);
        this.gXAxis.call(d3.axisBottom(this.xScale));

        showEmptyChartMessage(
            this.gChart,
            "No completion data for this period",
            this.dims.innerWidth,
            this.dims.innerHeight
        )
    }

    resize() {
        // re-read chartdimensions, update scales/ranges, redraws
        // Could even decrease margins + truncate labels or rotating them for smaller screens
    }

    async refreshBarChart() {
        const data = await getHabitsData(chartState.range);
        if (data.length === 0) {
            this.showEmptyChart();
            return;
        }
        this.updateBarChart(data);
    }
}

export async function init() {
    // setupHeatmap();
    enableStats();

    const heatmap = new HabitsHeatmap('.heatmap-group')
    await heatmap.refresh();

    const habitsChart = new HabitsChart('#habits-hbar-chart-container');
    await habitsChart.refreshBarChart();

    const observer = new ResizeObserver(debounce(() => {
        habitsChart.resize();
    }, 150));
    const containerEl = document.querySelector('#habits-stats-container');
    observer.observe(containerEl);

    // For habits chart timeframe pills
    const selector = document.querySelector('[data-timeframe="habits-chart"]');
    const btn = selector.querySelector('[data-range="7"]');
    btn.classList.add('active');

    initChartRangeButtons(chartState, () => habitsChart.refreshBarChart())

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;

        if (!(target.matches('.js-table-options'))) {
            return
        }
        const button = target.closest('.row-actions')!;
        const row = target.closest('tr')!;
        const { itemId, subtype } = row.dataset;
        const rect = button.getBoundingClientRect();

        if (subtype === 'habits') {
            const modal = document.querySelector('#habits-entry-dashboard-modal');

            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => openModalForEdit(itemId, modal, 'Habit', (data) => {
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
            });
        }
    });

    const dialog = document.querySelector<FormDialog>('#habits-entry-dashboard-modal')
    if (!dialog) {
        console.warn('tasks dashboard: #habits-entry-dashboard-modal not found')
        return
    }
    initHabitForm(dialog)

}