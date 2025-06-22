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