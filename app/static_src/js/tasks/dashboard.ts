
import { mount } from 'svelte';
import { required } from '../shared/dom';
import TasksDashboard from './TasksDashboard.svelte';


export async function init() {

    const dashboard = mount(TasksDashboard, {
        target: required(document.querySelector('#tasks-dashboard-root'), '#tasks-dashboard-root')
    })
    required(document.querySelector('#tasks-entry-dashboard-btn'), '#tasks-entry-dashboard-btn')
        .addEventListener('click', () => dashboard.openAddTask());

}

