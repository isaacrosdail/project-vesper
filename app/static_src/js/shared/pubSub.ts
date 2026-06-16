import { Task } from "../types";

// https://www.youtube.com/watch?v=HYqlmp8vh04
// Video for comparison of approach.

type Listener<T> = (data: T) => void;

// Pub/Sub-style store for resources (tasks, habits, etc.)
function createStore<T>(initial: T) {
    let state = initial;
    const listeners = new Set<Listener<T>>();

    // Publish
    function set(next: T) {
        state = next;
        listeners.forEach(fn => fn(state));
    }

    function get() {
        return state;
    }
    function subscribe(fn: Listener<T>) {
        listeners.add(fn);
    }

    function unsubscribe(fn: Listener<T>) {
        listeners.delete(fn);
    }


    return { set, get, subscribe, unsubscribe };
}

export const tasksStore = createStore<Map<number, Task>>(new Map());

// // Usage:
// const counter = createStore(0);
// counter.subscribe((val) => console.log('A sees: ', val));
// counter.subscribe((val) => console.log('B sees: ', val));

// counter.set(1);
// A sees: 1
// B sees: 1
// counter.set([1,2,2])