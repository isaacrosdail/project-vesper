

export function formatDecimal(value: number | string, precision = 2): string {
    return Number(value).toFixed(precision);
}
