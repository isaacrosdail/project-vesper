// Currently used to store/read cookie used for remembering dark/light theme setting

// This will work FOR NOW, but will need rewriting if we add any more cookies
function getCookie() {
    // Parse document.cookie, which is a plain string
    const cookie = document.cookie;

    // console.log(`Cookie read as: ${cookie}`);
    if (cookie.includes('theme=light')) {
        // set our form to light
        document.getElementById('theme').value = 'sun';
    } else if (cookie.includes('theme=dark')) {
        document.getElementById('theme').value = 'moon';
    } else {
        document.getElementById('theme').value = 'laptop';
    }

    // console.log(`Cookie parsed as: ${cookie}`);
}

// Also need to make this more robust
function setCookie() {
    const themeSetting = document.getElementById('theme').value;

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
    document.getElementById('theme').dispatchEvent(new Event('change'));
}

// Might need to make this more defensive (if element doesn't exist?)
document.addEventListener('DOMContentLoaded', () => {
    getCookie();            // Sync UI to the cookie
    applyThemeFromCookie(); // Apply the theme based on the value
    document.getElementById('theme').addEventListener('change', setCookie); // runs every time user picks new theme option
});