import { mount } from 'svelte';
import { required } from '../shared/dom';
import HabitsDashboard from './HabitsDashboard.svelte';

export async function init() {

    mount(HabitsDashboard, {
        target: required(document.querySelector('#habits-dashboard-root'), '#habits-dashboard-root')
    });
}
