/**
 * Theme toggle handling.
 * 
 * Inline script in base.html sets initial data-theme from cookie (prevents flash)
 * 
 */

import { required } from "../dom";

const THEME_COOKIE_LIFETIME_MS = 365 * 24 * 60 * 60 * 1000;

const themeToggle = required(document.querySelector<HTMLInputElement>('#theme-toggle'), '#theme-toggle');

function applyTheme(theme: 'light' | 'dark') {
    themeToggle.checked = theme === 'light';
    document.documentElement.dataset['theme'] = theme;
}

async function initTheme() {
    const stored = (await cookieStore.get('theme'))?.value;
    const theme = stored === 'light' || stored === 'dark'
        ? stored
        : window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
    applyTheme(theme);
}

themeToggle.addEventListener('change', () => {
    const theme = themeToggle.checked ? 'light' : 'dark';
    cookieStore.set({ name: 'theme', value: theme, expires: Date.now() + THEME_COOKIE_LIFETIME_MS });
    applyTheme(theme);
});

initTheme();
