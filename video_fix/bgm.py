# AI 가성비 설명 영상용 배경음 (직접 합성, 저작권 문제 없음)
# 112 BPM 미니멀 일렉트로닉: 패드 + 플럭 아르페지오 + 서브 베이스 + 소프트 킥/하이햇
# 장면 경계(6·16·27·38·47·55초)와 화면 강조 시점에 효과음을 맞춤
import numpy as np, wave, sys
from scipy.signal import butter, lfilter, fftconvolve

sr = 44100; D = 60.0; N = int(sr * D); t = np.arange(N) / sr
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): b, a = butter(o, fc / (sr / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (sr / 2), 'high'); return lfilter(b, a, x)
def put(sig, t0, gl, gr=None):
    gr = gl if gr is None else gr
    i0 = int(t0 * sr)
    if i0 >= N: return
    n = min(len(sig), N - i0)
    if i0 < 0: sig = sig[-i0:]; n = min(len(sig), N); i0 = 0
    L[i0:i0 + n] += gl * sig[:n]; R[i0:i0 + n] += gr * sig[:n]

BPM = 112; BEAT = 60 / BPM; BAR = 4 * BEAT; T0 = 6.0
SC = [0, 6, 16, 27, 38, 47, 55, 60]          # 장면 경계

# ---------- 화음 진행 ----------
# 훅: Am(add9) / 본문: Am - F - C - G 반복 / 주의할 점: Am - Am/G - F - E / 결론: F - G - C
Am = [45, 52, 57, 60, 64, 71]; F = [41, 53, 57, 60, 64, 69]; Cc = [48, 52, 55, 60, 64, 67]; G = [43, 50, 55, 59, 62, 67]
AmG = [43, 52, 57, 60, 64, 69]; Ee = [40, 52, 56, 59, 64, 68]
chords = [(0, 6, Am)]
x = T0; loop = [Am, F, Cc, G]; k = 0
while x < 47 - 1e-6:
    e = min(x + BAR, 47); chords.append((x, e, loop[k % 4])); x = e; k += 1
for c, (a, b) in zip([Am, AmG, F, Ee], [(47, 49), (49, 51), (51, 53), (53, 55)]): chords.append((a, b, c))
chords += [(55, 56.6, F), (56.6, 57.6, G), (57.6, 60, Cc)]
def chord_at(s):
    for a, b, c in chords:
        if a <= s < b: return c
    return chords[-1][2]

# ---------- 패드 ----------
pad = np.zeros((2, N))
for a, b, c in chords:
    i0, i1 = int(max(0, a - .25) * sr), int(min(D, b + .35) * sr)
    tt = t[i0:i1]; n = len(tt)
    env = np.minimum(1, np.minimum((tt - (a - .25)) / .5, ((b + .35) - tt) / .5)).clip(0, 1)
    for ch, det in ((0, -1), (1, 1)):
        s = np.zeros(n)
        for m in c[1:]:
            f = hz(m)
            for dd in (-.09, .09):
                ph = (f * (1 + det * 0.0015 + dd * 0.01)) * tt
                s += 2 * (ph % 1) - 1
        fc = 900 if a < 6 else (650 if 47 <= a < 55 else 1500)
        pad[ch, i0:i1] += lp(s, fc) * env
pad *= 0.022

# ---------- 서브 베이스 (8분음표, 본문에서만) ----------
bass = np.zeros(N)
for i in range(int((47 - T0) / (BEAT / 2))):
    s0 = T0 + i * BEAT / 2
    if s0 < 7.0: continue
    root = chord_at(s0 + .01)[0]
    f = hz(root - 12 if root > 44 else root)
    n = int(BEAT / 2 * sr * .92); tt = np.arange(n) / sr
    env = np.minimum(1, tt / .008) * np.exp(-tt * 3.5)
    put_i = int(s0 * sr); seg = env * (np.sin(2 * np.pi * f * tt) + .25 * np.sin(4 * np.pi * f * tt))
    bass[put_i:put_i + n] += seg[:max(0, min(n, N - put_i))]
bass = np.tanh(bass * 1.4) * 0.10

# ---------- 킥 · 하이햇 ----------
def kick():
    n = int(.38 * sr); tt = np.arange(n) / sr
    f = 45 + 85 * np.exp(-tt * 28); ph = 2 * np.pi * np.cumsum(f) / sr
    return np.sin(ph) * np.exp(-tt * 9) * np.minimum(1, tt / .002)
def hat(dec=55):
    n = int(.09 * sr); tt = np.arange(n) / sr
    return hp(rng.standard_normal(n), 7500) * np.exp(-tt * dec)
K = kick(); duck = np.ones(N); kicks = []
nb = int((47 - T0) / BEAT)
for i in range(nb):
    s0 = T0 + i * BEAT
    if s0 < 16.0: continue                     # 킥은 2장(16초)부터
    put(K, s0, .34); kicks.append(s0)
for i in range(int((47 - T0) / (BEAT / 2))):
    s0 = T0 + i * BEAT / 2
    if s0 < 6.5: continue
    off = i % 2 == 1
    v = (.05 if off else .018) * (1.0 if s0 >= 16 else .6)
    put(hat(), s0, v * (.8 if i % 4 == 1 else 1.1), v * (1.1 if i % 4 == 1 else .8))
    if 38 <= s0 < 47:                           # 4장: 16분음표로 속도감
        put(hat(80), s0 + BEAT / 4, .016)
for k0 in kicks:                                # 사이드체인 느낌의 펌핑
    i0 = int(k0 * sr); n = int(BEAT * sr); tt = np.arange(n) / sr
    n = min(n, N - i0); duck[i0:i0 + n] *= 1 - .55 * np.exp(-tt[:n] / .11)

# ---------- 플럭 아르페지오 (16분음표) ----------
arp = np.zeros((2, N)); step = BEAT / 4; pat = [0, 2, 4, 3, 1, 3, 4, 5]
for i in range(int((55 - T0) / step)):
    s0 = T0 + i * step
    if s0 < 7.6: continue
    c = chord_at(s0 + .01); tones = sorted(c[2:])
    m = tones[pat[i % 8] % len(tones)] + (12 if (i // 8) % 2 else 0)
    if 47 <= s0 < 55: m -= 12                   # 주의할 점: 낮고 어둡게
    f = hz(m); n = int(.5 * sr); tt = np.arange(n) / sr
    tri = 2 * np.abs(2 * ((f * tt) % 1) - 1) - 1
    s = (np.sin(2 * np.pi * f * tt) + .45 * tri) * np.exp(-tt * (16 if s0 < 38 else 20)) * np.minimum(1, tt / .003)
    v = .055 * (.55 + .45 * min(1, (s0 - 7.6) / 8)) * (1.15 if i % 4 == 0 else 1)
    p = .5 + .25 * np.sin(i * .9)
    i0 = int(s0 * sr); nn = min(n, N - i0)
    arp[0, i0:i0 + nn] += v * (1 - p) * 2 * s[:nn]; arp[1, i0:i0 + nn] += v * p * 2 * s[:nn]
arp = np.stack([lp(arp[0], 4200), lp(arp[1], 4200)])
dly = int(BEAT * .75 * sr)                      # 점8분 핑퐁 딜레이
echo = np.zeros_like(arp)
for k, g in ((1, .32), (2, .14), (3, .06)):
    src = arp[(k + 1) % 2]; echo[k % 2, k * dly:] += g * src[:N - k * dly]
arp += np.stack([lp(echo[0], 2600), lp(echo[1], 2600)])

# ---------- 효과음 ----------
fx = np.zeros((2, N))
def fxput(sig, t0, gl, gr=None):
    gr = gl if gr is None else gr; i0 = int(t0 * sr); n = min(len(sig), N - i0)
    if i0 < 0: return
    fx[0, i0:i0 + n] += gl * sig[:n]; fx[1, i0:i0 + n] += gr * sig[:n]
def riser(dur):                                  # 장면 직전 상승 노이즈
    n = int(dur * sr); tt = np.arange(n) / sr; out = np.zeros(n); x = rng.standard_normal(n)
    ch = 2048; zi = None
    for j in range(0, n, ch):
        fc = 300 + 6500 * (j / n) ** 2; b, a = butter(2, fc / (sr / 2))
        if zi is None: zi = np.zeros(max(len(a), len(b)) - 1)
        out[j:j + ch], zi = lfilter(b, a, x[j:j + ch], zi=zi)
    return out * (tt / dur) ** 2.2
def impact(sub=55, dur=1.6):                    # 강조 순간의 낮은 붐
    n = int(dur * sr); tt = np.arange(n) / sr
    f = sub * (1 + .9 * np.exp(-tt * 9)); ph = 2 * np.pi * np.cumsum(f) / sr
    body = np.sin(ph) * np.exp(-tt * 3.2)
    noise = lp(rng.standard_normal(n), 1800) * np.exp(-tt * 14) * .6
    return (body + noise) * np.minimum(1, tt / .002)
def chime(m, dur=2.4):                          # 숫자 등장 시 맑은 벨
    n = int(dur * sr); tt = np.arange(n) / sr; f = hz(m)
    mod = np.sin(2 * np.pi * f * 2.0 * tt) * 1.2 * np.exp(-tt * 6)
    return np.sin(2 * np.pi * f * tt + mod) * np.exp(-tt * 3.4) * np.minimum(1, tt / .003)
def tick():
    n = int(.05 * sr); tt = np.arange(n) / sr
    return np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 90)

for b in [6, 16, 27, 38, 47, 55]:
    fxput(riser(1.1), b - 1.1, .05)
    fxput(impact(48 if b != 47 else 41), b + .05, .26)
fxput(riser(1.0), 0.4, .04); fxput(impact(46, 2.2), 1.4, .40)     # 7.9배 등장
fxput(chime(81), 1.4, .10, .12); fxput(chime(88), 1.45, .05, .04)
fxput(chime(76), 3.9, .07)                                          # 부제 등장
for t0, m, p in [(7.6, 76, .4), (12.5, 79, .6), (19.4, 83, .5), (21.0, 86, .5), (23.3, 88, .55),
                 (29.0, 76, .4), (33.4, 81, .6), (40.5, 83, .45), (44.4, 86, .55),
                 (49.7, 74, .5), (51.0, 69, .5),
                 (55.4, 72, .5), (56.0, 76, .4), (56.7, 79, .6)]:
    fxput(chime(m), t0, .085 * (1 - p) * 2, .085 * p * 2)
for t0 in (55.95, 56.65): fxput(tick(), t0, .05)
fxput(impact(43, 2.5), 57.6, .30)                                   # 그게 가성비입니다
for m, d in ((84, 0), (88, .08), (91, .16), (96, .26)): fxput(chime(m, 3), 57.6 + d, .06)

# ---------- 리버브 (합성 임펄스) ----------
def reverb(x, sec=2.2, seed=1):
    n = int(sec * sr); tt = np.arange(n) / sr
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 3.1); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    return fftconvolve(x, ir)[:N]
wetsrc = pad * .8 + arp * .9 + fx * 1.0
wet = np.stack([reverb(wetsrc[0], seed=1), reverb(wetsrc[1], seed=2)]) * .55

mix = np.stack([L, R])
mix[0] += (pad[0] + bass * .9) * duck + arp[0] + fx[0] + wet[0]
mix[1] += (pad[1] + bass * .9) * duck + arp[1] + fx[1] + wet[1]
mix = hp(mix, 28)
# 마스터: 시작 페이드, 끝 2초 페이드아웃, 소프트 리미터
mix *= np.clip(t / .25, 0, 1) * np.clip((D - t) / 2.0, 0, 1)
mix = np.tanh(mix * 1.6) / np.tanh(1.6)
mix *= 10 ** (-1.0 / 20) / np.abs(mix).max()
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((mix.T * 32767).astype('<i2').tobytes()); w.close()
