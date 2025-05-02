

// DELETE fetch request when clicking delete button
function deleteTableItem(module, itemId, subtype = "none") { // Default to none if not passed
    // Confirm delete
    if (!confirm(`Are you sure you want to delete this item?`)) return;

    // Construct URL dynamically based on module & itemId
    const url = `/${module}/${subtype}/${itemId}`

    // Fetch request to DELETE from db
    // Remember: DELETE requests do not need a body nor a .then(data => ..)
    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (response.ok) {
            // Handle success (eg., remove item from DOM)
            // Need to grab the itemRow to remove visually by finding the
            // custom data attribute data-task-id that matches our itemId
            const itemRow = document.querySelector(`[data-task-id="${itemId}"]`);
            if (itemRow) itemRow.remove();
        } else {
            console.error('Failed to delete item.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })
}

// Allows us to double-click a table cell and change its value
function editTableField(td, module, field, itemId, currentValue) {

    alert("Module: " + module + " Field: " + field + " itemId: " + itemId + " CurrentValue: " + currentValue);
    // Select <td> element to edit (based on passed field)
    //const td = this; // This refers to the clicked <td> element

    // Create an input element to replace text with
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentValue; // Sets current value as the input's value

    // Clear the cell & append the input field
    td.innerHTML = '';     // Clears the content of the dblclicked <td>
    td.appendChild(input); // Add the input field to the <td>

    // Focus on the input field for editing
    input.focus()

    // Listen for blur (click away) or enter to save the update
    // NOTE: Notice how we're adding another listener for hitting 'enter' below, which actually triggers blur
    // This is good: It isolates the "real change" portion of our logic to only being in one place
    // Imagine what might occur if the user hits enter AND clicks away in rapid succession? This helps avoid potential issues
    input.addEventListener('blur', function() {
        const td = this.parentElement; // 'this' refers to the input, so we get the parent <td>
        saveUpdatedField(module, field, itemId, input.value, td); // Pass td along with other data
    });

    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            input.blur(); // Trigger the blur event when Enter is pressed
        }
    });
}

// Handles the actual updating of the title
// 1. Get the value from the input field (represents our edited title)
// 2. Send it to the backend to update the task in the db
// 3. Once updated, replace the input with the new title and hide the input field
function saveUpdatedField(module, field, itemId, newValue, td) {

    // Construct URL dynamically based on given module
    const url = `/${module}/${itemId}`;

    // Prep data to send in body
    const data = {}
    data[field] = newValue; // Dynamically update the specific field
    alert(newValue)

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
function updateFieldDisplay(td, newValue) {
    // Remove the input element
    td.innerHTML = ''; // Clear the cell content

    // Append the new title
    const newFieldElement = document.createElement('span');
    newFieldElement.textContent = newValue; // Set the new field value
    td.appendChild(newFieldElement); // Append to the td
}

// Functions to run on page load
window.onload = () => {
    deleteTableRow();
}

// Make function(s) exportable for testing using Jest
module.exports = {
    updateFieldDisplay
    // export others if needed
}