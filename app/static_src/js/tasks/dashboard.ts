
import { enableStats } from '../shared/charts';
import { displayDate, getUserTodayDate, isoToUserDate } from '../shared/datetime';
import { initTaskForm } from '../shared/forms';
import { generateKeyBetween } from '../shared/fractional_indexing';
import { tasksStore } from '../shared/pubSub';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { initSidebar } from '../shared/ui/left-sidebar';
import { confirmationManager, openModalForEdit } from '../shared/ui/modal-manager';
import { makeToast } from '../shared/ui/toast';
import { title } from '../shared/utils';
import { FormDialog, Task, TaskPriority } from '../types';

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

// pub/sub (tasksStore) handles reacting to changes, this fn handles making the changes
function taskUpsert(id: number, updated: Task) {
    // update source of truth
    const next = new Map(tasksStore.get()); // same O(n) cost as the old .map, but keeping fresh references
    next.set(id, updated);
    tasksStore.set(next); // triggers all subscribers
}

function applyTaskDelete(id: number) {
    const next = new Map(tasksStore.get())
    next.delete(id)
    tasksStore.set(next);
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

type TaskListState = {
    filter: Filter;
    priority: TaskPriority | 'all';
}

const state: TaskListState = { filter: 'all', priority: 'all' };

function setTaskListState(patch: Partial<TaskListState>) {
    Object.assign(state, patch);
    // Update priority icon
    if (state.priority === 'all') {
        tasksListEls.priorityBtn.setAttribute('href', '#icon-funnel');
    } else {
        tasksListEls.priorityBtn.setAttribute('href', `#badge-priority-${state.priority}`);
    }
    const filterOptions = tasksListEls.sidebar.querySelectorAll('[data-filter]');
    filterOptions.forEach(el => el.classList.remove('active'));
    // query for THIS option's svg?
    tasksListEls.sidebar.querySelector(`[data-filter="${state.filter}"]`)?.classList.add('active');
    renderTaskList(deriveVisibleTasks());
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
    return result.toSorted((a, b) => {
        // negative = a goes first, positive = b goes first, 0 = tie
        // Return negative when a < b?
        return a.sort_key < b.sort_key ? -1 : a.sort_key > b.sort_key ? 1 : 0
    })
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

function setupDragDrop(taskList: HTMLDivElement) {
    // Enables draggable for drag-n-drop: This way, only the button starts this, NOT "anywhere in the taskli"
    taskList.addEventListener('mousedown', (e) => {
        if (e.target.matches('.task-drag')) {
            const taskLi = e.target.closest<HTMLDivElement>('.task');
            taskLi.setAttribute('draggable', 'true')
        }
    })
    // TODO: Note: dragstart/dragend fire on the element that has draggable="true"
    // dragend - clean up state/classes regardless of whether a drop happened
    // TODO: Currently...."not working"?
    taskList.addEventListener('dragend', (e) => {
        if (e.target.matches('.task')) {
            e.target.setAttribute('draggable', 'false');
        }
    })

    type DragState = { sourceRef: any, targetRef: any,
        position: 'before' | 'after' | null   // drag to top-half vs bottom half of another task
    };
    const dragState: DragState = { sourceRef: null, targetRef: null, position: null };
    taskList.addEventListener('dragstart', (e) => {
        if (e.target.matches('.task')) {
            dragState.sourceRef = e.target;
        }
    })
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
        const taskName = taskLi.querySelector('.task-name');
        dragState.targetRef = taskLi;

        // top half or bottom half calc
        const rect = taskLi.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        dragState.position = e.clientY < midpoint ? 'before' : 'after';
    })
    const keyOf = (el) => el ? tasksStore.get().get(Number(el.dataset.id)).sort_key : null;
    // drop - fires once on the drop target when user releases
    taskList.addEventListener('drop', async (e) => {
        if (e.target.closest('.task')) {
            const taskId = dragState.targetRef.dataset.id;
            const task = tasksStore.get().get(Number(taskId));
            console.log(`task: ${task.name}, taskId: ${taskId}`)

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
            const sourceTaskId = dragState.sourceRef.dataset.id;
            const sourceTask = tasksStore.get().get(Number(sourceTaskId));
            sourceTask.sort_key = key;

            // In-mem update, then persist sort_key via PATCH
            // TODO: This fails since Pydantic model uses due_date: date NOT datetime and rejects the time portion
            // Should decide whether to make due_dates JUST dates in both schema.py AND models.py or keep datetimes?
            taskUpsert(Number(dragState.sourceRef.dataset.id), sourceTask);
            const response = await api.tasks.patch(sourceTaskId, { sort_key: key }); // Update ONLY sort_key

            Object.keys(dragState).forEach(key => delete dragState[key]); // reset state
        }
    })
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
    setupTaskList(); // Task list checkbox toggle
    setupSearch();
    enableStats(); // Circular progress/stats bar(s)

    tasksListEls.tasksList.addEventListener('contextmenu', (e: MouseEvent) => {
        e.preventDefault();
        setupContextMenu(e, dialog, populateEditModal);
    });
}