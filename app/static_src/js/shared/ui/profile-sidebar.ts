
import { mount } from 'svelte';
import { required } from '../dom';
import ProfileSidebar from './../components/ProfileSidebar.svelte';


export function init() {
    mount(ProfileSidebar, {
        target: required(document.querySelector('#profile-sidebar-root'), '#profile-sidebar-root')
    });

}