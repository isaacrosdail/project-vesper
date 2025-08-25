import * as esbuild from 'esbuild';
import { copyPlugin } from '@sprout2000/esbuild-copy-plugin'; // consider implementing this myself to avoid such a minor dependency

// Build JS/TS
const jsResult = await esbuild.build({
  entryPoints: ['app/static_src/js/app.js'],
  bundle: true,
  outfile: 'app/static/js/bundle.js',
  minify: true,
  metafile: true,
  logLevel: 'info',
  plugins: [
    copyPlugin({
      src: "./app/static_src/img/favicons/favicon.png",
      dest: "./app/static/favicon.png"
    })
  ]
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

console.log('JS Bundle analysis:')
console.log(await esbuild.analyzeMetafile(jsResult.metafile))

console.log('\nCSS Bundle analysis:')
console.log(await esbuild.analyzeMetafile(cssResult.metafile))