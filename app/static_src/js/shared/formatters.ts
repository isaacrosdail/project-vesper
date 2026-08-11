

export function hourMinsDisplay(total_minutes: number) {
    const hours = Math.floor(total_minutes / 60)
    const minutes = Math.round(total_minutes % 60);
    const str = hours >= 1
        ? `${hours}h${minutes}m`
        : `${minutes}m`
    return str
}


/**
 * Title-cases each word in a string using whitespace and underscores as delimiters.
 * Intended to mostly approximate Python's str.title() for simple cases.
 * Collapses runs of whitespace and underscores into single word boundaries.
 * 
 * @remark
 * Does not handle apostrophes, hyphens, or Unicode-aware word boundaries the way Python does.
 * @example
 * title("hey    there,___world!")
 * // -> "Hey There, World!"
 */
export function title(value: string): string {
    if (typeof value !== 'string') {
        throw new TypeError("title() expects a string");
    }
    if (!value || value.length === 0) {
        return "";
    }
    return value
        .split(/[\s_]+/) // or just /\s+/ for spaces
        .map(val => val.charAt(0).toUpperCase() + val.slice(1).toLowerCase())
        .join(" ");
}
