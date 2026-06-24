import { displayDate, getUserTodayDate, isoToUserDate } from '../shared/datetime';
import { api } from '../shared/services/api';
import { sortByField } from '../shared/tables';
import { required } from '../shared/utils';
import { Task, TaskPriority } from '../types';
import { openTaskDetails } from './details';
import { setupDragDrop } from './drag_n_drop';
import { tasksStore, taskUpsert } from './store';

let taskListEls!: ReturnType<typeof getTaskListEls>;
let taskListControlsEls!: ReturnType<typeof getTaskListControlsEls>;

export function initTaskList() {
    taskListEls = getTaskListEls();
    taskListControlsEls = getTaskListControlsEls();

    tasksStore.subscribe(() => renderTaskList(deriveVisibleTasks()));
    setupTaskList();
    setupListControls();
    setupDragDrop(taskListEls.taskList);
    syncControls();
}

function getTaskListEls() {
    return {
        taskList: required(document.querySelector<HTMLUListElement>('.task-list'), '.task-list'),
        sidebar: required(document.querySelector('.left-sidebar'), '.left-sidebar'),
        taskLiTemplate: required(document.querySelector<HTMLTemplateElement>('#task-li-template'), '#task-li-template'),
    };
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

function getTaskListControlsEls() {
    const taskListControls = required(document.querySelector('.task-list-controls'), 'task-list-controls');
    const els = {
        timeWindow: required(taskListControls.querySelector('#time-window-fieldset'), '#time-window-fieldset'),
        sortByDropdown: required(document.querySelector('#sort-by'), '#sort-by'),
        sortLabel: required(taskListControls.querySelector('[popovertarget="sort-by"] .dropdown-toggle-label'), 'sortLabel'),
        sortDirToggle: required(taskListControls.querySelector('.sort-order-toggle'), 'sortDirToggle'),
        priorityIcon: required(taskListControls.querySelector('[data-action="cycle-priority"] use'), '[data-action="cycle-priority"] use'),
        toggleCompletedCheckbox: required(taskListControls.querySelector<HTMLInputElement>('.toggle-completed'), '.toggle-completed'),
    };
    return els;
}


// Visually syncs controls from state declaratively?
function syncControls() {
    // 1. Update priority icon
    const priorityIconHref = state.priority === 'all' ? '#icon-funnel' : `#badge-priority-${state.priority}`;
    taskListControlsEls.priorityIcon.setAttribute('href', priorityIconHref);
    
    // 2. Set the checked radio from state.filter
    const filterDueDateRadio = taskListControlsEls.timeWindow.querySelector<HTMLInputElement>(`input[value="${state.filter}"]`);
    if (!filterDueDateRadio) {
        throw new Error(`syncControls: filterDueDateRadio not found for: #${state.filter}`)
    }
    filterDueDateRadio.checked = true;

    // 3a. Make toggle show state.sort's display text
    const activeOpt = document.querySelector(`#sort-by [data-value="${state.sort}"]`);
    if (activeOpt) taskListControlsEls.sortLabel.textContent = activeOpt.textContent;
    document.querySelectorAll('#sort-by [data-value]').forEach(opt =>
        opt.classList.toggle('active', opt.dataset.value === state.sort));
    // 3b. Flip sort asc/desc chevron accordingly
    taskListControlsEls.sortDirToggle.classList.toggle('flip', state.order === 'asc');
    taskListControlsEls.sortDirToggle.toggleAttribute('disabled', state.sort === 'manual');

    // 4. Gate off drag-n-drop sorting when sort isn't set to manual
    taskListEls.taskList.classList.toggle('sortable', state.sort === 'manual');
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

function renderTaskList(visibleTasks: Task[]) {
    // builds ul content using arr
    taskListEls.taskList.innerHTML = '';
    visibleTasks.forEach(t => {
        const clone = taskListEls.taskLiTemplate.content.cloneNode(true);
        clone.querySelector('li').dataset.id = t.id;
        clone.querySelector('.task__name').textContent = t.name;
        clone.querySelector('.task__done-toggle').checked = t.is_done;
        clone.querySelector('[data-priority]').dataset.priority = t.priority;
        clone.querySelector('.priority-use').setAttribute('href', `#badge-priority-${t.priority}`);
        if (t.due_date) {
            clone.querySelector('.due_date').textContent = displayDate(t.due_date);
        } else {
            clone.querySelector('.task__due-date').remove();
        }
        if (t.subtasks.length) {
            // populate subtask count text
            const thing = clone.querySelector('.task__subtask-count-text');
            // [icon] 0/1
            const subtaskStr = `${t.subtasks.filter(st => st.is_done).length}/${t.subtasks.length}`
            thing.textContent = subtaskStr;

            // For tasks where 1+ subtask is yet to be completed?
            // Add proper subtasks view for yet-to-complete subtasks of given task
            clone.querySelector('.task__subtasks').textContent = t.name
        } else {
            clone.querySelector('.task__expander').remove();
            clone.querySelector('.task__subtask-count').remove();
        }
        clone.querySelector('.task__pillars').textContent = t.pillars.map(p => p.name).join(' · ');

        taskListEls.taskList.appendChild(clone);
    })
}



function setupTaskList() {
    taskListEls.taskList.addEventListener('click', async (e) => {
        if (!(e.target instanceof Element)) return;
        const target = e.target;
        const taskLi = target.closest<HTMLLIElement>('.task');
        if (!taskLi) return;
        const taskId = taskLi.dataset.id;
        if (!taskId) return;

        if (target.matches('.task__done-toggle')) {
            const checkbox = target as HTMLInputElement;
            const response = await api.tasks.toggleComplete(taskId, checkbox.checked);
            taskUpsert(response.data.id, response.data);
        } else if (target.matches('.task__expander')) {
            const subtasksDiv = taskLi.querySelector<HTMLElement>('.task__subtasks');
            if (!subtasksDiv) return;
            subtasksDiv.hidden = !subtasksDiv.hidden;
        } else {
            const task = tasksStore.get().get(Number(taskId));
            if (!task) return;
            // taskDetailsPopover.open(task);
            openTaskDetails(task);
        }
    });
}


const FILTER_VALUES = ['all', 'today', 'upcoming'] as const;
type Filter = typeof FILTER_VALUES[number];

function isFilterValue(v: unknown): v is Filter {
    return FILTER_VALUES.includes(v as Filter);
}

const SORT_VALUES = ['manual', 'due_date', 'priority', 'name'] as const;
type SortValue = typeof SORT_VALUES[number];

// runtime guard that narrows e.detail.value -> SortValue?
function isSortValue(v: unknown): v is SortValue {
    return SORT_VALUES.includes(v as SortValue);
}


function setupListControls() {
    // Sidebar options
    const priorities = ['all', 'low', 'medium', 'high', 'frog'] as const;

    document.addEventListener('click', (e) => {
        if (!(e.target instanceof Element)) return;
        const target = e.target;
        const btn = target.closest<HTMLElement>('.js-filter-btn');
        if (btn?.dataset.action === 'cycle-priority') {
            const idx = priorities.indexOf(state.priority);
            const next = priorities[(idx + 1) % priorities.length];
            setTaskListState({ priority: next })
        }
        if (e.target.matches('.sort-order-toggle')) {
            setTaskListState({ order: state.order === 'asc' ? 'desc' : 'asc' });
        }
    })
    taskListControlsEls.sortByDropdown.addEventListener('dropdown:change', (e) => {
        const { value } = (e as CustomEvent).detail;
        if (!isSortValue(value)) return;
        setTaskListState({ sort: value });
    })
    taskListControlsEls.toggleCompletedCheckbox.addEventListener('change', () => {
        taskListEls.taskList.classList.toggle('show-completed', taskListControlsEls.toggleCompletedCheckbox.checked);
    })
    taskListControlsEls.timeWindow.addEventListener('change', (e) => {
        const filter = (e.target as HTMLInputElement).value;
        if (!isFilterValue(filter)) return;
        setTaskListState({ filter });
    })
}

