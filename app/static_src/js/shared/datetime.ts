import { userStore } from './services/userStore.js';

export const getJSInstant = (): string =>
    new Date().toISOString(); // Always UTC "..Z"


function safeCreateDate(isoString: string): Date {
    if (!isTZAwareISO(isoString)) {
        throw new Error(`Invalid timezone-aware ISO string: ${isoString}`);
    }
    const date = new Date(isoString);
    if (isNaN(date.getTime())) {
        throw new Error(`Invalid date after parsing: ${isoString}`);
    }
    return date;
}

/**
 * Validates an ISO 8601 string includes timezone information.
 *
 * @param isoString - ISO 8601 datetime string to validate.
 * @returns True if string has 'Z' or explicit offset (eg, '-5:00')
 */
function isTZAwareISO(isoString: string): boolean {
    // Note: Still learning RegEx, so this is firmly a work-in-progress point
    const hasUTCIndicator = /Z$/;
    const hasExplicitOffset = /[+-]\d{2}:\d{2}$/;

    return hasUTCIndicator.test(isoString) || hasExplicitOffset.test(isoString);
}

export function isoToTimeInput(isoString: string): string {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) {
        throw new Error(`isoToTimeInput: Invalid ISO date string "${isoString}"`)
    }
    return formatToUserTimeString(date);
}

export function isoToDateInput(isoString: string): string {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) {
        throw new Error(`isoToDateInput: Invalid ISO date string "${isoString}"`)
    }
    return formatToUserTimeString(date, {year: 'numeric', month: '2-digit', day: '2-digit'});
}

export function formatTimeString(date: Date): string {
    return formatToUserTimeString(date);
}

/**
 * Formats a Date object to be in the current user's timezone.
 *
 * @param date - Date to format
 * @param opts - Intl formatting options (defaults to HH:MM format)
 * @param hour12 - Use 12h format instead of 24h (default: 12h)
 */
export function formatToUserTimeString(
    date: Date,
    opts: Intl.DateTimeFormatOptions = { hour: '2-digit', minute: '2-digit' }, // default to "HH:MM"
    hour12: boolean = false // could override with user region? OR possible userTimeFormat setting
): string {
    // format using userStore.data.timezone
    const formatter = new Intl.DateTimeFormat('en-CA', { // gives ISO -> "2025-10-04"
        ...opts, // spread operator - takes every key-value pair in opts, copy them into new object, then override/add timeZone
        hour12,
        timeZone: (userStore.state === 'loaded' && userStore.data?.timezone) ? userStore.data.timezone : 'UTC',
    });
    return formatter.format(date); // eg, "03:45"
}
