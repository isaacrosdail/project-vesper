import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, enableStats, getChartDimensions, showEmptyChartMessage } from '../shared/charts';
import { apiRequest, routes } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager.js';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { initValidation, makeValidator } from '../shared/validators';
import { formatToUserTimeString } from '../shared/datetime';
import { userStore } from '../shared/services/userStore';


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
interface ChartState {
    range: number;
}
const chartState: ChartState = {
    range: 7,
}

type HeatmapApiEntry = {
    date: string;
    count: number;
}
type HeatmapCell = {
    date: Date;
    value: number;
    isFuture: boolean;
}

async function setupHeatmap() {
    const response = await apiRequest('GET', '/habits/habit_completions/heatmap');
    const heatmapData: HeatmapApiEntry[] = response.data;

    const lookup = new Map(heatmapData.map(d => [d.date, d.count]))

    // TODO: Fix - need to ensure we get a date matching current_user.timezone, not browser
    const todayStr = formatToUserTimeString(new Date(), {
        year: 'numeric', month: '2-digit', day: '2-digit'
    });
    const todayDate = new Date(todayStr + "T00:00:00") // no Z, so date JUST gets "yyyy-mm-dd" part, no TZ attached?
    const start = new Date(todayDate);
    start.setFullYear(todayDate.getFullYear() - 1)

    const days = d3.timeDays(start, todayDate) // generates one local-midnight Date per day in the range (zero-fills 'empty' dates)
    const data: HeatmapCell[] = days.map(d => {
        const dateStr = formatToUserTimeString(d, { year: 'numeric', month: '2-digit', day: '2-digit' });
        return {
            date: d,
            value: lookup.get(dateStr) ?? 0,
            isFuture: dateStr > todayStr
        };
    });

    const dims = getChartDimensions('.heatmap-group', { top: 20, right: 20, bottom: 20, left: 20 })
    const gap = 2;
    const numWeeks = 53;
    const cellSize = 14;
    const step = cellSize + gap
    const naturalWidth = numWeeks * step + dims.margin.left + dims.margin.right;

    const svg2 = d3.select(".heatmap-group").append("svg")
        .attr("width", naturalWidth)
        .attr("height", dims.height)

    const g = svg2.append("g")
        .attr("transform", `translate(${dims.margin.left}, ${dims.margin.top})`)

    const color2 = d3.scaleSequential()
        .domain([0, 4])
        .interpolator(d3.interpolateBlues)

    g.selectAll("rect") // draw cells
          .data(data)
          .join("rect")
          .attr("width", cellSize)
          .attr("height", cellSize)
          // Anchor left side of date starts to first date in data?
          .attr("x", d => d3.timeWeek.count(d3.timeYear(d.date), d.date) * step)
          .attr("y", d => d.date.getDay() * step)
          .attr("fill", d => d.isFuture
            ? "var(--text-muted)"
            : d.value === 0 ? "var(--bg-light)" : color2(d.value)
          )
          .attr("rx", 2) // rounded corners
          .on('mouseover', function(event, d) {
            const dateFormatted = formatToUserTimeString(d.date, { month: 'short', day: 'numeric', year: 'numeric'});
            createTooltip(this, `${d.value} completions - ${dateFormatted}`)
          })
          .on('mouseleave', function(event, d) {
            removeTooltip()
          })

    // Add legend
    const legendValues = [0, 1, 2, 3, 4]
    const legendY = 7 * step + 16; // some padding

    const legendG = g.append("g")
          .attr("transform", `translate(0, ${legendY})`)

    // TODO: align this, gets cut off :(
    legendG.append("text")
        .attr("class", "chart-legend-text")
        .attr("x", 0)
        .attr("y", cellSize / 2)
        .attr("dominant-baseline", "middle")
        .text("Less")

    legendValues.forEach((v, i) => {
        legendG.append("rect")
            .attr("x", 32 + i * step).attr("y", 0)
            .attr("width", cellSize).attr("height", cellSize)
            .attr("fill", v === 0
                ? "var(--bg-light)"
                : color2(v))
            .attr("rx", 2);
    });

    legendG.append("text")
        .attr("class", "chart-legend-text")
        .attr("x", 32 + legendValues.length * step + 4) // TODO: un-magic number this
        .attr("y", cellSize / 2)
        .attr("dominant-baseline", "middle")
        .text("More");

}


async function getHabitsData(lastNDays: number): Promise<BarData[]> {
    const params = new URLSearchParams({ lastNDays: lastNDays.toString()})
    const url = routes.habits.habit_completions.summary(params);
    const response = await apiRequest('GET', url, null);
    return response.data;
}

class HabitsChart {
    private dims;
    private gChart; gXAxis; gYAxis;
    private xScale; yScale;

    constructor(containerSelector: string) {
        this.dims = getChartDimensions(containerSelector, { top: 20, right: 20, bottom: 20, left: 40 });
        
        const svg = d3.select(containerSelector).append("svg")
                .attr("width", this.dims.width)
                .attr("height", this.dims.height)

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`)

        // TODO: FIX! looks weird
        const _title = svg.append("text")
            .attr("class", "chart-title")
            .attr("x", this.dims.innerWidth/2)
            .attr("y", this.dims.margin.top/2)
            .text("Completions by Habit")

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

    updateBarChart(data: BarData[]) {
        this.gChart.selectAll(".empty-message").remove();
        
        const maxVal = d3.max(data, (d: BarData) => Math.max(d.count, d.target_frequency * (chartState.range / 7)))!;

        // Target_frequency is per week, meaning we'll need to find 'cumulative' target frequency?
        this.xScale.domain([0, maxVal])
        this.yScale.domain(data.map(d => d.name))

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
                }).on('mouseleave', removeTooltip);

                // const rects = enter.append("rect")
                //     .attr("x", 0)
                //     .attr("y", (d: BarData) => this.yScale(d.name)!)
                //     .attr("width", 0)
                //     .attr("height", this.yScale.bandwidth())
                //     .attr("fill", "var(--accent-strong)") // TODO: css
                //     .attr("class", "bar")

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
                    // bar width is this.yScale.bandwidth() * 0.6
                    // so:
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
    setupHeatmap();
    enableStats();

    // const observer = new ResizeObserver(() => {
    //     console.log("nah")
    // });
    // const containerEl = document.querySelector('#habits-stats-container');
    // observer.observe(containerEl);

    const habitsChart = new HabitsChart('#habits-hbar-chart-container');
    await habitsChart.refreshBarChart();
    // set default chart range button's active class
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

            await habitsChart.refreshBarChart();
        }
        else if (target.matches('.table-range')) {
            const range = target.dataset['range']!;
            const table = target.dataset['table']!;
            
            const url = new URL(window.location.href);
            url.searchParams.set(`${table}_range`, range);
            window.location.href = url.toString();
        }

        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const row = target.closest('.table-row')!;
            const { itemId, subtype } = row.dataset;
            const rect = button.getBoundingClientRect();
            
            if (subtype === 'habits') {
                const url = routes.habits.habits.item(itemId);
                const modal = document.querySelector('#habits-entry-dashboard-modal');

                contextMenu.create({
                    position: { x: rect.left, y: rect.bottom },
                    items: [
                        {
                            label: 'Edit',
                            action: () => openModalForEdit(itemId, url, modal, 'Habit')
                        },
                        {
                            label: 'Delete',
                            action: () => handleDelete(itemId, url)
                        }
                    ]
                });
            } else if (subtype === 'leet_code_records') {
                const url = routes.habits.leet_code_records.item(itemId);
                const modal = document.querySelector<HTMLDialogElement>('#leet_code_records-entry-dashboard-modal');
                contextMenu.create({
                    position: { x: rect.left, y: rect.bottom },
                    items: [
                        {
                            label: 'Edit',
                            action: () => openModalForEdit(itemId, url, modal, 'lcrecord')
                        },
                        {
                            label: 'Delete',
                            action: () => handleDelete(itemId, url)
                        }
                    ]
                });
            }
        }
    });

    const validateHabitName = makeValidator('habit', { maxLength: 50 })
    const validateTargetFrequency = makeValidator('target_frequency', {
        isInt: true,
        min: 1,
        max: 21
    })

    const form = document.querySelector<HTMLFormElement>('#habits-form')!;
    initValidation(
        form,
        {
            name: validateHabitName,
            target_frequency: validateTargetFrequency,
        }
    )
}