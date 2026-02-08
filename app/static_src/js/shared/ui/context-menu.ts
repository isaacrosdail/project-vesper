import { makeToast } from './toast.js';
import { apiRequest } from '../services/api.js';

import { removeTableRow } from '../tables.js';
import { confirmationManager } from './modal-manager.js';
import { FormDialog } from '../../types';
import { getJSInstant } from '../datetime.js';
import { getSubtypeLabel } from '../../types.js';

type MenuOptionTypes = 'products' | 'transactions' | 'tasks';

type MenuItem = {
    text: string;
    action: string;
}

type ActionType = 'edit' | 'delete' | 'addToShoppingList' | 'toggleTaskComplete';

type ContextObject = {
    context: {
        itemId: string;
        module: string;
        subtype: MenuOptionTypes;
        isDone?: boolean;
        productId?: string;
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

const MENU_CONFIG: Record<'default' | 'products' | 'transactions' | 'tasks', MenuItem[]> = {
    default: [
        {text: 'Edit', action: 'edit'},
        {text: 'Delete', action: 'delete'}
    ],
    products: [{text: 'Add to shopping list', action: 'addToShoppingList'}],
    transactions: [{text: 'Add to shopping list', action: 'addToShoppingList'}],
    tasks: [{text: 'Toggle complete', action: 'toggleTaskComplete'}]
}

/**
 * Creates & displays a context menu at the specified position.
 * Removes any existing menu first to ensure clean slate.
 * Menu items are built from MENU_CONFIG based on the subtype
 * Note: Removes .context-menu's at start
 * 
 * @param {object} triggerInfo Contains positioning (x/y OR rect) and context data (itemId, module, subtype)
 */
function openMenu(triggerInfo: TriggerInfo) {
    closeMenu();

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

/**
 * Queries for `.context-menu` and removes it.
 */
export function closeMenu() {
    document.querySelector('.context-menu')?.remove();
}


/**
 * Opens form modal dialog and populates fields with data fetched from API.
 * 
 * Side Effects:
 * - Sets dialog `data-mode="edit"` to re-route submission to PATCH.
 * - Populates form inputs based on API response.
 * - For `transactions`, disables the `#product_id` select and 
 *   mirrors its value into `#product_id_hidden` to preserve submission.
 *   The disabled field is tagged with `data-disabled-overriden` and 
 *   must be reverted upon modal close.
 * 
 * @param menuContext Context containing itemId, module, & subtype
 */
function handleEdit(menuContext: ContextObject['context']) {
    const { itemId, module, subtype } = menuContext;

    const modal = document.querySelector<FormDialog>(`#${subtype}-entry-dashboard-modal`);
    if (!modal) {
        throw new Error(`Modal not found: ${subtype}-entry-dashboard-modal`);
    }

    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('GET', url, null, {
        onSuccess: (responseData) => {
            modal.dataset.mode = 'edit'; // to direct submits to PATCH instead of POST
            modal.dataset.itemId = responseData.data.id;
            modal.dataset.subtype = subtype;

            modal.showModal();
            populateModalFields(modal, responseData.data);

            // Set text
            const legend = modal.querySelector('legend');
            if (!legend?.textContent) {
                throw new Error('Modal legend missing or empty');
            }
            legend.dataset['originalText'] = legend.textContent;
            legend.textContent = `Edit ${getSubtypeLabel(subtype)}`;

            if (subtype === 'transactions') {
                const productSelectInput = modal.querySelector<HTMLSelectElement>('#product_id');
                const productInputHidden = modal.querySelector<HTMLInputElement>('#product_id_hidden');
                if (productSelectInput && productInputHidden) {
                    productSelectInput.dataset['originalInnerHTML'] = productSelectInput.innerHTML;
                    productSelectInput.innerHTML = `<option selected>${responseData.data.product_name}</option>`;

                    productSelectInput.disabled = true;
                    productInputHidden.value = responseData.data.product_id;
                    productInputHidden.disabled = false; // enable for edit, starts out disabled
                }
            }
        }
    });
}

// export function newHandleEdit(
//     itemId: string,
//     url: string,       // caller builds url
//     modal: FormDialog, // caller finds modal
//     itemLabel: string, // for legend text: "Edit Product", etc
// ) {
//     apiRequest('GET', url, null, {
//         onSuccess: (responseData) => {
//             modal.dataset.mode = 'edit';
//             modal.dataset.itemId = itemId;
//             // modal.dataset.subtype = subtype; does it break without this?
//             modal.showModal();
//             populateModalFields(modal, responseData.data);

//             const legend = modal.querySelector('legend');

//             modal.addEventListener('modal:cleanup', () => {
//                 if (legend?.dataset.originalText) {
//                     legend.textContent = legend.dataset.originalText;
//                     delete legend.dataset['originalText'];
//                 }
//             }, { once: true });

//             if (legend) {
//                 legend.dataset.originalText = legend.textContent;
//                 legend.textContent = `Edit ${itemLabel}`;
//             }
//         }
//     })
// }

/**
 * Prompts for confirmation, then deletes the item via API.
 * Removes the table row from DOM on success.
 */
async function handleDelete(menuContext: ContextObject['context']) {
    const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
    if (!confirmed) return;

    const { itemId, module, subtype } = menuContext;
    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('DELETE', url, null, {
        onSuccess: () => {
            makeToast(`${getSubtypeLabel(subtype)} deleted`, 'success');
            const itemRow = document.querySelector<HTMLElement>(`[data-item-id="${itemId}"]`);
            if (!itemRow) {
                console.warn('Error: could not find corresponding table row for removal.');
                return;
            }
            removeTableRow(itemRow);
        }
    });
}

// /**
//  * Adds product to shopping list or increments quantity if already present.
//  */
// function handleAddToShoppingList(menuContext: ContextObject['context']) {
//     const productId = (menuContext.subtype === 'transactions')
//         ? menuContext.productId
//         : menuContext.itemId;
//     const quantityWanted = 1;
//     const url = '/groceries/shopping-lists/items';
//     const data = { product_id: productId, quantity_wanted: quantityWanted };

//     apiRequest('POST', url, data, {
//         onSuccess: (responseData) => {
//             const { id, product_id, product_name } = responseData.data;
//             const existingLi = document.querySelector<HTMLLIElement>(`li[data-product-id="${productId}"]`);
//             if (existingLi) {
//                 const newQty = updateQty(existingLi);
//                 makeToast(`Updated ${product_name} quantity to ${newQty}`, 'success');
//                 return;
//             }

//             addShoppingListItemToDOM(id, product_id, product_name);
//             makeToast(`Added ${product_name} to shopping list`, 'success');
//         }
//     });
// }

function toggleTaskComplete(menuContext: ContextObject['context']) {
    const newIsDone = !menuContext.isDone;
    const completedAtUTC = getJSInstant();

    const data = {
        is_done: newIsDone,
        completed_at: completedAtUTC
    }
    const url = `/tasks/tasks/${menuContext.itemId}`;

    apiRequest('PATCH', url, data, {
        onSuccess: () => {
            const row = document.querySelector<HTMLElement>(`[data-item-id="${menuContext.itemId}"]`);
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

document.addEventListener('contextmenu', (e) => {
    if (e.ctrlKey) {
        const target = e.target as HTMLElement;
        const row = target.closest<HTMLElement>('.table-row');
        if (!row) {
            console.error('Missing table row');
            return;
        }
        const { itemId, module, subtype } = row.dataset;
        const productId = row?.dataset['productId'];
        const includeIsDone = module === 'tasks';
        const isDone = includeIsDone ? row.dataset['isDone'] === 'True' : undefined;

        if (!itemId || !module || !subtype) {
            console.error('Missing itemId/module/subtype attribute(s)');
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
                module,
                subtype: subtype as MenuOptionTypes,
                isDone: row?.dataset['isDone'] === 'True',
                ...(productId !== undefined ? { productId } : {}),
                ...(isDone !== undefined ? { isDone } : {})
                // productId: row?.dataset['productId']
            }
        };

        openMenu(triggerInfo);
    }
});

// document.addEventListener('keydown', (e) => {
//     if (e.key === 'Escape') {
//         closeMenu();
//     }
// });

// document.addEventListener('click', async (e) => {
    // const menu = document.querySelector('.context-menu');
    // const target = e.target as HTMLElement;

    // // if (menu && !menu.contains(target)) {
    // //     menu.remove();
    // //     return;
    // // }

    // const action = target.dataset['action'] as ActionType | undefined;

    // // // This is just an object where keys are strings and values are function references (not calling them, just storing them)
    // // const actionHandlers: Record<ActionType, (context: ContextObject['context']) => void> = {
    // //     'edit': handleEdit,
    // //     'delete': handleDelete,
    // //     'addToShoppingList': handleAddToShoppingList,
    // //     'toggleTaskComplete': toggleTaskComplete
    // // }

    // // With guard, call appropriate action & pass in menu.context
    // if (action && menu && actionHandlers[action]) {
    //     actionHandlers[action]((menu as any).context);
    //     // since handleX functions now lack access to menu element, we'll clean menu up here instead
    //     menu.remove();
    // }

//     if (target.matches('.js-table-options')) {
//         const button = target.closest<HTMLButtonElement>('.row-actions')!;
//         const row = target.closest<HTMLElement>('.table-row')!;
//         const { itemId, module, subtype } = row.dataset;

//         if (!itemId || !module || !subtype) {
//             console.error('Missing required data on row');
//             return;
//         }

//         const triggerInfo: DotsMenuTrigger =
//         {
//             type: 'dots',
//             rect: button.getBoundingClientRect(),
//             context: {
//                 itemId,
//                 module,
//                 subtype: subtype as MenuOptionTypes,
//                 isDone: row?.dataset['isDone'] === 'True',
//                 productId: row?.dataset['productId']
//             }
//         };

//         openMenu(triggerInfo);
//     }
// });

// function updateQty(existingLi: HTMLLIElement) {
//     const qtySpan = existingLi.querySelector('.item-qty');
//     if (!qtySpan) {
//         throw new Error('Quantity span not found');
//     }

//     const currentQty = parseInt(existingLi.dataset['quantityWanted'] ?? '0', 10);
//     const newQty = currentQty + 1;

//     qtySpan.textContent = String(newQty);
//     existingLi.dataset['quantityWanted'] = String(newQty);
//     return newQty;
// }

// function addShoppingListItemToDOM(itemId: string, productId: string, productName: string, quantity = 1) {
//     const ul = document.querySelector('.shopping-list');
//     if (!ul) {
//         throw new Error('Shopping list <ul> not found')
//     }

//     document.querySelector('#list-empty')?.remove(); // placeholder text

//     // Clone the contents of our template for the new li
//     const template = document.querySelector<HTMLTemplateElement>('#shoppinglist-item-template');
//     const fragment = template?.content.cloneNode(true) as DocumentFragment;

//     const li = fragment.querySelector('li');
//     if (!li) throw new Error('li not found in template');

//     const itemText = li.querySelector('.item-text');
//     const itemQty = li.querySelector('.item-qty');
//     if (!itemText || !itemQty) throw new Error('Template structure invalid');

//     itemText.textContent = productName;
//     itemQty.textContent = String(quantity);
//     li.dataset['itemId'] = itemId;
//     li.dataset['productId'] = productId;
//     li.dataset['quantityWanted'] = String(quantity);
//     ul.appendChild(li);
// }

// // Usage draft:
// contextMenu.create({
//     position: {x, y},
//     items: [
//         {
//             label: 'Delete',
//             action: () => {
//                 handleDelete(recipeId);
//             }
//         }
//     ]
// })

type ContextMenuItem = {
    label: string;
    action: () => void | Promise<void>;
}

type ContextMenuConfig = {
    position: {x: number, y: number};
    items: ContextMenuItem[];
}


// DRAFTING IMPROVED CONTEXT MENU 'API':
class ContextMenu {
    private isCreating = false;

    constructor() {
        this.setupGlobalListeners();
    }

    private setupGlobalListeners(): void {
        // close when clcking outside
        document.addEventListener('click', (e) => {
            if (this.isCreating) return;
            const menu = document.querySelector('.context-menu');
            const target = e.target;

            if (menu && !menu.contains(target)) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    create(config: ContextMenuConfig): void {
        // Close THIS menu
        this.close();
        this.isCreating = true; // prevent global click listener from auto-closing

        if (config.items.length === 0) {
            console.warn('ContextMenu: No items provided');
            this.isCreating = false;
            return;
        }

        // build menu from config
        const menu = document.createElement('ul');
        menu.classList.add('context-menu');

        // this time, caller just passes what they want :D
        const items = config.items;

        // build & append li els
        const menuEls = items.map(item => {
            const li = document.createElement('li');
            li.textContent = item.label; // was item.text now item.label

            // li.dataset.action = item.action; <-- now, instead of this approach
            // where we'd then look up the string action to dictate what to call
            // we'll feed the function to be exec'ed in as a callback,
            // and then attach a listener for said li to run said callback?
            li.addEventListener('click', async() => {
                // Note: await is only needed since some actions might be async
                // Case in point: Delete, since it shows the confirmationManager!
                try {
                    await item.action(); // exec stored func
                    this.close(); // exec internal close() method?
                } catch (error) {
                    console.error('ContextMenu action failed: ', error);
                    this.close();
                }
            });

            return li;
        });
        console.log("appending children...")
        menuEls.forEach(el => menu.appendChild(el));
        console.log(menu)
        // position menu
        // Since we're taking {x, y} directly from caller, this gets STUPID simple
        menu.style.left = config.position.x + 'px';
        menu.style.top = config.position.y + 'px';

        menu.style.display = 'block';
        console.log("appending menu to DOM...")
        // (menu as any).context = triggerInfo.context; <-- dont need! :D

        // append to body
        document.body.appendChild(menu);

        setTimeout(() => {
            this.isCreating = false;
        }, 0); // defer reset to next tick
    }

    close(): void {
        document.querySelector('.context-menu')?.remove();
    }
}

// export singleton
export const contextMenu = new ContextMenu();