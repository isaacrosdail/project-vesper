// Currently used by tasks/dashboard & groceries/dashboard
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
            const itemRow = document.querySelector(`[data-item-id="${itemId}"]`);
            if (itemRow) itemRow.remove();
        } else {
            console.error('Failed to delete item.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })
}