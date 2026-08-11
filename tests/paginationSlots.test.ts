
import { test, expect } from 'bun:test';
import { paginationSlots } from '../app/static_src/js/shared/pagination';


// curr, total, maxslots
test('one', () => {
    const inp = [1, 6, 5];
    // expect: 1 2 3 ... 6
    const res = paginationSlots(...inp);

    expect(res).toEqual([
        { kind: 'page', num: 0 },
        { kind: 'page', num: 1 },
        { kind: 'page', num: 2 },
        { kind: 'ellipsis', num: 2 },
        { kind: 'page', num: 5 },
    ]);
});

// 1 ... 4 5 6
test('two', () => {
    const inp = [4, 6, 5];
    const res = paginationSlots(...inp);

    expect(res).toEqual([
        { kind: 'page', num: 0 },
        { kind: 'ellipsis', num: 2 },
        { kind: 'page', num: 3 },
        { kind: 'page', num: 4 },
        { kind: 'page', num: 5 },
    ]);
});

// 0 ... 4 5 6 ... 10
test('three', () => {
    const current = 5;
    const maxSlots = 7;
    const inp = [current, 11, maxSlots];
    const res = paginationSlots(...inp);

    const wEdge = maxSlots - 2; // left/right-anchored
    const wMid = maxSlots - 4;  // centered case
    expect(current <= wEdge - 1).toBe(false);

    expect(res).toEqual([
        { kind: 'page', num: 0 },
        { kind: 'ellipsis', num: 3 },
        { kind: 'page', num: 4 },
        { kind: 'page', num: 5 },
        { kind: 'page', num: 6 },
        { kind: 'ellipsis', num: 5 },
        { kind: 'page', num: 10 },
    ]);
});
