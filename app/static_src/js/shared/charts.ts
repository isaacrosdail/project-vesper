
export interface ChartDimensions {
    width: number;
    height: number;
    innerWidth: number;
    innerHeight: number;
    margin: { top: number; right: number; bottom: number; left: number; }
}

export const D3_TRANSITION_DURATION_MS = 200;
export const D3_COLOR = "var(--accent-strong)";

/**
 * Helper to get/set up chart dimensions for D3 charts.
 * @param containerSelector 
 * @param margin 
 */
export function getChartDimensions(
    containerSelector: string,
    margin = { top: 20, right: 20, bottom: 30, left: 40 }
): ChartDimensions {
    const container = document.querySelector(containerSelector) as HTMLElement;

    const width = container.clientWidth || 400;
    const height = container.clientHeight || 400;

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    return { width, height, innerWidth, innerHeight, margin };
}

// TODO: Unsure where to put this
export function enableStats() {
    document.querySelectorAll<HTMLDivElement>('.stats-ring').forEach(statsCircle => {
        const progress = Number(statsCircle.dataset.progress ?? 50); // we'll need to update this value to update the visual progress

        statsCircle.setAttribute("role", "progressbar");
        statsCircle.setAttribute("aria-valuenow", progress); // this value is grabbed by our stats-progress
        // content to show the percentage/value
        statsCircle.style.setProperty('--progress', progress + "%"); // set visual ring val
        statsCircle.setAttribute("aria-live", "polite")

    })
}

// ...or this.
export function hourMinsDisplay(total_minutes: number) {
    const hours = Math.floor(total_minutes / 60)
    const minutes = total_minutes % 60;
    const str = hours >= 1
        ? `${hours}h${minutes}m`
        : `${minutes}m`
    return str
}

export function applyXAxisRotation(axis: d3.Selection<SVGGElement, unknown, HTMLElement, any>): void {
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

export function showEmptyChartMessage(container, message: string, width: number, height: number): void {
    container.selectAll("text.empty-message")
        .data([1])
        .join("text")
        .attr("class", "empty-message")
        .attr("text-anchor", "middle")
        .attr("x", width/2)
        .attr("y", height/2)
        .text(message)
}