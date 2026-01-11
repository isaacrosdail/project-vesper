// For frontend validation. (Name might be bad, idk)

/**
 * 'u' flag at end enables Unicode mode
 * p{L} = any Unicode letter
 * p{N} = any Unicode number
 * _ underscore
 */
const USERNAME_RE = /^[\p{L}\p{N}_]+$/u;


// Track whether we've triggered validation already for a field?
let track = {}

// Rules:
// 1. Between 3-30 chars
// 2. 
/**
 * Validates username string. Returns `null` when the string was valid, or the error string when invalid.
 * @param username 
 * @returns 
 */
function validateUsername(username: string): string | null {
    if (username.length < 3 || username.length > 30) {
        return 'Username must be 3-30 characters';
    }
    if (!USERNAME_RE.test(username)) {
        return 'Username can only contain letters, numbers, & underscores.'
    }

    return null;
}

// TESTING/DRAFTING:
if (document.querySelector('[data-page="auth.login"], [data-page="auth.register"]')) {
    
    // Listener for username field for blur to trigger validation
    const usernameField = document.querySelector<HTMLInputElement>('#username');
    usernameField?.addEventListener('blur', () => {
        const field = 'username';

        const value = usernameField.value.trim();
        // CASE: Empty -> strip any validity to reset
        if (value === '') {
            track.username = false; // set username field to "untouched"
            usernameField.classList.remove('valid');
            usernameField.classList.remove('invalid');
            return;
        };

        const result = validateUsername(value);

        // CASE A: Valid -> we receive null
        // CASE B: Invalid -> we receive a string

        // Toggle classes & set 'dirty' status of field
        usernameField.classList.toggle('invalid', result !== null);
        usernameField.classList.toggle('valid', result === null);
        track.username = (result === null);

        // If invalid, we need to update error-inline div text or create + setup.
        // VALID
        if (result === null) {
            console.log(`Valid, removing error-inline-${field}`)
            const errorBox = document.querySelector(`.error-inline-${field}`);
            errorBox?.remove();
        }
        // INVALID
        else {
            // Check for error-inline div
            const errorBox = document.querySelector(`.error-inline-${field}`);
            if (errorBox) {
                // Already there, just update
                console.log(`Invalid, updating error-inline-${field}`)
                errorBox.textContent = result;
            } else {
                // Doesn't exist -> make and setup
                console.log(`Invalid, creating error-inline-${field}`)
                const newThing = document.createElement('div');
                newThing.classList.add(`error-inline-${field}`);
                newThing.textContent = result;
                const fieldGroup = usernameField.closest('div');
                fieldGroup.appendChild(newThing)
            }
        }
    });
}