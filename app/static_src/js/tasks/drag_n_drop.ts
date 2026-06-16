
import { generateKeyBetween } from "../shared/fractional_indexing";
import { api } from '../shared/services/api';
import { tasksStore, taskUpsert } from "./store";


type DragState = {
    sourceRef: HTMLElement | null,
    targetRef: HTMLElement | null,
    position: 'before' | 'after' | null   // drag to top-half vs bottom half of another task
};

export function setupDragDrop(taskList: HTMLDivElement) {
    // Enables draggable for drag-n-drop: This way, only the button starts this, NOT "anywhere in the taskli"
    taskList.addEventListener('mousedown', (e) => {
        if (e.target.matches('.task-drag')) {
            const taskLi = e.target.closest<HTMLDivElement>('.task');
            if (!taskLi) return;
            taskLi.setAttribute('draggable', 'true')
        }
    })
    taskList.addEventListener('dragend', (e) => {
        if (e.target.matches('.task')) {
            e.target.setAttribute('draggable', 'false');
        }
        teardownMarked();
    })


    const dragState: DragState = { sourceRef: null, targetRef: null, position: null };
    // Tracks ref to marked row for removal
    let marked: { el: HTMLElement; side: 'above' | 'below' } | null = null;
    function teardownMarked() {
        marked?.el.classList.remove('drop-above', 'drop-below');
        marked = null;
    }

    taskList.addEventListener('dragstart', (e) => {
        if (e.target.matches('.task')) dragState.sourceRef = e.target;
    });
    // dragover - get "current" task we're over, so drop can apply it accordingly
    // Need two things:
    // 1. Which task are we over? -> targetRef
    // 2. Top half or bottom half
    taskList.addEventListener('dragover', (e: DragEvent) => {
        e.preventDefault(); // opt in to being a drop target
        const taskLi = e.target.closest('.task');
        if (!taskLi) {
            return;
        }
        dragState.targetRef = taskLi;

        // top half or bottom half calc
        const rect = taskLi.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        const side = e.clientY < midpoint ? 'above' : 'below';
        dragState.position = side === 'above' ? 'before' : 'after';

        // Apply class for affordance
        if (marked?.el === taskLi && marked.side === side) return; // unchanged -> skip
        marked?.el.classList.remove('drop-above', 'drop-below');
        taskLi.classList.add(`drop-${side}`);
        marked = { el: taskLi, side }
    });

    const keyOf = (el: Element | null) => el ? tasksStore.get().get(Number(el.dataset.id)).sort_key : null;
    // Fires once on the drop target when user releases
    taskList.addEventListener('drop', async (e) => {
        if (e.target.closest('.task')) {
            const taskId = dragState.targetRef.dataset.id;
            const task = tasksStore.get().get(Number(taskId));

            // Decide neighbors: 
            let prev, next;
            if (dragState.position === 'before') {
                prev = dragState.targetRef.previousElementSibling;
                next = dragState.targetRef;
            } else {
                prev = dragState.targetRef;
                next = dragState.targetRef.nextElementSibling;
            }
            // Generate a key between prev and next:
            const key = generateKeyBetween(keyOf(prev), keyOf(next));

            // Update data for sourceRef task:
            const sourceTaskId = Number(dragState.sourceRef.dataset.id);
            const sourceTask = tasksStore.get().get(sourceTaskId);
            const newTask = { ...sourceTask, sort_key: key };
            taskUpsert(sourceTask.id, newTask);
            await api.tasks.patch(String(sourceTaskId), { sort_key: key }); // Update ONLY sort_key

            // Clear state
            dragState.sourceRef = dragState.targetRef = null;
            dragState.position = null;
        }
    })
    teardownMarked();
}
