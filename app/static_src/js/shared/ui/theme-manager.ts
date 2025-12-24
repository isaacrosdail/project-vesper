/**
 * Theme toggle handling.
 * 
 * Setup:
 * - Inline script in base.html sets initial data-theme from cookie (prevents flash)
 * - This file syncs the <select> dropdown to cookie on load
 * - Change listener handles user interactions (updates cookie & data-theme)
 */

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

/**
 * Returns value of a cookie by key name.
 * 
 * @param name - Cookie name to search for
 * @returns Cookie value or null if not found
 */
export function getCookie(name: string): string | null {
    const cookies = document.cookie.split('; ');
    const targetCookie = cookies.find(x => x.startsWith(`${name}=`));
    if (!targetCookie) return null;

    const [_key, value] = targetCookie.split('=');
    return value ?? null;
}

/**
 * Writes a cookie with configurable expiration.
 * @param name - Cookie name
 * @param value - Value to store
 * @param maxAge - Expiration in seconds (default: 1 year)
 * @example setCookie('theme', 'dark')
 */
function setCookie(name: string, value: string, maxAge: number = 31536000): void {
    document.cookie = `${name}=${value}; path=/; max-age=${maxAge}`;
}

/**
 * Initializes theme system on page load.
 * 
 * Attaches change listener to sync cookie + apply theme
 * Syncs dropdown to saved cookie value (falls back to 'system')
 * Triggers change to ensure cookie is written on first visit.
 */
document.addEventListener('DOMContentLoaded', () => {
    const themeSelect = document.querySelector<HTMLSelectElement>('#theme')!;

    themeSelect.addEventListener('change', () => {
        const cookieValue = themeMap[themeSelect.value];
        setCookie('theme', cookieValue);
        document.documentElement.dataset['theme'] = cookieValue;
    });

    const savedTheme = getCookie('theme') ?? 'system';
    themeSelect.value = reverseThemeMap[savedTheme as keyof typeof reverseThemeMap];
    themeSelect.dispatchEvent(new Event('change'));
});