const { chromium } = require('/opt/node-tools/node_modules/playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  for (const lang of ['ko', 'en']) { await p.goto('file://' + path.join(__dirname, 'thumbnail.html') + '?lang=' + lang); await p.waitForFunction(() => window.done);
    await p.locator('#c').screenshot({ path: path.join(__dirname, `thumbnail_${lang}.png`) }); }
  await b.close(); })();
