
// declare => "not creating Window, merely informing TS that it has an additional property csrfToken"
declare global {
    interface Window {
        csrfToken: string;
    }
}
/**
 * Internal identifiers for entities across all modules.
 * Used for API routing, DB queries, & UI labels.
 */
type Subtype = 
| 'time_entries'
| 'leet_code_records'
| 'habits'
| 'tasks'
| 'products'
| 'transactions'
| 'shopping_list_items'
| 'daily_metrics';

/**
 * Structure for human-readable labels of a (database model) subtype.
 */
type SubtypeLabels = {
    singular: string;
    plural: string;
}

/**
 * Maps internal identifiers for subtypes to their human-readable singular and plural forms.
 */
export const SUBTYPE_LABELS: Record<Subtype, SubtypeLabels> = {
    time_entries: { singular: 'Time Entry', plural: 'Time Entries' },
    leet_code_records: { singular: 'LeetCode Record', plural: 'LeetCode Records' },
    habits: { singular: 'Habit', plural: 'Habits' },
    tasks: { singular: 'Task', plural: 'Tasks' },
    products: { singular: 'Product', plural: 'Products' },
    transactions: { singular: 'Transaction', plural: 'Transactions' },
    shopping_list_items: { singular: 'Shopping List Item', plural: 'Shopping List Items' },
    daily_metrics: { singular: 'Daily Metrics entry', plural: 'Daily Metrics Entries'}
}

/**
 * Returns a human-readable label for a given module subtype, either in singular or plural form.
 * @param subtype The internal identifier for the entity type (eg., 'time_entries', 'habits')
 * @param plural If true, returns plural form; otherwise singular (default)
 * @returns The display-friendly label (eg., 'Time Entry' or 'Time Entries')
 */
export function getSubtypeLabel(subtype: Subtype, plural = false): string {
    return plural
        ? SUBTYPE_LABELS[subtype].plural
        : SUBTYPE_LABELS[subtype].singular;
}

export type FormDialog = HTMLDialogElement & {
    dataset: {
        endpoint?: string;
        mode?: string;
        itemId?: string;
        subtype?: string;
    }
}

export type WeatherResult = {
    temp: number | string;
    emoji: string;
    sunsetFormatted: string;
    sunrise: number | null;
    sunset: number | null;
}