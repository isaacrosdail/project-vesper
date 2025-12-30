import * as d3 from 'd3';

export interface ChartDimensions {
    width: number;
    height: number;
    innerWidth: number;
    innerHeight: number;
    margin: { top: number; right: number; bottom: number; left: number; }
}

export const D3_TRANSITION_DURATION_MS = 200;

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