# =============================================================
# 21번 문제 풀이 그래프 그리기
#   f(x) = (x-α)²(x-β)          … (가) 서로 다른 실근 2개
#   g(x) = -f(x)  (f(x) ≥ 0)
#          7f(x)  (f(x) < 0)
#   p(x) = (x-1)(x-a)(x-4+a)
#   h(x) = g(x) + |p(x)|         … (나) 실수 전체에서 미분가능
#
# 실행 방법:  python3 q21_graphs.py
# 결과: 같은 폴더에 그림 5장(fig1 ~ fig5)이 저장됩니다.
# =============================================================

import os
from fractions import Fraction        # 분수를 오차 없이 계산하는 도구

import numpy as np                    # 숫자 배열(그래프의 x값 수백 개)을 다루는 도구
import matplotlib
matplotlib.use("Agg")                 # 화면 없이 그림 파일로만 저장하는 모드
import matplotlib.pyplot as plt
from matplotlib import font_manager

# -------------------------------------------------------------
# 0. 한글 글꼴 설정 (없으면 기본 글꼴로 그림 → 한글이 깨질 수 있음)
# -------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/nanum/"
for name in ["NanumBarunGothic.ttf", "NanumBarunGothicBold.ttf"]:
    if os.path.exists(FONT_DIR + name):
        font_manager.fontManager.addfont(FONT_DIR + name)
plt.rcParams.update({
    "font.family": "NanumBarunGothic",
    "axes.unicode_minus": False,      # 마이너스 기호 깨짐 방지
    "font.size": 11,
    "axes.spines.top": False,         # 위·오른쪽 테두리 제거 (깔끔하게)
    "axes.spines.right": False,
})

# 색상 이름 정해 두기
BLUE, RED, GREEN, GRAY, INK = "#2563eb", "#dc2626", "#059669", "#9ca3af", "#111827"
OUT = os.path.dirname(os.path.abspath(__file__))   # 그림을 저장할 폴더 = 이 파일이 있는 폴더


# -------------------------------------------------------------
# 1. 문제에 나오는 함수들을 파이썬 함수로 옮기기
# -------------------------------------------------------------
def f(x, al, be):
    """f(x) = (x-α)²(x-β)"""
    return (x - al) ** 2 * (x - be)

def g(x, al, be):
    """f ≥ 0 이면 -f, f < 0 이면 7f  (np.where = 조건에 따라 둘 중 하나 고르기)"""
    fx = f(x, al, be)
    return np.where(fx >= 0, -fx, 7 * fx)

def p(x, a):
    """p(x) = (x-1)(x-a)(x-4+a)"""
    return (x - 1) * (x - a) * (x - 4 + a)

def h(x, al, be, a):
    """h(x) = g(x) + |p(x)|"""
    return g(x, al, be) + np.abs(p(x, a))

def one_sided_slopes(func, c, eps=1e-7):
    """x=c 에서의 (좌미분계수, 우미분계수)를 수치로 근사.
       좌: (F(c) - F(c-eps)) / eps,  우: (F(c+eps) - F(c)) / eps"""
    left = (func(c) - func(c - eps)) / eps
    right = (func(c + eps) - func(c)) / eps
    return float(left), float(right)


# -------------------------------------------------------------
# 2. 조건을 만족하는 경우들 (풀이에서 구한 값)
#    a=3 은 p(x)가 a=1 일 때와 똑같으므로 a=1 로 대표
# -------------------------------------------------------------
CASES = [
    # (α,  β,  a,  이름)
    (4.0, 3.0, 1, "α=4, β=3, a=1(또는 3)"),
    (2.0, 3.0, 1, "α=2, β=3, a=1(또는 3)"),
    (1.5, 1.0, 2, "α=3/2, β=1, a=2"),
    (0.5, 1.0, 2, "α=1/2, β=1, a=2"),
]


# =============================================================
# 그림 1: 네 경우 각각의 f(x)와 g(x)
#   → g는 중근 α에서는 매끄럽고, 단일근 β에서만 꺾인다
# =============================================================
fig, axs = plt.subplots(2, 2, figsize=(11, 9))
for ax, (al, be, a, title) in zip(axs.flat, CASES):
    lo, hi = min(al, be) - 1.2, max(al, be) + 1.0          # 보여줄 x 범위
    x = np.linspace(lo, hi, 1000)                           # x값 1000개
    ax.plot(x, f(x, al, be), "--", color=GRAY, lw=1.5, label="f(x)")
    ax.plot(x, g(x, al, be), color=BLUE, lw=2.5, label="g(x)")
    ax.axhline(0, color="#ddd", lw=1)                       # x축

    ax.plot(al, 0, "o", color=GREEN, ms=8, zorder=5)
    ax.annotate("α (중근)", (al, 0), (8, 10), textcoords="offset points", color=GREEN)
    ax.plot(be, 0, "o", color=RED, ms=8, zorder=5)
    ax.annotate("β (단일근, 꺾임)", (be, 0), (8, -18), textcoords="offset points", color=RED)

    # β에서 g의 좌우 기울기를 계산해서 적어 두기
    gl, gr = one_sided_slopes(lambda t: g(t, al, be), be)
    ax.text(0.03, 0.05, f"x=β에서 g 기울기\n왼쪽 {gl:.2f} → 오른쪽 {gr:.2f}",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round", fc="#eff6ff", ec=BLUE))

    yr = max(abs(f(np.array([lo, hi]), al, be)).max(), 1)   # y 범위를 적당히 자르기
    ax.set_ylim(-min(7 * yr, 12), min(yr, 4))
    ax.set_title(title, fontweight="bold")
    ax.legend(loc="upper left", frameon=False)
fig.suptitle("그림 1. f(x)와 g(x) — g는 x=β 한 곳에서만 꺾인다", fontsize=15, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/fig1_f_and_g.png", dpi=150)
plt.close(fig)


# =============================================================
# 그림 2: a 값에 따른 |p(x)| 모양
#   → 근이 3개 다르면 꺾임 3개(불가), 중근이 생기면 꺾임 1개
# =============================================================
fig, axs = plt.subplots(2, 2, figsize=(11, 8.5))
A_LIST = [
    (2.5, "a=2.5: 근 1, 1.5, 2.5 → 꺾임 3개 (불가)", GRAY),
    (0.0, "a=0: 근 0, 1, 4 → 꺾임 3개 (불가)", GRAY),
    (1.0, "a=1 (또는 3): (x-1)²(x-3) → x=3 한 곳", RED),
    (2.0, "a=2: (x-1)(x-2)² → x=1 한 곳", GREEN),
]
x = np.linspace(-0.8, 4.8, 1200)
for ax, (a, title, col) in zip(axs.flat, A_LIST):
    ax.plot(x, np.abs(p(x, a)), color=col, lw=2.5, label="|p(x)|")
    ax.plot(x, p(x, a), ":", color=GRAY, lw=1.2, label="p(x)")
    ax.axhline(0, color="#ddd", lw=1)
    # 꺾이는 점 = p의 단일근. 근 목록에서 한 번만 나오는 값 찾기
    roots = [1, a, 4 - a]
    for k, r in enumerate(sorted(set(roots))):
        if roots.count(r) == 1:
            ax.plot(r, 0, "o", color=RED, ms=8, zorder=5)
            sl, sr = one_sided_slopes(lambda t: np.abs(p(t, a)), r)
            ax.annotate(f"꺾임\n{sl:.1f}→{sr:.1f}", (r, 0), (-10, 18 + 30 * (k % 2)),   # 글자 겹침 방지
                        textcoords="offset points", fontsize=9, color=RED)
    ax.set_ylim(-3, 6)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
fig.suptitle("그림 2. |p(x)|는 p의 '단일근'에서만 꺾인다 (중근에서는 매끄러움)",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/fig2_abs_p.png", dpi=150)
plt.close(fig)


# =============================================================
# 그림 3: x=β 근처 확대 + 좌·우 접선
#   → g의 꺾임과 |p|의 꺾임이 정확히 상쇄되어 h가 매끄러워짐
# =============================================================
fig, axs = plt.subplots(2, 2, figsize=(11, 9.5))
for ax, (al, be, a, title) in zip(axs.flat, CASES):
    d = 0.35                                           # β 좌우로 볼 폭
    xl = np.linspace(be - d, be, 300)                  # β 왼쪽
    xr = np.linspace(be, be + d, 300)                  # β 오른쪽
    x = np.linspace(be - d, be + d, 600)

    funcs = [
        ("g", lambda t: g(t, al, be), BLUE, 2),
        ("|p|", lambda t: np.abs(p(t, a)), RED, 2),
        ("h", lambda t: h(t, al, be, a), INK, 3),
    ]
    lines = []
    for name, F, col, lw in funcs:
        ax.plot(x, F(x), color=col, lw=lw, label=name)
        sl, sr = one_sided_slopes(F, be)
        y0 = float(F(be))
        # 왼쪽 접선(점선)과 오른쪽 접선(점선)을 β에서 그려 보기
        ax.plot(xl, y0 + sl * (xl - be), "--", color=col, lw=1, alpha=0.6)
        ax.plot(xr, y0 + sr * (xr - be), "--", color=col, lw=1, alpha=0.6)
        lines.append(f"{name:>3}:  왼쪽 {sl:6.2f}  오른쪽 {sr:6.2f}")
    ax.axvline(be, color="#ddd", lw=1)
    ax.plot(be, 0, "o", color=RED, ms=6)
    ax.text(0.02, 0.97, "x=β에서 기울기\n" + "\n".join(lines), transform=ax.transAxes,
            va="top", fontsize=9.5,
            bbox=dict(boxstyle="round", fc="white", ec="#d1d5db"))
    ax.set_title(title + "  (β 근처 확대)", fontweight="bold", fontsize=11)
    ax.legend(loc="lower right", frameon=False)
fig.suptitle("그림 3. 꺾임 상쇄: g의 기울기 변화 + |p|의 기울기 변화 = 0",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/fig3_cancel_zoom.png", dpi=150)
plt.close(fig)


# =============================================================
# 그림 4: h(x) 전체 모습 — 정답 경우(매끄러움) vs 반례(꺾임)
# =============================================================
fig, axs = plt.subplots(3, 2, figsize=(11, 12.5))
SHOW = CASES + [
    (1.0, 3.0, 1, "반례 α=1, β=3, a=1  → x=3에서 꺾임"),
    (2.0, 3.0, 2.5, "반례 α=2, β=3, a=2.5 → 여러 곳에서 꺾임"),
]
for ax, (al, be, a, title) in zip(axs.flat, SHOW):
    x = np.linspace(-0.5, 5, 1500)
    y = h(x, al, be, a)
    ok = "반례" not in title
    ax.plot(x, y, color=INK if ok else RED, lw=2.5)
    ax.axhline(0, color="#ddd", lw=1)
    # 꺾임 후보점(α, β, 1, a, 4-a)마다 좌우 기울기 차이를 계산해 표시
    for k, c in enumerate(sorted({al, be, 1, a, 4 - a})):
        sl, sr = one_sided_slopes(lambda t: h(t, al, be, a), c)
        jump = sr - sl
        if abs(jump) > 1e-3:                   # 기울기가 다르면 → 미분 불가능(꺾임)
            ax.plot(c, float(h(c, al, be, a)), "x", color=RED, ms=12, mew=3)
            ax.annotate(f"꺾임 (차이 {jump:.1f})", (c, float(h(c, al, be, a))),
                        (-70 if k % 2 else 8, 12 if k % 2 else -18),   # 글자 겹침 방지
                        textcoords="offset points", color=RED, fontsize=9)
    ax.set_ylim(-15, 15)
    ax.set_title(("정답: " if ok else "") + title, fontweight="bold", fontsize=11,
                 color=INK if ok else RED)
fig.suptitle("그림 4. h(x) = g(x) + |p(x)| — 정답 4가지는 모두 매끄럽다",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/fig4_h_graphs.png", dpi=150)
plt.close(fig)


# =============================================================
# 그림 5: f(0) = -α²β 값을 수직선에 표시하고 답 계산
#   Fraction 으로 계산해서 소수 오차 없이 정확한 값 확인
# =============================================================
exact = [(Fraction(4), Fraction(3)), (Fraction(2), Fraction(3)),
         (Fraction(3, 2), Fraction(1)), (Fraction(1, 2), Fraction(1))]
f0 = [-(al ** 2) * be for al, be in exact]          # f(0) = (0-α)²(0-β) = -α²β
mx, mn = max(f0), min(f0)

fig, ax = plt.subplots(figsize=(11, 3.2))
ax.axhline(0, color=INK, lw=1.2)
for i, ((al, be), v) in enumerate(zip(exact, f0)):
    col = RED if v in (mx, mn) else GRAY
    ax.plot(float(v), 0, "o", color=col, ms=11, zorder=5)
    dy = 0.6 if i % 2 == 0 else -0.7
    ax.text(float(v), dy, f"{v}\n(α={al}, β={be})", ha="center", va="center", color=col)
ax.set_xlim(-52, 5); ax.set_ylim(-1.2, 1.4)
ax.axis("off")
ax.set_title(f"그림 5. f(0)의 최댓값 {mx}, 최솟값 {mn}  →  곱 = {mx * mn}",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/fig5_answer.png", dpi=150)
plt.close(fig)

print("f(0) 후보:", [str(v) for v in f0])
print("최댓값 × 최솟값 =", mx * mn)
print("그림 저장 위치:", OUT)
