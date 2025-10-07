import { beforeEach, test, expect } from 'bun:test';
// Note: Use extensionless paths when testing here (no .ts, .js) - Bun + TS will resolve it
import { userStore } from '../app/static_src/js/shared/services/userStore';
import { formatToUserTimeString } from '../app/static_src/js/shared/datetime';


beforeEach(() => {
    userStore.state = 'loaded'
    userStore.data = { timezone: "America/New_York"}
})

// Using userStore.data.timezone
test.each([
  ["2025-10-07T05:00:00Z", "America/New_York", "01:00"],
  ["2025-10-07T12:30:00Z", "Europe/Berlin",     "14:30"],
  ["2025-10-07T00:00:00Z", "Asia/Tokyo",        "09:00"],
])("uses userStore timezone: %s + %s -> %s", (iso: string, tz: string, expected: string) => {
  userStore.state = 'loaded';
  userStore.data = { timezone: tz };

  const date = new Date(iso);
  const result = formatToUserTimeString(date);

  expect(result).toBe(expected);
});

// Fallback cases: Using UTC
test.each([
  ["loading", null],                // State not loaded
  ["loaded", null],                 // Data is null
])("falls back to UTC when state=%s, data=%s", (state, data) => {
  userStore.state = state;
  userStore.data = data;
  
  const result = formatToUserTimeString(new Date("2025-10-07T12:00:00Z"));
  expect(result).toBe("12:00");
});