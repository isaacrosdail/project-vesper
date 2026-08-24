
import { mount } from 'svelte';
import { required } from '../../shared/dom';
import RecipesPage from './RecipesPage.svelte';


export async function init() {
    mount(RecipesPage, {
        target: required(document.querySelector('#recipes-root'), '#recipes-root')
    })
}