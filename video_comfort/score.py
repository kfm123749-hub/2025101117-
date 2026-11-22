# 「찍어 갈 수 없는 것」 30초 음악 — 장면 시각에 맞춰 직접 작곡·합성 (numpy, scipy)
#  불안(낮은 드론 + 카메라 신호음) → 줌아웃 → 따뜻한 화음 → C장조의 응원으로 마무리
import numpy as np, wave, sys, math
from scipy.signal import butter, lfilter, fftconvolve
sr=44100; D=30.0; N=int(sr*D); t=np.arange(N)/sr
rng=np.random.default_rng(1119)
out=np.zeros((2,N)); wet=np.zeros((2,N))
hz=lambda m:440*2**((m-69)/12)
T=dict(zoom=4.5,field=7.6,one=8.3,pct=10.0,ten=11.5,rules=13.1,ring=19.1,close=25.4)
def lp(x,fc,o=2): b,a=butter(o,min(fc,sr*.45)/(sr/2)); return lfilter(b,a,x)
def hp(x,fc,o=2): b,a=butter(o,fc/(sr/2),'high'); return lfilter(b,a,x)
def add(sig,t0,g=1.,pan=.5,w=.4):
    i0=int(round(t0*sr))
    if i0>=N: return
    n=min(len(sig),N-i0); s=sig[:n]*g; l,r=math.cos(pan*math.pi/2)*1.41,math.sin(pan*math.pi/2)*1.41
    out[0,i0:i0+n]+=s*l*(1-w*.5); out[1,i0:i0+n]+=s*r*(1-w*.5); wet[0,i0:i0+n]+=s*l*w; wet[1,i0:i0+n]+=s*r*w
def pad(notes,a,b,g,fc=1800,att=.9,rel=1.3):
    i0,i1=int(max(0,a-att*.4)*sr),int(min(D,b+rel)*sr); tt=t[i0:i1]-a; n=len(tt)
    env=np.clip((tt+att*.4)/att,0,1)*np.clip((b-a+rel-tt)/rel,0,1); env=np.sin(env*np.pi/2)**2
    for j,m in enumerate(notes):
        f=hz(m); s=np.zeros(n)
        for d in (-.0035,0,.0035):
            ph=f*(1+d)*tt+rng.random(); s+=(2*(ph%1)-1)*.5+np.sin(2*np.pi*ph)*.5
        add(lp(s,fc)*env/3,max(0,a-att*.4),g,.5+.32*((j%2)*2-1)*(.4+.6*j/len(notes)),.6)
def bell(m,t0,g=.1,pan=.5,dec=2.0,w=.65):
    f=hz(m); n=int(4*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt+1.3*np.exp(-tt*4)*np.sin(2*np.pi*f*3.5*tt))*np.exp(-tt*dec)*np.minimum(1,tt/.004); add(s,t0,g,pan,w)
def soft(m,t0,g=.1,pan=.5,dec=1.8):                 # 둥근 건반음
    f=hz(m); n=int(3.5*sr); tt=np.arange(n)/sr
    s=(np.sin(2*np.pi*f*tt)+.3*np.sin(4*np.pi*f*tt)*np.exp(-tt*5)+.2*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*14))*np.exp(-tt*dec)*np.minimum(1,tt/.006); add(s,t0,g,pan,.6)
def impact(t0,g=.4,f0=44,dur=2.4):
    n=int(dur*sr); tt=np.arange(n)/sr; f=f0*(1+1.2*np.exp(-tt*9)); ph=2*np.pi*np.cumsum(f)/sr
    add((np.sin(ph)*np.exp(-tt*2.2)+lp(rng.standard_normal(n),800)*np.exp(-tt*12)*.4)*np.minimum(1,tt/.003),t0,g,.5,.35)
def tick(t0,f,g,pan=.5,dec=70):
    n=int(.08*sr); tt=np.arange(n)/sr; add(np.sin(2*np.pi*f*tt)*np.exp(-tt*dec),t0,g,pan,.4)
def swell(t0,dur,g=.1,f_end=6000,rev=False,p=2.2):
    n=int(dur*sr); x=rng.standard_normal(n); u=np.arange(n)/n
    if rev: u=1-u
    y=np.zeros(n); zi=np.zeros(2); ch=512
    for j in range(0,n,ch):
        b,a=butter(2,(200+f_end*u[j]**2)/(sr/2)); y[j:j+ch],zi=lfilter(b,a,x[j:j+ch],zi=zi)
    add(y*u**p,t0,g,.5,.6)

# ---------- 0. 불안 (0–4.5초) ----------
env0=np.clip(t/.4,0,1)*np.clip((5.0-t)/1.2,0,1)
dr=np.zeros(N)
for m,g in [(33,1.0),(45,.6),(46,.35),(57,.25)]:
    ph=hz(m)*t+rng.random(); dr+=g*((2*(ph%1)-1)*.5+np.sin(2*np.pi*ph)*.5)
add(lp(dr,700)*env0*(1-.25*(.5+.5*np.sin(2*np.pi*5.2/6.283*t))),0,.17,.5,.5)
for k in range(4):                                           # 붉은 점이 깜빡일 때마다 신호음
    x=.11+1.208*k; n=int(.5*sr); tt=np.arange(n)/sr
    add(np.sin(2*np.pi*1760*tt)*np.exp(-tt*14)*np.minimum(1,tt/.003),x,.075,.5,.7)
    add(np.sin(2*np.pi*1760*tt)*np.exp(-tt*14)*np.minimum(1,tt/.003),x+.14,.035,.5,.7)
impact(.15,.34,40,2.0)
# ---------- 1. 줌아웃과 숫자 (4.5–13.1초) ----------
swell(4.4,3.1,.26,7000)
pad([33,45,52,57,60],4.3,7.6,.11,fc=1100,att=1.6)
for k in range(26):                                          # 숫자가 올라가는 소리 (점점 느려지며 도착)
    x=5.3+2.3*(1-(1-k/25)**2.2); tick(x,1400+25*k,.045+.03*k/25,.35+.3*(k%2))
impact(7.6,.34,46,2.6); bell(77,7.62,.10,.4); bell(84,7.66,.05,.6)
pad([41,53,57,60,64],7.6,10.0,.13,fc=1700)                    # Fmaj7
soft(50,8.3,.10,.55,3.0); tick(8.3,620,.05,.55,30)            # 붉은 점 하나
pad([36,48,55,60,64,67],10.0,11.5,.13,fc=2000)                # C
bell(84,10.02,.11,.5,1.8); bell(88,10.06,.05,.6,1.8)          # 0.018%
pad([38,50,57,60,65],11.5,13.1,.12,fc=1700)                   # Dm7
for k in range(9): tick(11.5+.07*k,700+40*k,.035,.3+.05*k,40) # 붉은 점 아홉 개 더
bell(81,12.0,.08,.5,1.8)
# ---------- 2. 규칙 (13.1–19.1초) ----------
pad([33,45,52,57,60,64],13.1,16.2,.13,fc=1800)                # Am7
pad([41,53,57,60,65,69],16.2,19.1,.14,fc=2100)                # F
swell(13.4,2.3,.07,5000,p=1.2)                                # 훑고 지나가는 빛
for k,(x,m) in enumerate([(13.65,72),(14.75,76),(15.85,79)]): soft(m,x,.13,.35+.15*k,1.6); tick(x,2400,.025,.5,120)
bell(81,17.0,.07,.5,1.8)
# ---------- 3. 내가 바꿀 수 있는 것 (19.1–25.4초) ----------
swell(18.6,2.6,.09,8000,p=1.6)
pad([36,48,55,60,64,67,72],19.1,22.3,.16,fc=2500)             # C
pad([43,55,59,62,67,71],22.3,25.4,.15,fc=2500)                # G
for j,m in enumerate([60,64,67,72,76,79]): soft(m,19.9+j*.17,.06,.2+.6*j/5,1.6)   # 점들이 모이는 동안
for k,(x,m) in enumerate([(21.2,76),(21.75,79),(22.3,84)]): soft(m,x,.13,.4+.1*k,1.5); bell(m+12,x+.02,.03,.6-.1*k,2.0)
bell(79,22.6,.06,.5,1.8)
# ---------- 4. 마무리 (25.4–30초) ----------
pad([41,53,57,60,65,69,72],25.4,27.6,.16,fc=2800)             # F
pad([36,48,55,60,64,67,72,74],27.6,30.0,.18,fc=3200,rel=1.2)  # C(add9)
for x,m,pn in [(25.7,72,.4),(26.4,76,.5),(26.9,79,.6)]: soft(m,x,.11,pn,1.6)
impact(27.7,.32,43,2.8)
for j,m in enumerate([60,64,67,72,74,79,84]): bell(m,27.72+j*.075,.06,.2+.6*j/6,1.5,.75)

def ir(seed,sec=2.8):
    n=int(sec*sr); tt=np.arange(n)/sr; r=np.random.default_rng(seed).standard_normal(n)*np.exp(-tt*2.3); r=lp(r,5000); return r/np.sqrt((r**2).sum())
mix=out+np.stack([fftconvolve(wet[0],ir(1))[:N],fftconvolve(wet[1],ir(2))[:N]])*.9
mix=hp(mix,28); mix*=np.clip(t/.02,0,1)*np.clip((D-t)/1.8,0,1)
mix=np.tanh(mix*1.5)/np.tanh(1.5); mix*=10**(-1/20)/np.abs(mix).max()
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix.T*32767).astype('<i2').tobytes()); w.close()
