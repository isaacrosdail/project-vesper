
import { formatToUserTimeString, getJSInstant } from "../shared/datetime";
import { apiRequest, routes } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager.js';
import { makeToast } from '../shared/ui/toast';
import { initValidation, makeValidator } from '../shared/validators';


function validateDueDate(dueDateString: string): string | null {
    const isFrogCheckBox = document.querySelector<HTMLInputElement>('#is_frog');
    const isFrog = isFrogCheckBox!.checked;

    // duedate exists -> check in future
    if (dueDateString) {
        // check in future
        const today = formatToUserTimeString(new Date(), {})
        const valid = today < dueDateString;
        return valid ? null : 'ERROR: Due date must be in the future';
    } else {
        return isFrog ? 'Due date required for frog tasks' : null;
    }
}

// Validators
const validateTaskName = makeValidator('name', {
    maxLength: 3,
});

// function validateSleepTimes() {
//     const blech = document.querySelector<HTMLInputElement>('#wake_datetime');
//     const blech2 = document.querySelector<HTMLInputElement>('#sleep_datetime');

//     // ensure sleep is after wake?

// }


function toggleTaskComplete(
    itemId: string,
    isDone: boolean
) {
    const newIsDone = !isDone;
    const completedAtUTC = getJSInstant();

    const data = {
        is_done: newIsDone,
        completed_at: completedAtUTC
    }
    const url = routes.tasks.tasks.item(itemId);

    apiRequest('PATCH', url, data, {
        onSuccess: () => {
            const row = document.querySelector<HTMLElement>(`[data-item-id="${itemId}"]`);
            if (!row) return;
            const statusSpan = row.querySelector('.status-span');

            if (newIsDone) {
                row.dataset['isDone'] = 'True';
            } else {
                delete row.dataset['isDone'];
            }
            statusSpan?.classList.toggle('is-done');

            makeToast('Task status updated', 'success')
        }
    });
}

function enableStats() {
    document.querySelectorAll<HTMLDivElement>('.stats-ring').forEach(statsCircle => {
        const progress = Number(statsCircle.dataset.progress ?? 50); // we'll need to update this value to update the visual progress

        statsCircle.setAttribute("role", "progressbar");
        statsCircle.setAttribute("aria-valuenow", progress); // this value is grabbed by our stats-progress
        // content to show the percentage/value
        statsCircle.style.setProperty('--progress', progress + "%"); // set visual ring val
        statsCircle.setAttribute("aria-live", "polite")

    })
}

export function init() {
    const isFrogCheckbox = document.querySelector<HTMLInputElement>('#is_frog');
    const dueDateField = document.querySelector<HTMLInputElement>('#due_date');
    const priorityField = document.querySelector<HTMLInputElement>('#priority');
    if (!isFrogCheckbox || !dueDateField) return;

    isFrogCheckbox.addEventListener('change', () => {
        dueDateField.required = isFrogCheckbox.checked;
        priorityField.disabled = isFrogCheckbox.checked;
    });

    enableStats(); // Circular progress/stats bar(s)

    // Stuff for the tasks form search thing:
    const taskForm = document.querySelector('#tasks-entry-dashboard-modal');
    const taskCardTemplate = taskForm.querySelector('[data-task-template]');
    const taskCardContainer = taskForm.querySelector('[data-task-card-container]');
    const searchInput = taskForm.querySelector('[data-search]');
    const pillTemplate = taskForm.querySelector('[data-pill-template]');
    const pillContainer = taskForm.querySelector('.pill-container');
    let tasks = [] // empty arr for hiding stuff?
    let selectedTasks = [] // selected tasks from the input list

    // Hook into modal:cleanup so we clear off pills and hidden
    taskForm.addEventListener('modal:cleanup', () => {
        selectedTasks = []
        pillContainer.innerHTML = ''
        searchInput.value = ''
        tasks.forEach(task => task.element.classList.remove('hide'));
        document.querySelector('#subtask_ids_hidden').value = '';
    })

    searchInput.addEventListener('input', (e) => {
        const value = e.target.value;
        const normalizedValue = value.trim().toLowerCase();

        tasks.forEach(task => {
            const isSelected = selectedTasks.some(s => s.id === task.element.dataset.id);
            if (isSelected) return;
            const isVisible = task.name.toLowerCase().includes(normalizedValue);
            task.element.classList.toggle("hide", !isVisible)
        })
    })

    // event delegation events as closures, so we can keep refs
    function handleSubtaskEntry(e) {
        const clickedEl = e.target;
        // Click on a card for a task within the "dropdown":
        if (clickedEl.closest('.card')) {
            const card = clickedEl.closest('.card');
            
            card.classList.toggle('hide', true); // hide from list

            // 2. push {id, name} to selectedTasks, grab from dataset on div.card
            const { id, name } = card.dataset;
            selectedTasks.push({ id: id, name: name });

            // 3. Render a pill for this task; clone pill, modify text, & append to container
            const pill = pillTemplate.content.cloneNode(true).children[0];
            const pillName = pill.querySelector('.pill-name');
            pillName.textContent = name;
            // also put data-id on the pill for easy removal
            pill.dataset.id = id;
            pillContainer.appendChild(pill);

            // 4. append hidden input's .value for this task for submission
            // const hiddenTaskInput = document.createElement('input');
            const hiddenTaskInput = document.querySelector('#subtask_ids_hidden');
            // update value for hidden input (remember: this is a comma-separated list! "7,5,2" etc)
            hiddenTaskInput.value = selectedTasks.map(task => task.id).join(',');
            console.log(selectedTasks)
        }

        if (clickedEl.matches('.pill-remove')) {
            console.log("clicked")
            // 1. filter out of selectedTasks
            const pill = clickedEl.closest('.my-pill');
            const taskId = pill.dataset.id;
            // want to keep only the task that dont match this id
            selectedTasks = selectedTasks.filter(task => task.id !== taskId)

            // find the card matching data-id in the dropdown and remove hide
            const card = taskForm.querySelector(`[data-id="${taskId}"]`);
            card.classList.remove('hide');

            // remove pill & remove this task's id from our hidden input
            const hiddenTaskInput = document.querySelector('#subtask_ids_hidden');
            hiddenTaskInput.value = selectedTasks.map(task => task.id).join(',');
            pill.remove();
        }

        // if clickedEl is search -> open dropdown
        // remove hidden from the card container
        else if (clickedEl.closest('[data-search-wrapper]')) {
            const cardContainer = document.querySelector('[data-task-card-container]');
            console.log(cardContainer)
            cardContainer.classList.remove('hide');

            // Position under search bar input
            const inputRect = searchInput.getBoundingClientRect();
            cardContainer.style.top = `${inputRect.bottom}px`;
            cardContainer.style.left = `${inputRect.left}px`;
            cardContainer.style.width = `${inputRect.width}px`;
        }
        // Click outside search area -> hide 'dropdown'
        else if (!(clickedEl.closest('[data-search-wrapper]'))) {
            const cardContainer = document.querySelector('[data-task-card-container]');
            cardContainer.classList.add('hide');
        }
    }

    taskForm.addEventListener('click', handleSubtaskEntry);

    const url = routes.tasks.tasks.collection;
    const response = apiRequest('GET', url, null, {
        onSuccess: (responseData) => {
            tasks = responseData.data.map(task => {
                const card = taskCardTemplate.content.cloneNode(true).children[0];
                const header = card.querySelector("[data-header]")
                const body = card.querySelector("[data-body]")
                card.dataset.id = task.id;
                card.dataset.name = task.name;
                header.textContent = task.name;
                body.textContent = task.priority;
                taskCardContainer.append(card)
                return { name: task.name, priority: task.priority, element: card }
            })
        }
    })

    const form = document.querySelector<HTMLFormElement>('#tasks-form')!;
    initValidation(
    form,
        {
        due_date: validateDueDate,
        name: validateTaskName,
    })

    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;

        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const row = target.closest('.table-row')!;
            const { itemId } = row.dataset;
            const url = routes.tasks.tasks.item(itemId);
            const modal = document.querySelector('#tasks-entry-dashboard-modal');
            const rect = button.getBoundingClientRect();

            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => openModalForEdit(itemId, url, modal, 'Task')
                    },
                    {
                        label: 'Delete',
                        action: () => handleDelete(itemId, url)
                    },
                    {
                        label: 'Toggle task complete',
                        action: () => {
                            const isDone = row.dataset.isDone === 'True';
                            toggleTaskComplete(itemId, isDone);
                        }
                    }
                ]
            })
        }
    });
}