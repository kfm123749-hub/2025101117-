// 사용법: node audit.js <html 경로> <길이(초)> [fps=10]
// 화면에 그려지는 모든 글자의 실제 위치(변환 적용)를 기록해, 서로 겹치거나 너무 가까운 곳·쇼츠 UI에 가리는 곳을 찾음
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const [file, durS, fpsS] = process.argv.slice(2); const DUR = +durS, FPS = +(fpsS || 10);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: .25 });
  p.on('pageerror', e => console.error('PAGE', e.message));
  await p.goto('file://' + file); await p.evaluate(() => window.ready);
  const res = await p.evaluate(({ DUR, FPS }) => {
    const cvs = document.getElementById('c'), c2 = cvs.getContext('2d'); let LOG = [], inRich = 0, richShrunk = false;
    const ot = window.txt, orich = window.rich;
    window.txt = function (s, x, y, size, weight, color, align = 'left', alpha = 1, ls = -0.02, maxW = 960) {
      if (alpha > 0.003 && s && String(s).trim()) {
        let sz = size; const w0 = meas(s, size, weight, ls); let shr = false; if (w0 > maxW) { sz = size * maxW / w0; shr = true; }
        const w = meas(s, sz, weight, ls), x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
        const m = c2.getTransform(), k = 1 / (cvs.width / 1080);
        const pts = [[x0, y - sz * .78], [x0 + w, y - sz * .78], [x0, y + sz * .2], [x0 + w, y + sz * .2]].map(([X, Y]) => [(m.a * X + m.c * Y + m.e) * k, (m.b * X + m.d * Y + m.f) * k]);
        const xs = pts.map(q => q[0]), ys = pts.map(q => q[1]);
        LOG.push({ s: String(s), x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys), a: c2.globalAlpha * alpha, sz: sz * Math.hypot(m.a, m.b) * k, shr: shr || (inRich && richShrunk), base: (m.b * x + m.d * y + m.f) * k, rich: inRich });
      }
      return ot.apply(this, arguments);
    };
    window.rich = function (parts, x, y, alpha = 1, align = 'center', maxW = 920) {
      const tw = parts.reduce((a, q) => a + meas(q[0], q[1], q[2]), 0); richShrunk = tw > maxW; inRich++; try { return orich.apply(this, arguments); } finally { inRich--; }
    };
    const frames = [];
    for (let i = 0; i < DUR * FPS; i++) {
      const t = i / FPS; LOG = []; window.renderFrame(t);
      // 같은 줄의 조각(rich)은 하나로 합침
      const L = []; for (const e of LOG) { const last = L[L.length - 1];
        if (last && e.rich && last.rich && Math.abs(last.base - e.base) < 2 && Math.abs(e.x0 - last.x1) < 3) { last.x1 = Math.max(last.x1, e.x1); last.y0 = Math.min(last.y0, e.y0); last.y1 = Math.max(last.y1, e.y1); last.s += e.s; last.a = Math.max(last.a, e.a); last.shr = last.shr || e.shr; last.sz = Math.max(last.sz, e.sz); }
        else L.push({ ...e }); }
      document.querySelectorAll('.tx').forEach(d => { const op = +getComputedStyle(d).opacity; if (op > .02) { const r = d.querySelector('.katex') || d; const bb = r.getBoundingClientRect(); L.push({ s: '[수식] ' + d.textContent.slice(0, 18), x0: bb.left, x1: bb.right, y0: bb.top, y1: bb.bottom, a: op, sz: 40, shr: false }); } });
      frames.push({ t, L: L.filter(e => e.a > .25).map(e => ({ s: e.s, x0: Math.round(e.x0), x1: Math.round(e.x1), y0: Math.round(e.y0), y1: Math.round(e.y1), sz: Math.round(e.sz), shr: e.shr })) });
    }
    return frames;
  }, { DUR, FPS });
  await b.close();
  const issues = new Map(); const add = (k, t, d) => { if (!issues.has(k)) issues.set(k, { t0: t, t1: t, d }); const v = issues.get(k); v.t1 = t; if (d < v.d) v.d = d; };
  for (const f of res) {
    const L = f.L;
    for (let i = 0; i < L.length; i++) for (let j = i + 1; j < L.length; j++) {
      const A = L[i], B = L[j]; const gx = Math.max(A.x0 - B.x1, B.x0 - A.x1), gy = Math.max(A.y0 - B.y1, B.y0 - A.y1);
      const gap = Math.max(gx, gy); if (gap < 10) add(`겹침/근접 | "${A.s}"  ↔  "${B.s}"`, f.t, gap);
    }
    for (const A of L) {
      if (A.shr) add(`자동 축소됨 | "${A.s}" (${A.sz}px)`, f.t, 0);
      if (A.x0 < 36 || A.x1 > 1044) add(`화면 가장자리 | "${A.s}" x ${A.x0}–${A.x1}`, f.t, 0);
      if (A.y1 > 1600) add(`쇼츠 하단 설명란 영역(>1600) | "${A.s}" y1=${A.y1}`, f.t, 0);
      if (A.x1 > 930 && A.y1 > 1080 && A.y0 < 1650) add(`쇼츠 오른쪽 버튼 영역 | "${A.s}" x1=${A.x1} y=${A.y0}`, f.t, 0);
      if (A.sz < 24) add(`폰에서 너무 작은 글자(<24px) | "${A.s}" ${A.sz}px`, f.t, 0);
    }
  }
  const out = [...issues.entries()].map(([k, v]) => `${v.t0.toFixed(1).padStart(5)}–${v.t1.toFixed(1).padEnd(5)} ${k}${k.startsWith('겹침') ? `  (최소 간격 ${v.d}px)` : ''}`);
  out.sort((a, b) => a.slice(0, 5) - b.slice(0, 5)); console.log(out.join('\n')); console.log('\n총', out.length, '건');
})();
