# 「137.5°의 비밀」 배경음악 — 화면 타임라인에 맞춰 직접 작곡·합성 (numpy, scipy)
# 조성: B단조 → D장조로 해소. 각 장면의 감정선:
#   훅   : 반짝이는 입자음이 씨앗 개수만큼 쏟아짐
#   1장  : 씨앗 하나마다 음 하나 (음 높이 = 그 씨앗의 각도)
#   2·3장: 빈틈 = 긴장 (텅 빈 5도 드론, 낮은 쿵 소리)
#   4장  : 각도를 찾는 동안 음이 따라 미끄러지고 심장 박동이 빨라짐 → 직전 0.4초 정적
#   5장  : 황금각 공개와 함께 D장조 화음이 활짝, 피보나치 수에 맞춘 벨
#   결말 : 하프 글리산도 → 마지막 화음
import numpy as np, wave, sys
from scipy.signal import butter, lfilter, fftconvolve

sr = 44100; D = 60.0; N = int(sr * D); t = np.arange(N) / sr
rng = np.random.default_rng(137)
out = np.zeros((2, N)); wetbus = np.zeros((2, N))
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): b, a = butter(o, min(fc, sr * .45) / (sr / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (sr / 2), 'high'); return lfilter(b, a, x)
def add(sig, t0, g=1.0, pan=.5, wet=.4):
    i0 = int(round(t0 * sr))
    if i0 >= N or i0 + len(sig) <= 0: return
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    n = min(len(sig), N - i0); s = sig[:n] * g
    l, r = np.cos(pan * np.pi / 2) * 1.41, np.sin(pan * np.pi / 2) * 1.41
    out[0, i0:i0 + n] += s * l * (1 - wet * .5); out[1, i0:i0 + n] += s * r * (1 - wet * .5)
    wetbus[0, i0:i0 + n] += s * l * wet; wetbus[1, i0:i0 + n] += s * r * wet

# ---------- 화면과 같은 타임라인 ----------
PHI = (1 + 5 ** .5) / 2; GOLDEN = 1 - 1 / PHI
def io3(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def kf(x, ks):
    if x <= ks[0][0]: return ks[0][1]
    for (a, va), (b, vb) in zip(ks, ks[1:]):
        if x <= b: return va + (vb - va) * io3((x - a) / (b - a))
    return ks[-1][1]
TURN = [[12.7, GOLDEN], [13.7, .5], [15.7, .5], [16.6, 1 / 3], [18.3, 1 / 3], [19.2, .4], [23.5, .4], [24.6, 1 / np.pi],
        [33.2, 1 / np.pi], [37.0, .4472], [38.6, .36], [39.7, .3925], [40.6, .379], [41.3, GOLDEN]]
ONE = [5.7, 6.15, 6.6, 7.0, 7.38, 7.74, 8.08, 8.4, 8.7, 8.98]
def io5(x): return 16 * x ** 5 if x < .5 else 1 - (-2 * x + 2) ** 5 / 2
def n_at(x):
    if x < 5.2: return 34 + (900 - 34) * io5(min(1, max(0, x / 3.4)))
    if x < 9.2: return sum(1 for o in ONE if x >= o)
    s = min(1, max(0, (x - 9.2) / 3.2)); return 10 + 890 * (s ** 3 * .15 + io3(s) * .85)

# ---------- 악기 ----------
def pad(notes, a, b, g, fc=1800, att=.8, rel=1.2, det=.004, pan_spread=.35):
    i0, i1 = int(max(0, a - att * .3) * sr), int(min(D, b + rel) * sr)
    tt = t[i0:i1] - a; n = len(tt)
    env = np.clip((tt + att * .3) / att, 0, 1) * np.clip((b - a + rel - tt) / rel, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    for j, m in enumerate(notes):
        f = hz(m); s = np.zeros(n)
        for d in (-det, 0, det):
            ph = f * (1 + d) * tt + rng.random()
            s += (2 * (ph % 1) - 1) * .6 + np.sin(2 * np.pi * ph) * .4
        s = lp(s, fc) * env / 3
        add(s, a - att * .3 if a - att * .3 > 0 else 0, g * 1.45, .5 + pan_spread * ((j % 2) * 2 - 1) * (.4 + .6 * j / len(notes)), .55)
def pluck(m, t0, g=.2, pan=.5, dec=3.2, wet=.5, bright=1.0):
    f = hz(m); n = int(2.6 * sr); tt = np.arange(n) / sr
    s = (np.sin(2 * np.pi * f * tt) + .35 * bright * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 6)
         + .15 * bright * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 10)) * np.exp(-tt * dec) * np.minimum(1, tt / .002)
    add(s, t0, g, pan, wet)
def bell(m, t0, g=.12, pan=.5, dec=2.2, wet=.6):
    f = hz(m); n = int(4 * sr); tt = np.arange(n) / sr
    mod = 1.6 * np.exp(-tt * 4) * np.sin(2 * np.pi * f * 3.5 * tt)
    s = np.sin(2 * np.pi * f * tt + mod) * np.exp(-tt * dec) * np.minimum(1, tt / .003)
    add(s, t0, g, pan, wet)
def impact(t0, g=.5, f0=46, dur=2.4):
    n = int(dur * sr); tt = np.arange(n) / sr
    f = f0 * (1 + 1.2 * np.exp(-tt * 10)); ph = 2 * np.pi * np.cumsum(f) / sr
    s = np.sin(ph) * np.exp(-tt * 2.2) + lp(rng.standard_normal(n), 900) * np.exp(-tt * 12) * .5
    add(s * np.minimum(1, tt / .002), t0, g * .7, .5, .35)
def swell(t0, dur, g=.12, f_end=7000):           # 장면 직전 상승음 (필터가 열리는 노이즈)
    n = int(dur * sr); x = rng.standard_normal(n); y = np.zeros(n); zi = None; ch = 1024
    for j in range(0, n, ch):
        fc = 200 + f_end * (j / n) ** 2.2; b, a = butter(2, fc / (sr / 2))
        if zi is None: zi = np.zeros(2)
        y[j:j + ch], zi = lfilter(b, a, x[j:j + ch], zi=zi)
    add(y * (np.arange(n) / n) ** 2.5, t0, g, .5, .6)
def tick(t0, f, g, pan):
    n = int(.06 * sr); tt = np.arange(n) / sr
    add(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 70), t0, g, pan, .5)

# ---------- 0. 훅 (0–5초) ----------
pad([47, 54, 59, 62, 66, 73], 0, 4.9, .10, fc=1400)              # Bm(add9)
impact(.9, .42); bell(78, .9, .12); bell(85, .95, .06, .7)       # '빈틈없이'
bell(74, 2.4, .08, .35)
last = 34
for i in range(int(3.6 * 200)):                                  # 씨앗이 늘어나는 만큼 입자음
    x = i / 200; nn = n_at(x); k = int(nn) - int(last); last = nn
    for _ in range(min(k, 3)):
        if rng.random() < .55:
            m = [74, 76, 78, 81, 83, 86, 88, 90][rng.integers(8)] + (12 if rng.random() < .2 else 0)
            tick(x + rng.random() * .005, hz(m), .018 + .02 * (x / 3.6), rng.random())
swell(3.9, 1.1, .08)

# ---------- 1. 규칙 (5–13초) ----------
pad([47, 54, 59, 62, 66], 5.2, 12.9, .07, fc=1100)
PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83]                  # D장조 5음 음계 2옥타브
for k, x in enumerate(ONE, start=1):
    ang = (k * GOLDEN) % 1                                       # 그 씨앗의 각도가 곧 음 높이
    m = PENTA[int(ang * len(PENTA))]
    pluck(m, x, .17, .3 + .4 * ang, 2.6, .55); pluck(m + 12, x + .004, .035, .7 - .4 * ang, 4, .7)
last = 10
for i in range(int(3.3 * 300)):                                  # 900개로 불어나는 동안 가속하는 입자음
    x = 9.2 + i / 300; nn = n_at(x); k = int(nn) - int(last); last = nn
    for _ in range(min(k, 2)):
        if rng.random() < .35:
            tick(x + rng.random() * .003, hz(PENTA[rng.integers(10)] + 12), .012 + .02 * (x - 9.2) / 3.3, rng.random())
swell(11.9, 1.2, .12); impact(13.0, .36, 41)

# ---------- 2. 딱 떨어지는 각도 (13–24초): 빈 5도 드론 + 쿵 ----------
pad([35, 42, 47, 54], 13.2, 23.8, .11, fc=700, det=.002)        # B5 드론 (3음이 없는 텅 빈 소리)
for x, ms in [(13.7, [59, 71]), (16.6, [59, 66, 71]), (19.2, [59, 66, 71, 76, 80])]:
    impact(x - .02, .30, 40, 1.6)
    for j, m in enumerate(ms): pluck(m, x + j * .05, .10, .3 + .1 * j, 1.6, .6, .6)
for x in np.arange(13.7, 23.5, 60 / 84):                        # 느린 맥박
    tick(x, 1200, .012, .5)
swell(22.6, 1.3, .1); impact(24.55, .32, 38)

# ---------- 3. 무리수라면? (24–33초): 불안한 화음 ----------
pad([43, 50, 55, 58, 61], 24.6, 32.9, .09, fc=900)               # G단조 + 반음 긴장 (C#)
pad([79, 80], 26.0, 32.6, .018, fc=4000, att=2.0)                 # 높은 단2도 떨림
for j in range(22):                                              # '22갈래' — 22개의 작은 음
    bell(86 + (j % 3) * 0 - (j % 2) * 12, 28.9 + j * .1, .028, (j * 7 % 22) / 22, 1.8, .8)
swell(32.2, 1.1, .1)

# ---------- 4. 탐색 (33–41.5초): 각도를 따라 미끄러지는 음 + 빨라지는 맥박 ----------
seg = (t >= 33.0) & (t < 41.1); ts = t[seg]
turn = np.array([kf(x, TURN) for x in ts[::64]]); turn = np.interp(np.arange(len(ts)), np.arange(0, len(ts), 64)[:len(turn)], turn)
f = 220 * 2 ** ((turn - .3) * 12)                                # 회전 각도 → 음 높이
ph = 2 * np.pi * np.cumsum(f * (1 + .004 * np.sin(2 * np.pi * 5.5 * ts))) / sr
env = np.clip((ts - 33) / 1.2, 0, 1) * np.clip((41.1 - ts) / .15, 0, 1) * (.6 + .4 * (ts - 33) / 8)
glide = (np.sin(ph) + .3 * np.sin(2 * ph) + .12 * np.sin(3 * ph)) * env
add(glide, ts[0], .07, .5, .6)
pad([43, 55, 59, 62], 33.2, 37.0, .07, fc=900)                    # G
pad([45, 57, 61, 64], 37.0, 41.0, .08, fc=1500)                   # A (D로 가기 직전의 끌림)
beat = 33.4; gap = .78
while beat < 40.95:                                              # 심장 박동: 점점 빠르게
    n = int(.3 * sr); tt = np.arange(n) / sr
    k = np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-tt * 30)) / sr) * np.exp(-tt * 12)
    add(k, beat, .30 * (.6 + .4 * (beat - 33) / 8), .5, .1); add(k, beat + gap * .28, .16, .5, .1)
    beat += gap; gap = max(.34, gap * .93)
swell(39.6, 1.45, .16, 9000)

# ---------- 5. 황금각 (41.5–52.5초) ----------
T5 = 41.45
impact(T5, .55, 37, 3.0)
pad([38, 50, 57, 62, 64, 66, 69, 74], T5, 46.3, .12, fc=3000, att=.25)   # D(add9) 활짝
for j, m in enumerate([62, 66, 69, 74, 78, 81, 86, 90]):                 # 위로 번지는 아르페지오
    bell(m, T5 + .05 + j * .07, .07, .2 + .6 * j / 7, 2.4, .7)
pad([45, 57, 61, 64, 69, 73], 46.3, 49.4, .10, fc=2600)                   # A
pad([47, 59, 62, 66, 71, 74], 49.4, 52.4, .10, fc=2600)                   # Bm
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
for i, v in enumerate(FIB):                                              # 피보나치 수열이 뜰 때
    bell([62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86][i], 47.2 + i * .06 + .1, .045, .2 + .6 * i / 10, 2.8, .7)
impact(46.5, .26, 45, 1.5); bell(81, 46.5, .12, .35); bell(85, 46.55, .06, .65)   # 21
impact(49.4, .26, 43, 1.5); bell(83, 49.4, .12, .65); bell(86, 49.45, .06, .35)   # 34
for x in np.arange(46.5, 52.3, 60 / 92):                                 # 부드러운 박
    n = int(.25 * sr); tt = np.arange(n) / sr
    add(np.sin(2 * np.pi * np.cumsum(48 + 50 * np.exp(-tt * 35)) / sr) * np.exp(-tt * 14), x, .20, .5, .1)
    add(hp(rng.standard_normal(int(.05 * sr)), 8000) * np.exp(-np.arange(int(.05 * sr)) / sr * 70), x + 60 / 184, .03, .7, .3)
swell(51.6, .9, .1)

# ---------- 결말 (52.5–60초) ----------
pad([43, 55, 59, 62, 66, 71], 52.5, 54.4, .10, fc=2200)                  # Gmaj7
pad([45, 57, 61, 64, 69, 76], 54.4, 55.4, .10, fc=2400)                  # A
pad([38, 50, 57, 62, 66, 69, 74, 78], 55.4, 59.0, .13, fc=3400, rel=2.5) # D — 해소
for j, m in enumerate([55, 59, 62, 66, 67, 71, 74, 78, 79, 83, 86, 90]): # 꽃잎이 필 때 하프 글리산도
    pluck(m, 52.7 + j * .14, .08, .15 + .7 * j / 11, 2.2, .6, .8)
impact(55.45, .5, 37, 3.2)
for j, m in enumerate([74, 78, 81, 86]): bell(m, 55.5 + j * .09, .08, .3 + .13 * j, 1.6, .75)
bell(90, 57.2, .05, .7, 1.4, .8)

# ---------- 공간감 (합성 잔향) ----------
def ir(seed, sec=2.8):
    n = int(sec * sr); tt = np.arange(n) / sr
    r = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 2.4); r = lp(r, 5200); return r / np.sqrt((r ** 2).sum())
wet = np.stack([fftconvolve(wetbus[0], ir(1))[:N], fftconvolve(wetbus[1], ir(2))[:N]])
mix = out + wet * .9
# 4장→5장 직전 정적 (41.05~41.45초)
gate = 1 - .92 * np.clip((t - 41.0) / .06, 0, 1) * np.clip((41.45 - t) / .02, 0, 1)
mix *= gate
mix = hp(mix, 30)
mix *= np.clip(t / .08, 0, 1) * np.clip((D - t) / 2.2, 0, 1)
mix = np.tanh(mix * 1.5) / np.tanh(1.5)
mix *= 10 ** (-1 / 20) / np.abs(mix).max()
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((mix.T * 32767).astype('<i2').tobytes()); w.close()
