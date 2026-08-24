import * as d3 from "d3";

import { withTooltip } from "../../shared/charts";
import { fmtDate } from "../../shared/datetime";
import { densifyTrailingDays, MetricType } from "../shared";

// Hit-goal vs missed-goal
export class ConsistencyMap {
    svg;
    gRoot;
    step;
    rows = 7;

    #config = {
        cellSize: 14,
        gap: 2,
    }

    // TODO(d3): Generally need to figure out "lower-is-better" vs "higher-is-better" handling
    // EX: for weight, lower-is-better, but for steps, going OVER is..also good.
    // Actually for weight, "closer to goal" is ideal.
    constructor(containerSelector: string) {
        this.step = this.#config.cellSize + this.#config.gap;
        const margin = { top: 5, left: 5, bottom: 30, right: 20 };

        this.svg = d3.select(containerSelector).append("svg")
        //     // .attr("viewBox", `0 0 ${width} ${height}`);

        // Shifts the origin inward by the margins
        this.gRoot = this.svg.append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`);

        this.#renderLegend();
    }

    renderGrid(data, targets: Record<MetricType, number>, metricType: MetricType, range: number) {
        // const cols = Math.ceil(data.length / rows);

        // TODO(d3): This is a repeat of densifyTrailingDays basically

    //    // Get start val as day matching beginning of update?
    //     const todayStr = getUserTodayDate();
    //     // Date for {range} days ago - 1:
    //     // start = today - (range - 1) // range=7 -> today - 6
    //     const today = new Date(todayStr + 'T00:00:00'); // local-midnight
    //     const start = d3.timeDay.offset(today, -(range-1)); // today - 6 for range=7
    //     const end = d3.timeDay.offset(today, 1); // +1, since timeDays is end-excl.
    //     const days = d3.timeDays(start, end); // exactly `range` Dates (asc)
        const gridData = densifyTrailingDays(data, range);
        const start = gridData[0].date;
        // Use generated 'days' for length/cols calc
        const last = gridData[gridData.length - 1].date;
        const cols = d3.timeWeek.count(start, last) + 1;
        const innerWidth = cols * this.step;
        const innerHeight = this.rows * this.step;
        const margin = { top: 5, left: 5, bottom: 30, right: 20 };
        const width = innerWidth + margin.left + margin.right;
        const height = innerHeight + margin.top + margin.bottom;

        this.svg.attr("width", width).attr("height", height);

        const target = targets[metricType];
        // const KEY_FMT = { year: 'numeric', month: '2-digit', day: '2-digit' } as const;
        // const lookup = new Map(data.map(d => [formatToUserTimeString(d.date, KEY_FMT), d.value]));

        // const gridData = days.map(d => {
        //     const dateStr = formatToUserTimeString(d, KEY_FMT);
        //     return { date: d, value: lookup.get(dateStr) ?? null }
        // })
        this.gRoot.selectAll("rect.cell")
            .data(gridData)
            .join("rect")
            .attr("class", "cell")
            .attr("width", this.#config.cellSize)
            .attr("height", this.#config.cellSize)
            // .attr("x", i => i * this.step) // walk across
            // How many _complete_ rows have i finished? -> quotient.
            // .attr("x", (_d, i) => Math.floor(i / rows) * this.step)

            // d3.timeWeek.count(a, b) counts the week-boundaries between two dates.
            //  The colfor a cell is "how many weeks from the start _is this cell_?"
            .attr("x", d => d3.timeWeek.count(start, d.date) * this.step) // week -> col
            // Where am i within the curr row? -> remainder (%)
            // .attr("y", (_d, i) => (i % rows) * this.step)
            .attr("y", d => d.date.getDay() * this.step) // weekday -> row
            .attr("rx", 2)
            // if d.value >= target[d.type] -> fill with metric color?
            .attr("fill", d => d.value !== null && d.value >= target
                ? "var(--metric-color)"
                : "var(--bg-light)"
            )
            .call(withTooltip(d => d.value !== null
                ? `${d.value} (${fmtDate(d.date)})`
                : null
            ));

    }

    #renderLegend() {
        // Render legend
        const gLegend = this.gRoot.append("g")
            .attr("transform", `translate(0, ${this.rows * this.step + 10})`)

        const [textWidthA, textWidthB] = [32,32];
        gLegend.append("text")
            .attr("class", "secondary")
            .attr("x", 0)
            .attr("y", this.#config.cellSize / 2)
            .attr("dominant-baseline", "middle")
            .text("Missed");

        gLegend.selectAll("rect.legend-cell")
            .data(d3.range(2))
            .join("rect")
            .attr("class", "legend-cell")
            .attr("x", (_v, i) => textWidthA + i * this.step)
            .attr("y", 0)
            .attr("width", this.#config.cellSize).attr("height", this.#config.cellSize)
            .attr("fill", (v) => v === 0 ? "var(--bg-light)" : "var(--metric-color)")
            .attr("rx", 2);

        gLegend.append("text")
            .attr("class", "secondary")
            .attr("x", textWidthA + 2 * this.step + 4)
            .attr("y", this.#config.cellSize / 2)
            .attr("dominant-baseline", "middle")
            .text("Hit goal");
    }
}