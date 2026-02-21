
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

    // Circular progress/stats bar(s)
    enableStats();

    // Stuff for the tasks form search thing:
    const taskCardTemplate = document.querySelector('[data-task-template]');
    const taskCardContainer = document.querySelector('[data-task-card-container]');
    const searchInput = document.querySelector('[data-search]');
    let tasks = [] // empty arr for hiding stuff?

    searchInput.addEventListener('input', (e) => {
        const value = e.target.value;
        const normalizedValue = value.trim().toLowerCase();
        console.log(`normalized: ${normalizedValue}`)
        tasks.forEach(task => {
            const isVisible = task.name.toLowerCase().includes(normalizedValue);
            task.element.classList.toggle("hide", !isVisible)
        })
    })

    document.addEventListener('click', (e) => {
        // if target is search -> open dropdown
        const target = e.target;
        if (target.closest('[data-search-wrapper]')) {
            console.log("yes")
        }
    })
    // If click outside search wrapper -> close dropdown
    const taskForm = document.querySelector('#tasks-entry-dashboard-modal');
    taskForm.addEventListener('click', (e) => {
        if (!(e.target.closest('[data-search-wrapper]'))) {
            console.log("no")
        }
     })

    const url = routes.tasks.tasks.collection;
    const response = apiRequest('GET', url, null, {
        onSuccess: (responseData) => {
            console.table(responseData)
            tasks = responseData.data.map(task => {
                const card = taskCardTemplate.content.cloneNode(true).children[0];
                const header = card.querySelector("[data-header]")
                const body = card.querySelector("[data-body]")
                header.textContent = task.name;
                body.textContent = task.priority;
                taskCardContainer.append(card)
                return { name: task.name, priority: task.priority, element: card }
            })
        }
    })

    const form = document.querySelector<HTMLFormElement>('#tasks-form')!;
    // Validation
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