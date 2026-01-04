import * as d3 from 'd3';

import { apiRequest } from '../shared/services/api';
import { createTooltip, removeTooltip } from '../shared/ui/tooltip';
import { getChartDimensions, D3_TRANSITION_DURATION_MS } from '../shared/charts';

type BarData = {
    name: string;
    count: number;
}

const chartState = {
    range: 7,
}

async function getHabitsData(lastNDays: number): Promise<BarData[]> {
    const params = new URLSearchParams({ lastNDays: lastNDays.toString()})
    const url = `/habits/completions/summary?${params}`;
    const response = await apiRequest('GET', url, null);
    return response.data;
}

class HabitsChart {
    private gChart;
    private xScale;
    private yScale;
    private gXAxis;
    private gYAxis;
    private dims;

    constructor(containerSelector: string) {
        // get dims
        this.dims = getChartDimensions(containerSelector);
        
        const svg = d3.select(containerSelector)
            .append("svg")
                .attr("width", this.dims.width)
                .attr("height", this.dims.height)

        const gRoot = svg.append("g")
            .attr("transform", `translate(${this.dims.margin.left}, ${this.dims.margin.top})`)

        const _title = svg.append("text")
            .attr("x", this.dims.innerWidth/2)
            .attr("y", this.dims.margin.top/2)
            .attr("font-size", "var(--font-size-l)")
            .attr("fill", "var(--text)")
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

        this.xScale.domain([0, d3.max(data, (d: BarData) => d.count)!])
        this.yScale.domain(data.map(d => d.name))

        this.gXAxis.call(
            d3.axisBottom(this.xScale)
                .tickValues(d3.range(0, d3.max(data, (d: BarData) => d.count)! + 1, 1))
            )
        this.gYAxis.call(d3.axisLeft(this.yScale));

        const bars = this.gChart.selectAll("rect.bar")
        .data(data)
        .join(
            enter => {
                const rects = enter.append("rect")
                    .attr("x", 0)
                    .attr("y", (d: BarData) => this.yScale(d.name)!)
                    .attr("width", 0)
                    .attr("height", this.yScale.bandwidth())
                    .attr("fill", "var(--accent-strong)")
                    .attr("class", "bar")
                
                rects.transition()
                    .duration(D3_TRANSITION_DURATION_MS)
                    .attr("width", (d: BarData) => this.xScale(d.count))

                return rects
            },
            update => update
                .transition()
                .duration(D3_TRANSITION_DURATION_MS)
                .attr("width", (d: BarData) => this.xScale(d.count))
                .attr("height", this.yScale.bandwidth()),
            exit => exit.remove()
        );

        bars.on('mouseenter', function(this: d3.BaseType, _event: Event, d: BarData) {
            createTooltip(this as SVGRectElement, `${d.name}: ${d.count}`);
        }).on('mouseleave', removeTooltip);
    }

    showEmptyChart() {
        this.gChart.selectAll('rect.bar').remove();

        // Clear axes
        this.yScale.domain([]); // empty domain = no tick labels
        this.gYAxis.call(d3.axisLeft(this.yScale));

        this.xScale.domain([]);
        this.gXAxis.call(d3.axisBottom(this.xScale));

        const _emptyMessage = this.gChart.selectAll('text.empty-message')
            .data([1])
            .join("text")
            .attr("class", "empty-message")
            .attr("x", this.dims.innerWidth/2)
            .attr("y", this.dims.innerHeight/2)
            .attr("text-anchor", "middle")
            .attr("fill", "grey")
            .text("No completion data for this period.")
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
    const habitsChart = new HabitsChart('#habits-chart-container');
    await habitsChart.refreshBarChart();

    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        
        if (target.matches('.chart-range')) {
            chartState.range = parseInt(target.dataset['range']!, 10);
            await habitsChart.refreshBarChart();
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