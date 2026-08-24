import * as d3 from 'd3';

import {
    D3_GRIDLINES_DASHARR_VALS,
    D3_GRIDLINES_OPACITY,
    D3_TICKS,
    D3_TRANSITION_DURATION_MS,
    getDims,
    getTickValues,
} from '../../shared/charts';
import type { LineData, LineDataPoint, LineMetricType, MetricType, ReferenceLine } from '../shared';
import { drawReferenceLines, HERO_PANEL_CHART_CONFIG, TYPE_LABELS } from '../shared';

export class MetricsLineChart {
    private dims;
    private gLines;
    gXAxis;
    gYAxis;
    private overlay;
    bisectLine;
    focusLabel;
    private xScale;
    yScale;
    private line;
    area;

    constructor(
        containerSelector: string,
        private config: Record<MetricType, ReferenceLine[]>,
    ) {
        this.dims = getDims(
            HERO_PANEL_CHART_CONFIG.height,
            HERO_PANEL_CHART_CONFIG.width,
            HERO_PANEL_CHART_CONFIG.margin,
        );

        const svg = d3
            .select(containerSelector)
            .append('svg')
            .attr('viewBox', `0 0 ${this.dims.width} ${this.dims.height}`);

        const gRoot = svg
            .append('g')
            .attr('transform', `translate(${this.dims.margin.left}, ${this.dims.margin.top})`);

        // Groups inside svg
        this.gXAxis = gRoot
            .append('g')
            .attr('transform', `translate(0, ${this.dims.innerHeight})`)
            .attr('class', 'axis-x');
        this.gYAxis = gRoot.append('g').attr('class', 'axis-y');
        this.gLines = gRoot.append('g').attr('class', 'chart');

        // Overlay to capture mouseover event for bisect line
        this.overlay = gRoot
            .append('rect')
            .attr('width', this.dims.innerWidth)
            .attr('height', this.dims.innerHeight)
            .attr('fill', 'none')
            .attr('pointer-events', 'all');

        // vertical line + label for bisect display
        this.bisectLine = gRoot
            .append('line')
            .attr('class', 'bisect-line')
            .attr('y1', 0)
            .attr('y2', this.dims.innerHeight)
            .attr('opacity', 0)
            .attr('pointer-events', 'none'); // prevent line hijacking mousemove from overlay

        this.focusLabel = gRoot.append('text').attr('class', 'bisect-label').attr('opacity', 0);

        // Create scales. Define only range/pixel values since data is dynamic
        this.xScale = d3.scaleTime().range([0, this.dims.innerWidth]);
        this.yScale = d3.scaleLinear().range([this.dims.innerHeight, 0]);

        this.line = d3
            .line<LineDataPoint>()
            .x((d) => this.xScale(d.date))
            .y((d) => this.yScale(d.value));

        // Area and gradient def for the "highlighted/color under the line chart line" thing
        this.area = d3
            .area<LineDataPoint>()
            .x((d) => this.xScale(d.date))
            .y0(this.dims.innerHeight) // baseline: bottom of the chart
            .y1((d) => this.yScale(d.value)); // top: data line

        const gradient = svg
            .append('defs')
            .append('linearGradient')
            .attr('id', 'line-area-gradient')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', 0)
            .attr('y2', 1); // 0,0 -> 0,1 = top-to-bottom
        gradient.append('stop').attr('offset', '0%').attr('class', 'area-stop-top');
        gradient.append('stop').attr('offset', '100%').attr('class', 'area-stop-bottom');
    }

    drawStaticLines(metricType: LineMetricType) {
        const config = this.config[metricType as StaticLineMetric];
        if (!config) return;

        this.gLines
            .selectAll(`rect.${config[metricType].class.split(' ')[0]}`)
            .data([config.value])
            .join(
                (enter) =>
                    enter
                        .append('rect')
                        .attr('class', config.class)
                        .attr('x', 0)
                        .attr('y', (d: number) => this.yScale(d) - 1)
                        .attr('width', this.dims.innerWidth)
                        .attr('height', 2)
                        .attr('opacity', 0.6),
                (update) =>
                    update
                        .transition()
                        .duration(D3_TRANSITION_DURATION_MS)
                        .attr('y', (d: number) => this.yScale(d) - 1),
            );
    }

    update(data: LineDataPoint[], metricType: LineMetricType, range: number) {
        drawReferenceLines(this.gLines, this.config[metricType], this.yScale, this.dims.innerWidth);

        this.xScale.domain(d3.extent(data, (d) => d.date) as [Date, Date]);

        // TODO: Distill - feels like we ought to be able to extract helpers by now
        const dataValues = data.map((d) => d.value);
        const refValues = this.config[metricType].map((r) => r.value);
        const [min, max] = d3.extent([...dataValues, ...refValues]);

        // Give a more reasonable "window" for min-max range
        const spread = max - min;
        const padding = spread === 0 ? 1 : spread * 0.2;
        this.yScale.domain([Math.max(0, Math.floor(min - padding)), max + padding]);

        // Consistent ticks for dates
        const tickValues = getTickValues(data, range, this.xScale);

        this.gXAxis.call(
            d3
                .axisBottom(this.xScale)
                .tickValues(tickValues)
                .tickFormat((d) => d3.timeFormat('%b %d')(d as Date)),
        );

        // TODO: For bisect thing?
        // NOTE: bisect expects ASCENDING order (backend repo method does this, needs to stay that way)
        const bisect = d3.bisector((d: LineDataPoint) => d.date).left;
        this.overlay
            .on('mousemove', (event) => {
                const [mouseX] = d3.pointer(event);
                const date = this.xScale.invert(mouseX);
                const idx = bisect(data, date);
                const left = data[idx - 1];
                const right = data[idx];

                let closest;
                if (!left) closest = right;
                else if (!right) closest = left;
                else closest = date - left.date < right.date - date ? left : right;

                const [leftDate, rightDate] = [left.date.getTime(), right.date.getTime()];
                const t = (date.getTime() - leftDate) / (rightDate - leftDate);
                const interpolated = left.value + (right.value - left.value) * t;

                // For rendering a comparison to target/goal value, if applicable
                const config = this.config[metricType as StaticLineMetric];
                const target = config?.targetValue;
                let label = interpolated.toFixed(1);
                if (target) {
                    const percent = ((interpolated - target) / target) * 100;
                    const sign = percent > 0 ? '+' : '';
                    label += ` (${sign}${percent.toFixed(1)}% vs target)`;
                }

                this.bisectLine.attr('opacity', 1).attr('transform', `translate(${mouseX}, 0)`);
                this.focusLabel
                    .attr('opacity', 1)
                    .attr('x', mouseX + 8) // appear to right of bisect line?
                    .attr('y', 12)
                    .text(`${label} - ${d3.timeFormat('%b %d')(date)}`);
            })
            .on('mouseleave', () => {
                this.bisectLine.attr('opacity', 0);
                this.focusLabel.attr('opacity', 0);
            });

        this.gYAxis
            .call(d3.axisLeft(this.yScale).ticks(D3_TICKS))
            .call((g) =>
                g
                    .selectAll('.tick line')
                    .attr('x2', this.dims.innerWidth)
                    .attr('stroke-opacity', D3_GRIDLINES_OPACITY)
                    .attr('stroke-dasharray', D3_GRIDLINES_DASHARR_VALS),
            );

        // Draw the area path before the line join so the line paints OVER the fill:
        this.gLines
            .selectAll<SVGPathElement, LineData>('path.area')
            .data([{ id: metricType, values: data }], (d) => d.id)
            .join(
                (enter) =>
                    enter
                        .append('path')
                        .attr('class', 'area')
                        .attr('fill', 'url(#line-area-gradient)')
                        .attr('d', (d) => this.area(d.values)),
                (update) =>
                    update
                        .transition()
                        .duration(D3_TRANSITION_DURATION_MS)
                        .attr('d', (d) => this.area(d.values)),
                (exit) => exit.remove(),
            );

        // Metric line?
        this.gLines
            .selectAll<SVGPathElement, LineData>('path.line')
            .data([{ id: metricType, values: data }], (d) => d.id) // makes each metric a datum
            .join(
                (enter) => {
                    return enter
                        .append('path')
                        .attr('class', 'line')
                        .attr('d', (d: LineData) => this.line(d.values))
                        .each(function () {
                            const len = this.getTotalLength();
                            d3.select(this)
                                .attr('stroke-dasharray', len) // makes entire line one "dash"
                                .attr('stroke-dashoffset', len) // hides whole line
                                .transition()
                                .duration(800)
                                .attr('stroke-dashoffset', 0); // reveals left to right
                        });
                },
                (update) =>
                    update
                        .attr('stroke-dasharray', 'none') // so it doesn't interfere on updates
                        .transition()
                        .duration(D3_TRANSITION_DURATION_MS)
                        .attr('d', (d: LineData) => this.line(d.values)),
                (exit) => exit.remove(),
            );
    }
}
