import { makeToast } from './toast.js';
import { apiRequest } from '../services/api.js';
import { isoToTimeInput, isoToDateInput } from '../datetime.js';
import { formatDecimal } from '../numbers.js';
import { removeTableRow } from '../tables.js';
import { confirmationManager } from './modal-manager.js';
import { FormDialog } from '../../types';


type MenuOptionTypes = 'products' | 'transactions';

type MenuItem = {
    text: string;
    action: string;
}

type ActionType = 'edit' | 'delete' | 'addToShoppingList';

const MENU_CONFIG: Record<'default' | 'products' | 'transactions', MenuItem[]> = {
    default: [
        {text: 'Edit', action: 'edit'},
        {text: 'Delete', action: 'delete'}
    ],
    products: [{text: 'Add to shopping list', action: 'addToShoppingList'}],
    transactions: [{text: 'Add to shopping list', action: 'addToShoppingList'}]
}

// Disciminated union for triggerInfo object:
type ContextObject = {
    context: {
        itemId: string;
        name: string | null;
        module: string;
        subtype: MenuOptionTypes;
    }
}
type ContextMenuTrigger = ContextObject & {
    type: 'context';
    x: number;
    y: number;
}
type DotsMenuTrigger = ContextObject & {
    type: 'dots';
    rect: DOMRect;
}

type TriggerInfo = ContextMenuTrigger | DotsMenuTrigger;

/**
 * 
 * @param {object} triggerInfo - Object containing relevant positioning + data context needed, bound to menu itself before finishing
 * @returns 
 */
function openMenu(triggerInfo: TriggerInfo) {
    document.querySelector('.context-menu')?.remove(); // Always remove any menus before opening a new one to ensure clean slate

    const menu = document.createElement('ul');
    menu.classList.add(`context-menu`);

    // Shallow copy of menuItems using spread operator: [...menuItems]
    // Splice items list together based on config above
    const { subtype } = triggerInfo.context;
    const items: MenuItem[] = [
        ...MENU_CONFIG.default,
        ...(MENU_CONFIG[subtype] || [])
    ]

    // Build & append <li> elements
    const menuElements = items.map(item => {
        const li = document.createElement('li');
        li.textContent = item.text;
        li.dataset['action'] = item.action;
        return li;
    });
    menuElements.forEach(element => menu.appendChild(element));

    // Position menu either at cursor (type context) OR button (type dots)
    if (triggerInfo.type === 'context') {
        menu.style.left = triggerInfo.x + 'px';
        menu.style.top = triggerInfo.y + 'px';
    }
    else if (triggerInfo.type === 'dots') {
        const { left, top } = triggerInfo.rect;
        menu.style.left = `${left}px`;
        menu.style.top  = `${top}px`;
    }

    menu.style.display = 'block';
    (menu as any).context = triggerInfo.context; // bind context info to menu itself

    document.body.appendChild(menu);
}
// Use Object.entries(..) to take the responseData object and make it iterable
// Then forEach to loop through each entry, using [fieldName, fieldValue] here to
// destructure each entry into its key-value parts
// Inside the loop body (predicate?) we can select the current input since the IDs align with the to_dict key names
function populateModalFields(modal: HTMLDialogElement, data: Record<string, any>) {
    Object.entries(data).forEach(([fieldName, fieldValue]) => {
        const input = modal.querySelector<HTMLInputElement>(`#${fieldName}`);
        if (!input || fieldValue === null) return;

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
                        input.value = String(Math.round(fieldValue));
                    } else {
                        input.value = formatDecimal(fieldValue, 2);
                    }
                } else {
                    input.value = String(fieldValue);
                }
        }
        // For time entries, derive entry_date from started_at
        if (data['started_at']) {
            const entryDateInput = modal.querySelector<HTMLInputElement>('#entry_date');
            if (entryDateInput) {
                entryDateInput.value = isoToDateInput(data['started_at']);
            }
        }
    });
}

function handleEdit(menuContext: ContextObject['context']) {
    const { itemId, module, subtype } = menuContext;

    const modal = document.querySelector<FormDialog>(`#${subtype}-entry-dashboard-modal`); // NOTE: Consider expanding macro naming usage further
    if (!modal) {
        throw new Error(`Modal not found: ${subtype}-entry-dashboard-modal`);
    }

    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('GET', url, (responseData) => {
        modal.dataset.mode = 'edit'; // to direct submits to PATCH instead of POST
        modal.dataset.itemId = responseData.data.id;
        modal.dataset.subtype = subtype;

        modal.showModal();
        populateModalFields(modal, responseData.data);
    })
}

async function handleDelete(menuContext: ContextObject['context']) {
    const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
    if (!confirmed) return;

    const { itemId, module, subtype } = menuContext;
    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('DELETE', url, (responseData) => {
        console.log(responseData.data);
        removeTableRow(itemId);
    });
}

function handleAddToShoppingList(menuContext: ContextObject['context']) {
    const { itemId, name: productName } = menuContext;
    const quantityWanted = 1;

    if (!productName) {
        console.error('Product name required for shopping list');
        return;
    }

    const url = '/groceries/shopping-lists/items';
    const data = { product_id: itemId, quantity_wanted: quantityWanted };

    apiRequest('POST', url, (responseData) => {
        const existingLi = document.querySelector<HTMLLIElement>(`li[data-product-id="${itemId}"]`);
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
        const target = e.target as HTMLElement;
        const row = target.closest<HTMLElement>('.table-row');
        if (!row) {
            console.error('Missing table row');
            return;
        }
        const { itemId, module, subtype } = row.dataset;
        const name = row?.querySelector('td:nth-child(2)')?.textContent ?? null;

        if (!itemId || !module || !subtype) {
            console.error('Missing required dataset attributes');
            return;
        }
        e.preventDefault();

        const triggerInfo: ContextMenuTrigger =
        {
            type: 'context',
            x: e.clientX,
            y: e.clientY,
            context: {
                itemId,
                name,
                module,
                subtype: subtype as MenuOptionTypes
            }
        };

        openMenu(triggerInfo);
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelector('.context-menu')?.remove();
    }
});

document.addEventListener('click', async (e) => {
    const menu = document.querySelector('.context-menu');
    const target = e.target as HTMLElement;

    if (menu && !menu.contains(target)) {
        menu.remove();
        return;
    }

    const action = target.dataset['action'] as ActionType | undefined;

    // This is just an object where keys are strings (duh), and values are function references (not calling them, just storing them)
    const actionHandlers: Record<ActionType, (context: ContextObject['context']) => void> = {
        'edit': handleEdit,
        'delete': handleDelete,
        'addToShoppingList': handleAddToShoppingList
    }

    // With guard, call appropriate action & pass in menu.context
    if (action && menu && actionHandlers[action]) {
        actionHandlers[action]((menu as any).context);
        // since handleX functions now lack access to menu element, we'll clean menu up here instead
        menu.remove();
    }

    // TODO: Refine/rename
    if (target.matches('.dots-btn')) {
        // const target = e.target as HTMLButtonElement;
        const button = target.closest('.row-actions')!; // non-assert for now!
        const row = target.closest<HTMLElement>('.table-row')!; // non-assert for now!
        const { itemId, module, subtype } = row.dataset;
        const name = row.querySelector('td:nth-child(2)')?.textContent;

        if (!itemId || !module || !subtype || !name) {
            console.error('Missing required data on row');
            return;
        }

        const triggerInfo: DotsMenuTrigger =
        {
            type: 'dots',
            rect: button.getBoundingClientRect(),
            context: {
                itemId,
                name,
                module,
                subtype: subtype as MenuOptionTypes
            }
        };

        openMenu(triggerInfo);
    }
});

function updateQty(existingLi: HTMLLIElement) {
    const qtySpan = existingLi.querySelector('.item-qty');
    if (!qtySpan) {
        throw new Error('Quantity span not found');
    }

    const currentQty = parseInt(existingLi.dataset['quantityWanted'] ?? '0', 10);
    const newQty = currentQty + 1;

    qtySpan.textContent = String(newQty);
    existingLi.dataset['quantityWanted'] = String(newQty);
    return newQty;
}

function addShoppingListItemToDOM(itemId: string, productId: string, productName: string, quantity = 1) {
    const ul = document.querySelector('.shopping-list');
    if (!ul) {
        throw new Error('Shopping list <ul> not found')
    }
    const emptyText = document.querySelector('#list-empty');
    emptyText?.remove();

    // Clone the contents of our template for the new li
    const template = document.querySelector('#shoppinglist-item-template');
    const li = (template as HTMLTemplateElement).content.cloneNode(true) as DocumentFragment;

    const liEl = li.querySelector('li');
    if (!liEl) throw new Error('li not found in template');

    const itemText = liEl.querySelector('.item-text');
    const itemQty = liEl.querySelector('.item-qty');
    if (!itemText || !itemQty) throw new Error('Template structure invalid');

    itemText.textContent = productName;
    itemQty.textContent = String(quantity);
    liEl.dataset['itemId'] = itemId;
    liEl.dataset['productId'] = productId;
    liEl.dataset['quantityWanted'] = String(quantity);
    ul.appendChild(liEl);
}