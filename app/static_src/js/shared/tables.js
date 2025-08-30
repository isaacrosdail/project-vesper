// Bundler: Auto-runner => wires tables on DOMContentLoaded
// Functions for our tables, such as editTableField or deleteTableItem?
import { confirmationManager } from './ui/modal-manager.js';

/**
 * Creates table row for given item data for realtime modal entries
 * @param {Object} data - Return data from backend for new item
 */
export function makeTableRow(data) {
    const row = document.createElement("tr");

    // Build cells

}


// Currently used by tasks/dashboard & groceries/dashboard
// DELETE fetch request when clicking delete button
/**
 * Deletes item from DB when clicking delete button
 * @async
 * @param {string} module 
 * @param {number} itemId 
 * @param {string} subtype 
 * @returns 
 */
async function deleteTableItem(module, itemId, subtype = "none") {
    const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
    if (!confirmed) return;

    const url = `/${module}/${subtype}/${itemId}`;

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        });
        const responseData = await response.json();

        if (responseData.success) {
            const itemRow = document.querySelector(`[data-item-id="${itemId}"]`);
            if (itemRow) itemRow.remove();
        } else {
            console.error('Failed to delete item:', responseData.message);
        }
    } catch (error) {
        console.error('Fetch request failed: ', error);
    }
}

/** 
 * Handles inline editing for a given element.
 * @param {HTMLElement} element - Element whose contents are to be edited.
 * @param {string} module  - API module name for the update endpoint 
 * @param {string} field   - Field of table being updated
 * @param {string|number} itemId - ID of the item being updated 
 */
// Allows us to double-click a table cell and change its value
export function inlineEditElement(element, module, field, itemId, subtype) {
    // Call modal for this!! Maybe a new "confirm" modal macro :D -> alert(`Module: ${module}, Field: ${field}, ID: ${itemId}, Value: ${element.textContent}`);

    const originalText = element.textContent.trim();

    // Create input element
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'input-inline';
    input.value = originalText;
    input.size = originalText.length + 2;

    // Clear element & append input
    element.textContent = '';
    element.appendChild(input);
    input.focus();

    // Listen for blur (click away) or enter to save the update
    // TODO: NOTES: adding another listener for hitting 'enter' below which triggers blur
    // Isolates the "real change" portion of our logic to only being in one place
    //  what if the user hits enter AND clicks away in rapid succession?
    input.addEventListener('blur', function() {
        const newValue = input.value.trim();
        if (newValue !== '') {
            onSave(newValue, element);
        } else {
            element.textContent = originalText; // don't save if input is left empty
        }
        // saveUpdatedField(module, field, itemId, input.value, td, subtype); // Pass td along with other data
    });

    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            input.blur(); // Trigger the blur event when Enter is pressed
        }
    });
}

function editTableField(td, module, field, itemId, subtype) {
    inlineEditElement(td, {
        onSave: (val, el) => saveUpdatedField(td, module, field, itemId, val, el, subtype)
    });
}


// 1. Get the value from the input field (represents our edited title)
// 2. Send it to the backend to update the task in the db
// 3. Once updated, replace the input with the new title and hide the input field
/** 
 * Updates item's corresponding field with new table cell's value.
 * @param {string} module - API module name 
 * @param {string} field - Field name being updated
 * @param {string|number} itemId - ID of item to update
 * @param {string} newValue - New field value
 * @param {HTMLElement} td - Table cell element to update
 */
async function saveUpdatedField(module, field, itemId, newValue, td, subtype = "none") {

    // Construct URL & request body
    const url = `/${module}/${subtype}/${itemId}`;
    const data = {}
    data[field] = newValue;

    try {
        const response = await fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        const responseData = await response.json();

        if (responseData.success) {
            updateFieldDisplay(td, newValue);
        } else {
            console.error('Error updating field:', responseData.message);
        }
    } catch (error) {
        console.error('Error during fetch request:', error);
    }
}

// TODO: Stupid to have such a tiny function
// Another function to handle "clean up"
// Remove the input field & display the new title after changes
/**
 * Replaces input field with updated text display
 * @param {HTMLElement} td - Table cell containing the input
 * @param {string} newValue - Updated value to display
 */
export function updateFieldDisplay(td, newValue) {
    td.textContent = newValue;
}

/**
 * Handles delete button clicks using event delegation
 * @param {Event} e - Click event
 */
function handleDeleteClick(e) {
    // Handle clicks on delete button or its contents (SVG)
    if (e.target.matches('.delete-btn') || e.target.closest('.delete-btn')) {
        const row = e.target.closest('tr');
        if (!row) return;
        deleteTableItem(row.dataset.module, row.dataset.itemId, row.dataset.subtype)
    }
}

/**
 * Handles double-click editing on table cells
 * To use: Add class 'editable-cell' on given cell
 * @param {Event} e - Double-click event
 */
function handleEditClick(e) {
    if (e.target.classList.contains('editable-cell')) {
        const td = e.target;
        editTableField(td, td.dataset.module, td.dataset.field, td.dataset.itemId, td.dataset.subtype)
    }
}

// TODO: Move to...somewhere else! Implement real options here
function handleCustomContextMenu(e) {
    if (e.target.closest('.table-row')) {
        // Accessing OR making our custom context menu
        let menu = document.querySelector('.context-menu');
        if (!menu) {
            menu = document.createElement('ul');
            const menuItems = ['Edit', 'Delete', 'Close'];
        
            const menuElements = menuItems.map(item => {
                const menuItem = document.createElement('li');
                menuItem.textContent = item;
                return menuItem;
            });
            menuElements.forEach(element => menu.appendChild(element));
            menu.classList.add('context-menu');
        }

        // Position menu at cursor
        menu.style.left = e.clientX + 'px';
        menu.style.top = e.clientY + 'px';
        menu.style.display = 'block';
        document.body.appendChild(menu); // createElement adds to JS mem, appendChild to add to DOM
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', handleDeleteClick);
    document.addEventListener('dblclick', handleEditClick);
    document.addEventListener('contextmenu', (e) => {
        if (e.ctrlKey) {
            console.log('shift pressed!');
            e.preventDefault();
            handleCustomContextMenu(e); // TODO?: Pull our context menu handling into some kind of global.js
        }
    });

    // Click away for context menu close
    document.addEventListener('click', (e) => {
        if (!e.target.matches('.context-menu')) {
            const menu = document.querySelector('.context-menu');
            menu?.remove();
        }
    });
});