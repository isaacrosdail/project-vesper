
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

    // Now need to break out original PATCH request into two different requests.
    if (checkbox.checked) {
        // POST a new HabitCompletion record
        fetch(`/habits/${habitId}/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        // Awaits Flask's response; .json() converts it from raw response to usable JS obj ( {success: true })
        .then(response => {
            if (response.ok) {
                // Immediately apply strikethrough effect
                const textSpan = checkbox.nextElementSibling; // Grabs the span right after checkbox element
                if (textSpan) {
                    textSpan.classList.add("line-through", "text-gray-400");
                }
            }
        })
        // Error Catching (eg, network fails, Flask throws error) // Could later show a popup, retry, etc.
        // If network fails or Flask throws an error, you'll see it here
        .catch(error => {
            console.error('Error marking habit complete:', error);
        });
    } else {
        // DELETE the existing HabitCompletion record
        fetch(`/habits/${habitId}/completions/today`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        // Awaits Flask's response; .json() converts it from raw response to usable JS obj ( {success: true })
        .then(response => {
            if (response.ok) {
                // Immediately remove strikethrough effect
                const textSpan = checkbox.nextElementSibling; // Grabs the span right after checkbox element
                if (textSpan) {
                    textSpan.classList.remove("line-through", "text-gray-400");
                }
            }
        })
        .catch(error => {
            console.error('Error un-marking habit complete:', error);
        });
        }
}




// Beginning work for function to update time display on homepage in real-time w/o reload
function getCurrentTimeString() {
    let date = new Date(); // First we need to get today's date obj
    let hours = date.getHours();
    let minutes = date.getMinutes();
    
    // Pad times
    let paddedHours = hours.toString().padStart(2, '0');
    let paddedMinutes = minutes.toString().padStart(2, '0');
    // Template literal to conjoin
    let timeString = `${paddedHours}:${paddedMinutes}`;
    
    return timeString;
}

function updateClock() {
    // Get the element by id
    let timeDisplay = document.getElementById("time-display");
    // use getCurrentTimeString to call that and inject that value
    timeDisplay.textContent = getCurrentTimeString();
}

window.onload = () => {
    setInterval(updateClock, 30 * 1000); // 30 seconds
    updateClock();
}