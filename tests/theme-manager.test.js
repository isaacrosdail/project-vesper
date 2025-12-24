import { describe, it, expect, beforeEach } from 'bun:test';

import { getCookie } from '../app/static_src/js/shared/ui/theme-manager';

// Mock DOM
global.document = {
    cookie: '',
    querySelector: () => ({ value: null })
}


describe('getCookie', () => {
    beforeEach(() => {
        document.cookie = '';
    });

    it.each([
        { cookie: 'theme=light', name: 'theme', expected: 'light' },
        { cookie: 'theme=dark', name: 'theme', expected: 'dark' },
        { cookie: 'user=JohnTheRipper', name: 'theme', expected: null },
        { cookie: 'user=steve; theme=dark; session=abc', name: 'theme', expected: 'dark' },
    ])('returns $expected for "$cookie"', ({ cookie, name, expected }) => {
        document.cookie = cookie;
        expect(getCookie(name)).toBe(expected);
    });
})