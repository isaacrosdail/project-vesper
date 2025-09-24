import { describe, it, expect, beforeEach } from 'bun:test';

// Mock DOM
global.document = {
    cookie: '',
    querySelector: () => ({ value: null })
}

function getCookie() {
    // Parse document.cookie, which is a plain string
    const cookie = document.cookie;
    const themeSelect = document.querySelector('.theme');

    if (cookie.includes('theme=light')) {
        // set our form to light
        themeSelect.value = 'sun';
    } else if (cookie.includes('theme=dark')) {
        themeSelect.value = 'moon';
    } else {
        themeSelect.value = 'laptop';
    }
}

describe('getCookie', () => {
    let mockElement;

    beforeEach(() => {
        mockElement = { value: null };
        document.querySelector = () => mockElement;
    });

    it('sets sun for light theme', () => {
        document.cookie = 'theme=light';
        getCookie();
        expect(mockElement.value).toBe('sun');
    });
    it('sets moon for dark theme', () => {
        document.cookie = 'theme=dark';
        getCookie();
        expect(mockElement.value).toBe('moon');
    });
    it('sets laptop as default', () => {
        document.cookie = 'theme=system';
        getCookie();
        expect(mockElement.value).toBe('laptop');
    });
    it('handles multiple cookies properly', () => {
        document.cookie = 'user=steve; theme=dark; session=fooBar';
        getCookie();
        expect(mockElement.value).toBe('moon');
    });
    it('handles missing element gracefully', () => {
        document.querySelector = () => null;
        document.cookie = 'theme=light';
        expect(() => getCookie()).not.toThrow();
    });
})