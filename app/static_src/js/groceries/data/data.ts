
import { mount } from 'svelte';
import { required } from '../../shared/dom';
import DataPage from './DataPage.svelte';
import type { Action } from 'svelte/action';


export const priceMask: Action<HTMLInputElement> = (input) => {
    const centsOf = () => Math.round(Number(input.value || '0') * 100);

    function commit(cents: number) {
        input.value = cents === 0 ? '' : (cents / 100).toFixed(2);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function onKeydown(e: KeyboardEvent) {
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        if (/^\d$/.test(e.key)) {
            e.preventDefault();
            commit(centsOf() * 10 + Number(e.key));
        } else if (e.key === 'Backspace') {
            e.preventDefault();
            commit(Math.floor(centsOf() / 10));
        } else if (e.key.length === 1) {
            e.preventDefault(); // letters, '.', ','
        }
    }

    function onPaste(e: ClipboardEvent) {
        e.preventDefault();
        const digits = (e.clipboardData?.getData('text') ?? '').replace(/\D/g, '');
        commit(Number(String(centsOf()) + digits));
    }

    input.addEventListener('keydown', onKeydown);
    input.addEventListener('paste', onPaste);
    return {
        destroy() {
            input.removeEventListener('keydown', onKeydown);
            input.removeEventListener('paste', onPaste);
        },
    };
};

export async function init() {

    mount(DataPage, {
        target: required(document.querySelector('#data-page-root'), '#data-page-root')
    });

    // // Hide default browser display, make button pull that up
    // els.csvImportBtn.addEventListener('click', () => els.csvFileInput.click())
    // els.csvFileInput.addEventListener('change', () => {
    //     if (els.csvFileInput.files?.length) {
    //         els.csvFileInput.form!.requestSubmit();
    //     }
    // })

}
