
// Functions for our tables, such as editTableField or deleteTableItem?


// Event listener to listen for dblclick event on td's with class "editable-cell"
document.addEventListener('dblclick', function(event) {
    
    if (event.target.classList.contains('editable-cell')) {
        const td = event.target;
        editTableField(td, td.dataset.module, td.dataset.field, td.dataset.itemId)
    }
});


/** 
 * Inline table cell editing. Allows double-clicking table cells to edit values in place.
 * @param {HTMLElement} td - The table cell element
 * @param {string} module - API module name for the update endpoint 
 * @param {string} field 
 * @param {string|number} itemId - ID of the item being updated 
 */
// Allows us to double-click a table cell and change its value
function editTableField(td, module, field, itemId) {

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
        saveUpdatedField(module, field, itemId, input.value, td); // Pass td along with other data
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
function saveUpdatedField(module, field, itemId, newValue, td, subtype = "none") {

    // Construct URL dynamically based on given module
    const url = `/${module}/${subtype}/${itemId}`;

    // Create request body with dynamic field name
    const data = {}
    data[field] = newValue;

    // Send PATCH request via fetch with field data
    fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Send the updated field and value
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateFieldDisplay(td, newValue)
            console.log(`${field} updated to:`, newValue);
        } else {
            console.error('Error updating field:', data.message);
        }
    })
    .catch(error => {
        console.error('Error during fetch request:', error);
    });
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

// Functions to run on page load
window.onload = () => {
    // Useful for event listeners, UI/form initialization, dynamic content loading (like for a weather widget?)
}

// Make function(s) exportable for testing using Jest
if (typeof module !== 'undefined') {
    module.exports = { updateFieldDisplay };
}