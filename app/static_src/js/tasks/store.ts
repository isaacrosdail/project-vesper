
import { createStore } from '../shared/pubSub';
import { Task } from "../types";

export const tasksStore = createStore<Map<number, Task>>(new Map());

// pub/sub (tasksStore) handles reacting to changes, this fn handles making the changes
export function taskUpsert(id: number, updated: Task) {
    // update source of truth
    const next = new Map(tasksStore.get()); // same O(n) cost as the old .map, but keeping fresh references
    next.set(id, updated);
    tasksStore.set(next); // triggers all subscribers
}

export function applyTaskDelete(id: number) {
    const next = new Map(tasksStore.get())
    next.delete(id)
    tasksStore.set(next);
}
