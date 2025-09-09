// Runs on DOMContentLoaded, syncs cookie + <select>, applies theme
import { between } from '../strings.js';

const themeMap = {
    sun: 'light',
    moon: 'dark',
    laptop: 'system'
}
const reverseThemeMap = {
    light: 'sun',
    dark: 'moon',
    system: 'laptop'
}

function getCookie() {
    const themeSelect = document.querySelector('#theme');
    if (!themeSelect) return;

    const cookie = document.cookie;
    const themeValue = between(cookie, "=", ";");

    themeSelect.value = reverseThemeMap[themeValue] ?? "laptop";
}


function setCookie() {
    const themeSelect = document.querySelector('#theme');
    if (!themeSelect) return;

    const themeSetting = themeSelect.value;
    const cookieVal = themeMap[themeSetting] ?? "system";

    document.cookie = `theme=${cookieVal}; path=/; max-age=31536000`;
    console.log(`Cookie set as: ${document.cookie}`)
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