import { mount } from 'svelte';
import HomePage from './Homepage.svelte';
import { required } from '../shared/dom';


export function init() {

    // TODO(svelte): revamp
    mount(HomePage, {
        target: required(document.querySelector('#homepage-root'), '#homepage-root')
    });
}
