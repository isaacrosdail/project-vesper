
import { enableStats } from '../shared/charts';
import { displayDate, getUserTodayDate, isoToUserDate } from '../shared/datetime';
import { initTaskForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { initSidebar } from '../shared/ui/left-sidebar';
import { confirmationManager, openModalForEdit } from '../shared/ui/modal-manager';
import { makeToast } from '../shared/ui/toast';
import { title } from '../shared/utils';
import { setupDragDrop } from '../tasks/drag_n_drop';
import { applyTaskDelete, tasksStore, taskUpsert } from '../tasks/store';
import { ENUM_SORT_ORDERS, FormDialog, Task, TaskPriority } from '../types';
import { sortByField } from '../shared/tables';

// TODO:
// 1. For due dates that are nearer, use "the day" (ex: Friday instead of Mar 20)


// All elements for task list filtering/altering/etc
//#region QuerySelects
function getTasksListElements() {
    const els = {
        tasksList: document.querySelector('.tasks-list'),
        sidebar: document.querySelector('.left-sidebar'),
        priorityBtn: document.querySelector('[data-action="cycle-priority"] use'),
        taskLiTemplate: document.querySelector('#task-li-template'),
        toggleCompletedCheckbox: document.querySelector('.toggle-completed')
    };
    return els;
}

// All elements for showing a task's details popover/view
function getTaskDetailPopoverElements() {
    const els = {
        taskDetailsPopover: document.querySelector('#task-details-popover'),
        subtasksContainer: document.querySelector('.subtasks-container'),
        subtaskTemplate: document.querySelector('#subtask-list-template'),
    }
    return els;
}

function getSearchElements() {
    const els = {
        searchPopover: document.querySelector('#search-popover'),
        searchInput: document.querySelector('.task-search'),
        resultsContainer: document.querySelector('.results-container'),
    }
    return els;
}

const tasksListEls = getTasksListElements();
const taskDetailEls = getTaskDetailPopoverElements();
const searchEls = getSearchElements();
//#endregion


// Pure data shaping
function deriveTaskView(task: Task) {
    const subtasks = task.subtasks
        .map(id => tasksStore.get().get(id))
        .filter(Boolean);
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


async function setupTaskFormModal() {
    const dialog = document.querySelector<FormDialog>('#tasks-entry-dashboard-modal');
    if (!dialog) {
        throw new Error('tasks dashboard: #tasks-entry-dashboard-modal not found');
    }
    const { selectTask, setExcludeId, tasks } = await initTaskForm(dialog);

    function onPopulatedCallback(data: Task) {
        setExcludeId(String(data.id)); // self can't be its own subtask
        // data.subtasks = [8, 11] -- loop, make pills, hide cards
        data.subtasks.forEach((id: number) => {
            const task = tasks.find(t => t.element.dataset.id === String(id));
            if (!task) {
                console.warn(`onPopulated: no task card found for subtask id ${id}`, { tasksLength: tasks.length })
            }
            selectTask((String(id)), task.element.dataset.name)
        })
        data.pillars.forEach((p: {id: number}) => {
            const cb = dialog.querySelector(`input[value="${p.id}"]`);
            if (cb) cb.checked = true;
        })
        // also sync the hidden input
        dialog.querySelector('#pillar_ids_hidden').value = data.pillars.map(p => p.id).join(',') ?? '';
    }

    return { dialog, populateEditModal: onPopulatedCallback };
}

// Make this dumb: No business logic, no .find, no .filter
function renderTaskDetails(view, els: ReturnType<typeof getTaskDetailPopoverElements>) {
    const root = els.taskDetailsPopover;

    root.querySelector('.name').textContent = view.name;
    root.querySelector('.priority').textContent = view.priority;
    root.querySelector('.created_at').textContent = view.created_at;

    const row = root.querySelector('.due-date-row')
    const text = root.querySelector('.due_date')
    if (view.due_date !== null) {
        text.textContent = view.due_date;
        row.classList.remove('hide');
    } else {
        row.classList.add('hide');
    }

    root.querySelector('.pillars').textContent = view.pillars;
    root.querySelector('.priority-badge')
        .setAttribute('href', view.priorityHref);

    els.subtasksContainer.innerHTML = ''; // reset markup

    if (view.subtasks.length !== 0) {
        const header = document.createElement('div');
        header.className = 'subtasks-header';
        header.textContent = `Subtasks ${view.subtasksSummary}`;
        els.subtasksContainer.appendChild(header);
    }

    view.subtasks.forEach(st => {
        const clone = els.subtaskTemplate.content.cloneNode(true);
        clone.querySelector('.subtask-name').textContent = st.name;
        const checkbox = clone.querySelector('.subtask-checkbox');
        checkbox.checked = st.is_done;
        checkbox.setAttribute('data-id', st.id);
        els.subtasksContainer.appendChild(clone);
    });

    const doneToggle = root.querySelector('.task-details__done-toggle');
    doneToggle.checked = view.is_done;
}

// Cache one li to be cloned?
type Filter = 'all' | 'today' | 'upcoming';

const SORT_VALUES = ['manual', 'due_date', 'priority', 'name'] as const;
type SortValue = typeof SORT_VALUES[number];

// runtime guard that narrows e.detail.value -> SortValue?
function isSortValue(v: unknown): v is SortValue {
    return SORT_VALUES.includes(v as SortValue);
}

type TaskListState = {
    filter: Filter;
    priority: TaskPriority | 'all';
    sort: 'manual' | 'due_date' | 'priority' | 'name';
    order: 'asc' | 'desc';
}

const state: TaskListState = { filter: 'all', priority: 'all', sort: 'manual', order: 'asc'};

function setTaskListState(patch: Partial<TaskListState>) {
    Object.assign(state, patch);
    syncControls();
    renderTaskList(deriveVisibleTasks());
}

// Visually syncs controls from state declaratively?
function syncControls() {
    // 1. Update priority icon
    const priorityIconHref = state.priority === 'all' ? '#icon-funnel' : `#badge-priority-${state.priority}`;
    tasksListEls.priorityBtn.setAttribute('href', priorityIconHref);
    
    // 2. Set the checked radio from state.filter
    const timeWindow = document.querySelector('.time-window');
    const leRadio = timeWindow.querySelector(`#${state.filter}`);
    leRadio.checked = true;

    // 3a. Make toggle show state.sort's display text
    const sortLabel = document.querySelector('[popovertarget="sort-by"] .dropdown-toggle-label');
    const activeOpt = document.querySelector(`#sort-by [data-value="${state.sort}"]`);
    if (sortLabel && activeOpt) sortLabel.textContent = activeOpt.textContent;
    document.querySelectorAll('#sort-by [data-value]').forEach(opt =>
        opt.classList.toggle('active', opt.dataset.value === state.sort));
    // 3b. Flip sort asc/desc chevron accordingly
    const sortDir = document.querySelector('.sort-order-toggle');
    sortDir.classList.toggle('flip', state.order === 'asc');
    sortDir.toggleAttribute('disabled', state.sort === 'manual');
}

// Also now sorts by sort_key (fractional index) so the list respects stored order
function deriveVisibleTasks(): Task[] {
    let result = [...tasksStore.get().values()]; // get map contents as arr for filter
    // Primary filter
    if (state.filter === 'today') {
        result = result.filter(t => t.due_date && isoToUserDate(t.due_date) === getUserTodayDate())
    } else if (state.filter === 'upcoming') {
        result = result.filter(t => t.due_date && isoToUserDate(t.due_date) > getUserTodayDate())
    }

    // Secondary filter
    if (state.priority !== 'all') {
        result = result.filter(t => t.priority === state.priority);
    }

    if (state.sort === 'manual') {
        // Negative = a goes first, positive = b goes first
        result = result.toSorted((a, b) => a.sort_key < b.sort_key ? -1 : a.sort_key > b.sort_key ? 1 : 0)
    } else {
        result = sortByField(result, state.sort, state.order)
    }

    return result;
}

async function deleteTask(id: number) {
    const confirmed = await confirmationManager.show('Are you sure?');
    if (!confirmed) return;
    await api.tasks.delete(String(id));
    applyTaskDelete(id);
    makeToast('Task deleted', 'success');
}

function renderTaskList(visibleTasks: Task[]) {
    // builds ul content using arr
    tasksListEls.tasksList.innerHTML = '';
    visibleTasks.forEach(t => {
        const clone = tasksListEls.taskLiTemplate.content.cloneNode(true);
        clone.querySelector('li').dataset.id = t.id
        clone.querySelector('.task-name').textContent = t.name;
        clone.querySelector('.task-toggle').checked = t.is_done;
        clone.querySelector('[data-priority]').dataset.priority = t.priority;
        clone.querySelector('.priority-use').setAttribute('href', `#badge-priority-${t.priority}`);
        if (t.due_date) {
            clone.querySelector('.due_date').textContent = displayDate(t.due_date);
        } else {
            clone.querySelector('.task-due-date').remove();
        }
        if (t.subtasks.length) {
            // populate subtask count text
            const thing = clone.querySelector('.meta-subtasks-text');
            // [icon] 0/1
            const subtaskStr = `${t.subtasks.filter(st => st.is_done).length}/${t.subtasks.length}`
            thing.textContent = subtaskStr;

            // For tasks where 1+ subtask is yet to be completed?
            // Add proper subtasks view for yet-to-complete subtasks of given task
            clone.querySelector('.task-subtasks').textContent = t.name
        } else {
            clone.querySelector('.subtask-toggle').remove();
            clone.querySelector('.meta-subtasks').remove();
        }
        clone.querySelector('.task-pillars').textContent = t.pillars.map(p => p.name).join(' · ');

        tasksListEls.tasksList.appendChild(clone);
    })
}

function setupSidebar() {
    // Sidebar options
    const priorities = ['all', 'low', 'medium', 'high', 'frog'] as const;

    tasksListEls.sidebar.addEventListener('click', (e) => {
        if (!(e.target instanceof Element)) return;
        const target = e.target;
        const btn = target.closest<HTMLElement>('.filter-btn');
        if (btn?.dataset.filter && btn.dataset.filter !== state.filter) {
            setTaskListState({ filter: btn.dataset.filter })
        }
        if (btn?.dataset.action === 'cycle-priority') {
            const idx = priorities.indexOf(state.priority);
            const next = priorities[(idx + 1) % priorities.length];
            setTaskListState({ priority: next })
        }
        // Toggle completed tasks
        if (target.matches('.toggle-completed')) {
            tasksListEls.tasksList.classList.toggle('show-completed', tasksListEls.toggleCompletedCheckbox.checked)
        }
    });
}

function setupListControls() {
    // Sidebar options
    const priorities = ['all', 'low', 'medium', 'high', 'frog'] as const;
    const sorts = ['manual', 'due_date', 'priority', 'name'] as const;

    document.addEventListener('click', (e) => {
        if (!(e.target instanceof Element)) return;
        const target = e.target;
        const btn = target.closest<HTMLElement>('.filter-btn');
        if (btn?.dataset.filter && btn.dataset.filter !== state.filter) {
            setTaskListState({ filter: btn.dataset.filter })
        }
        if (btn?.dataset.action === 'cycle-priority') {
            const idx = priorities.indexOf(state.priority);
            const next = priorities[(idx + 1) % priorities.length];
            setTaskListState({ priority: next })
        }
        if (e.target.matches('.show-completed')) {
            console.log("hit meeee")
            tasksListEls.tasksList.classList.toggle('show-completed', !tasksListEls.toggleCompletedCheckbox.checked)
        }
        if (e.target.matches('.sort-order-toggle')) {
            console.log("hit")
            setTaskListState({ order: state.order === 'asc' ? 'desc' : 'asc' });
        }
        // if (e.target.matches('.sort-by')) {
        //     const idx = sorts.indexOf(state.sort);
        //     const next = sorts[(idx+1) % sorts.length];
        //     console.log(`sorting by: ${next}`)
        //     setTaskListState({ sort: next })
        // }
    })
    const sortSelect = document.querySelector('#sort-by');
    sortSelect.addEventListener('dropdown:change', (e) => {
        const { value } = (e as CustomEvent).detail;
        if (!isSortValue(value)) return;
        setTaskListState({ sort: value });
    })
}

function setupContextMenu(e: MouseEvent, dialog: FormDialog, onPopulatedCallback) {
    const taskLi = e.target.closest('.task');
    const itemId: string = taskLi.dataset.id;

    contextMenu.create({
        position: { x: e.clientX, y: e.clientY },
        items: [
            {
                label: 'Edit', action: () => openModalForEdit(itemId, dialog, 'Task', onPopulatedCallback)
            },
            { label: 'Delete', action: async () => deleteTask(Number(itemId))}
        ]
    })
}

function setupTaskList() {
    tasksListEls.tasksList.addEventListener('click', async (e) => {
        const task = e.target.closest<HTMLLIElement>('.task');
        if (!task) return;
        const taskId = task.dataset.id;
        if (e.target.matches('.task-toggle')) {
            const checkbox = e.target;
            const response = await api.tasks.toggleComplete(taskId, checkbox.checked);
            taskUpsert(response.data.id, response.data);
        } else if (e.target.matches('.subtask-toggle')) {
            console.log("clicked")
            const taskLi = e.target.closest('.task') // parent li for this task ofc
            const subtasksDiv = taskLi.querySelector('.task-subtasks');
            subtasksDiv.hidden = !subtasksDiv.hidden;
        } else {
            const task = tasksStore.get().get(Number(taskId));
            taskDetailsPopover.open(task);
        }
    });
}

function setupSearch() {
    // Search input
    searchEls.searchInput.addEventListener('input', () => {
        // on input, filter by allTasks.include?
        const query = searchEls.searchInput.value.toLowerCase();
        const matches = [...tasksStore.get().values()].filter(task => task.name.toLowerCase().includes(query));

        // use matches to populate container in search popover with matching tasks
        searchEls.resultsContainer.innerHTML = '';
        matches.forEach(t => {
            const div = document.createElement('div');
            div.textContent = t.name;
            div.dataset.id = String(t.id);
            searchEls.resultsContainer.appendChild(div);
        });
    });

    // Click search result to open details popover
    searchEls.resultsContainer.addEventListener('click', (e) => {
        const target = e.target.closest('[data-id]');
        if (!target) return;
        const task = tasksStore.get().get(Number(target.dataset.id));
        taskDetailsPopover.open(task);
    });
}



// Functional core, impure shell?
class TaskDetailsPopover {
    #activeTaskId: number | null = null;
    #els = getTaskDetailPopoverElements();
    #unsubscribe: (() => void) | null = null;

    get activeTaskId(): number | null {
        // return this.#activeTask?.id ?? null;
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
        console.log("hit render")
        renderTaskDetails(deriveTaskView(task), this.#els);
    }
}
const taskDetailsPopover = new TaskDetailsPopover(); // Popover singleton, module-level
class SearchPopover {
    #els = getSearchElements();

    open() {
        this.#els.searchPopover.showPopover();
    }
}

export async function init() {

    // TODO: Clean up; for drag task li stuff
    const taskList = document.querySelector<HTMLDivElement>('.tasks-list');
    setupDragDrop(taskList);

    tasksStore.subscribe(() => {
        // taskMap.clear();
        // tasks.forEach(t => taskMap.set(t.id, t));
        renderTaskList(deriveVisibleTasks());
    })

    const { data } = await api.tasks.getAll();
    const next = new Map(data.map(t => [t.id, t]));
    tasksStore.set(next); // subscriber fires, taskMap built automatically

    // 2. Modal (needed by popover + context menu)
    const { dialog, populateEditModal } = await setupTaskFormModal();

    // Listen on emitted modal:success to update live after any submits/changes posted to API:
    dialog.addEventListener('modal:success', async (e: CustomEvent) => {
        if (e.detail.isEdit) taskUpsert(e.detail.data.id, e.detail.data);
        else {
            const { data } = await api.tasks.getAll();
            tasksStore.set(new Map(data.map(t => [t.id, t])));
        }
    })

    initSidebar();

    taskDetailEls.taskDetailsPopover.addEventListener('toggle', (e: ToggleEvent) => {
        if (e.newState === 'closed') taskDetailsPopover.close();
    });
    searchEls.searchPopover.addEventListener('toggle', (e: ToggleEvent) => {
        if (e.newState === 'closed') {
            searchEls.resultsContainer.innerHTML = '';
            searchEls.searchInput.value = '';
        }
    });

    // Edit / Delete options for task details popover
    taskDetailEls.taskDetailsPopover.addEventListener('click', async (e: MouseEvent) => {
        const id = taskDetailsPopover.activeTaskId; // from JS state, not the DOM now
        if (id === null) return;
        const target = e.target as HTMLElement;

        if (target.matches('.task-delete-btn')) deleteTask(id);
        else if (target.matches('.task-edit-btn')) openModalForEdit(String(id), dialog, 'Task', populateEditModal);
        else if (target.matches('.js-add-subtask')) {
            // Seed hidden supertask_ids input for submission
            const supertaskIdsInput = dialog.querySelector<HTMLInputElement>('#supertask_ids_hidden')!;
            supertaskIdsInput.value = String(id);
            dialog.showModal();
        } else if (target.matches('.task-details__done-toggle')) {
            const res = await api.tasks.toggleComplete(String(id), target.checked);
            taskUpsert(res.data.id, res.data);
        } else if (target.matches('.task-details__subtask-checkbox')) {
            const subtaskId = target.dataset.id;
            const res = await api.tasks.toggleComplete(subtaskId, target.checked);
            taskUpsert(res.data.id, res.data);
        }
    })

    setupSidebar();  // Task sidebar buttons - filtering/show completed/etc
    // TODO: currently wip - transition sidebar list controls to being atop list itself
    setupListControls();
    setupTaskList(); // Task list checkbox toggle
    setupSearch();
    enableStats(); // Circular progress/stats bar(s)

    tasksListEls.tasksList.addEventListener('contextmenu', (e: MouseEvent) => {
        e.preventDefault();
        setupContextMenu(e, dialog, populateEditModal);
    });
}