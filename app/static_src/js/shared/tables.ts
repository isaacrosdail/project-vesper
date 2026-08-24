// Bundler: Auto-runner => wires tables on DOMContentLoaded
import { ENUM_SORT_ORDERS } from '../types';

/**
 * Return a copy of the array, sorted by field T.
 * @returns 
 */
export function sortByField<T>(items: T[], field: keyof T, order: 'asc' | 'desc'): T[] {
    const customOrder = ENUM_SORT_ORDERS[field as string];

    return items.toSorted((a, b) => {
        const valA = a[field]
        const valB = b[field]

        // Sort nulls last
        if (valA === null && valB === null) return 0;
        if (valA === null) return 1;
        if (valB === null) return -1;

        const result = customOrder
            ? customOrder[valA as string] - customOrder[valB as string]
            : typeof valA === 'string'
                ? valA.localeCompare(valB as string)
                : (valA as number) - (valB as number);
        return order === 'asc' ? result : -result; // localeCompare returns -1/1/0 too, so we can use -result to flip order!! :D
    })
}
