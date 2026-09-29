// Writes tools/phrases.json: every line the game can speak (from window.__phonicsPhrases in index.html).
// Usage: node tools/export_phrases.js   (needs the `playwright` package)
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  const phrases = await page.evaluate(() => window.__phonicsPhrases());
  await browser.close();
  fs.writeFileSync(path.join(__dirname, 'phrases.json'), JSON.stringify(phrases, null, 1) + '\n');
  console.log(`${phrases.length} phrases -> tools/phrases.json`);
})();
