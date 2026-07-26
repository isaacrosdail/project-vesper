import { Temporal } from 'temporal-polyfill';
import { userState } from './services/userState.svelte';

// TODO(dt): How to use hour_cycle to inform these too?

const _userTZ = (): string => 
    userState.me!.timezone;

// For UTC now -> backend primarily
// rename -> nowISO
export const nowISO = (): string =>
    Temporal.Now.instant().toString();


export const todayUser = (): Temporal.PlainDate =>
    Temporal.Now.plainDateISO(_userTZ());

// UTC ISO string -> user's date - for comparisons
// rename -> userDay
// Callers now do toString() as needed.
export const userDay = (iso: string | Date): Temporal.PlainDate => {
    const d = typeof iso === 'string' ? iso : Temporal.Instant.fromEpochMilliseconds(iso.getTime())
    return Temporal.Instant.from(d).toZonedDateTimeISO(_userTZ()).toPlainDate()
}

// Rolling [today - (rangeDays - 1), today]
export function rangeLabel(rangeDays: number): string {
    const start = todayUser().subtract({ days: rangeDays });
    const end = todayUser();
    return `${fmtDate(start)} - ${fmtDate(end)}, ${end.year}`;
}

// UTC ISO string -> display "Mar 18"
// rename -> fmtDate(iso | PlainDate) => "Mar 18"
export const fmtDate = (d: string | Temporal.PlainDate): string => {
    const day = typeof d === 'string' ? userDay(d) : d;
    return day.toLocaleString(undefined, { month: 'short', day: 'numeric' }) // undefned - browser's locale
}

// UTC ISO string -> display "Mar 18, 3:45 PM"
export const fmtDateTime = (iso: string): string =>
    Temporal.Instant.from(iso).toZonedDateTimeISO(_userTZ()).toLocaleString(undefined, {
        month: 'short', day: 'numeric',
        hour: 'numeric', minute: '2-digit'
    });

// "15:45"
export const fmtTime = (d: string | Date): string => {
    const t = typeof d === 'string' ? d : Temporal.Instant.fromEpochMilliseconds(d.getTime());
    return Temporal.Instant.from(t).toZonedDateTimeISO(_userTZ()).toLocaleString(undefined, {
        timeStyle: 'short'
    });
}

// "Mar 18, 2026"
export const fmtDateYear = (d: string | Temporal.PlainDate): string => {
    const date = typeof d === 'string' ? userDay(d) : d;
    return date.toLocaleString(undefined, {
        month: 'short', day: 'numeric', year: 'numeric'
    })
}

// "2026-07-22T15:45"
export const toDateTimeLocalValue = (iso: string): string =>
    Temporal.Instant.from(iso).toZonedDateTimeISO(_userTZ()).toPlainDateTime().toString({
        smallestUnit: 'minute'
    });


export const toTypeTimeInputValue = (iso: string): string =>
    Temporal.Instant.from(iso).toZonedDateTimeISO(_userTZ()).toPlainTime().toString({
        smallestUnit: 'minute'
    });
