import { makeToast } from './toast.js';
import { apiRequest } from '../services/api.js';
import { isoToTimeInput, isoToDateInput } from '../datetime.js';

const menuItems = ['Edit', 'Delete'];
const menuItemsGroceries = ['Add to shopping list'];

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
    let items = [...menuItems];

    // Append our shopping list option if it's the transactions table
    // so: items = ['Edit', 'Delete', 'Add to shopping list']
    if (triggerInfo.context.subtype === 'transactions' || triggerInfo.context.subtype === 'products') {
        items = [...items, ...menuItemsGroceries];
    }

    // Now we map over 'items' to render <li> elements
    const menuElements = items.map(label => {
        const li = document.createElement('li');
        li.textContent = label;
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

document.addEventListener('contextmenu', (e) => {
    if (e.ctrlKey) {
        e.preventDefault();

        const row = e.target.closest('.table-row');
        if (!row) return;

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

    // TODO: Should rewrite this to separate concerns but have got to stop committing to rewrites for now
    if (e.target.textContent === 'Add to shopping list') {
        const { productId, productName } = menu.context;
        const quantity = 1;
        menu?.remove();

        // Actually send to backend:
        const url = '/groceries/shopping-lists/items';
        const data = { product_id: itemId };

        apiRequest('POST', url, (responseData) => {
            const existingLi = document.querySelector(`li[data-product-id="${productId}"]`);
            if (existingLi) {
                const newQty = updateQty(existingLi);
                makeToast(`Updated ${productName} quantity to ${newQty}`, 'success');
                return;
            }
            addShoppingListItemToDOM(responseData.data.item_id, responseData.data.product_id, productName);
        }, data);
    }

    // SCRATCH WORK
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
    if (e.target.textContent === 'Delete') {
        const { itemId, module, subtype } = menu.context;
        const url = `/${module}/${subtype}/${itemId}`;

        apiRequest('DELETE', url, (responseData) => {
            console.log(`Deleted item: ${responseData.data.name}`);
        });
    }
    // Prototype - refine/delete
    if (e.target.textContent === 'Edit') {
        const { itemId, module, subtype } = menu.context;

        const url = `/${module}/${subtype}/${itemId}`;

        apiRequest('GET', url, (responseData) => {
            console.log(responseData.data.name);

            // Grab our modal (tasks first here) & pre-fill name input
            const modal = document.querySelector('#task-entry-dashboard-modal');
            modal.dataset.mode = 'edit'; // to direct submits to PATCH instead of POST
            modal.dataset.itemId = responseData.data.id;
            modal.dataset.subtype = subtype;
            modal.showModal();

            // Use Object.entries(..) to take the responseData object and make it iterable
            // Then forEach to loop through each entry, using [fieldName, fieldValue] here to
            // destructure each entry into its key-value parts
            // Inside the loop body (predicate?) we can select the current input since the IDs align with the to_dict key names
            // 
            console.log(responseData.data)
            Object.entries(responseData.data).forEach(([fieldName, fieldValue]) => {
                const currentInput = modal.querySelector(`#${fieldName}`);
                if (currentInput) {
                    if (fieldValue == null) {
                        return; // skip null/undefined fields to leave them empty
                    }
                    if (currentInput.type === 'checkbox') {
                        currentInput.checked = fieldValue;
                    } else if (currentInput.type === 'date') {
                        currentInput.value = isoToDateInput(fieldValue);
                    } else if (currentInput.type === 'select-one') {
                        currentInput.value = fieldValue.toLowerCase();
                    } else if (currentInput.type === 'time') {
                        console.log(fieldValue);
                        currentInput.value = isoToTimeInput(fieldValue);
                        console.log(fieldValue);
                    }
                    else {
                        currentInput.value = String(fieldValue);
                    }
                }
            });
        })
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