// TODO: NOTES: Bundler => auto-runner
// Runs on DOMContentLoaded, syncs cookie + <select>, applies theme

// This will work FOR NOW, but will need rewriting if we add any more cookies
function getCookie() {
    // Parse document.cookie, which is a plain string
    const cookie = document.cookie;
    const themeSelect = document.querySelector('#theme');
    if (!themeSelect) return;

    if (cookie.includes('theme=light')) {
        // set our form to light
        themeSelect.value = 'sun';
    } else if (cookie.includes('theme=dark')) {
        themeSelect.value = 'moon';
    } else {
        themeSelect.value = 'laptop';
    }
}

// Also need to make this more robust
function setCookie() {
    const themeSetting = document.querySelector('#theme').value;

    // console.log(`Theme detected from form as: ${themeSetting}`);
    if (themeSetting === 'sun') {
        // set cookie to 'theme=light'
        // so key-value pair, then path=/ makes it accessible to all routes/pages
        // and max-age=31536000 (optional) time in seconds = 1 year till it expires
        document.cookie = "theme=light; path=/; max-age=31536000"
    } else if (themeSetting === 'moon') {
        // set cookie to 'theme=dark'
        document.cookie = "theme=dark; path=/; max-age=31536000"
    } else {
        // if no cookie
        document.cookie = "theme=system; path=/; max-age=31536000"
    }

    // console.log(`Cookie set/saved as: ${document.cookie}`);
}

function applyThemeFromCookie() {
    // After sync, force CSS to re-evaluate
    // TODO: Study use cases of dispatchEvent
    document.querySelector('#theme').dispatchEvent(new Event('change'));
}

// Might need to make this more defensive (if element doesn't exist?)
document.addEventListener('DOMContentLoaded', () => {
    getCookie();            // Sync UI to the cookie
    applyThemeFromCookie(); // Apply the theme based on the value
    document.querySelector('#theme').addEventListener('change', setCookie); // runs every time user picks new theme option
});