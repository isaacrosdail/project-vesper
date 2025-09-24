import { makeToast } from './toast.js';
import { apiRequest } from '../services/api.js';

const menuItems = ['Edit', 'Delete'];
const menuItemsGroceries = ['Add to shopping list'];

// TODO: Properly implement & wire into tables.js functionalities
function createContextMenu(e) {
    const row = e.target.closest('.table-row');
    if (!row) return;

    // Accessing OR making our custom context menu
    let menu = document.querySelector('.context-menu');
    if (!menu) {
        menu = document.createElement('ul');

        // Start with copy of the base items
        // spread operator here [...menuItems] makes a shallow copy
        let items = [...menuItems];

        // If clicked row is from the Transactions table, extend the list
        // Append our shopping list option if it's the transactions table
        // so: items = ['Edit', 'Delete', 'Add to shopping list']
        if (row.dataset.subtype === 'transaction') {
            items = [...items, ...menuItemsGroceries];
        }
    
        // Now we map over 'items' to render <li> elements
        const menuElements = items.map(label => {
            const li = document.createElement('li');
            li.textContent = label;
            return li;
        });
        menuElements.forEach(element => menu.appendChild(element));
        menu.classList.add('context-menu');
    }

    // Position menu at cursor
    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    menu.style.display = 'block';

    // Bind data to menu for retrieval elsewhere without relying on DOM traversal + relationships
    menu.context = {
        itemId: row.dataset.itemId,
        name: row.querySelector('td:nth-child(2)').textContent,
        subtype: row.dataset.subtype
    }
    document.body.appendChild(menu);
}

document.addEventListener('contextmenu', (e) => {
    if (e.ctrlKey) {
        e.preventDefault();
        createContextMenu(e); // TODO?: Pull our context menu handling into some kind of global.js
    }
});

document.addEventListener('click', async (e) => {
    const menu = document.querySelector('.context-menu');

    // TODO: Should rewrite this to separate concerns but have got to stop committing to rewrites for now
    if (e.target.textContent === 'Add to shopping list') {
        const productId = menu.context.itemId;
        const productName = menu.context.name;
        const quantity = 1;
        menu?.remove();

        // Actually send to backend:
        const url = '/groceries/shopping-list/items';
        const data = { product_id: productId };

        apiRequest('POST', url, () => {
            const existingLi = document.querySelector(`li[data-item-id="${productId}"]`);
            if (existingLi) {
                const newQty = updateQty(existingLi);
                makeToast(`Updated ${productName} quantity to ${newQty}`, 'success');
                return;
            }
            addShoppingListItemToDOM(productId, productName);
        }, data);
    }

    else if (!e.target.matches('.context-menu')) {
        menu?.remove();
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

function addShoppingListItemToDOM(productId, productName, quantity = 1) {
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
    liEl.dataset.itemId = productId;
    liEl.dataset.quantityWanted = quantity;
    ul.appendChild(liEl);
}