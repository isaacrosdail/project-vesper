
// Variable for critical-task text input
let criticalTask;

// Constant for critical-task-submit button
const criticalTaskSubmitBtn = document.getElementById("critical-task-submit");
// Variables for critical-task-text and critical-task-result
let criticalTaskText = document.getElementById("critical-task-text");
let criticalTaskResult = document.getElementById("critical-task-result");

// Want the value of critical-task-text to become critical-task-result, then hide critical-task-edit again
criticalTaskSubmitBtn.onclick = () => {
    // Get critical-task text from input using element id
    criticalTask = document.getElementById("critical-task-text").value;
    // Set critical-task-result = critical-task
    document.getElementById("critical-task-result-text").textContent = criticalTask;
    // And hide the input text box and submit button
    document.getElementById("critical-task-result").classList.remove("hidden");
    document.getElementById("critical-task-edit").classList.add("hidden");
}

function enableEdit() {
    document.getElementById("critical-task-result").classList.add("hidden");
    document.getElementById("critical-task-edit").classList.remove("hidden");
    document.getElementById("critical-task-text").focus();
}

// Function that activates when checkbox for anchor habits are checked, indicating completion
// Function will then use fetch() to trigger POST to tell Flask to update DB
function markHabitComplete(checkbox, habitId) {
    // Fetch sends a request to flask server
    // POSTing to a dynamic URL like /complete_habit/7
    // Translation: "Hey, mark habit 7 as complete"

    // If .checked == True  -> user just checked it
    // If .checked == False -> user just un-checked it
    const isDone = checkbox.checked;

    // Fetch PATCH request to update is_done
    fetch(`/tasks/${habitId}`, { 
        // Request config
        // Making a POST request | Set Content-Type to application/json even if 
        // we're not sending a body (good habit)
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json' // Good habit to set this, research why later
        },
        body: JSON.stringify({ is_done: isDone })
    })
    // Awaits Flask's response; .json() converts it from raw response to usable JS obj ( {success: true })
    .then(response => response.json())
    // Once you have that response, do something - here, just log it
    // Later, could update the UI, disable the checkbox, add animation, etc
    .then(data => {
        console.log('Anchor habit (task) marked complete:', data);
        // Optional, update UI here later
    })
    // Error Catching (eg, network fails, Flask throws error) // Could later show a popup, retry, etc.
    // If network fails or Flask throws an error, you'll see it here
    .catch(error => {
        console.error('Error marking anchor habit (task) complete:', error);
    });
}