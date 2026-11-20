// 사용법
//   node render.js still <출력폴더> 3,8,12.5      → 지정한 시각(초)의 정지 화면 PNG
//   node render.js frames <출력폴더> [fps=60]      → 전체 프레임 JPEG (4개 창 병렬)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const [mode, outDir, arg] = process.argv.slice(2);
const url = 'file://' + path.join(__dirname, 'index.html');
const DUR = 60;

async function open(browser, scale) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: scale });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  await page.goto(url);
  await page.evaluate(() => window.ready);
  return page;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  if (mode === 'still') {
    const page = await open(browser, 0.5);
    for (const t of arg.split(',').map(Number)) {
      await page.evaluate(t => window.renderFrame(t), t);
      await page.screenshot({ path: path.join(outDir, `t${t.toFixed(2).padStart(5, '0')}.png`) });
    }
  } else {
    const fps = Number(arg || 60), total = DUR * fps, N = 4;
    let done = 0;
    await Promise.all([...Array(N).keys()].map(async w => {
      const page = await open(browser, 1);
      for (let i = w; i < total; i += N) {
        await page.evaluate(t => window.renderFrame(t), i / fps);
        await page.screenshot({ path: path.join(outDir, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 96 });
        if (++done % 300 === 0) console.log(`${done}/${total}`);
      }
    }));
  }
  await browser.close();
})();
