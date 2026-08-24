import { beforeEach, expect, setSystemTime, test } from 'bun:test';
import { isoDaysAgo, fmtDateTime, fmtTime, fmtDateYear, rangeLabel } from '../app/static_src/js/shared/datetime';
import { userStore } from '../app/static_src/js/shared/services/userStore';


beforeEach(() => {
    userStore.state = 'loaded'
    userStore.data = { timezone: "America/New_York"}
})

// // Using userStore.data.timezone
// test.each([
//   ["2025-10-07T05:00:00Z", "America/New_York", "01:00"],
//   ["2025-10-07T12:30:00Z", "Europe/Berlin",     "14:30"],
//   ["2025-10-07T00:00:00Z", "Asia/Tokyo",        "09:00"],
// ])("uses userStore timezone: %s + %s -> %s", (iso: string, tz: string, expected: string) => {
//   userStore.state = 'loaded';
//   userStore.data = { timezone: tz };

//   const date = new Date(iso);
//   const result = formatToUserTimeString(date);

//   expect(result).toBe(expected);
// });

// // Fallback cases: Using UTC
// test.each([
//   ["loading", null],                // State not loaded
//   ["loaded", null],                 // Data is null
// ])("falls back to UTC when state=%s, data=%s", (state, data) => {
//   userStore.state = state;
//   userStore.data = data;
  
//   const result = formatToUserTimeString(new Date("2025-10-07T12:00:00Z"));
//   expect(result).toBe("12:00");
// });

test('rangeLabel', () => {
    const res = rangeLabel(5);
    expect(res).toBe("Jul 17 - Jul 22, 2026")
});

test('isoDaysAgo returns n days back as YYYY-MM-DD', () => {
    setSystemTime(new Date('2026-06-18T12:00:00'));
    expect(isoDaysAgo(7)).toBe('2026-06-11');
    setSystemTime(); // reset system time
});

test('thingyy', () => {
    const t = fmtDateTime("2025-10-07T12:00:00Z");
    expect(t).toBe("Oct 07, 08:00 AM")
});

test('thingggg', () => {
    const t = fmtTime("2025-10-07T12:00:00Z");
    expect(t).toBe("8:00 AM")
});

test('yass', () => {
    const t = fmtDateYear("2025-10-07T12:00:00Z");
    expect(t).toBe("Oct 7, 2025")
});
