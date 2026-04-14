import fs from 'node:fs';
import path from 'node:path';

const walk = (d) =>
  fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(d, e.name);
    return e.isDirectory() ? walk(p) : [p];
  });

const htmls = walk('dist').filter((f) => f.endsWith('.html'));
const refs = new Set();
for (const h of htmls) {
  const c = fs.readFileSync(h, 'utf8');
  for (const m of c.matchAll(/["'](\/images\/[^"'?)]+)["')]/g)) refs.add(m[1]);
}
console.log('Referenced images:', refs.size);

const all = walk('public/images').map(
  (p) => '/' + p.split(path.sep).join('/').replace('public/', '')
);
console.log('Total images:', all.length);

const unused = all.filter((f) => !refs.has(f));
console.log('Unused:', unused.length);
let total = 0;
for (const u of unused) {
  const size = fs.statSync('public' + u).size;
  total += size;
  console.log((size / 1024).toFixed(0).padStart(6) + ' KB  ' + u);
}
console.log('Unused total:', (total / 1024 / 1024).toFixed(2) + ' MB');

console.log('\nTop 10 referenced images by size:');
const refList = [...refs]
  .map((r) => {
    try {
      return { path: r, size: fs.statSync('public' + r).size };
    } catch {
      return { path: r, size: 0 };
    }
  })
  .sort((a, b) => b.size - a.size)
  .slice(0, 10);
for (const r of refList) {
  console.log((r.size / 1024).toFixed(0).padStart(6) + ' KB  ' + r.path);
}
