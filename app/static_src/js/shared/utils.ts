// Misc. utilities

// TODO: Make this minIncl, maxExcl & ensure callsites are updated
// half-open intervals follows indexing/iteration
// this way the end is the length or count, not the last valid index
export const randInt = (min: number, max: number) =>
    // remove +1 here
    Math.floor(Math.random() * (max - min + 1)) + min;

export const randFloat = (min: number, max: number) =>
    (Math.random() * (max - min) + min);

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


export const debounce = (callback: Function, wait: number) => {
    let timeoutId: number;
    return (...args: any[]) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => {
            callback(...args);
        }, wait);
    }
}


export function swapToInput(el: HTMLElement): HTMLInputElement {
    const originalText = el.textContent?.trim() ?? '';
    const input = document.createElement('input');
    input.dataset.original = originalText;
    input.type = 'text';
    input.className = 'input-sidebar-inline';
    input.value = originalText;
    el.textContent = '';
    el.appendChild(input);
    return input;
}

function swapToSelect(el: HTMLElement, options: string[]): HTMLSelectElement {
    const original = el.textContent?.trim() ?? '';
    const select = document.createElement('select');
    select.dataset.original = original;
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        if (opt === original) option.selected = true;
        select.appendChild(option);
    });
    el.textContent = '';
    el.appendChild(select);
    return select;
}

export function swapToText(el: HTMLElement, value: string) {
    el.textContent = value;
}

// TODO: Dedupe (also in models.py for auth)
const SUPPORTED_LOCATIONS = {
    "US": ["New York", "Chicago", "Denver", "Miami", "Los Angeles"],
    "GB": ["London", "Manchester"],
    "AU": ["Syndey", "Melbourne", "Brisbane"],
    "CA": ["Toronto", "Vancouver"],
    "DE": ["Berlin", "Munich"],
    "IT": ["Rome", "Naples"],
    "RU": ["Moscow", "Novosibirsk"],
    "NO": ["Oslo", "Bergen"]
}


// Swap dispatcher TODO: messy
export function swapField(span: HTMLElement) {
    const inputType = span.dataset.input;

    if (inputType === 'select') {
        const options = (span.dataset.options || '').split(',');
        swapToSelect(span, options);
    } else if (inputType === 'timezone') {
        swapToSelect(span, Intl.supportedValuesOf('timeZone'));
    } else if (inputType === 'country') {
        const select = swapToSelect(span, Object.keys(SUPPORTED_LOCATIONS));
        // When country changes, update city options
        select.addEventListener('change', () => {
            const citySpan = span.closest('.sidebar-section')?.querySelector('[data-target="city"]');
            if (citySpan) {
                citySpan.textContent = '';
                swapToSelect(citySpan as HTMLElement, SUPPORTED_LOCATIONS[select.value]);
            }
        });
    } else if (inputType === 'city') {
        // Get current country to determine city options
        const section = span.closest('.sidebar-section');
        const countrySelect = section?.querySelector('[data-target="country"] select') as HTMLSelectElement;
        const country = countrySelect?.value || span.closest('.sidebar-section')?.querySelector('[data-target="country"]')?.textContent?.trim() || 'US';
        swapToSelect(span, SUPPORTED_LOCATIONS[country] || []);
    }
    else {
        swapToInput(span);
    }
}

export function readField(span: HTMLElement): string {
    const input = span.querySelector('input, select') as HTMLInputElement | HTMLSelectElement | null;
    return input?.value ?? '';
}

export function restoreOriginal(el: HTMLElement) {
    const input = el.querySelector('input, select') as HTMLInputElement | HTMLSelectElement | null;
    if (input) {
        el.textContent = input.dataset.original || '';
    }
}

const KG_TO_LBS = 2.20462;
export const lbsToKg = (lbs: number) => lbs / KG_TO_LBS;
export const kgToLbs = (kg: number) => kg * KG_TO_LBS;

// Mifflin-St Jeor equation for resting BMR calculation.
export function calculateBMR(
    sex: 'f' | 'm',
    weightKG: number,
    heightCM: number,
    birthYear: number,
    currentYear: number = new Date().getFullYear()
): number {
    // Females: (10 * weight[kg]) + (6.25 * height[cm]) - (5 * age[yrs]) - 161
    // Males:   (10 * weight[kg]) + (6.25 * height[cm]) - (5 * age[yrs]) + 5
    const age = currentYear - birthYear
    const constant = sex === 'f' ? -161 : 5;
    return (10 * weightKG) + (6.25 * heightCM) - (5 * age) + constant;
}


export function formToJSON(form: HTMLFormElement): Record<string, unknown> {
    return parseFormData(new FormData(form));
}
/**
 * Extracts data from a form element into JSON.
 * 
 * @param formData
 * @returns JSON-ified form data
 */
export function parseFormData(formData: FormData): Record<string, unknown> {
    // const formData = new FormData(form);
    const result: Record<string, unknown> = {};

    for (const [rawName, value] of formData) {
        // coerce checkbox "on" to bool true
        let name = rawName;
        let finalValue: unknown = value;

        if (name.endsWith('[]') && typeof value === 'string') {
            name = name.slice(0, -2); // remove '[]' off end
            finalValue = value ? value.split(',').map(Number).filter(n => !isNaN(n)) : [];
        } else if (value === "on") {
            finalValue = true;
        } else if (value === "") {
            finalValue = null;
        }

        const path = name.replace(/\]/g, '').split('[');
        let current = result;

        for (let i = 0; i < path.length - 1; i++) {
            const key = path[i];
            const nextKey = path[i + 1];
            const nextIsArray = /^\d+$/.test(nextKey);

            if (!(key in current)) {
                current[key] = nextIsArray ? [] : {};
            }
            current = current[key];
        }
        current[path[path.length - 1]] = finalValue;
    }
    return result;
}

// TODO: implemented this for task list view reordering
export const BASE_62_DIGITS =
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

function midpoint(a: string, b: string, digits: string) {
    const zero = digits[0];
    // b != null -> no upper bound - caller wants a key that sorts after a with no ceiling
    // ie, "at the end" or?
    if (b != null && a >= b) {
        throw new Error(a + " >= " + b);
    }
    // a.slice(-1) -> last char of the string a, not "the char at index a"
    // so: "if the last char of a is the zero-digit, OR if b exists and its last char is the zero-digit, throw"
    // Trailing zeroes break a key invariant:
    // In fractional base-62, two strings can represent the same numeric value if one has a trailing zero:
    // "U" -> 0.U in base-62?
    // "U" -> O.U0 = same value
    if (a.slice(-1) === zero || (b && b.slice(-1) === zero)) {
        throw new Error('trailing zero');
    }
}