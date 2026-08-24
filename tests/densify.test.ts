
import { beforeEach, describe, expect, test, setSystemTime } from 'bun:test';

import { userStore } from '../app/static_src/js/shared/services/userStore';
import { densifyTrailingDays, Point } from '../app/static_src/js/metrics/shared';

import * as d3 from 'd3';

beforeEach(() => {
    setSystemTime(new Date('2026-07-22T12:00:00Z'));
    userStore.state = 'loaded';
    userStore.data = { timezone: 'America/New_York' };
});

const NOW = new Date('2026-07-22T12:00:00Z');   // same instant pinned in beforeEach
const daysAgo = (n: number) => d3.timeDay.offset(NOW, -n);

// Gap mid-window comes backk as null
test('densify', () => {
    const data: Point[] = [
        { date: daysAgo(4), value: 45 },
        { date: daysAgo(2), value: 35 },
        { date: daysAgo(0), value: 60 },
    ];
    const result = densifyTrailingDays(data, 5);
    const expected: Point[] = [
        { date: new Date('2026-07-18T00:00:00'), value: 45 },
        { date: new Date('2026-07-19T00:00:00'), value: null },
        { date: new Date('2026-07-20T00:00:00'), value: 35 },
        { date: new Date('2026-07-21T00:00:00'), value: null },
        { date: new Date('2026-07-22T00:00:00'), value: 60 },
    ];
    expect(result).toEqual(expected);
});

// Data older than the window is excluded not front-padded
test('window position is fixed by "today" not stretched to reach old data', () => {
    const data = [
        { date: daysAgo(10), value: 55 },
    ];
    const result = densifyTrailingDays(data, 5);
    const expected: Point[] = [
        { date: new Date('2026-07-18T00:00:00'), value: null },
        { date: new Date('2026-07-19T00:00:00'), value: null },
        { date: new Date('2026-07-20T00:00:00'), value: null },
        { date: new Date('2026-07-21T00:00:00'), value: null },
        { date: new Date('2026-07-22T00:00:00'), value: null },
    ];
    expect(result).toEqual(expected);

})

// Empty input -> range entries all null
test('empty input still produces windowed output', () => {
    const result = densifyTrailingDays([], 5);
    const expected: Point[] = [
        { date: new Date('2026-07-18T00:00:00'), value: null },
        { date: new Date('2026-07-19T00:00:00'), value: null },
        { date: new Date('2026-07-20T00:00:00'), value: null },
        { date: new Date('2026-07-21T00:00:00'), value: null },
        { date: new Date('2026-07-22T00:00:00'), value: null },
    ];
    expect(result).toEqual(expected);
});
