import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';
import fullReload from 'vite-plugin-full-reload';

export default defineConfig(({ command }) => ({
    plugins: [
        svelte(),  // was: esbuild-svelte plugin
        fullReload(['app/_templates/**/*.html', 'app/modules/**/templates/**/*.html']),
    ],
    // Base: Vite needs to know the url prefix our files get served under
    base: command === 'build' ? '/static/' : '/',
    build: {
        outDir: 'app/static',
        emptyOutDir: false,
        manifest: true,
        sourcemap: false,
        rollupOptions: {
            input: {                      // was: the two entryPoints arrays
                app: 'app/static_src/js/app.ts',
                style: 'app/static_src/css/app.css',
            },
        },
    },
    server: {
        port: 5173,
        strictPort: true, // don't port hop if taken
        warmup: {
            clientFiles: ['./app/static_src/js/app.ts'],
        },
    },
}));
