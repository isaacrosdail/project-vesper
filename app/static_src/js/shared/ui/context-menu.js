import { makeToast } from './toast.js';
import { apiRequest } from '../services/api.js';

const menuItems = ['Edit', 'Delete'];
const menuItemsGroceries = ['Add to shopping list'];

// TODO: Properly implement & wire into tables.js functionalities
function createContextMenu(e) {
    const row = e.target.closest('.table-row');
    if (row) {
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
        row.appendChild(menu); // Append to actual row now to enable easy use of .closest
    }
}

document.addEventListener('contextmenu', (e) => {
    if (e.ctrlKey) {
        e.preventDefault();
        createContextMenu(e); // TODO?: Pull our context menu handling into some kind of global.js
    }
});

document.addEventListener('click', async (e) => {
    const menu = document.querySelector('.context-menu');
    // Handle context menu <li> clicks
    if (e.target.textContent === 'Add to shopping list') {
        const row = e.target.closest('.table-row');
        // td:nth-child(2) => 2nd column (ie, our product name :D)
        const productName = row.querySelector('td:nth-child(2)').textContent;
        const productId = row.dataset.itemId;
        makeToast(`Adding ${productName} (ID: ${productId}) to shopping list!`, 'success', 4000)
        menu?.remove();

        // Actually send to backend:
        const url = '/groceries/shopping-list/items';
        const data = { product_id: productId };

        apiRequest('POST', url, () => {
            makeToast('Product added successfully!', 'success');
        }, data);
    }
    // Click away for context menu close
    else if (!e.target.matches('.context-menu')) {
        menu?.remove();
    }
});