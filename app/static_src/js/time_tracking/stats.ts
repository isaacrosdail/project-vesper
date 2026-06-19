
import { hourMinsDisplay } from "../shared/charts";
import type { TimeEntry } from "../types";


export type StatsEntry = { date: string; category: string; duration: number };
// Anti-corruption layer? So if db-side naming changes, this is the only place we need to change
export function toStatsShape(t: TimeEntry): StatsEntry {
    return {
        date: t.started_at.split('T')[0],
        category: t.category,
        duration: t.duration_minutes,
    }
}

function topCategoryLabel(topCat: Ranked, total: number) {
    const part1 = hourMinsDisplay(topCat.total);
    const pct = Math.round(topCat.total / total * 100);
    return `${part1} · ${pct}% of time`;
}

// Parametrize the grouping key so that it covers category and date (and others)
export function totalsBy(entries: StatsEntry[], keyFn: (e: StatsEntry) => string) {
    const obj: Record<string, number> = {};
    for (const e of entries) {
        const k = keyFn(e);
        obj[k] = (obj[k] ?? 0) + e.duration;
    }
    return obj;
}

type Ranked = { key: string | null; total: number }
export function topEntry(totals: Record<string, number>): Ranked {
    return Object.entries(totals).reduce(
        (best, [key, total]) => total > best.total ? { key, total } : best,
        { key: null, total: -Infinity }
    );
}

const sumDur = (entries: StatsEntry[]) => entries.reduce((acc, e) => acc + e.duration, 0);

// avg:
// final date - start date / num days obv
function dailyAverage(entries: StatsEntry[]) {
    const totalMins = sumDur(entries);
    const dayDelta = daySpan(entries);
    const raw = totalMins / dayDelta;
    return hourMinsDisplay(raw)
}
// Return number of distinct days with non-zero logged time.
export function numActiveDays(entries: StatsEntry[]) {
    return Object.keys(totalsBy(entries, e => e.date)).length;
}

export function daySpan(entries: StatsEntry[]) {
    if (entries.length === 0) return 0;
    const days = entries.map(e => e.date).sort();
    const first = new Date(days[0]).getTime();
    const last = new Date(days[days.length - 1]).getTime();
    const dayInMS = 24 * 60 * 60 * 1000; // day * hr * min * s
    return Math.floor((last-first) / dayInMS) + 1;  // inclusive
}

export function deltaLabel(current: number, prev: number): string {
    if (prev === 0) return "";                           // no baseline -> hide
    const pct = Math.round((current - prev) / prev * 100);
    return `${pct >= 0 ? "▲" : "▼"} ${Math.abs(pct)}% vs prior period`;
}

export function mostActiveDayView(entries: StatsEntry[]) {
    const top = topEntry(totalsBy(entries, e => e.date));
    if (top.key === null) return { day: "—", label: "" };

    const d = new Date(top.key + 'T00:00:00');  // local midnight, no UTC shift
    return {
        day: d.toLocaleDateString(undefined, { weekday: 'short' }),
        label: `${hourMinsDisplay(top.total)} logged ${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`, // "1h30m logged Jun 11"
    };
}

export function deriveStatsView(entries: StatsEntry[], prior: StatsEntry[]) {
    const categoryTotals = totalsBy(entries, e => e.category);
    const sumDurations = sumDur(entries);
    const activeDay = mostActiveDayView(entries);

    return {
        totalLabel: hourMinsDisplay(sumDurations),
        avgLabel: dailyAverage(entries),    // Daily Average
        activeDaysLabel: `across ${numActiveDays(entries)} active days`,
        topCategory: topEntry(categoryTotals).key,
        topCatLabel: topCategoryLabel(topEntry(categoryTotals), sumDurations), // "2h36m · 34%"
        mostActiveDay: activeDay.day,
        mostActiveLabel: activeDay.label,    // "1h45m logged Jun 11"
        totalDelta: deltaLabel(sumDurations, sumDur(prior)),   // "▲ 24%" — deferred, needs the prior window
    };
}
