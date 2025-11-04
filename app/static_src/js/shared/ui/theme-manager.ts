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
    const themeSelect = document.querySelector('#theme') as HTMLSelectElement;
    if (!themeSelect) return;

    const cookie = document.cookie;
    // const themeValue = between(cookie, "=", ";") as 'light' | 'dark' | 'system';

    // themeSelect.value = reverseThemeMap[themeValue] ?? "laptop";
    // vs.
    const themeValue = between(cookie, "=", ";");

    // 'as keyof typeof reverseThemeMap' part tells TypeScript "this string is definitely one of those three keys."
    themeSelect.value = reverseThemeMap[themeValue as keyof typeof reverseThemeMap] ?? "laptop";
}


function setCookie() {
    const themeSelect = document.querySelector('#theme') as HTMLSelectElement;
    if (!themeSelect) return;

    const themeSetting = themeSelect.value;
    const cookieVal = themeMap[themeSetting as keyof typeof themeMap] ?? "system";

    document.cookie = `theme=${cookieVal}; path=/; max-age=31536000`;
}

function applyThemeFromCookie() {
    document.querySelector('#theme')!.dispatchEvent(new Event('change'));
}

// Might need to make this more defensive (if element doesn't exist?)
document.addEventListener('DOMContentLoaded', () => {
    getCookie();            // Sync UI to the cookie
    applyThemeFromCookie(); // Apply the theme based on the value
    document.querySelector('#theme')!.addEventListener('change', setCookie); // runs every time user picks new theme option
});