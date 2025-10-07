// Replicating our Python datetime/helpers.py

// TODO: NOTES: Dependency injection
import { userStore } from './services/userStore.js';

function nowUTC(): string {
    return new Date().toISOString(); // Returns "2025-08-17T15:02:33.022Z"
}

export const getJSInstant = (): string =>
    new Date().toISOString(); // Always UTC "..Z"

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

function padTime(number: number): string {
    return number.toString().padStart(2, '0');
}