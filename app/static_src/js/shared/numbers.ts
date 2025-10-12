// Utilities for working with numbers

export function formatDecimal(value: number | string, precision = 2): string {
    return Number(value).toFixed(precision);
}

export const randInt = (min: number, max: number) =>
    Math.floor(Math.random() * (max - min + 1)) + min;

export const randFloat = (min: number, max: number) =>
    (Math.random() * (max - min) + min);