import * as esbuild from 'esbuild';
import fs from 'fs';
import path from 'path';

// Build JS/TS
const jsResult = await esbuild.build({
  entryPoints: ['app/static_src/js/app.js'],
  bundle: true,
  outfile: 'app/static/js/bundle.js',
  minify: true,
  metafile: true,
  logLevel: 'info',
});

// Build CSS
const cssResult = await esbuild.build({
    entryPoints: ['app/static_src/css/app.css'],
    bundle: true,
    outfile: 'app/static/css/app.css',
    minify: true,
    metafile: true,
    logLevel: 'info',
});

// Simply copy over non-bundled assets
const staticFiles = ['img/favicons/favicon.png']
staticFiles.forEach(file => {
    const src = path.join('app/static_src', file);
    const dest = path.join('app/static', file);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log(`Copied ${file}`);
    }
});

console.log('JS Bundle analysis:')
console.log(await esbuild.analyzeMetafile(jsResult.metafile))

console.log('\nCSS Bundle analysis:')
console.log(await esbuild.analyzeMetafile(cssResult.metafile))