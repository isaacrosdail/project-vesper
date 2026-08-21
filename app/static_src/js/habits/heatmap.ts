import { getDims, withTooltip } from "../shared/charts";
import * as d3 from 'd3';
import { todayUser } from "../shared/datetime";
import { Temporal } from "temporal-polyfill";

export type HeatmapApiEntry = {
    date: string;
    count: number;
}
type HeatmapCell = {
    date: Date;
    value: number;
    isFuture: boolean;
}

const LEGEND_VALUES = [0, 1, 2, 3, 4];


export class HabitsHeatmap {
    #dims;
    #gRoot;
    #gLegend;
    #color;

    private config = {
        cellSize: 14,
        gap: 2,
        numWeeks: 53,
        legendTextWidth: 32,
    };

    constructor(containerSelector: string | HTMLElement) {
        this.#color = d3.scaleSequential(d3.interpolateBlues);

        const step = this.config.cellSize + this.config.gap
        this.#dims = getDims(100, 100, { top: 20, right: 20, bottom: 20, left: 20 });

        const naturalWidth = this.config.numWeeks * step + this.#dims.margin.left + this.#dims.margin.right;
        const naturalHeight = 7 * step + 40 + this.#dims.margin.top + this.#dims.margin.bottom;

        const svg = d3.select(containerSelector).append("svg")
            .attr("width", naturalWidth)
            .attr("height", naturalHeight)

        this.#gRoot = svg.append("g")
            .attr("transform", `translate(${this.#dims.margin.left}, ${this.#dims.margin.top})`);


        const legendTotalWidth = this.config.legendTextWidth * 2 + LEGEND_VALUES.length * step;
        const legendX = (this.#dims.innerWidth - legendTotalWidth) / 2;
        const legendY = 7 * step + 16; // some padding

        this.#gLegend = this.#gRoot.append("g")
            .attr("transform", `translate(${legendX}, ${legendY})`);

        this.#gLegend.append("text")
            .attr("class", "chart-legend-text")
            .attr("x", 0)
            .attr("y", this.config.cellSize / 2)
            .attr("dominant-baseline", "middle")
            .text("Less")

        this.#gLegend.append("text")
            .attr("class", "chart-legend-text")
            .attr("x", this.config.legendTextWidth + LEGEND_VALUES.length * step + 4) // TODO: un-magic number this
            .attr("y", this.config.cellSize / 2)
            .attr("dominant-baseline", "middle")
            .text("More");
    }

    render(heatmapData: HeatmapApiEntry[]) {
        const step = this.config.cellSize + this.config.gap;
        const lookup = new Map(heatmapData.map(d => [d.date, d.count]))

        // TODO: Fix - need to ensure we get a date matching current_user.timezone, not browser
        const today = todayUser();
        const jan1 = new Temporal.PlainDate(today.year, 1, 1);
        const days = Array.from({ length: jan1.daysInYear, }, (_, i) => jan1.add({ days: i }));
        const data: HeatmapCell[] = days.map(day => {
            return {
                date: new Date(day.toString() + 'T00:00:00'),
                value: lookup.get(day.toString()) ?? 0,
                isFuture: Temporal.PlainDate.compare(day, today) > 0
            };
        });

        this.#color.domain([0, d3.max(data, d => d.value) ?? 4]); // better? otherwise 4+ completions

        // Cells
        this.#gRoot.selectAll("rect.cell")
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
                : d.value === 0 ? "var(--bg-light)" : this.#color(d.value)
            )
            .attr("rx", 2) // rounded corners
            .call(withTooltip(d => {
                if (!d.value) return null;
                const dateFormatted = d3.timeFormat("%b %d, %Y")(d.date);
                const completions = d.value === 1 ? 'completion' : 'completions';
                return `${d.value} ${completions} - ${dateFormatted}`;
            }))

        this.#renderLegend(step);
    }

    #renderLegend(step: number) {
        this.#gLegend.selectAll("rect.legend-cell")
            .data(LEGEND_VALUES)
            .join("rect")
            .attr("class", "legend-cell")
            .attr("x", (_v, i) => this.config.legendTextWidth + i * step)
            .attr("y", 0)
            .attr("width", this.config.cellSize)
            .attr("height", this.config.cellSize)
            .attr("fill", (v) => v === 0 ? "var(--bg-light)" : this.#color(v))
            .attr("rx", 2);
    }
}