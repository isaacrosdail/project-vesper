import * as esbuild from 'esbuild';
import sveltePlugin from 'esbuild-svelte';
import { readFileSync, writeFileSync, rmSync } from 'fs';

const isWatch = process.argv.includes('--watch');
const isProd = process.argv.includes('--prod');

// Wipe previous fingerprinted outdirs
if (!isWatch) {
    rmSync('app/static/js', { recursive: true, force: true });
    rmSync('app/static/css', { recursive: true, force: true });
}

// Enables file signatures for caching bundles
// Only when isProd
const manifestPlugin = {
    name: 'manifest',
    setup(build) {
        build.onEnd(result => {
        if (!result.metafile) return;
        const file = 'app/static/manifest.json';
        let manifest = {};
        try { manifest = JSON.parse(readFileSync(file)); } catch {}   // merge JS + CSS builds
        for (const [outPath, meta] of Object.entries(result.metafile.outputs)) {
            if (!meta.entryPoint) continue;   // skip sourcemaps/chunks — they have no entryPoint
            const key = meta.entryPoint
            .replace(/^app\/static_src\//, '')   // app/static_src/js/app.ts -> js/app.ts
            .replace(/\.[^.]+$/, '');            //                          -> js/app
            manifest[key] = outPath.replace(/^app\/static\//, '');  // app/static/js/app-HASH.js -> js/app-HASH.js
            if (meta.cssBundle) {
                manifest[key + '.css'] = meta.cssBundle.replace(/^app\/static\//, '');
            }
        }
        writeFileSync(file, JSON.stringify(manifest, null, 2));
        });
    },
};

// Build JS/TS
const jsOptions = {
  entryPoints: ['app/static_src/js/app.ts'],
  outdir: 'app/static/js',
  entryNames: isProd ? '[name]-[hash]' : '[name]', // name is the entrypoint's base name (aka app.ts -> app, not bundle.js)
  bundle: true,
  sourcemap: !isProd,
  minify: isProd,
  format: 'esm',
  metafile: true,
  logLevel: 'warning',
  plugins: [manifestPlugin, sveltePlugin()],
};

// Build CSS
const cssOptions = {
    entryPoints: ['app/static_src/css/app.css'],
    outdir: 'app/static/css',
    entryNames: isProd ? '[name]-[hash]' : '[name]',
    bundle: true,
    sourcemap: !isProd,
    minify: isProd,
    metafile: true,
    logLevel: 'warning',
    external: ['/static/*'],
    plugins: [manifestPlugin, sveltePlugin()],
};

const jsContext = await esbuild.context(jsOptions);
const cssContext = await esbuild.context(cssOptions);

if (isWatch) {
  await jsContext.watch();
  await cssContext.watch();
  console.log('[esbuild] Watching...')

  process.on('SIGINT', async () => {
    console.log('\n[esbuild] Cleaning up...');
    await jsContext.dispose();
    await cssContext.dispose();
    process.exit(0);
  });
  process.on('SIGTERM', async () => {
    await jsContext.dispose();
    await cssContext.dispose();
    process.exit(0);
  });
} else {
  const jsResult = await jsContext.rebuild();
  const cssResult = await cssContext.rebuild();

  console.log('JS Bundle analysis:');
  console.log(await esbuild.analyzeMetafile(jsResult.metafile));

  console.log('\nCSS Bundle analysis:');
  console.log(await esbuild.analyzeMetafile(cssResult.metafile));

  await jsContext.dispose();
  await cssContext.dispose();
}

