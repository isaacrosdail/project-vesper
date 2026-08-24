
import * as d3 from 'd3';
import { D3_TRANSITION_DURATION_MS } from "../shared/charts";
import { hourMinsDisplay } from '../shared/formatters';
import { todayUser, userDay } from "../shared/datetime";
import { api } from '../shared/services/api';
import { userState } from '../shared/services/userState.svelte';


type MetricTargets = Record<MetricType, number>;
export type ReferenceLine = { value: number; class: string; label: string; };


export const HERO_PANEL_CHART_CONFIG = {
    margin: { top: 20, bottom: 30, left: 40, right: 50 },
    width: 600,
    height: 350,
} as const;


export type LineDataPoint = {
    date: Date;
    value: number;
}

export type LineData = {
    id: LineMetricType;
    values: LineDataPoint[];
}


export function drawReferenceLines(
    g: d3.Selection<SVGGElement, unknown, HTMLElement, any>,
    lines: ReferenceLine[],
    yScale: d3.ScaleLinear<number, number>,
    width: number,
) {
    g.selectAll<SVGRectElement, ReferenceLine>("g.reference-line")
        .data(lines, d => d.class) // key by class
        .join(
            enter => {
                const group = enter.append("g").attr("class", d => `reference-line ${d.class}`);
                group.append("line")
                    .attr("x1", 0).attr("x2", width)
                    .attr("y1", d => yScale(d.value)).attr("y2", d => yScale(d.value));
                group.append("text")
                    .attr("x", width + 4)
                    .attr("y", d => yScale(d.value))
                    .attr("dy", "0.32em")          // vertically center on the line
                    .text(d => d.label);
                return group;
            },
            update => {
                update.select("line").transition().duration(D3_TRANSITION_DURATION_MS)
                    .attr("y1", d => yScale(d.value)).attr("y2", d => yScale(d.value));
                update.select("text").transition().duration(D3_TRANSITION_DURATION_MS)
                    .attr("y", d => yScale(d.value));
                return update;
            },
            exit => exit.remove()
        );
}

export const TYPE_LABELS: Record<MetricType, string> = {
    weight: "Weight",
    steps: "Steps",
    calories: "Calories",
    sleep_duration_minutes: "Sleep"
} as const;

export const TYPE_UNITS: Record<MetricType, string> = {
    weight: 'lbs', // TODO: Should come from userPrefs (kg vs lbs)
    steps: '',
    calories: 'kcal',
    sleep_duration_minutes: 'h',
};

export const TYPE_FORMAT: Record<MetricType, (v: number) => string> = {
    weight: v => v.toLocaleString(),
    steps: v => v.toLocaleString(),
    calories: v => v.toLocaleString(),
    sleep_duration_minutes: hourMinsDisplay,
}

const TARGET_DEFAULTS: MetricTargets = {
    weight: 76,
    steps: 10_000,
    calories: 2200,
    sleep_duration_minutes: 480,
};

export type BarMetricType = 'steps' | 'calories' | 'sleep_duration_minutes';
export type LineMetricType = 'weight';
export type MetricType = BarMetricType | LineMetricType;

export function getMetricTargets(): MetricTargets {
    const targets = {} as MetricTargets;
    for (const m of Object.keys(TARGET_DEFAULTS) as MetricType[]) {
        targets[m] = userState.me?.goals[m] ?? TARGET_DEFAULTS[m];
    }
    return targets;
}

type ApiMetricData = {
    date: string;
    value: string;
}

export async function getMetricData(lastNDays: number, metricType?: MetricType): Promise<LineDataPoint[]> {
    const params = new URLSearchParams({ lastNDays: lastNDays.toString() });
    if (metricType) params.set('metric_type', metricType)
    const response = await api.daily_metrics.getAll(params);

    const chartData = response.data.map((d: ApiMetricData) => ({
        date: new Date(d.date.split('T')[0] + 'T00:00:00'),
        value: parseFloat(d.value),
    }));
    return chartData;
}

export type Point = { date: Date; value: number | null; };

// TODO: duped in consistency.ts: should we distill into datetime.ts helper? prob gonna come up again
// const KEY_FMT = { year: 'numeric', month: '2-digit', day: '2-digit' } as const;
// const key = (d: Date) => formatToUserTimeString(d, KEY_FMT);

export type Pairs = { date: string; valA: number; valB: number; }[];

// Pairs by matching key, and drops non-matches
// Inner join on date then zip the matches values
export function pairByDate(a: Point[], b: Point[]): Pairs {
    const newArr: { date: string; valA: number; valB: number; }[] = [];
    const bMap = new Map(b.map(p => [userDay(p.date).toString(), p.value])); // one pass over B
    for (const entry of a) {
        // if theres an entry for that same date in B -> push to newArr together
        const bEntry = bMap.get(userDay(entry.date).toString());
        if (bEntry != null && entry.value != null) {
            newArr.push({ date: entry.date, valA: entry.value, valB: bEntry });
        }
    }
    return newArr;
}


export function densifyTrailingDays(data: Point[], range: number): Point[] {
    // const todayStr = getUserTodayDate();
    // const today = new Date(todayStr + 'T00:00:00'); // local-midnight
    const today = todayUser(); // profile tz
    // const start = d3.timeDay.offset(today, -(range - 1));
    // const end = d3.timeDay.offset(today, 1);
    // exactly 'range' Dates, asc
    // const days = d3.timeDays(start, end);
    const days = Array.from({ length: range }, (_, i) => today.subtract({ days: range - 1 - i }));
    // const lookup2 = d3.index(data, d => key(d.date));
    // const lookup = new Map(data.map(d => [formatToUserTimeString(d.date, KEY_FMT), d.value]));
    const lookup = new Map(data.map(d => [userDay(d.date).toString(), d.value]));

    return days.map(d => {
        // const dateStr = formatToUserTimeString(d, KEY_FMT);
        return { date: new Date(d.toString() + 'T00:00:00'), value: lookup.get(d.toString()) ?? null }
    })
}

export function pearson(pairs: Pairs) {
    const n = pairs.length;
    // Running sums
    let [sumA, sumB, sumProd, sumASq, sumBSq] = [0,0,0,0,0];
    for (const p of pairs) {
        sumA += p.valA;
        sumB += p.valB;
        sumProd += p.valA * p.valB;
        sumASq += p.valA ** 2;
        sumBSq += p.valB ** 2;
    };
    // Pearson calculation
    const num = n * (sumProd) - (sumA * sumB);
    const den = Math.sqrt((n * sumASq - (sumA**2)) * (n * sumBSq - (sumB ** 2)));
    if (den === 0) {
        return { corr: 0, regressionSlope: null, regressionIntercept: null }
    };
    // Line of best fit (Least squares regression line):
    // y = mx + b
    // m = (n * SUMxy - SUMx * SUMy) / (n * SUMASq - (SUMx ** 2))
    // b = (SUMy - m * SUMx) / n
    // Numerator of pearson's r is the numerator of the slope of the line of best fit
    // m = (n * SUMxy - SUMx * SUMy)

    const m = num / (n * sumASq - (sumA ** 2));
    const b = (sumB - m * sumA) / n;
    return {
        corr: num / den,
        regressionSlope: m,
        regressionIntercept: b, 
    }
}