
// Functions for our tables, such as editTableField or deleteTableItem?

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
async function deleteTableItem(module, itemId, subtype = "none") { // Default to none if not passed
    // Confirm delete
    if (!confirm(`Are you sure you want to delete this item?`)) return;

    // Construct URL dynamically based on module & itemId
    const url = `/${module}/${subtype}/${itemId}`

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        });
        const responseData = await response.json();

        if (responseData.success) {
            // update DOM
            const itemRow = document.querySelector(`[data-item-id="${itemId}"]`);
            if (itemRow) itemRow.remove();
        } else {
            // error from Flask route
            console.error('Failed to delete item:', responseData.message);
        }
    } catch (error) {
        // If fetch request as a whole failed (network/server errors)
        console.error('Fetch request failed: ', error);
    }
}

/** 
 * Inline table cell editing. Allows double-clicking table cells to edit values in place.
 * @param {HTMLElement} td - The table cell element
 * @param {string} module  - API module name for the update endpoint 
 * @param {string} field   - Field of table being updated
 * @param {string|number} itemId - ID of the item being updated 
 */
// Allows us to double-click a table cell and change its value
function editTableField(td, module, field, itemId, subtype) {

    // Debug alert
    // alert(`Module: ${module}, Field: ${field}, ID: ${itemId}, Value: ${td.textContent}`);

    // Create an input element to replace cell content
    const input = document.createElement('input');
    input.type = 'text';
    input.value = td.textContent;

    // Clear the cell & append the input field
    td.innerHTML = '';      // Clears the content of the dblclicked <td>
    td.appendChild(input);  // Add the input field to the <td>
    input.focus()           // Focus on the input field for editing

    // Listen for blur (click away) or enter to save the update
    // NOTE: Notice how we're adding another listener for hitting 'enter' below, which actually triggers blur
    // This is good: It isolates the "real change" portion of our logic to only being in one place
    // Imagine what might occur if the user hits enter AND clicks away in rapid succession? This helps avoid potential issues
    input.addEventListener('blur', function() {
        const td = this.parentElement; // 'this' = input element, so here we get the parent <td>
        saveUpdatedField(module, field, itemId, input.value, td, subtype); // Pass td along with other data
    });

    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            input.blur(); // Trigger the blur event when Enter is pressed
        }
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

    // Construct URL dynamically based on given module
    const url = `/${module}/${subtype}/${itemId}`;

    // Create request body with dynamic field name
    const data = {}
    data[field] = newValue;

    // Converting fetch to modern async variant
    try {
        // 1. Replaces our previous fetch() and first .then
        const response = await fetch(url, {
            // Send PATCH request with field data
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data) // Send updated field & value
        });

        // 2. Replaces our .then(data => ..)
        const responseData = await response.json();

        // 3. Handles our if/else within the .then(data => ...) portion from before
        if (responseData.success) {
            // update display field + console.log
            updateFieldDisplay(td, newValue);
            //console.log(`${field} updated to:`, newValue);
        } else {
            // console.error with data.message
            console.error('Error updating field:', responseData.message);
        }
    } catch (error) {
        // replaces our .catch() - handles fetch/network errors
        console.error('Error during fetch request:', error);
    }
}

// Another function to handle "clean up"
// Remove the input field & display the new title after changes
/**
 * Replaces input field with updated text display
 * @param {HTMLElement} td - Table cell containing the input
 * @param {string} newValue - Updated value to display
 */
function updateFieldDisplay(td, newValue) {
    td.textContent = newValue;
}

/**
 * Handles delete button clicks using event delegation
 * @param {Event} e - Click event
 */
function handleDeleteClick(e) {
    // debug
    // console.log('Clicked:', e.target)

    // Click the delete button OR anything inside it (ie, our SVG)
    if (e.target.matches('.delete-btn') || e.target.closest('.delete-btn')) {
        // This runs when ANY delete button in the table is clicked
        // Since e.target is the delete button we clicked, we need to get to the tr for the module, id, & subtype info
        const row = e.target.closest('tr'); // this walks up the DOM tree to find the first parent element that matches the selector, ie 'tr'
        deleteTableItem(row.dataset.module, row.dataset.itemId, row.dataset.subtype)
    }
}

// Event listener to listen for dblclick event on td's with class "editable-cell"
/**
 * Handles double-click editing on table cells
 * @param {Event} e - Double-click event
 */
function handleEditClick(e) {
    if (e.target.classList.contains('editable-cell')) {
        const td = e.target;
        editTableField(td, td.dataset.module, td.dataset.field, td.dataset.itemId, td.dataset.subtype)
    }
}

function handleContextMenu(e) {
    if (e.target.closest('.table-row')) {
        e.preventDefault(); // Prevents appearance of default browser context menu?

        // Accessing OR making our custom context menu
        let menu = document.querySelector('.context-menu');
        if (!menu) {
            menu = document.createElement('ul');
            const menuItems = ['Edit', 'Delete', 'Close'];
        
            for (const item of menuItems) {
                const menuItem = document.createElement('li');
                menuItem.textContent = item; // set string from array as textContent property for element
                menu.appendChild(menuItem);
            }
            menu.classList.add('context-menu'); // add class (for CSS)
        }

        // Position menu at cursor
        menu.style.left = e.clientX + 'px';
        menu.style.top = e.clientY + 'px';
        menu.style.display = 'block';
        document.body.appendChild(menu); // Now we made our HTML element in JS memory, but need to add it to the page!
    }
}
// Fires when the HTML is fully parsed & DOM tree is built
// All HTML elements exist & can be selected
// Images, stylesheets, fonts might still be loading
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', handleDeleteClick);
    document.addEventListener('dblclick', handleEditClick);
    document.addEventListener('contextmenu', handleContextMenu); // TODO?: Pull our context menu handling into some kind of global.js

    // Listener for click away (to remove context menu)
    document.addEventListener('click', (e) => {
        if (!e.target.matches('.context-menu')) {
            const menu = document.querySelector('.context-menu');
            // Below is functionally similar to: document.body.removeChild(menu);
            menu?.remove();
        }
    });
});

// Functions to run on page load
// Fires later/slower => Once EVERYTHING is completely loaded
//  All HTML elements, all images/CSS/fonts/Externala resources
window.onload = () => {
    // Useful for event listeners, UI/form initialization
}

// Make function(s) exportable for testing using Jest
if (typeof module !== 'undefined') {
    module.exports = { updateFieldDisplay };
}