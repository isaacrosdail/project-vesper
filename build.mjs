import * as esbuild from 'esbuild';

const isWatch = process.argv.includes('--watch');
const isProd = process.argv.includes('--prod');

// Build JS/TS
const jsOptions = {
  entryPoints: ['app/static_src/js/app.js'],
  outfile: 'app/static/js/bundle.js',
  bundle: true,
  sourcemap: !isProd,
  minify: isProd,
  format: 'esm',
  metafile: true,
  logLevel: 'info',
};

// Build CSS
const cssOptions = {
    entryPoints: ['app/static_src/css/app.css'],
    outfile: 'app/static/css/app.css',
    bundle: true,
    sourcemap: !isProd,
    minify: isProd,
    metafile: true,
    logLevel: 'info',
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

