
import type { HabitCompletionProgressRead, HabitOverviewItemRead } from '../apiTypes';
import { api } from '../shared/services/api';
import { BarData } from './barchart';
import { HeatmapApiEntry } from './heatmap';


export const habitsState = $state<{
    habits: HabitOverviewItemRead[];
    progress: HabitCompletionProgressRead | null;
    heatmapData: HeatmapApiEntry[] | null;
    barData: BarData[] | null;
    range: number;
}>({
    habits: [],
    progress: null,
    heatmapData: null,
    barData: null,
    range: 7,
});

export async function refreshHabits() {
    const { data } = await api.habits.overview();
    habitsState.habits = data.habits;
    habitsState.progress = data.progress;
}

export async function refreshHeatmapData() {
    const { data } = await api.habitCompletions.heatmap();
    habitsState.heatmapData = data;
}

export async function refreshBarchartData(range: number) {
    const { data } = await api.habitCompletions.summary(new URLSearchParams({ lastNDays: range.toString() }));
    habitsState.barData = data;
}

export async function toggleEntry(habitId: number, date: string) {
    const h = habitsState.habits.find(h => h.id === habitId);
    if (!h) throw new Error(`habit ${habitId} not in state`);
    const idx = h.data.findIndex(e => e.entry_date === date);
    try {
        if (idx !== -1) {
            h.data.splice(idx, 1);
            await api.habitCompletions.delete(habitId, date);
        } else {
            h.data.push({ entry_date: date, value: null });
            await api.habitCompletions.post(habitId, date, null);
        }
    } catch {
        // swallow: refreshHabits below resyncs to server truth
    }
    await refreshHabits();   // success or failure: resync to server truth
}

export async function postCompletionValue(habitId: number, date: string, value: number) {
    const h = habitsState.habits.find(h => h.id === habitId);
    if (!h) throw new Error(`habit ${habitId} not in state`);
    const entry = h.data.find(e => e.entry_date === date);
    if (entry) entry.value = value;
    else h.data.push({ entry_date: date, value });
    try {
        await api.habitCompletions.post(habitId, date, value);
    } catch {
        // swallow: refreshHabits below resyncs to server truth
    }
    await refreshHabits();
}

export async function deleteHabit(id: number) {
    await api.habits.delete(String(id));
    await refreshHabits();
}
