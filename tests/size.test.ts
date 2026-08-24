import { test, expect } from 'bun:test';
import { $ } from 'bun';

test('bundle stays under budget', async () => {
    await $`node build.mjs --prod`.quiet();
    const manifest = await Bun.file('app/static/manifest.json').json();
    const bundle = await Bun.file(`app/static/${manifest['js/app']}`).arrayBuffer();
    const gzipped = Bun.gzipSync(new Uint8Array(bundle));
    expect(gzipped.byteLength).toBeLessThan(80_000);
});
