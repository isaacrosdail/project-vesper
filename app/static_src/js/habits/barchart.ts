import * as d3 from 'd3';
import { D3_TRANSITION_DURATION_MS, getDims } from '../shared/charts';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';

export type BarData = {
    name: string;
    count: number;
    expected: number;
}


export class HabitsChart {
    #dims;
    #gChart; #gXAxis; #gYAxis;
    #xScale; #yScale;

    constructor(containerSelector: string) {
        this.#dims = getDims(320, 640, { top: 20, right: 20, bottom: 20, left: 160 })
        
        const svg = d3.select(containerSelector).append("svg")
                .attr("width", this.#dims.width)
                .attr("height", this.#dims.height)

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.#dims.margin.left}, ${this.#dims.margin.top})`)

        this.#gXAxis = gRoot.append("g")
            .attr("class", "axis-x")
            .attr("transform", `translate(0, ${this.#dims.innerHeight})`);
        this.#gYAxis = gRoot.append("g")
            .attr("class", "axis-y");
        this.#gChart = gRoot.append("g")
            .attr("class", "chart");

        this.#xScale = d3.scaleLinear().range([0, this.#dims.innerWidth]);
        this.#yScale = d3.scaleBand().range([0, this.#dims.innerHeight]).padding(0.2);
    }

    #updateScales(data: BarData[]) {
        const maxVal = d3.max(
            data,
            d => Math.max(d.count, d.expected)
        ) ?? 0;

        this.#xScale.domain([0, maxVal]);
        this.#yScale.domain(data.map(d => d.name));

        return maxVal;
    }

    updateBarChart(data: BarData[]) {
        this.#gChart.selectAll(".empty-message").remove();

        const maxVal = this.#updateScales(data);
        // TODO: dry this up, still have some repetitive copies of this sprinkled around
        // Rounds up to nearest 5
        const step = Math.max(1, Math.ceil(maxVal / 10 / 5) * 5);
        this.#gXAxis.call(
            d3.axisBottom(this.#xScale)
                .tickValues(d3.range(0, maxVal! + 1, step))
                .tickFormat(d3.format("d")) // force integer display for bottom-axis ticks
            )
        this.#gYAxis.call(d3.axisLeft(this.#yScale));

        // Math for the "bar height vs track height" thing
        const bw = this.#yScale.bandwidth();
        const barHeight = bw * 0.7;

        this.#gChart.selectAll("g.habit-row") // was: const bars
        .data(data, d => d.name)
        .join(
            enter => {
                // Group for actual bar + target bar
                // This will get the y position for the both of them, then
                // each track and bar pairing will sit at y=0 relative to the group
                // since the group represents the pair of them
                const habitRow = enter.append("g")
                    .attr("class", "habit-row")
                    .attr("transform", d => `translate(0, ${this.#yScale(d.name)})`)

                // For target frequency
                habitRow.append("rect")  // was habitTrack
                    .attr("class", "track")
                    .attr("opacity", 0.3)
                    .attr("fill", "var(--accent-subtle)")
                    .attr("width", d => this.#xScale(d.expected))
                    .attr("height", this.#yScale.bandwidth())

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
                    .attr("width", (d: BarData) => this.#xScale(d.count))

                return habitRow
            },
            update =>  {
                update.attr("transform", d => `translate(0, ${this.#yScale(d.name)})`)

                update.select("rect.track")
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("width", (d: BarData) => this.#xScale(d.expected))
                    .attr("height", this.#yScale.bandwidth())
                
                update.select("rect.bar")
                    .transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("width", d => this.#xScale(d.count))
                    .attr("height", barHeight)
                    // want y = (track width - bar width) / 2
                    // track width is this.#yScale.bandwidth()
                    // bar width is this.#yScale.bandwidth() * 0.6, so:
                    .attr("y", (bw - barHeight) / 2)

                return update
            },
            exit => exit.remove()
        );

        this.#gChart.selectAll("text.value") // was const labels
        .data(data, d => d.name)
        .join(
            enter => enter.append("text")
                .attr("class", "value") // TODO: rename, this is the text on the right side of hbar bars for value
                .attr("dominant-baseline", "middle")
                .attr("x", 0)
                .attr("y", d => this.#yScale(d.name)! + this.#yScale.bandwidth() / 2)
                .text(d => d.count)
                .call(enter => enter.transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.#xScale(d.count) + 6)
            ),
            update => update
                .text(d => d.count)
                .call(update => update.transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("x", d => this.#xScale(d.count) + 6)
                    .attr("y", d => this.#yScale(d.name)! + this.#yScale.bandwidth() / 2)
            ),
            exit => exit.remove()
        )
    }
}