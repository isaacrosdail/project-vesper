
import { enableStats } from '../shared/charts';
import { initTaskForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { confirmationManager, openModalForEdit } from '../shared/ui/modal-manager';
import { makeToast } from '../shared/ui/toast';
import { required } from '../shared/utils';
import { applyTaskDelete, tasksStore, taskUpsert } from '../tasks/store';
import type { FormDialog, Task } from '../types';
import { initTaskDetails, openTaskDetails } from './details';
import { initTaskList } from './list';


let searchEls!: ReturnType<typeof getSearchEls>;
function getSearchEls() {
    return {
        searchPopover: required(document.querySelector('#search-popover'), '#search-popover'),
        searchInput: required(document.querySelector<HTMLInputElement>('.task-search'), '.task-search'),
        resultsContainer: required(document.querySelector('.results-container'), 'results-container'),
    }
}

async function setupTaskFormModal() {
    const dialog = document.querySelector<FormDialog>('#tasks-entry-dashboard-modal');
    if (!dialog) {
        throw new Error('tasks dashboard: #tasks-entry-dashboard-modal not found');
    }
    const { selectTask, setExcludeId, tasks } = await initTaskForm(dialog);
    const dialogNarrowed = dialog;

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
            const cb = dialogNarrowed.querySelector<HTMLInputElement>(`input[value="${p.id}"]`);
            if (cb) cb.checked = true;
        })
        // also sync the hidden input
        const pillarIdsHidden = required(dialogNarrowed.querySelector<HTMLInputElement>('#pillar_ids_hidden'), '#pillar_ids_hidden');
        pillarIdsHidden.value = data.pillars.map(p => p.id).join(',');
    }

    return { dialog, populateEditModal: onPopulatedCallback };
}


async function deleteTask(id: number) {
    const confirmed = await confirmationManager.show('Are you sure?');
    if (!confirmed) return;
    await api.tasks.delete(String(id));
    applyTaskDelete(id);
    makeToast('Task deleted', 'success');
}


function setupContextMenu(e: MouseEvent, dialog: FormDialog, onPopulatedCallback: (data: Task) => void) {
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
        if (!task) return;
        openTaskDetails(task);
    });
}


// TODO: Strip?
class SearchPopover {
    #els = getSearchEls();

    open() {
        this.#els.searchPopover.showPopover();
    }
}

export async function init() {
    searchEls = getSearchEls();

    initTaskList(); // els, controls, list clicks, drag, store subscription

    const { data } = await api.tasks.getAll();
    tasksStore.set(new Map(data.map(t => [t.id, t]))); // subscriber fires, taskMap built automatically

    // 2. Modal (needed by popover + context menu)
    const { dialog, populateEditModal } = await setupTaskFormModal();
    initTaskDetails(dialog, populateEditModal, deleteTask);

    // Listen on emitted modal:success to update live after any submits/changes posted to API:
    dialog.addEventListener('modal:success', async (e: CustomEvent) => {
        if (e.detail.isEdit) taskUpsert(e.detail.data.id, e.detail.data);
        else {
            const { data } = await api.tasks.getAll();
            tasksStore.set(new Map(data.map(t => [t.id, t])));
        }
    })

    searchEls.searchPopover.addEventListener('toggle', (e: ToggleEvent) => {
        if (e.newState === 'closed') {
            searchEls.resultsContainer.innerHTML = '';
            searchEls.searchInput.value = '';
        }
    });

    setupSearch();
    enableStats(); // Circular progress/stats bar(s)

    const taskList = required(document.querySelector('.task-list'), '.task-list');
    taskList.addEventListener('contextmenu', (e: MouseEvent) => {
        e.preventDefault();
        setupContextMenu(e, dialog, populateEditModal);
    });
}
