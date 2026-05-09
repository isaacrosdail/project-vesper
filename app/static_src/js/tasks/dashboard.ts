
import { enableStats } from '../shared/charts';
import { displayDate, getUserTodayDate, isoToUserDate } from '../shared/datetime';
import { initTaskForm } from '../shared/forms';
import { tasksStore } from '../shared/pubSub';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { initSidebar } from '../shared/ui/left-sidebar';
import { confirmationManager, openModalForEdit } from '../shared/ui/modal-manager';
import { makeToast } from '../shared/ui/toast';
import { title } from '../shared/utils';
import { FormDialog, Task } from '../types';
import { generateKeyBetween, generateNKeysBetween } from '../shared/fractional_indexing';

// TODO:
// 1. For due dates that are nearer, use "the day" (ex: Friday instead of Mar 20)


// All elements for task list filtering/altering/etc
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

type PopoverState = {
    activePopover: 'taskDetails' | 'search' | null
};
const popoverState: PopoverState = {
    activePopover: null
};

function setPopoverState(thing: Partial<PopoverState>) {
    // popoverState.activePopover = thing;
    Object.assign(popoverState, thing);
    renderPopover();
}
// const taskDetailsPopover = document.querySelector('.task-details-popover');
// const searchPopover = document.querySelector('.search-popover');

function renderPopover() {
    if (popoverState.activePopover === 'taskDetails') {
        taskDetailEls.taskDetailsPopover.showPopover();
    } else {
        taskDetailEls.taskDetailsPopover.hidePopover();
    }

    if (popoverState.activePopover === 'search') {
        searchEls.searchPopover.showPopover();
    } else {
        searchEls.searchPopover.hidePopover();
    }
}

// Pure data shaping
function deriveTaskView(task: Task) {
    const subtasks = task.subtasks
        .map(id => taskMap.get(id))
        .filter(Boolean);
    return {
        name: task.name,
        id: task.id,
        priority: title(task.priority),
        created_at: displayDate(task.created_at),
        due_date: task.due_date !== null ? displayDate(task.due_date) : null,
        pillars: task.pillars.map(p => p.name).join(' · '),
        priorityHref: `#badge-priority-${task.priority}`,
        subtasks: subtasks.map(st => ({
            name: st.name,
            is_done: st.is_done
        })),
        subtasksSummary: `${subtasks.filter(st => st.is_done).length}/${subtasks.length}`
    };
}

const taskMap = new Map<number, Task>();

// pub/sub (tasksStore) handles reacting to changes, this fn handles making the changes
function applyTaskUpdate(id: number, updated: Task) {
    // update source of truth
    const tasks = tasksStore.get();
    const next = tasks.map(t => t.id === id ? updated : t);
    tasksStore.set(next); // triggers all subscribers
}

function applyTaskDelete(id: number) {
    const next = tasksStore.get().filter(t => t.id !== id);
    tasksStore.set(next);
}

async function setupTaskFormModal() {
    const dialog = document.querySelector<FormDialog>('#tasks-entry-dashboard-modal');
    if (!dialog) {
        throw new Error('tasks dashboard: #tasks-entry-dashboard-modal not found');
    }
    const { selectTask, tasks } = await initTaskForm(dialog);

    function onPopulatedCallback(data: Task) {
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
        clone.querySelector('.subtask-checkbox').checked = st.is_done;
        els.subtasksContainer.appendChild(clone);
    });

    // Set activeTaskId for delete/edit buttons:
    // TODO: Put both on parent div instead for one spot
    root.querySelector('.task-delete-btn').setAttribute('data-active-task-id', `${view.id}`);
    root.querySelector('.task-edit-btn').setAttribute('data-active-task-id', `${view.id}`);
}

// Thin orchestrator
function showTaskDetails(task: Task) {
    const view = deriveTaskView(task);
    renderTaskDetails(view, taskDetailEls);
    setPopoverState({ activePopover: 'taskDetails' });
}

// Cache one li to be cloned?
type Filter = 'all' | 'today' | 'upcoming';
type Priority = 'all' | 'low' | 'medium' | 'high' | 'frog';

type TaskListState = {
    filter: Filter;
    priority: Priority;
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
    let result = tasksStore.get();
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
    // return result.toSorted((a, b) => a.sort_key.localeCompare(b.sort_key));
    return result.toSorted((a, b) => {
        // negative = a goes first
        // positive = b goes first
        // 0 = tie
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
            applyTaskUpdate(response.data.id, response.data);
        } else if (e.target.matches('.subtask-toggle')) {
            console.log("clicked")
            const taskLi = e.target.closest('.task') // parent li for this task ofc
            const subtasksDiv = taskLi.querySelector('.task-subtasks');
            subtasksDiv.hidden = !subtasksDiv.hidden;
        } else {
            const task = taskMap.get(Number(taskId));
            showTaskDetails(task);
        }
    });
}

function setupSearch() {
    // Search input
    searchEls.searchInput.addEventListener('input', () => {
        // on input, filter by allTasks.include?
        const query = searchEls.searchInput.value.toLowerCase();
        const matches = tasksStore.get().filter(task => task.name.toLowerCase().includes(query));

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
        const task = taskMap.get(Number(target.dataset.id));
        searchEls.searchPopover.hidePopover();
        showTaskDetails(task);
    });
}

export async function init() {

    // TODO: Clean up; for drag task li stuff
    const taskList = document.querySelector('.tasks-list');

    // Enables draggable for drag-n-drop: This way, only the button starts this, NOT "anywhere in the taskli"
    taskList.addEventListener('mousedown', (e) => {
        if (e.target.matches('.task-drag')) {
            const taskLi = e.target.closest<HTMLDivElement>('.task');
            taskLi.setAttribute('draggable', 'true')
        }
    })
    // TODO: Note: dragstart/dragend fire on the element that has draggable="true"
    // dragend - clean up state/classes regardless of whether a drop happened
    // Currently...."not working"?
    taskList.addEventListener('dragend', (e) => {
        if (e.target.matches('.task')) {
            e.target.setAttribute('draggable', 'false');
        }
    })

    // let sourceRef = null; // dragged task
    // let targetRef = null; // "dragged-over" task
    // let position: 'before' | 'after' | null = null; // top-half vs bottom half
    type DragState = { sourceRef: any, targetRef: any, position: 'before' | 'after' | null };
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
    taskList.addEventListener('dragover', (e) => {
        e.preventDefault(); // opt in to being a drop target
        const taskLi = e.target.closest('.task');
        if (taskLi) {
            const taskName = taskLi.querySelector('.task-name');
            console.log(`dragover: ${taskName.textContent}`);
            dragState.targetRef = taskLi;

            // top half or bottom half calc
            const rect = taskLi.getBoundingClientRect();
            const midpoint = rect.top + rect.height / 2;
            dragState.position = e.clientY < midpoint ? 'before' : 'after';
            console.log(`dragState.position: ${dragState.position}`)
        }
    })
    const keyOf = (el) => el ? taskMap.get(Number(el.dataset.id)).sort_key : null;
    // drop - fires once on the drop target when user releases
    taskList.addEventListener('drop', async (e) => {
        if (e.target.closest('.task')) {
            const taskId = dragState.targetRef.dataset.id;
            const task = taskMap.get(Number(taskId));
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
            const sourceTask = taskMap.get(Number(sourceTaskId));
            sourceTask.sort_key = key;

            // In-mem update, then persist sort_key via PATCH
            // TODO: This fails since Pydantic model uses due_date: date NOT datetime and rejects the time portion
            // Should decide whether to make due_dates JUST dates in both schema.py AND models.py or keep datetimes?
            applyTaskUpdate(Number(dragState.sourceRef.dataset.id), sourceTask);
            const response = await api.tasks.patch(sourceTaskId, { sort_key: key }); // Update ONLY sort_key
            console.log(response.data)

            // Reset state:
            Object.keys(dragState).forEach(key => delete dragState[key]);
            
        }
    })
    tasksStore.subscribe((tasks) => {
        console.log('store updated, task count: ', tasks.length)
        taskMap.clear();
        tasks.forEach(t => taskMap.set(t.id, t));
        renderTaskList(deriveVisibleTasks());
    })

    const { data } = await api.tasks.getAll();

    // --------------------------
    // TODO: Temporarily mock fractional index on frontend-only:
    // const keys = generateNKeysBetween(null, null, data.length);
    // data.forEach((t: Task, i: number) => t.sort_key = keys[i]);
    // console.log(`Keys generated!`)
    // --------------------------
    console.log(data)

    tasksStore.set(data); // subscriber fires, taskMap built automatically
    console.log('tasksStore has:', tasksStore.get())

    // 2. Modal (needed by popover + context menu)
    const { dialog, populateEditModal } = await setupTaskFormModal();

    initSidebar();
    // =====================================================
    // General sidebar setup (not tasks specific)
    // TODO: This should prob end up in a new left-sidebar.ts handler/file after we're done sketching
    // const sidebarToggle = document.querySelector('#sidebar-toggle');
    // const wrapper = document.querySelector('.wrapper');
    // if (!wrapper || !sidebarToggle) {
    //     console.error('setupSidebar: missing sidebar-toggle/wrapper');
    //     return;
    // }
    // // Toggle
    // sidebarToggle.addEventListener('click', () => wrapper.classList.toggle('sidebar-open'));
    // ======================================================

    taskDetailEls.taskDetailsPopover.addEventListener('toggle', (e: ToggleEvent) => {
        if (e.newState === 'closed') {
            setPopoverState({ activePopover: null }) // redundant but harmless? calls
        }
    })

    // Edit / Delete options for task details popover
    taskDetailEls.taskDetailsPopover.addEventListener('click', async (e: MouseEvent) => {
        if (e.target.matches('.task-delete-btn')) {
            const activeTaskId: string = e.target.dataset.activeTaskId;
            deleteTask(Number(activeTaskId));
            setPopoverState({ activePopover: null });
        } else if (e.target.matches('.task-edit-btn')) {
            const activeTaskId = e.target.dataset.activeTaskId;
            setPopoverState({ activePopover: null });
            openModalForEdit(activeTaskId, dialog, 'Task', populateEditModal);
        }
    })

    setupSidebar();  // Task sidebar buttons - filtering/show completed/etc
    setupTaskList(); // Task list checkbox toggle

    // Listener in 'capture' phase so that the first click while a popover is open closes it, but
    // doesn't apply to whatever else was clicked
    document.addEventListener('click', (e) => {
        if (popoverState.activePopover === null) return;

        // TODO: Using this means, when we open a popover then hit Esc, our next click is STILL captured
        const target = e.target as HTMLElement;
        if (!target.closest('.popover')) {
            e.stopPropagation(); //
            e.preventDefault(); // optional?
            setPopoverState({ activePopover: null });
        }
    }, true);

    setupSearch();
    enableStats(); // Circular progress/stats bar(s)

    tasksListEls.tasksList.addEventListener('contextmenu', (e: MouseEvent) => {
        e.preventDefault();
        setupContextMenu(e, dialog, populateEditModal);
    });
}