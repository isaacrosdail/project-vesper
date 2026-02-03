// Utilities for working with numbers

export function formatDecimal(value: number | string, precision = 2): string {
    return Number(value).toFixed(precision);
}

// TODO: Make this minIncl, maxExcl & ensure callsites are updated
// half-open intervals follows indexing/iteration
// this way the end is the length or count, not the last valid index
export const randInt = (min: number, max: number) =>
    // remove +1 here
    Math.floor(Math.random() * (max - min + 1)) + min;

export const randFloat = (min: number, max: number) =>
    (Math.random() * (max - min) + min);
