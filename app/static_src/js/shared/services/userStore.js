// TODO: NOTES: Bundler => utility/singleton, defines userStore class instance
// Import explicitly where needed

// TODO: NOTES: Container Pattern / state machine pattern?
// userStore acting as a "container"
// Keeps related data/state + behavior nicely bundled together
// Idea is userStore can only be in one of four states at any time, and follows
// specific rules about how to transition between states

export const userStore = {
    data: null,
    state: 'not-loaded',

    // Giving userStore an object method to fetch
    fetch: async function() {

        if (this.state === 'loaded') {
            return this.data; // Return cached data
        }

        // Make call, set state to loading prior
        this.state = 'loading';
        const response = await fetch('/api/profile/me', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });
        if (response.ok) {
            const responseData = await response.json();
            this.state = 'loaded';
            // data contains our { timezone: '..' }, now cached in memory until refresh
            this.data = responseData; // can now access tz => 'userStore.data.timezone'
        } else {
            this.state = 'error';
            this.data = null;
            throw new Error(`Failed to fetch user data: ${response.status}`);
        }
    }
}