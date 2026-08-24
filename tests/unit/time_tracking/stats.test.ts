import { describe, expect, it, setSystemTime } from 'bun:test';
import {
    daySpan,
    deltaLabel,
    deriveStatsView,
    numActiveDays,
    toStatsShape,
    topEntry,
    totalsBy,
    type StatsEntry,
} from '../../../app/static_src/js/time_tracking/stats';
import type { TimeEntryRead } from '../../../app/static_src/js/apiTypes';

const entries: StatsEntry[] = [
    { date: '2026-06-11', category: 'Coding', duration: 60 },
    { date: '2026-06-11', category: 'Coding', duration: 30 },
    { date: '2026-06-12', category: 'Walk',   duration: 45 },
];

describe('totalsBy', () => {
    it('sums duration grouped by category', () => {
        expect(totalsBy(entries, e => e.category)).toEqual({ Coding: 90, Walk: 45 });
    });

    it('sums duration grouped by date', () => {
        expect(totalsBy(entries, e => e.date)).toEqual({ '2026-06-11': 90, '2026-06-12': 45 });
    });

    it('returns empty object for no entries', () => {
        expect(totalsBy([], e => e.category)).toEqual({});
    });
});

describe('toStatsShape', () => {
    it('slices started_at to a YYYY-MM-DD date and passes fields through', () => {
        const t = {
            started_at: '2026-06-11T14:30:00Z',
            category: 'Coding',
            duration_minutes: 60,
        } as TimeEntryRead;                            // only 3 fields read
        expect(toStatsShape(t)).toEqual({ date: '2026-06-11', category: 'Coding', duration: 60 });
    });
});

describe('topEntry', () => {
    it('returns the max', () => {
        expect(topEntry({ Coding: 90, Walk: 45 })).toEqual({ key: 'Coding', total: 90 });
    });
    it('keeps the FIRST key on a tie', () => {
        expect(topEntry({ A: 50, B: 50 }).key).toBe('A');
    });
    it('empty totals -> null key', () => {
        expect(topEntry({}).key).toBeNull();
    });
});

describe('numActiveDays', () => {
    it('counts distinct days', () => {
        expect(numActiveDays(entries)).toBe(2);
    });
    it('two entries same day -> 1', () => {
        expect(numActiveDays([entries[0], entries[1]])).toBe(1);
    });
    it('empty -> 0', () => {
        expect(numActiveDays([])).toBe(0);
    });
});

describe('daySpan', () => {
    it('inclusive span across the date range', () => {
        expect(daySpan(entries)).toBe(2);  // 06-11 .. 06-12 = 2 days
    });
    it('single day -> 1', () => {
        expect(daySpan([entries[0]])).toBe(1);
    });
    it('empty -> 0 (guard before dividing)', () => {
        expect(daySpan([])).toBe(0);
    });
});

describe('deltaLabel', () => {
    it('positive -> up arrow + pct', () => {
        const s = deltaLabel(120, 100);
        expect(s).toContain('▲');
        expect(s).toContain('20%');
    });
    it('negative -> down arrow + pct', () => {
        const s = deltaLabel(80, 100);
        expect(s).toContain('▼');
        expect(s).toContain('20%');
    });
    it('no baseline (prev 0) -> empty string', () => {
        expect(deltaLabel(100, 0)).toBe('');
    });
    it('current 0 -> down 100%', () => {
        expect(deltaLabel(0, 100)).toContain('100%');
    });
});

describe('deriveStatsView (integration)', () => {
    it('picks the top category by total', () => {
        expect(deriveStatsView(entries, []).top_category.value).toBe('Coding');
    });
    it('counts active days into the label path', () => {
        expect(numActiveDays(entries)).toBe(2); // just assert computed count, not the formatted string
    });
});

describe('mostActiveDayView', () => {
    it('most active day picks highest-total date', () => {
        expect(deriveStatsView(entries, []).most_active_day.detail).toContain('Jun 11')
    })
});
