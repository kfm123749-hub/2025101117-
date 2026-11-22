# 「생성형 AI의 10년」 음악 — 화면 시간표(events.json)에 맞춰 직접 작곡·합성 (numpy, scipy)
#  훅   : 2014년 느낌의 거친 8비트 소리 → 얼굴이 선명해질 때마다 음이 오르며 깨끗해짐
#  1장  : 줌아웃마다 바람 소리와 쿵, ×1,500에서 첫 화음
#  2장  : 개월이 지날수록 빨라지는 시계, 1억 명 도달마다 '딩', 9억에서 고조
#  3장  : 글자 입력음 → 노이즈가 걷히는 소리 → 일그러진 음 → 매끄러운 음 → '소리' 장면에서 비트가 본격 시작
#  4장  : 동전 소리 → 빨려 들어가는 소리 → 동전 하나 '딩'
#  5장  : 사람이 켜질 때마다 오르는 음
#  6장  : 비트가 멈추고 시계 초침, 틀린 답에 버저
#  반전 : 한 박 쉬고 큰 화음, 끝은 첫 장면의 8비트 음으로 이어져 반복 재생이 자연스럽게
import numpy as np, wave, sys, json, math
from scipy.signal import butter, lfilter, fftconvolve
ev = json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'events.json'))   # 영어판은 events_en.json
sr = 44100; D = 60.0; N = int(sr * D); t = np.arange(N) / sr
rng = np.random.default_rng(2026)
out = np.zeros((2, N)); wet = np.zeros((2, N))
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): b, a = butter(o, min(fc, sr * .45) / (sr / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (sr / 2), 'high'); return lfilter(b, a, x)
def add(sig, t0, g=1., pan=.5, w=.35):
    i0 = int(round(t0 * sr))
    if i0 >= N: return
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    n = min(len(sig), N - i0); s = sig[:n] * g; l, r = math.cos(pan * math.pi / 2) * 1.41, math.sin(pan * math.pi / 2) * 1.41
    out[0, i0:i0 + n] += s * l * (1 - w * .5); out[1, i0:i0 + n] += s * r * (1 - w * .5)
    wet[0, i0:i0 + n] += s * l * w; wet[1, i0:i0 + n] += s * r * w
def env_ar(n, att, rel_from):
    tt = np.arange(n) / sr; return np.minimum(1, tt / att) * np.clip((n / sr - tt) / max(1e-3, n / sr - rel_from), 0, 1)
def pad(notes, a, b, g, fc=1800, att=.6, rel=1.0, det=.004, wob=0.0):
    i0, i1 = int(max(0, a - .1) * sr), int(min(D, b + rel) * sr); tt = t[i0:i1] - a; n = len(tt)
    env = np.clip((tt + .1) / att, 0, 1) * np.clip((b - a + rel - tt) / rel, 0, 1); env = np.sin(env * np.pi / 2) ** 2
    for j, m in enumerate(notes):
        f = hz(m) * (1 + wob * .02 * np.sin(2 * np.pi * (3.1 + j * .7) * tt + j)); s = np.zeros(n)
        for d in (-det, 0, det):
            ph = np.cumsum(f * (1 + d)) / sr + rng.random(); s += (2 * (ph % 1) - 1) * .5 + np.sin(2 * np.pi * ph) * .5
        add(lp(s, fc) * env / 3, max(0, a - .1), g, .5 + .32 * ((j % 2) * 2 - 1) * (.4 + .6 * j / len(notes)), .55)
def bell(m, t0, g=.1, pan=.5, dec=2.2, w=.6):
    f = hz(m); n = int(3.5 * sr); tt = np.arange(n) / sr
    add(np.sin(2 * np.pi * f * tt + 1.3 * np.exp(-tt * 4) * np.sin(2 * np.pi * f * 3.5 * tt)) * np.exp(-tt * dec) * np.minimum(1, tt / .003), t0, g, pan, w)
def pluck(m, t0, g=.1, pan=.5, dec=4.5):
    f = hz(m); n = int(1.6 * sr); tt = np.arange(n) / sr
    add((np.sin(2 * np.pi * f * tt) + .4 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 9)) * np.exp(-tt * dec) * np.minimum(1, tt / .002), t0, g, pan, .45)
def square(m, t0, dur, g=.08, pan=.5, crush=True):
    f = hz(m); n = int(dur * sr); tt = np.arange(n) / sr
    s = np.sign(np.sin(2 * np.pi * f * tt)) * env_ar(n, .004, dur * .6)
    if crush: s = np.round(s * 4) / 4; s = np.repeat(s[::6], 6)[:n]
    add(s, t0, g, pan, .2)
def impact(t0, g=.4, f0=42, dur=2.4):
    n = int(dur * sr); tt = np.arange(n) / sr; f = f0 * (1 + 1.2 * np.exp(-tt * 9)); ph = 2 * np.pi * np.cumsum(f) / sr
    add((np.sin(ph) * np.exp(-tt * 2.3) + lp(rng.standard_normal(n), 900) * np.exp(-tt * 12) * .4) * np.minimum(1, tt / .003), t0, g, .5, .3)
def whoosh(t0, dur, g=.1, up=True):
    n = int(dur * sr); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n); zi = np.zeros(2)
    for j in range(0, n, 512):
        q = u[j] if up else 1 - u[j]; b, a = butter(2, (250 + 7000 * q * q) / (sr / 2)); y[j:j + 512], zi = lfilter(b, a, x[j:j + 512], zi=zi)
    add(y * np.sin(np.pi * u) ** 1.5, t0, g, .5, .6)
def tick(t0, f, g, pan=.5, dec=70):
    n = int(.07 * sr); tt = np.arange(n) / sr
    add(np.sin(2 * np.pi * f * tt) * np.exp(-tt * dec) + hp(rng.standard_normal(n), 4000) * np.exp(-tt * 220) * .3, t0, g, pan, .3)
def kick(t0, g=.5):
    n = int(.32 * sr); tt = np.arange(n) / sr; add(np.sin(2 * np.pi * np.cumsum(46 + 90 * np.exp(-tt * 32)) / sr) * np.exp(-tt * 9), t0, g, .5, .05)
def snare(t0, g=.2):
    n = int(.22 * sr); tt = np.arange(n) / sr
    add(hp(rng.standard_normal(n), 1500) * np.exp(-tt * 22) * .8 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * .5, t0, g, .5, .3)
def hat(t0, g=.05, pan=.6):
    n = int(.06 * sr); tt = np.arange(n) / sr; add(hp(rng.standard_normal(n), 7500) * np.exp(-tt * 70), t0, g, pan, .2)

BEAT = .6
# ---------- 0. 훅 ----------
for k in range(7):                                                    # 2014년: 거친 8비트 아르페지오
    square([62, 65, 69, 72, 69, 65, 62][k], .05 + k * .24, .2, .085, .4 + .2 * (k % 2))
for k, x in enumerate(ev['face']):                                    # 얼굴이 선명해질 때마다 한 음씩 위로, 점점 깨끗하게
    m = [62, 64, 65, 67, 69, 72, 74][k]
    if k < 3: square(m + 12, x, .18, .07, .5)
    else: pluck(m + 12, x, .12 + .01 * k, .3 + .1 * (k % 3))
bell(86, 2.95, .1, .5, 1.6); bell(81, 2.97, .08, .4, 1.6); bell(78, 2.99, .06, .6, 1.6)
pad([50, 57, 62, 65, 69], 2.9, 4.55, .11, fc=2200, att=.3)
whoosh(3.8, .8, .12); impact(4.6, .5, 40, 2.5)
# ---------- 1. 커지는 AI ----------
pad([38, 50, 57, 60, 65], 4.6, 8.4, .08, fc=900)
pad([34, 46, 53, 58, 62], 8.4, 12.5, .08, fc=1300)
for x, m in [(4.65, 81), (6.2, 76), (9.0, 69)]: bell(m, x, .1, .5, 1.8)
whoosh(6.0, 1.5, .11, False); impact(7.4, .3, 48, 1.6)
whoosh(9.0, 1.6, .13, False); impact(10.5, .42, 38, 2.6)
pad([38, 50, 57, 62, 66, 69, 74], 10.6, 12.5, .1, fc=3000, att=.08)    # ×1,500: D장조로 열림
for j, m in enumerate([62, 66, 69, 74, 78]): bell(m, 10.62 + j * .05, .05, .2 + .15 * j, 1.6)
for k in range(13): kick(4.6 + k * BEAT * 2 + 1.2, .22 if k < 7 else .3)  # 낮은 맥박
whoosh(11.9, .7, .1)
# ---------- 2. ChatGPT ----------
pad([45, 52, 57, 60, 64], 12.6, 17.3, .07, fc=1500)
for m in range(1, 31): tick(13.3 + 4.0 * math.sqrt(m / 30), 1900 + 15 * m, .06, .4 + .2 * (m % 2))   # 경과 개월
for x, m, p in zip(ev['finish'], [88, 83, 79], [.35, .5, .65]): bell(m, x, .13, p, 1.7); bell(m - 12, x, .06, p, 1.7)
for k in range(int(4.0 / (BEAT / 2))): hat(13.3 + k * BEAT / 2, .035 + .02 * (k % 2))
whoosh(17.1, .6, .1)
seg_ = (t >= 17.8) & (t < 19.0); ts = t[seg_]; u = (ts - 17.8) / 1.2; f = 220 * 2 ** (u * 2)  # 9억까지 올라가는 소리
add(np.sin(2 * np.pi * np.cumsum(f) / sr) * np.sin(np.pi * u) ** .5 * (.4 + .6 * u), 17.8, .06, .5, .5)
impact(19.0, .35, 44, 2.0)
pad([41, 53, 57, 60, 65, 69], 19.0, 21.5, .1, fc=2600, att=.1)
pluck(81, 19.25, .1, .5); pluck(86, 19.4, .07, .55)
# ---------- 3. 글에서 영상까지 ----------
for x in ev['type'] + ev['reply']: tick(x, 2600 + rng.random() * 600, .075, .3 + .4 * rng.random(), 120)
pad([45, 52, 57, 60, 64], 21.6, 24.0, .12, fc=1400)
n = int(1.5 * sr); u = np.arange(n) / n; y = np.zeros(n); zi = np.zeros(2); x = rng.standard_normal(n)   # 노이즈가 걷힘
for j in range(0, n, 512): b, a = butter(2, (7000 * (1 - u[j]) ** 2 + 300) / (sr / 2)); y[j:j + 512], zi = lfilter(b, a, x[j:j + 512], zi=zi)
add(y * (1 - u) ** 1.2, 24.0, .22, .5, .5)
pad([41, 53, 60, 64, 69], 25.3, 26.6, .14, fc=2400, att=.2)
bell(84, 25.5, .09, .5, 1.6)
pad([40, 52, 59, 62, 67], 26.6, 29.4, .14, fc=1500, wob=1.0)            # 일그러진 2023년: 떨리는 음
for k in range(8): square(64 + [0, 3, -2, 5, 1, -4, 7, 2][k], 26.7 + k * .34, .12, .05, rng.random(), True)
pad([43, 55, 59, 62, 67, 71], 29.4, 31.0, .14, fc=2600)                # 매끄러운 2024년
for k in range(6): pluck([71, 74, 79, 83, 79, 74][k], 29.5 + k * .25, .09, .3 + .08 * k)
for x in ev['modes'][1:]: whoosh(x - .3, .35, .07)
# 2025년 '소리' — 비트가 본격 시작 (31.0 ~ 49.0)
B0 = 31.0
for k in range(int((49.0 - B0) / BEAT)):
    x = B0 + k * BEAT; kick(x, .27)
    if k % 2 == 1: snare(x, .16)
    hat(x + BEAT / 2, .05, .65); hat(x + BEAT / 4, .022, .35)
CH = [[38, 50, 57, 62, 66], [35, 47, 54, 59, 62], [43, 55, 59, 62, 67], [45, 57, 61, 64, 69]]   # D–Bm–G–A
for k in range(int((49.0 - B0) / (BEAT * 4))):
    a = B0 + k * BEAT * 4; c = CH[k % 4]; pad(c, a, a + BEAT * 4, .075, fc=2400, att=.05, rel=.4)
    for j in range(8): pluck(c[1 + (j % 4)] + 12, a + j * BEAT / 2, .045, .3 + .4 * (j % 2), 6)
    nb = int(BEAT * 4 * sr); tt = np.arange(nb) / sr; add(np.sin(2 * np.pi * hz(c[0]) * tt) * np.clip(1 - tt / (BEAT * 4), 0, 1) ** .3, a, .12, .5, .05)
impact(31.0, .3, 46, 1.6); bell(86, 31.02, .08, .5, 1.6)
# ---------- 4. 값은 폭락 ----------
order = np.argsort(ev['coinA'])
for i in order[::4]: add(np.sin(2 * np.pi * (2600 + 900 * rng.random()) * np.arange(int(.08 * sr)) / sr) * np.exp(-np.arange(int(.08 * sr)) / sr * 60), ev['coinA'][i], .03, rng.random(), .3)
whoosh(36.3, 1.1, .14, False)
seg_ = (t >= 36.3) & (t < 37.4); ts = t[seg_]; u = (ts - 36.3) / 1.1
add(np.sin(2 * np.pi * np.cumsum(1400 * 2 ** (-u * 3)) / sr) * np.sin(np.pi * u) ** .7, 36.3, .05, .5, .5)
bell(93, 37.6, .1, .5, 2.4); bell(81, 37.62, .07, .5, 2.4)
impact(38.1, .3, 52, 1.4)
# ---------- 5. 모두의 도구 ----------
PENT = [62, 64, 66, 69, 71]
for k, x in enumerate(ev['lit']): pluck(PENT[k % 5] + 12 * (k // 18), x, .05 + .02 * (k / 52), .3 + .4 * ((k * 7) % 10) / 10, 5)
bell(86, 44.5, .09, .5, 1.6)
# ---------- 6. 그래도 아직 ----------
pad([40, 46, 52, 58], 49.0, 53.7, .14, fc=1300)                         # 반음·트라이톤의 불안한 화음
for k in range(5): tick(49.3 + k, 1400, .13, .5, 50)
for x in (49.6, 50.3):
    n = int(.25 * sr); tt = np.arange(n) / sr; add(np.sign(np.sin(2 * np.pi * 130 * tt)) * np.exp(-tt * 10) * .6, x, .05, .5, .2)
bell(76, 51.0, .08, .5, 1.6)
seg_ = (t >= 51.7) & (t < 52.6); ts = t[seg_]; u = (ts - 51.7) / .9
add(np.sin(2 * np.pi * np.cumsum(330 * 2 ** (u * .5)) / sr) * np.sin(np.pi * u) ** .5, 51.7, .05, .5, .4)
# ---------- 반전 ----------
pluck(69, 54.15, .1, .5, 2.5)
impact(54.75, .5, 37, 3.0)
pad([38, 50, 57, 62, 66, 69, 74, 78], 54.75, 59.2, .12, fc=3400, att=.06, rel=1.0)
for j, m in enumerate([62, 66, 69, 74, 78, 81, 86]): bell(m, 54.78 + j * .06, .06, .15 + .7 * j / 6, 1.6, .7)
for k, m in enumerate([74, 78, 81, 86]): bell(m, 55.5 + k * .22, .08, .3 + .13 * k, 1.8)
bell(81, 57.15, .07, .5, 1.6)
for k in range(4): square([62, 65, 69, 72][k], 59.45 + k * .12, .1, .03 + .01 * k, .5)     # 첫 장면의 8비트로 이어짐

def ir(seed, sec=2.6):
    n = int(sec * sr); tt = np.arange(n) / sr; r = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 2.5); r = lp(r, 5200); return r / np.sqrt((r ** 2).sum())
mix = out + np.stack([fftconvolve(wet[0], ir(1))[:N], fftconvolve(wet[1], ir(2))[:N]]) * .8
gate = 1 - .9 * np.clip((t - 53.9) / .05, 0, 1) * np.clip((54.12 - t) / .03, 0, 1)        # 반전 직전 한 박 쉼
mix *= gate; mix = hp(mix, 28); mix *= np.clip(t / .01, 0, 1)
mix *= 10 ** (-18 / 20) / np.sqrt((mix ** 2).mean()); mix = np.tanh(mix / .85) * .85; mix *= min(1, 10 ** (-1 / 20) / np.abs(mix).max())
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix.T * 32767).astype('<i2').tobytes()); w.close()
