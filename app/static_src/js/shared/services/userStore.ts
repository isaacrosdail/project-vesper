// TODO: NOTES: Bundler => utility/singleton, defines userStore class instance
// Import explicitly where needed
import { apiRequest } from './api.js';
// TODO: NOTES: Container Pattern / state machine pattern?
// userStore acting as a "container"
// Keeps related data/state + behavior nicely bundled together
// Idea is userStore can only be in one of four states at any time, and follows
// specific rules about how to transition between states

type UserState = 'not-loaded' | 'loading' | 'loaded' | 'error';

type UserData = {
    timezone: string;
    // other fields from profile/me
};

type UserStore = {
    data: UserData | null;
    state: UserState;
    fetch: () => Promise<UserData | null>;
};

export const userStore: UserStore = {
    data: null,
    state: 'not-loaded',

    // Giving userStore an object method to fetch
    async fetch() {

        if (this.state === 'loaded') {
            return this.data; // Return cached
        }

        this.state = 'loading';
        const response = await fetch('/api/profile/me', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });
        if (response.ok) {
            const responseData: UserData = await response.json();
            this.state = 'loaded';
            // data contains our { timezone: '..' }
            this.data = responseData; // can now access tz => 'userStore.data.timezone'
            return responseData;
        } else {
            this.state = 'error';
            this.data = null;
            throw new Error(`Failed to fetch user data: ${response.status}`);
        }
    }
}