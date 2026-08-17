import type { TaskRead, TaskStatRead } from '../apiTypes';
import { generateKeyBetween } from '../shared/fractional_indexing';
import { api } from '../shared/services/api';

export const tasksState = $state<{
    tasks: TaskRead[];
    stats: { overdue: TaskStatRead, frog: TaskStatRead } | null;
    range: number;
}>({
    tasks: [],
    stats: null,
    range: 7
});

const tasksById = $derived(new Map(tasksState.tasks.map(t => [t.id, t])));
export function subtasksOf(task: TaskRead): TaskRead[] {
    return task.subtasks
        .map(id => tasksById.get(id))
        .filter(t => t !== undefined);
}

export async function refreshTasks() {
    const { data } = await api.tasks.getAll();
    tasksState.tasks = data;
}

export async function refreshStats() {
    const { data } = await api.tasks.stats(new URLSearchParams({ lastNDays: String(tasksState.range) }));
    tasksState.stats = data;
}

export async function toggleTask(task: TaskRead) {
    await api.tasks.toggleComplete(String(task.id), !task.is_done);
    await refreshTasks();
}

export async function deleteTask(id: number) {
    await api.tasks.delete(String(id));
    await refreshTasks();
}

export async function createLink(subtaskId: number, supertaskId: number) {
    await api.taskLinks.post({ subtask_id: subtaskId, supertask_id: supertaskId });
    await refreshTasks();
}

export async function editTaskIndex(id: number, prevKey: string | null, nextKey: string | null) {
    const key = generateKeyBetween(prevKey, nextKey);
    const task = tasksState.tasks.find(t => t.id === id);
    if (!task) return;
    task.sort_key = key;
    await api.tasks.patch(String(id), { sort_key: key });
}
