
import { formatToUserTimeString } from "../shared/datetime";
import { api } from '../shared/services/api';
import { handleModalFormSubmit } from '../shared/ui/modal-manager';
import { handleErrorMessages, initValidation, makeValidator } from '../shared/validators';
import { FormDialog, Task, TaskPriority, Unit } from '../types';


type UnitGroupKey = 'weight' | 'volume';

const unitGroups = {
    weight: ['g', 'kg', 'oz', 'lb'],
    volume: ['ml', 'l', 'fl_oz']
} as const satisfies Record<UnitGroupKey, Unit[]>

type UnitOptionsMap = Record<string, UnitGroupKey[]>;
// Map categories to groups: keys are categories, values are groups (in turn, keys for above dict)
const unitOptionsMap: UnitOptionsMap = {
    beverages: ["volume"],
    condiments_sauces: ["volume"],
    fruits: ["weight"],
    vegetables: ["weight"], 
    legumes: ["weight"],
    grains: ["weight"],
    bakery: ["weight"],
    meats: ["weight"],
    seafood: ["weight"],
    snacks: ["weight"],
    sweets: ["weight"],
    processed_convenience: ["weight", "volume"],
    supplements: ["weight", "volume"],
    dairy_eggs: ["weight", "volume"],
    fats_oils: ["weight", "volume"],
}


/**
 * Initialize "click eye icon for password/text toggle".
 * 
 * Conventions:
 * - Buttons must have a [data-password-toggle] attribute
 * - whose value = the ID of the <input type="password">
 * Script will:
 * - Find the target <input>
 * - Toggle type="password" <-> type="text" on click
 * - Reflect toggle state in `aria-pressed`
 * 
 * @example
 * <input id="pwd1" type="password">
 * <button data-password-toggle="pwd1">(eye)</button>
 */
export function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll<HTMLElement>('[data-password-toggle]');
    if (toggleButtons.length === 0) return;

    toggleButtons.forEach(btn => {
        const inputId = btn.dataset["passwordToggle"];
        if (!inputId) return;
        const input = document.querySelector<HTMLInputElement>(`#${inputId}`);
        if (!input) return;
        const ariaPressed = input.type === 'text'
            ? 'true'
            : 'false';
        btn.setAttribute('aria-pressed', ariaPressed)

        btn.addEventListener('click', () => {
            const isPressed = btn.getAttribute('aria-pressed') === 'true';
            input.type = isPressed ? 'password' : 'text';
            btn.setAttribute('aria-pressed', String(!isPressed));
        })
    })
}

document.addEventListener('submit', (e) => {
    const submittedForm = e.target as HTMLFormElement;
    e.preventDefault();

    // Route to appropriate handler
    const formType = submittedForm.dataset['formType'];
    if (!formType) {
        console.warn('forms.ts: No formType attr found for submitted form')
        return
    }

    switch (formType) {
        case 'modal':
            const modal = submittedForm.closest<FormDialog>('dialog');
            handleModalFormSubmit(submittedForm, modal);
            break;
        case 'page':
        case 'action':
            submittedForm.submit();
    }
});

/**
 * Making my own type=number field.
 */
function setupNumericInputRestrictions() {
    const numberInputs = document.querySelectorAll('[data-type-int], [data-type-float]');
    // Don't impede functional keys
    const FUNCTIONAL_KEYS = [
        'Backspace', 
        'Delete',
        'Tab',
        'ArrowLeft', 
        'ArrowRight',
        'Home',         // Jump to start
        'End',          // Jump to end
    ];

    numberInputs.forEach(el => {
        const input = el as HTMLInputElement;
        const isFloat = input.hasAttribute('data-type-float');

        input.addEventListener('keydown', (e: KeyboardEvent) => {
            if (FUNCTIONAL_KEYS.includes(e.key)) {
                return;
            }

            // Arrows up/down to inc/dec
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                const currVal = input.value;
                let num = isFloat
                    ? parseFloat(currVal)
                    : parseInt(currVal, 10);
                
                if (isNaN(num)) {
                    num = 0;
                }

                const stepSize = parseFloat(input.dataset.step || '1'); // default 1 for ints
                const stepInterval = e.key === 'ArrowDown'
                    ? -stepSize
                    : stepSize;
                
                const newVal = Math.max(0, num + stepInterval);
                const multiplier = 1 / stepSize;
                const roundedVal = isFloat
                    ? Math.round(newVal * multiplier) / multiplier
                    : newVal;

                if (roundedVal === 0) {
                    input.value = '';
                } else {
                    input.value = String(roundedVal);
                }

                input.dispatchEvent(new Event('input', { bubbles: true }));
                e.preventDefault();
                return;
            }

            // Allow: Ctrl+A, Ctrl+C
            if (e.ctrlKey || e.metaKey) return;
            // Allow digits
            if (/^\d+$/.test(e.key)) return;
            // Allow '.' for floats
            if (isFloat && e.key === '.') return;

            e.preventDefault();
        });

        input.addEventListener('paste', (e) => {
            const pastedText = e.clipboardData?.getData('text') ?? '';

            // Validation RegEx
            const isValid = isFloat
                ? /^\d*\.?\d*$/.test(pastedText) // digits w/optional single '.'
                : /^\d+$/.test(pastedText)       // digits only

            if (!isValid) {
                e.preventDefault();
            }
        });
    })
}

export async function initTaskForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#tasks-form');
    if (!form) {
        console.warn('initTaskForm: #tasks-form not found in dialog');
        return;
    }
    const dueDateField = form.querySelector<HTMLInputElement>('#due_date');
    const priorityField = form.querySelector<HTMLInputElement>('#priority-fieldset');
    const taskCardTemplate = form.querySelector<HTMLTemplateElement>('[data-subtask-template]');
    const pillTemplate = form.querySelector<HTMLTemplateElement>('[data-subtask-chip-template]');
    const taskCardContainer = form.querySelector<HTMLDivElement>('[data-subtask-dropdown]');
    const searchInput = form.querySelector<HTMLInputElement>('[data-search]');
    const pillContainer = form.querySelector<HTMLDivElement>('.subtask-chips');

    // TODO: clean up all this stuff
    const searchWrapper = form.querySelector('[data-search-wrapper]');

    if (!taskCardTemplate || !taskCardContainer || !searchInput || !pillTemplate || !pillContainer || !dueDateField || !priorityField) {
        console.warn('initTaskForm: missing subtask UI elements')
        return
    }

    const hiddenTaskInput = dialog.querySelector<HTMLInputElement>('#subtask_ids_hidden');
    if (!hiddenTaskInput) {
        console.warn('initTaskForm: Error no hiddenTaskInput')
        return
    }

    priorityField.addEventListener('change', () => {
        const selected = form.querySelector<HTMLInputElement>('input[name="priority"]:checked');
        dueDateField.required = selected?.value === ('frog' satisfies TaskPriority);
    });

    initPillarCheckboxes(dialog);

    // Stuff for the tasks form search thing:
    type TaskCard = { name: string; priority: TaskPriority; element: HTMLElement; }
    const tasks: TaskCard[] = []
    const selectedTasks: { id: string; name: string; }[] = []

    // Hook into modal:cleanup so we clear off pills and hidden
    dialog.addEventListener('modal:cleanup', () => {
        selectedTasks.length = 0
        pillContainer.innerHTML = ''
        searchInput.value = ''
        tasks.forEach(task => task.element.classList.remove('hide'));
        taskCardContainer.classList.add('hide');
    })

    searchInput.addEventListener('input', (e) => {
        const value = (e.target as HTMLInputElement).value;
        const normalizedValue = value.trim().toLowerCase();

        tasks.forEach(task => {
            const isSelected = selectedTasks.some(s => s.id === task.element.dataset.id);
            if (isSelected) return;
            const isVisible = task.name.toLowerCase().includes(normalizedValue);
            task.element.classList.toggle("hide", !isVisible)
        })
    })

    /**
     * Find the card in the tasks array by ID
     * Hide it in the dropdown
     * Add it to selectedTasks
     * Clone a pill, set its name text and data-id, append to pill container
     * Update the hidden input (comma-separated IDs that get submitted with the form)
     * 
     * @param id 
     * @param name 
     * @returns 
     */
    function selectTask(id: string, name: string) {
        const card = tasks.find(t => t.element.dataset.id === id)?.element;
        if (!card) {
            console.warn(`selectTask: no card for task id ${id}`);
            return;
        };

        card.classList.add('hide'); // hide card
        selectedTasks.push({ id, name }); // include in selectedTasks

        // Render a pill for this task; clone pill, modify text, & append to container
        const pill = pillTemplate.content.cloneNode(true).children[0] as HTMLElement;
        const pillName = pill.querySelector('.subtask-chip-name');
        if (!pillName) { console.warn('selectTask: no .subtask-chip-name div found'); return; }
        pillName.textContent = name;
        pill.dataset.id = id; // put ID on dataset for pill for removal
        pillContainer.appendChild(pill);

        // update value for hidden input (remember: this is a comma-separated list! "7,5,2" etc)
        hiddenTaskInput.value = selectedTasks.map(task => task.id).join(',');
    }

    // event delegation events as closures, so we can keep refs
    function handleSubtaskEntry(e: MouseEvent) {
        const clickedEl = e.target as HTMLElement;
        // Click on a card for a task within the "dropdown":
        const card = clickedEl.closest<HTMLDivElement>('.subtask-option');
        if (card) {
            selectTask(card.dataset.id, card.dataset.name);
            return;
        }
        if (clickedEl.matches('.subtask-chip-remove')) {
            const pill = clickedEl.closest<HTMLDivElement>('.subtask-chip');
            const taskId = pill.dataset.id;
            
            // filter out of selectedTasks: keep only the tasks that dont match this id
            const idx = selectedTasks.findIndex(task => task.id === taskId);
            if (idx !== -1) selectedTasks.splice(idx, 1);

            // find the card matching data-id in the dropdown and remove hide
            const taskCard = dialog.querySelector<HTMLDivElement>(`[data-id="${taskId}"]`);
            taskCard.classList.remove('hide');

            // remove pill & remove this task's id from our hidden input
            hiddenTaskInput.value = selectedTasks.map(task => task.id).join(',');
            pill.remove();
            return;
        }

        // if clickedEl is search -> open & position task card container under search bar input
        if (clickedEl.closest('[data-search-wrapper]')) {
            taskCardContainer.classList.remove('hide');
            searchWrapper.classList.add('open');
            const inputRect = searchInput.getBoundingClientRect();
            taskCardContainer.style.top = `${inputRect.bottom}px`;
            taskCardContainer.style.left = `${inputRect.left}px`;
            taskCardContainer.style.width = `${inputRect.width}px`;
            return
        }
        // Click anywhere else -> hide dropdown
        taskCardContainer.classList.add('hide');
        searchWrapper.classList.remove('open');
    }

    dialog.addEventListener('click', handleSubtaskEntry);

    const response = await api.tasks.getAll();
    if (!response.data?.length) {
        console.warn('[tasks form] fetch returned empty');
        return;
    }
    tasks.length = 0;
    response.data.forEach(task => {
        const card = taskCardTemplate.content.cloneNode(true).children[0] as HTMLElement;
        const { id, name, priority } = task;
        card.dataset.id = String(id);
        card.dataset.name = name;
        card.querySelector("[data-header]").textContent = name;
        card.querySelector("[data-body]").innerHTML = `
            <svg class="icon" data-priority="${task.priority}">
                <use href="#badge-priority-${task.priority}"></use>
            </svg>
        `;
        taskCardContainer.append(card)
        tasks.push({ name, priority, element: card })
    });

    function validateDueDate(dueDateString: string): string | null {
        const selectedPriority = form.querySelector<HTMLInputElement>('input[name="priority"]:checked');
        // duedate exists -> check in future
        if (dueDateString) {
            if (dialog.dataset.mode !== 'edit') {
                const today = formatToUserTimeString(new Date(), {})
                if (today >= dueDateString) return 'Due date must be in the future';
            }
            return null;
        }
        return selectedPriority?.value === ('frog' satisfies TaskPriority) ? 'Due date required for frog tasks' : null;
    }

    const validateTaskName = makeValidator('name', { maxLength: 150 });
    initValidation(form, { due_date: validateDueDate, name: validateTaskName })

    return { selectTask, tasks }; // Return these so Edit context menu in dashboard has them
}

export function initHabitForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#habits-form');
    if (!form) {
        console.warn('initHabitForm: #habits-form not found in dialog');
        return;
    }
    initPillarCheckboxes(dialog);

    const validateHabitName = makeValidator('habit', { maxLength: 50 })
    const validateTargetFrequency = makeValidator('target_frequency', { numType: 'int', min: 1, max: 21 })
    initValidation(form, { name: validateHabitName, target_frequency: validateTargetFrequency })
}

export function initMetricsForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#daily_metrics-form');
    if (!form) {
        console.warn('initMetricsForm: #daily_metrics-form not found in dialog');
        return;
    }

    const validateSteps = makeValidator('steps', {
        numType: 'int', min: 1, max: 40_000, pattern: /^\d+$/
    })
    const validateCalories = makeValidator('calories', {
        numType: 'int', min: 0, max: 10_000
    })
    const validateWeight = makeValidator('weight', {
        numType: 'float', min: 0, max: 300
    })
    // Validation
    initValidation(form,
        {
            steps: validateSteps,
            calories: validateCalories,
            weight: validateWeight,

        }
    )
}

// Shared by product and transaction forms
const validateNetWeight = makeValidator('net_weight', {
    numType: 'float', min: 0,
});

const validateCalories = makeValidator('calories_per_100g', {
    numType: 'float', min: 0, max: 900,
});

const validateBarcode = makeValidator('barcode', {
    minLength: 8, maxLength: 14, pattern: /^\d+$/
});

const validateProductName = makeValidator('name', {
    maxLength: 80,
});


export function initProductForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#products-form');
    if (!form) {
        console.warn('initProductForm: #products-form not found in dialog');
        return;
    }

    dialog.addEventListener('change', (e) => {
        const target = e.target;
        if (!(target instanceof HTMLElement)) return;

        if (target.matches('[name="category"]')) {
            handleUnitFiltering(form, e);
        }
    });

    initValidation(form,
        {
            name: validateProductName,
            barcode: validateBarcode,
            calories_per_100g: validateCalories,
            net_weight: validateNetWeight,
        }
    )
}

export function initTransactionForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#transactions-form');
    if (!form) {
        console.warn('initTransactionForm: #transactions-form not found in dialog');
        return;
    }

    const priceField = dialog.querySelector<HTMLInputElement>('[name="price_at_scan"]');
    if (!priceField) {
        console.warn('initTransactionForm: priceField input element not found');
        return;
    }

    dialog.addEventListener('change', (e) => {
        const target = e.target;
        if (!(target instanceof HTMLElement)) return;

        if (target.matches('[name="category"]')) {
            handleUnitFiltering(form, e);
        }
        else if (target.matches('[name="product_id"]')) {
            toggleProductFields(e);
        }
    });

    // TODO: should use our modal:close event instead?
    dialog.addEventListener('modal:cleanup', () => {
        // Reset product fields visibility/disabled state
        const productFields = dialog.querySelectorAll<HTMLInputElement | HTMLSelectElement>(
            '.product-field input, .product-field select'
        );
        productFields.forEach(el => {
            el.parentElement!.hidden = true;
            el.disabled = true;
        });

        // Reset select back to full list (after edit mode swapped it)
        // Restore product_id product list for Transaction form modal
        const productSelect = dialog.querySelector<HTMLSelectElement>('#product_id');
        if (productSelect?.dataset['originalInnerHTML']) {
            productSelect.innerHTML = productSelect.dataset['originalInnerHTML'];
            delete productSelect.dataset['originalInnerHTML'];
        }

        // Clear hidden product id input
        const productHidden = dialog.querySelector<HTMLInputElement>('#product_id_hidden');
        if (productHidden) {
            productHidden.value = "";
        }
    })

    priceField.addEventListener('keydown', (e: Event) => {
        if (!(e instanceof KeyboardEvent)) return;

        const isDigit = /^\d$/.test(e.key); // digit 0-9

        if (isDigit) {
            e.preventDefault();

            const currentCents = Math.round(Number(priceField.value) * 100);
            const newCentsString = String(currentCents) + e.key;
            const newCents = Number(newCentsString);
            const newPrice = newCents / 100;

            priceField.value = newPrice.toFixed(2);
            priceField.dispatchEvent(new Event('input', { bubbles: true }));

        } else if (e.key === 'Backspace') {
            e.preventDefault();
            const currentCents = Math.round(Number(priceField.value) * 100);

            if (currentCents === 0) {
                priceField.value = '';
            } else {
                const centsAfterBackspace = Math.floor(currentCents / 10);
                const newPrice = centsAfterBackspace / 100;

                priceField.value = newPrice.toFixed(2);
            }

            priceField.dispatchEvent(new Event('input', { bubbles: true }));
        }
    })

    priceField.addEventListener('paste', (e) => {
        e.preventDefault();
        const currentCents = Math.round(Number(priceField.value) * 100);
        const pastedDigits = e.clipboardData?.getData('text') ?? "";
        const nextCentsString = String(currentCents) + pastedDigits;
        const newCents = Number(nextCentsString);
        const newPrice = newCents / 100;

        priceField.value = newPrice.toFixed(2);
        priceField.dispatchEvent(new Event('input', { bubbles: true }));
    })

    const validatePrice = makeValidator('price_at_scan', {
        numType: 'float', min: 0.01, max: 1000000,
    });

    const validateQuantity = makeValidator('quantity', {
        numType: 'int', min: 1, max: 999
    });

    initValidation(form,
        {
            price_at_scan: validatePrice,
            quantity: validateQuantity,
            name: validateProductName,
            barcode: validateBarcode,
            calories_per_100g: validateCalories,
            net_weight: validateNetWeight,
        }
    )
}


export function initTimeEntryForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#time_entries-form');
    if (!form) {
        console.warn('initTimeEntryForm: #time_entries-form not found in dialog');
        return;
    }

    const startInput = dialog.querySelector<HTMLInputElement>('[name="started_at"]');
    const endInput = dialog.querySelector<HTMLInputElement>('[name="ended_at"]');

    [startInput, endInput].forEach(el => {
        el?.addEventListener('input', () => {
            if (!startInput?.value || !endInput?.value) return;
            const message = startInput.value < endInput.value
                ? null
                : 'Error: End time before start time';
            handleErrorMessages('started_at', message);
            handleErrorMessages('ended_at', message);
        });
    });

    initPillarCheckboxes(dialog);

    const validateCategory = makeValidator('category', {
        maxLength: 50,
    });

    const validateDescription = makeValidator('description', {
        maxLength: 200,
    })

    initValidation(form, {
        category: validateCategory,
        description: validateDescription,
    });
}


function reindexRow(row: HTMLElement, idx: number) {
    row.dataset.index = String(idx); // update data-index to new index
    row.querySelectorAll('[name], [for]').forEach(el => {
        for (const attr of ['name', 'for']) {
            const val = el.getAttribute(attr);
            if (val) el.setAttribute(attr, val.replace(/\[\d+\]/, `[${idx}]`));
        }
    })
    // const span = row.querySelector('.ingredient-number-span')
    // if (span) span.textContent = String(idx + 1);
}

export function initRecipeForm(dialog: FormDialog) {
    const form = dialog.querySelector<HTMLFormElement>('#recipes-form');
    if (!form) {
        console.warn('initRecipeForm: #recipes-form not found in dialog');
        return;
    }
    const addIngredientButton = dialog.querySelector<HTMLButtonElement>('#add-ingredient');
    const ingredientsContainer = dialog.querySelector<HTMLDivElement>('#ingredients-container'); // div! so label+select
    const firstIngredientRow = ingredientsContainer.querySelector('.ingredient-row');
    const cleanIngredientRow = firstIngredientRow.cloneNode(true); // store initial state of first row for modal cleanup
    if (!addIngredientButton || !ingredientsContainer || !firstIngredientRow || !cleanIngredientRow) {
        console.warn('initRecipeForm: addIng/ingContainer/firstIngRow/cleanIngRow missing')
        return;
    }

    dialog.addEventListener('modal:cleanup', () => {
        ingredientsContainer.innerHTML = ''; // clear container
        ingredientsContainer.appendChild(cleanIngredientRow.cloneNode(true)); // add back 1 original row
    });

    // Clone clean row & reindex
    addIngredientButton.addEventListener('click', () => {
        const newIdx = ingredientsContainer.querySelectorAll('.ingredient-row').length;
        const clone = cleanIngredientRow.cloneNode(true) as HTMLDivElement;
        clone.removeAttribute('id');
        reindexRow(clone, newIdx)
        ingredientsContainer.appendChild(clone);
    });
    dialog.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (!(target.matches('.js-remove-ingredient'))) {
            return
        }
        // Remove row & re-index others
        const thisIngredientRow = target.closest('.ingredient-row');
        thisIngredientRow.remove();
        ingredientsContainer.querySelectorAll('.ingredient-row')
            .forEach((row, newIdx) => reindexRow(row, newIdx))
    })
}

function toggleProductFields(e: Event): void {
    if (!(e.target instanceof HTMLSelectElement)) return;

    const form = e.target.closest('form');
    const productFields = form.querySelectorAll('.product-field input, .product-field select');
    const isNew = (e.target.value === '__new__');

    productFields.forEach(field => {
        const htmlField = field as HTMLInputElement | HTMLSelectElement;
        htmlField.parentElement!.hidden = !isNew;
        htmlField.disabled = !isNew;

        if (!isNew) {
            htmlField.value = '';
        }
    })
}


/**
 * Filters available unit options in product/transaction form modals
 * based on selected category (eg, hides ml/l for "Bakery")
 * @param {Event} e Change event from a category <select>
 */
function handleUnitFiltering(form: HTMLFormElement, e: Event): void {
    if (!(e.target instanceof HTMLSelectElement)) return;

    const categoryElement = form.querySelector<HTMLSelectElement>('[name="category"]');
    const unitSelect = form.querySelector<HTMLSelectElement>('[name="unit_type"]');
    if (!categoryElement || !unitSelect) return;

    const categorySelection = categoryElement.value;
    const unitTypes = unitSelect.querySelectorAll('option');

    // 2-step lookup with dict keys to store appropriate list of allowed units for given selection in allowedUnits
    const groupKeys = unitOptionsMap[categorySelection];
    if (!groupKeys) return;

    const allowedUnits = groupKeys.flatMap(key => unitGroups[key]);

    const currentUnitsSelected = unitSelect.value as Unit;
    if (!allowedUnits.includes(currentUnitsSelected)) {
        unitSelect.value = '';
    }

    unitTypes.forEach(option => {
        option.hidden = !allowedUnits.includes(option.value as Unit);
    });
}

/**
 * Wire live checkbox <-> hidden input sync and cleanup, called at form init.
 */
export function initPillarCheckboxes(dialog: FormDialog) {
    const fieldset = dialog.querySelector<HTMLFieldSetElement>('#pillar-fieldset');
    const hidden = dialog.querySelector<HTMLInputElement>('#pillar_ids_hidden');
    if (!fieldset || !hidden) {
        console.warn('initPillarCheckboxes: #pillar-fieldset/#pillar_ids_hidden not found');
        return;
    }
    fieldset.addEventListener('change', () => {
        const checked = Array.from(fieldset.querySelectorAll<HTMLInputElement>('input:checked'));
        hidden.value = checked.map(el => el.value).join(',');
    });
    dialog.addEventListener('modal:cleanup', () => {
        fieldset.querySelectorAll<HTMLInputElement>('[type="checkbox"]').forEach(cb => cb.checked = false);
        hidden.value = '';
    });
}


/**
 * Set checkboxes and hidden input from existing pillar data, call in onPopulated.
 */
export function populatePillarCheckboxes(container: HTMLElement, pillars: {id: number}[]) {
    pillars.forEach(p => {
        const cb = container.querySelector<HTMLInputElement>(`input[value="${p.id}"]`);
        if (cb) cb.checked = true;
    });
    const hidden = container.querySelector<HTMLInputElement>('#pillar_ids_hidden');
    if (hidden) hidden.value = pillars.map(p => p.id).join(',');
}


document.addEventListener('DOMContentLoaded', () => {
    setupNumericInputRestrictions();
});

initPasswordToggles();