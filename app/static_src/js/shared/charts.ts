import { createTooltip, removeTooltip } from "./ui/tooltip";

export type ChartDimensions = {
    width: number;
    height: number;
    innerWidth: number;
    innerHeight: number;
    margin: { top: number; right: number; bottom: number; left: number; }
};

export const D3_GRIDLINES_DASHARR_VALS = "2,4";
export const D3_GRIDLINES_OPACITY = 0.7;
export const D3_OTHER_DIM_OPACITY = 0.4;
export const D3_TICKS = 7;
export const D3_TRANSITION_DURATION_MS =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 200;

export function getDims(
    height: number,
    width: number,
    margin = { top: 20, right: 20, bottom: 30, left: 40 }
) {
    return {
        width,
        height,
        innerWidth: width - margin.left - margin.right,
        innerHeight: height - margin.top - margin.bottom,
        margin
    }
}


// TODO: Unsure where to put this
// export function enableStats() {
//     document.querySelectorAll<HTMLDivElement>('.stats-ring').forEach(statsCircle => {
//         const progress = Number(statsCircle.dataset.progress ?? 50); // we'll need to update this value to update the visual progress

//         statsCircle.setAttribute("role", "progressbar");
//         statsCircle.setAttribute("aria-valuenow", progress); // this value is grabbed by our stats-progress
//         // content to show the percentage/value
//         statsCircle.style.setProperty('--progress', progress + "%"); // set visual ring val
//         statsCircle.setAttribute("aria-live", "polite")

//     })
// }


export function applyXAxisRotation(axis: d3.Selection<SVGGElement, unknown, HTMLElement, unknown>): void {
    axis.selectAll("text")
        .attr("transform", "rotate(-45)")
        .attr("text-anchor", "end")
        .attr("dx", "-.5em")
        .attr("dy", "0.15em");
}

export function getTickValues<T>(data: T[], range: number, xScale: d3.ScaleTime<number, number>): Date[] {
    // Consistent ticks for dates
    const idealTicks = range <= 14
        ? range
        : 7;
    const tickCount = Math.min(data.length, idealTicks)
    const [start, end] = xScale.domain();
    if (!start || !end) return [];
    const step = (end.getTime() - start.getTime()) / (tickCount - 1);
    const tickValues = Array.from(
        {length: tickCount}, (_, i) => new Date(start.getTime() + i * step)
    );
    return tickValues;
}

// TODO(d3): type this?
// (local function)(this:  | SVGRectElement, _event: any, d: Point): void
export function withTooltip<D>(label: (d: D) => string | null) {
    return (selection: d3.Selection<any, unknown, any, unknown>) => {
        selection
            .on('mouseenter', function(_e, d: D) {
                const text = label(d);
                if (text !== null) createTooltip(this, text);
            })
            .on('mouseleave', function() { removeTooltip(this); });
    }
}
