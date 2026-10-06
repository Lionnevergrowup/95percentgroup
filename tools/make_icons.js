// Draw the site icons from the SVGs that tools/make_icon_svg.py writes ("ABC" with Leo the lion):
//   favicon.ico (16, 32 and 48 px; the tab sizes, 16 and 32, are just "ABC"), icons/apple-touch-icon.png (180 px, iPhone home screen),
//   icons/icon-192.png and icons/icon-512.png (Android, app install), icons/icon-maskable-512.png (Android round icons).
// Usage: NODE_PATH=$(npm root -g) node tools/make_icons.js   (needs the playwright package)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const art = name => fs.readFileSync(path.join(ROOT, 'icons', name), 'utf8');

async function render(page, size, svg){
  await page.setViewportSize({width: size, height: size});
  await page.setContent(`<html><body style="margin:0;width:${size}px;height:${size}px;background:transparent">${svg.replace('<svg ', '<svg width="100%" height="100%" ')}</body></html>`);
  return page.screenshot({omitBackground: true, clip: {x: 0, y: 0, width: size, height: size}});
}

// An .ico file holding PNG images (supported by every current browser)
function ico(pngs){
  const head = Buffer.alloc(6 + 16 * pngs.length);
  head.writeUInt16LE(0, 0); head.writeUInt16LE(1, 2); head.writeUInt16LE(pngs.length, 4);
  let offset = head.length;
  pngs.forEach(([size, png], i) => {
    const e = 6 + 16 * i;
    head.writeUInt8(size >= 256 ? 0 : size, e); head.writeUInt8(size >= 256 ? 0 : size, e + 1);
    head.writeUInt16LE(1, e + 4); head.writeUInt16LE(32, e + 6);
    head.writeUInt32LE(png.length, e + 8); head.writeUInt32LE(offset, e + 12);
    offset += png.length;
  });
  return Buffer.concat([head, ...pngs.map(p => p[1])]);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({deviceScaleFactor: 1});
  const out = (name, buf) => { fs.writeFileSync(path.join(ROOT, name), buf); console.log(`${name}: ${buf.length} bytes`); };
  const tab = [];
  for (const z of [16, 32, 48]) tab.push([z, await render(page, z, art(z <= 32 ? 'icon-small.svg' : 'icon.svg'))]);
  out('favicon.ico', ico(tab));
  out('icons/apple-touch-icon.png', await render(page, 180, art('icon-full.svg')));
  out('icons/icon-192.png', await render(page, 192, art('icon-full.svg')));
  out('icons/icon-512.png', await render(page, 512, art('icon-full.svg')));
  out('icons/icon-maskable-512.png', await render(page, 512, art('icon-maskable.svg')));
  await browser.close();
})();
