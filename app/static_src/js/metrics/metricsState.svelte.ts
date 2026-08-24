import { DailyMetricsRead } from "../apiTypes";
import { api } from "../shared/services/api";
import { userState } from "../shared/services/userState.svelte";
import { densifyTrailingDays, LineDataPoint, MetricType, pairByDate } from "./shared";

// Source
export const metricsState = $state<{
    selected: MetricType | 'all';
    range: number;
}>({ selected: 'all', range: 7 });

// Fetched:
// seris, compare, sleepSeries -> $state too but only loadData writes these
export const metricsData = $state<{
    series: LineDataPoint[];
    compare: Compare;
    sleepSeries: any;
    allSeries: any;
}>({ series: [], compare: { previous: {}, current: {} }, sleepSeries: [], allSeries: [] });


// Derived: pairs, dense
const pairs = $derived(pairByDate(metricsData.series, metricsData.sleepSeries));
export function getPairs() { return pairs; } // $derived's can't be exported as consts
// since importers would get a frozen snapshot?
const dense = $derived(densifyTrailingDays(metricsData.series, metricsState.range));
export function getDense() { return dense; }

const multiData = $derived(transformMultiData(metricsData.allSeries));
export function getMultiData() { return multiData; }

// Series: keyed on (selected, range)
// Compare and sleep series keyed on (range) each

export async function loadData() {
    const { selected, range } = metricsState; // snapshot reactive state?

    const [series, compare, sleepSeries, allSeries] = await Promise.all([
        selected === 'all' ? Promise.resolve([]) : fetchMetricSeries(selected, range),
        fetchCompare(range),
        fetchMetricSeries('sleep_duration_minutes', range),
        fetchAllSeries(range),
    ]);

    Object.assign(metricsData, { series, compare, sleepSeries, allSeries });
}

async function fetchMetricSeries(metricType: MetricType, range: number): Promise<LineDataPoint[]> {
    const params = new URLSearchParams({ lastNDays: range.toString(), metric_type: metricType });
    const resp = await api.daily_metrics.getAll(params);
    return resp.data.map(d => ({
        date: new Date(d.date.split('T')[0] + 'T00:00:00'),
        value: parseFloat(d.value),
    }));
}

async function fetchCompare(range: number): Promise<Compare> {
    const resp = await api.daily_metrics.compare(new URLSearchParams({ lastNDays: String(range) }));
    return resp.data;
}

async function fetchAllSeries(range: number): Promise<DailyMetricsRead[]> {
    const resp = await api.daily_metrics.getAll(new URLSearchParams({ lastNDays: String(range) }));
    return resp.data;
}


function transformMultiData(data: any[]) {
    if (!data) return [];
    const targets = {
        weight: userState.me?.goals.weight ?? 76,
        steps: userState.me?.goals.steps ?? 10_000,
        sleep_duration_minutes: userState.me?.goals.sleep_duration_minutes ?? 480,
        calories: userState.me?.goals.calories ?? 2200,
    };    
    const interim = data.map(e => ({
        date: new Date(e.entry_datetime.split('T')[0] + 'T00:00:00'),
        ...Object.fromEntries(Object.keys(targets).map(key => [key, e[key] / targets[key]]))
    }))
    
    const chartData = Object.keys(targets).map(key => ({
        id: key,
        values: interim.map(e => ({ date: e.date, value: e[key] }))
    }))

    return chartData;
}