import { makeToast } from './toast.js';
import { apiRequest } from '../services/api.js';
import { isoToTimeInput, isoToDateInput } from '../datetime.js';
import { formatDecimal } from '../numbers.js';
import { removeTableRow } from '../tables.js';
import { confirmationManager } from '../ui/modal-manager.js';


const MENU_CONFIG = {
    default: [
        {text: 'Edit', action: 'edit'},
        {text: 'Delete', action: 'delete'}
    ],
    products: [{text: 'Add to shopping list', action: 'addToShoppingList'}],
    transactions: [{text: 'Add to shopping list', action: 'addToShoppingList'}]
}

/**
 * 
 * @param {string} type - Type of menu to open. Determines which actions array to use, how to position (cursor vs rect)
 * @param {object} triggerInfo - Object containing relevant positioning + data context needed, bound to menu itself before finishing
 * @returns 
 */
function openMenu(type, triggerInfo) {
    document.querySelector('.context-menu')?.remove(); // Always remove any menus before opening a new one to ensure clean slate

    const menu = document.createElement('ul');
    menu.classList.add(`context-menu`);

    // Shallow copy of menuItems using spread operator: [...menuItems]
    // Splice items list together based on config above
    const { subtype } = triggerInfo.context;
    const items = [
        ...MENU_CONFIG.default,
        ...(MENU_CONFIG[subtype] || [])
    ]

    // Build & append <li> elements
    const menuElements = items.map(item => {
        const li = document.createElement('li');
        li.textContent = item.text;
        li.dataset.action = item.action;
        return li;
    });
    menuElements.forEach(element => menu.appendChild(element));

    // Position menu either at cursor (type context) OR button (type dots)
    if (type === 'context') {
        menu.style.left = triggerInfo.x + 'px';
        menu.style.top = triggerInfo.y + 'px';
    }
    else if (type === 'dots') {
        const { left, top } = triggerInfo.rect;
        menu.style.left = `${left}px`;
        menu.style.top  = `${top}px`;
    }

    menu.style.display = 'block';
    menu.context = triggerInfo.context; // bind context info to menu itself

    document.body.appendChild(menu);
}
// Use Object.entries(..) to take the responseData object and make it iterable
// Then forEach to loop through each entry, using [fieldName, fieldValue] here to
// destructure each entry into its key-value parts
// Inside the loop body (predicate?) we can select the current input since the IDs align with the to_dict key names
function populateModalFields(modal, data) {
    Object.entries(data).forEach(([fieldName, fieldValue]) => {
        const input = modal.querySelector(`#${fieldName}`);
        if (!input || fieldValue == null) return;

        switch (input.type) {
            case 'checkbox':
                input.checked = fieldValue;
                break;
            case 'date':
                input.value = isoToDateInput(fieldValue);
                break;
            case 'time':
                input.value = isoToTimeInput(fieldValue);
                break;
            case 'select-one':
                if (typeof fieldValue === 'string') {
                    input.value = fieldValue.toLowerCase();
                } else {
                    input.value = fieldValue;
                }
                break;
            default:
                if (input.type === 'number') {
                    const step = parseFloat(input.step) || 1;
                    if (step === 1) {
                        input.value = Math.round(fieldValue);
                    } else {
                        input.value = formatDecimal(fieldValue, 2);
                    }
                } else {
                    input.value = String(fieldValue);
                }
        }
        // For time entries, derive entry_date from started_at
        if (data.started_at) {
            const entryDateInput = modal.querySelector('#entry_date');
            if (entryDateInput) {
                entryDateInput.value = isoToDateInput(data.started_at);
            }
        }
    });
}

function handleEdit(menuContext) {
    const { itemId, module, subtype } = menuContext;
    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('GET', url, (responseData) => {
        const modal = document.querySelector(`#${subtype}-entry-dashboard-modal`); // NOTE: Consider expanding macro naming usage further
        modal.dataset.mode = 'edit'; // to direct submits to PATCH instead of POST
        modal.dataset.itemId = responseData.data.id;
        modal.dataset.subtype = subtype;

        modal.showModal();
        populateModalFields(modal, responseData.data);
    })
}

async function handleDelete(menuContext) {
    const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
    if (!confirmed) return;

    const { itemId, module, subtype } = menuContext;
    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('DELETE', url, (responseData) => {
        console.log(responseData.data);
        removeTableRow(itemId);
    });
}

function handleAddToShoppingList(menuContext) {
    const { itemId, productName } = menuContext;
    const quantity = 1;
    menu?.remove();

    // Actually send to backend:
    const url = '/groceries/shopping-lists/items';
    const data = { product_id: itemId };

    apiRequest('POST', url, (responseData) => {
        const existingLi = document.querySelector(`li[data-product-id="${itemId}"]`);
        if (existingLi) {
            const newQty = updateQty(existingLi);
            makeToast(`Updated ${productName} quantity to ${newQty}`, 'success');
            return;
        }
        addShoppingListItemToDOM(responseData.data.item_id, responseData.data.product_id, productName);
    }, data);
}

document.addEventListener('contextmenu', (e) => {
    if (e.ctrlKey) {
        const row = e.target.closest('.table-row');
        if (!row) return;
        e.preventDefault();

        const triggerInfo =
        {
            x: e.clientX,
            y: e.clientY,
            context: {
                itemId: row.dataset.itemId,
                name: row.querySelector('td:nth-child(2)').textContent,
                module: row.dataset.module,
                subtype: row.dataset.subtype
            }
        };

        openMenu('context', triggerInfo); // TODO?: Pull our context menu handling into some kind of global.js
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelector('.context-menu')?.remove();
    }
});

document.addEventListener('click', async (e) => {
    const menu = document.querySelector('.context-menu');

    if (menu && !menu.contains(e.target)) {
        menu?.remove();
        return;
    }

    const action = e.target.dataset.action;

    // This is just an object where keys are strings (duh), and values are function references (not calling them, just storing them)
    const actionHandlers = {
        'edit': handleEdit,
        'delete': handleDelete,
        'addToShoppingList': handleAddToShoppingList
    }

    // With guard, call appropriate action & pass in menu.context
    if (actionHandlers[action]) {
        actionHandlers[action](menu.context);
        // since handleX functions now lack access to menu element, we'll clean menu up here instead
        menu?.remove();
    }

    // TODO: Refine/rename
    if (e.target.matches('.dots-btn')) {
        const button = e.target.closest('.row-actions');
        const row = e.target.closest('.table-row');
        const triggerInfo =
        {
            rect: button.getBoundingClientRect(),
            context: {
                itemId: row.dataset.itemId,
                name: row.querySelector('td:nth-child(2)').textContent,
                module: row.dataset.module,
                subtype: row.dataset.subtype
            }
        };

        openMenu('dots', triggerInfo);
    }
});

function updateQty(existingLi) {
    const qtySpan = existingLi.querySelector('.item-qty');
    const currentQty = parseInt(existingLi.dataset.quantityWanted, 10);
    const newQty = currentQty + 1;

    qtySpan.textContent = newQty;
    existingLi.dataset.quantityWanted = newQty;
    return newQty;
}

function addShoppingListItemToDOM(itemId, productId, productName, quantity = 1) {
    const ul = document.querySelector('.shopping-list');
    const emptyText = document.querySelector('#list-empty');
    emptyText?.remove();
    // Clone the contents of our template for the new li
    const li = document
                .querySelector('#shoppinglist-item-template')
                .content
                .cloneNode(true);

    const liEl = li.querySelector('li');
    liEl.querySelector('.item-text').textContent = productName;
    liEl.querySelector('.item-qty').textContent = quantity;
    liEl.dataset.itemId = itemId;
    liEl.dataset.productId = productId;
    liEl.dataset.quantityWanted = quantity;
    ul.appendChild(liEl);
}