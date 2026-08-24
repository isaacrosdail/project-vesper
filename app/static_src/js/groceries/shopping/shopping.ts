
import { mount } from 'svelte';
import { required } from '../../shared/dom';
import Shopping from './Shopping.svelte';


export async function init() {
    mount(Shopping, {
        target: required(document.querySelector('#shopping-root'), '#shopping-root')
    })
}