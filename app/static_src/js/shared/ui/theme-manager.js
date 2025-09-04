// Runs on DOMContentLoaded, syncs cookie + <select>, applies theme

const themeMap = {
    sun: 'light',
    moon: 'dark',
}
const reverseThemeMap = {
    light: 'sun',
    dark: 'moon'
}

function getCookie() {
    const cookie = document.cookie;
    const themeSelect = document.querySelector('#theme');
    if (!themeSelect) return;

    themeSelect.value = ``

    if (cookie.includes('theme=light')) {
        themeSelect.value = 'sun';
    } else if (cookie.includes('theme=dark')) {
        themeSelect.value = 'moon';
    } else {
        themeSelect.value = 'laptop';
    }
}


function setCookie() {
    const themeSetting = document.querySelector('#theme').value;

    console.log(`Theme detected from form as: ${themeSetting}`);

    document.cookie = `theme=${themeMap[themeSetting] || system }; path=/; max-age=31536000`;

    console.log(`Cookie set/saved as: ${document.cookie}`);
}

function applyThemeFromCookie() {
    document.querySelector('#theme').dispatchEvent(new Event('change'));
}

// Might need to make this more defensive (if element doesn't exist?)
document.addEventListener('DOMContentLoaded', () => {
    getCookie();            // Sync UI to the cookie
    applyThemeFromCookie(); // Apply the theme based on the value
    document.querySelector('#theme').addEventListener('change', setCookie); // runs every time user picks new theme option
});