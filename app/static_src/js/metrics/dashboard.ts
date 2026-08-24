import { mount } from 'svelte';
import { required } from '../shared/dom';
import MetricsDashboard from './MetricsDashboard.svelte';



export async function init() {

    mount(MetricsDashboard, {
        target: required(document.querySelector('#metrics-dashboard-root'), '#metrics-dashboard-root')
    });
}
