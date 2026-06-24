
import { displayDate } from '../shared/datetime';
import { api } from '../shared/services/api';
import { openModalForEdit } from '../shared/ui/modal-manager';
import { required, title } from '../shared/utils';
import type { FormDialog, Task } from '../types';
import { tasksStore, taskUpsert } from './store';

let taskDetailsPopover: TaskDetailsPopover;

export function openTaskDetails(task: Task) {
    taskDetailsPopover.open(task);
}

export function initTaskDetails(
    dialog: FormDialog,
    populateEditModal: (data: Task) => void,
    deleteTask: (id: number) => Promise<void>
) {
    const taskDetailEls = getTaskDetailPopoverEls();
    taskDetailsPopover = new TaskDetailsPopover();

    taskDetailEls.taskDetailsPopover.addEventListener('toggle', (e: ToggleEvent) => {
        if (e.newState === 'closed') taskDetailsPopover.close();
    });

    taskDetailEls.taskDetailsPopover.addEventListener('click', async (e: MouseEvent) => {
        const id = taskDetailsPopover.activeTaskId;
        if (id === null) return;
        const target = e.target as HTMLElement;

        if (target.closest('.js-task-delete')) deleteTask(id);
        else if (target.closest('.js-task-edit')) openModalForEdit(String(id), dialog, 'Task', populateEditModal);
        else if (target.closest('.js-add-subtask')) {
            const supertaskIdsInput = dialog.querySelector<HTMLInputElement>('#supertask_ids_hidden')!;
            supertaskIdsInput.value = String(id);
            dialog.showModal();
        } else if (target.matches('.task-details__done-toggle')) {
            const res = await api.tasks.toggleComplete(String(id), (target as HTMLInputElement).checked);
            taskUpsert(res.data.id, res.data);
        } else if (target.matches('.task-details__subtask-checkbox')) {
            const res = await api.tasks.toggleComplete(target.dataset.id, (target as HTMLInputElement).checked);
            taskUpsert(res.data.id, res.data);
        }
    });
}

// All elements for showing a task's details popover/view
function getTaskDetailPopoverEls() {
    const root = required(document.querySelector<HTMLElement>('#task-details-popover'), '#task-details-popover');

    return {
        taskDetailsPopover: root,
        name: required(root.querySelector('.name'), '.name'),
        priority: required(root.querySelector('.priority'), '.priority'),
        priorityBadge: required(root.querySelector('.priority-badge'), '.priority-badge'),
        dueDateRow: required(root.querySelector('.due-date-row'), '.due-date-row'),
        dueDate: required(root.querySelector('.due_date'), '.due_date'),
        pillarsRow: required(root.querySelector('.pillars-row'), '.pillars-row'),
        pillars: required(root.querySelector('.pillars'), '.pillars'),
        subtasksContainer: required(document.querySelector('.subtasks-container'), '.subtasks-container'),
        subtaskTemplate: required(document.querySelector<HTMLTemplateElement>('#subtask-list-template'), '#subtask-list-template'),
        createdAt: required(root.querySelector('.created_at'), '.created_at'),
        doneToggle: required(root.querySelector<HTMLInputElement>('.task-details__done-toggle'), '.task-details__done-toggle'),
        subtasksHeader: required(root.querySelector<HTMLSpanElement>('.subtasks-header'), '.subtasks-header'),
        subtasksSummary: required(root.querySelector<HTMLSpanElement>('.subtasks-summary'), '.subtasks-summary'),
    }
}


// Pure data shaping
function deriveTaskView(task: Task) {
    const subtasks = task.subtasks
        .map(id => tasksStore.get().get(id))
        .filter((t): t is Task => t !== undefined);
    return {
        name: task.name,
        id: task.id,
        is_done: task.is_done,
        priority: title(task.priority),
        created_at: displayDate(task.created_at),
        due_date: task.due_date !== null ? displayDate(task.due_date) : null,
        pillars: task.pillars.map(p => p.name).join(' · '),
        priorityHref: `#badge-priority-${task.priority}`,
        subtasks: subtasks.map(st => ({
            name: st.name,
            id: st.id,
            is_done: st.is_done
        })),
        subtasksSummary: `${subtasks.filter(st => st.is_done).length}/${subtasks.length}`
    };
}

function renderTaskDetails(view: ReturnType<typeof deriveTaskView>, els: ReturnType<typeof getTaskDetailPopoverEls>) {
    els.name.textContent = view.name;
    els.doneToggle.checked = view.is_done;
    els.priority.textContent = view.priority;
    els.createdAt.textContent = view.created_at;

    if (view.due_date !== null) {
        els.dueDate.textContent = view.due_date;
        els.dueDateRow.classList.remove('hide');
    } else {
        els.dueDateRow.classList.add('hide');
    }

    if (view.pillars !== '') {
        els.pillars.textContent = view.pillars;
        els.pillarsRow.classList.remove('hide');
    } else {
        els.pillarsRow.classList.add('hide');
    }

    els.priorityBadge.setAttribute('href', view.priorityHref);

    if (view.subtasks.length) {
        els.subtasksSummary.textContent = view.subtasksSummary;
        els.subtasksHeader.classList.remove('hide');
    } else {
        els.subtasksHeader.classList.add('hide');
        
    }

    els.subtasksContainer.replaceChildren(
        ...view.subtasks.map(st => {
            const clone = els.subtaskTemplate.content.cloneNode(true);
            const cb = clone.querySelector<HTMLInputElement>('.subtask-checkbox');
            if (!cb) return;
            clone.querySelector('.subtask-name')!.textContent = st.name;
            cb.checked = st.is_done;
            cb.dataset.id = String(st.id);
            return clone;
        })
    );
}

class TaskDetailsPopover {
    #activeTaskId: number | null = null;
    #els = getTaskDetailPopoverEls();
    #unsubscribe: (() => void) | null = null;

    get activeTaskId(): number | null {
        return this.#activeTaskId;
    }

    open(task: Task) {
        this.#activeTaskId = task.id;
        this.#render();
        this.#els.taskDetailsPopover.showPopover();
        this.#unsubscribe = tasksStore.subscribe(() => this.#render());
    }
    close() {
        this.#activeTaskId = null;
        this.#unsubscribe?.();
        this.#unsubscribe = null;
    }
    #render() {
        if (this.#activeTaskId === null) return;
        const task = tasksStore.get().get(this.#activeTaskId);
        if (!task) return;
        renderTaskDetails(deriveTaskView(task), this.#els);
    }
}

