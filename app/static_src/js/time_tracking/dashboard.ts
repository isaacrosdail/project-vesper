
import { mount } from 'svelte';
import { required } from '../shared/dom';
import TimeTrackingDashboard from './TimeTrackingDashboard.svelte';

export async function init() {

    mount(TimeTrackingDashboard, {
        target: required(document.querySelector('#time-dashboard-root'), '#time-dashboard-root')
    });
}
