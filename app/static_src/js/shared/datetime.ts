// Replicating our Python datetime/helpers.py

// TODO: NOTES: Dependency injection
import { userStore } from './userStore.js';

function nowUTC(): string {
    return new Date().toISOString(); // Returns "2025-08-17T15:02:33.022Z"
}
// debug: console.log(nowUTC())

function formatTimeString(date: Date){
    // Use user timezone if available
    if (userStore.state === 'loaded') {
        // format using userStore.data.timezone
        const formatter = new Intl.DateTimeFormat('en-US', {
            timeZone: userStore.data.timezone,
            hour: '2-digit',
            minute: '2-digit',
            hour12: false       // could override with user region?
        });
        return formatter.format(date);
    } else {
        // fall back to browser timezone
        const hours = date.getHours();
        const minutes = date.getMinutes();
        
        const timeString = `${padTime(hours)}:${padTime(minutes)}`;
        return timeString;
    }
}

export const getJSInstant = (): string =>
    new Date().toISOString(); // Always UTC "..Z"

export function formatDateString(date: Date) {
    if (userStore.state === 'loaded') {
        const formatter = new Intl.DateTimeFormat('en-CA', {
            timeZone: userStore.data.timezone,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
        return formatter.format(date);  // "2025-08-17"
    } else {
        // Fall back to browser timezone
        return new Date().toISOString().split('T')[0];
    }
}

function getCurrentTimeString() {
    return formatTimeString(new Date());
}
function getCurrentDateString() {
    return formatDateString(new Date());
}

function padTime(number: number): string {
    return number.toString().padStart(2, '0');
}