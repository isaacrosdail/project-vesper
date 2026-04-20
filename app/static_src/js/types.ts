
// declare => "not creating Window, merely informing TS that it has an additional property csrfToken"
declare global {
    interface Window {
        csrfToken: string;
    }
}

export type Pillar = {
    id: number;
    name: string;
}

type BaseEntity = {
    id: number;
    created_at: string;
}

export type Task = BaseEntity & {
    name: string;
    priority: TaskPriority;
    due_date: string | null;
    is_done: boolean; // Now comes from @hybrid_property -> serializer
    completed_at: string | null;
    supertasks: number[];
    subtasks: number[];
    pillars: Pillar[];
    subtype: Extract<Subtype, 'tasks'>;
}

export type TaskPriority = 'low' | 'medium' | 'high' | 'frog';

export const ENUM_SORT_ORDERS: Record<string, Record<string, number>> = {
    priority: { low: 0, medium: 1, high: 2, frog: 3 },
    difficulty: { easy: 0, medium: 1, hard: 2 },
} as const;


export type Habit = BaseEntity & {
    name: string;
    status: 'experimental' | 'established' | null;
    established_date: string | null;
    // promotion_threshold: number | null;
    target_frequency: number;
    is_promotable: boolean;
    subtype: Extract<Subtype, 'habits'>;
}

type HabitCompletion = {
    id: number;
    habit_id: number;
}

// TODO: Work on this one. for the generic patch completion on homepage checkboxes
// also used by Tasks
export type Progress = { completed: number; percent: number; total: number; }

// POST returns the completion record + progress
export type HabitCompletionResponse = HabitCompletion & { progress: Progress };

// DELETE returns just progress
export type HabitDeleteResponse = { progress: Progress };

export type ShoppingListItem = BaseEntity & {
    product_id: number;
    product_name: string;
    quantity_wanted: number;
    shopping_list_id: number;
    subtype: Extract<Subtype, 'shopping_list_items'>;
}

export type RecipeIngredient = BaseEntity & {
    product_id: string;
    product_name: string;
    amount_value: number;
    amount_units: Unit;
}

export type Recipe = BaseEntity & {
    name: string;
    yields: number;
    yields_units: Unit;
    ingredients: RecipeIngredient[];
    subtype: Extract<Subtype, 'recipes'>;
}

export type ProductCategory = 
    'fruits' | 'vegetables' | 'legumes' | 'grains' | 'bakery' | 'dairy_eggs' |
    'meats' | 'seafood' | 'fats_oils' | 'snacks' | 'sweets' | 'beverages' | 
    'condiments_sauces' | 'processed_convenience' | 'supplements';

export type Product = BaseEntity & {
    created_at: Date;
    deleted_at: Date;
    barcode: string | null;
    name: string;
    net_weight: number;
    subtype: Extract<Subtype, 'products'>;
    unit_type: Unit;
    category: ProductCategory;

    calories_per_100g: number;
    carbs_fiber_per_100g: number | null;
    carbs_per_100g: number | null;
    carbs_sugar_per_100g: number | null;
    fat_per_100g: number | null;
    fat_mono_per_100g: number | null;
    fat_poly_per_100g: number | null;
    fat_sat_per_100g: number | null;
    potassium_per_100g: number | null;
    sodium_per_100g: number | null;
    protein_per_100g: number | null;
}

export type Transaction = BaseEntity & {
    product_id: number;
    product_name: string;
    price_at_scan: number;
    quantity: number;
    subtype: Extract<Subtype, 'transactions'>;
}

export type TimeEntry = BaseEntity & {
    category: string;
    started_at: string;
    ended_at: string;
    duration_minutes: number;
    description: string | null;
    subtype: Extract<Subtype, 'time_entries'>;
}

export type DailyMetrics = BaseEntity & {
    entry_datetime: string;
    created_at: string;
    calories: number | null;
    steps: number | null;
    weight: number | null;
    wake_datetime: string | null;
    sleep_datetime: string | null;
    sleep_duration_minutes: number | null;
    subtype: Extract<Subtype, 'daily_metrics'>;
}

export const UNITS = {
    G: 'g',
    KG: 'kg',
    OZ: 'oz',
    LB: 'lb',
    ML: 'ml',
    L: 'l',
    FL_OZ: 'fl_oz',
    EA: 'ea',
} as const;

export type Unit = typeof UNITS[keyof typeof UNITS];


/**
 * List of valid module subtypes used for runtime subtype checks.
 */
const SUBTYPES = [
    'time_entries', 'leet_code_records', 'habits', 'tasks', 'products',
    'transactions', 'shopping_list_items', 'daily_metrics', 'recipes', 'recipe_ingredients'
] as const;

/**
 * Internal identifiers for entities across all modules.
 * Used for API routing, DB queries, & UI labels.
 */
type Subtype = typeof SUBTYPES[number];

/**
 * Structure for human-readable labels of a (database model) subtype.
 */
type SubtypeLabels = {
    singular: string;
    plural: string;
}

/**
 * Type guard to check if a string is a valid Subtype identifier.
 * Narrows type from string to Subtype when true.
 * 
 * @param x String to validate as a Subtype
 */
export function isSubtype(x: string): x is Subtype {
    return (SUBTYPES as readonly string[]).includes(x);
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
} as const;

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
        module: string;
        subtype: Subtype;
        endpoint: string;
        mode?: 'edit';
        itemId?: string;
        resource: Subtype;
    }
}

export type FormControlElement = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

export type ValidatableElement = HTMLInputElement | HTMLTextAreaElement;

export type WeatherResult = {
    temp: number | string;
    emoji: string;
    sunsetFormatted: string;
    sunrise: number | null;
    sunset: number | null;
}