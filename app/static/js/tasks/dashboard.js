
function editTableTask(module, field, itemId, currentValue) {
    
    // Get the task title
    const taskTitle = td.querySelector('.task-title').textContent;

    // Create an input element to replace text with
    const input = document.createElement('input');
    input.type = 'text';
    input.value = taskTitle; // Sets the current title as the input's value

    // Clear the cell & append the input field
    td.innerHTML = '';     // Clears the content of the dblclicked <td>
    td.appendChild(input); // Add the input field now

    // Focus on the input field for editing
    input.focus()

    // Listen for blur (click away) or enter to save the update
    // NOTE: Notice how we're adding another listener for hitting 'enter' below, which actually triggers blur
    // This is good: It isolates the "real change" portion of our logic to only being in one place
    // Imagine what might occur if the user hits enter AND clicks away in rapid succession? This helps avoid potential issues
    input.addEventListener('blur', function() {
        saveUpdatedTitle(taskId, td, input.value);
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
function saveUpdatedTitle(taskId, td, newTitle) {
    // fetch() request to PATCH via update_task
    fetch(`/update_task/${taskId}`, {
        method: "PATCH",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "title": newTitle }) // Send the new title to the server
    })
    .then(response => response.json())
    .then(data => {
        if (data.succes) {
            updateTaskTitleDisplay(newTitle)
            console.log('Task title updated to:', data);
        } else {
            console.error('Failed to update task.');
        }
    })
    .catch(error => {
        console.error('Error updating task title:', error);
    });
}

// Another function to handle "clean up"
// Remove the input field & display the new title after changes
function updateTaskTitleDisplay(newTitle) {
    // Remove the input element
    td.innerHTML = ''; // Clear the cell content

    // Append the new title
    const newTitleElement = document.createElement('span');
    newTitleElement.textContent = newTitle; // Set the new title
    td.appendChild(newTitleElement); // Append to the td
}