# 「해왕성의 1년」 20초 음악 — 화면과 같은 시간축(timeline.js)을 그대로 옮겨 작곡·합성
#  · 지구가 한 바퀴 돌 때마다 '똑' 소리 1개 → 시간이 빨라지면 소리가 이어져 하나의 음처럼 들림
#  · D단조에서 출발해 해왕성이 한 바퀴를 마치는 순간 D장조로 해소
import numpy as np, wave, sys, math
from scipy.signal import butter, lfilter, fftconvolve
sr=44100; D=20.0; N=int(sr*D); t=np.arange(N)/sr
rng=np.random.default_rng(1846)
out=np.zeros((2,N)); wet=np.zeros((2,N))
hz=lambda m:440*2**((m-69)/12)
def lp(x,fc,o=2): b,a=butter(o,min(fc,sr*.45)/(sr/2)); return lfilter(b,a,x)
def hp(x,fc,o=2): b,a=butter(o,fc/(sr/2),'high'); return lfilter(b,a,x)
def add(sig,t0,g=1.,pan=.5,w=.4):
    i0=int(round(t0*sr))
    if i0>=N: return
    n=min(len(sig),N-i0); s=sig[:n]*g; l,r=math.cos(pan*math.pi/2)*1.41,math.sin(pan*math.pi/2)*1.41
    out[0,i0:i0+n]+=s*l*(1-w*.5); out[1,i0:i0+n]+=s*r*(1-w*.5); wet[0,i0:i0+n]+=s*l*w; wet[1,i0:i0+n]+=s*r*w

# ---------- 화면과 같은 시간축 ----------
NEP=164.79
def io3(x): return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
def years(x):
    c=lambda v:min(1,max(0,v))
    if x<2.8: return .03*x
    if x<7.4: return .084+(1-.084)*io3(c((x-2.8)/4.6))
    if x<8.6: return 1.
    if x<11.0: return 40**c((x-8.6)/2.4)
    s=c((x-11.0)/4.8); return 40+(NEP-40)*(1-(1-s)**2.2)
DONE=15.79

def pad(notes,a,b,g,fc=1600,att=.6,rel=1.0):
    i0,i1=int(max(0,a-.2)*sr),int(min(D,b+rel)*sr); tt=t[i0:i1]-a; n=len(tt)
    env=np.clip((tt+.2)/att,0,1)*np.clip((b-a+rel-tt)/rel,0,1); env=np.sin(env*np.pi/2)**2
    for j,m in enumerate(notes):
        f=hz(m); s=np.zeros(n)
        for d in (-.004,0,.004):
            ph=f*(1+d)*tt+rng.random(); s+=(2*(ph%1)-1)*.55+np.sin(2*np.pi*ph)*.45
        add(lp(s,fc)*env/3,max(0,a-.2),g,.5+.3*((j%2)*2-1)*(.4+.6*j/len(notes)),.55)
def bell(m,t0,g=.1,pan=.5,dec=2.0,w=.65,ratio=3.5):
    f=hz(m); n=int(4*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt+1.5*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt))*np.exp(-tt*dec)*np.minimum(1,tt/.003); add(s,t0,g,pan,w)
def ping(m,t0,g=.12,pan=.5):                       # 해왕성 신호음 (수중 음파 느낌)
    f=hz(m); n=int(3*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt*(1-.02*tt))*np.exp(-tt*1.8)*np.minimum(1,tt/.004); add(s,t0,g,pan,.8)
def impact(t0,g=.5,f0=40,dur=2.6):
    n=int(dur*sr); tt=np.arange(n)/sr; f=f0*(1+1.3*np.exp(-tt*9)); ph=2*np.pi*np.cumsum(f)/sr
    s=np.sin(ph)*np.exp(-tt*2)+lp(rng.standard_normal(n),900)*np.exp(-tt*11)*.5; add(s*np.minimum(1,tt/.002),t0,g,.5,.35)
def tick(t0,f,g,pan):
    n=int(.07*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt)*np.exp(-tt*55)+hp(rng.standard_normal(n),5000)*np.exp(-tt*160)*.35; add(s,t0,g,pan,.35)
def swell(t0,dur,g=.12,f_end=7000):
    n=int(dur*sr); x=rng.standard_normal(n); y=np.zeros(n); zi=np.zeros(2); ch=1024
    for j in range(0,n,ch):
        b,a=butter(2,(200+f_end*(j/n)**2.2)/(sr/2)); y[j:j+ch],zi=lfilter(b,a,x[j:j+ch],zi=zi)
    add(y*(np.arange(n)/n)**2.5,t0,g,.5,.6)

# ---------- 훅 0–2.8 ----------
impact(0.02,.38,36,3.0)
pad([38,50,57,60,64,69],0,2.8,.11,fc=1200)              # Dm(add9)
ping(81,.55,.13,.75); ping(81,1.55,.09,.75)              # 해왕성 신호 고리와 같은 시점
# ---------- 지구 1년 2.8–8.6 ----------
pad([34,46,53,57,62,65],2.8,7.4,.19,fc=1800)             # B♭maj7
for x in np.arange(3.0,7.4,.5): tick(x,1900,.09,.42+.16*((x*2)%2))   # 시계 초침
bell(86,7.4,.12,.4); bell(90,7.45,.06,.6)                # 지구 1바퀴 완료
pad([43,55,58,62,69],7.4,8.6,.10,fc=900)                 # Gm(add9): 2.2°의 정지
ping(74,7.45,.10,.75)
# ---------- 시간 가속 8.6–15.79: 지구 1년마다 '똑' ----------
grid=np.arange(8.6,DONE+.001,1/4000); yy=np.array([years(x) for x in grid])
cross=grid[1:][np.floor(yy[1:]+1e-9)>np.floor(yy[:-1]+1e-9)]
SC=[62,64,65,69,72,74,76,77,81,84,86,88]
for k,x in enumerate(cross):
    rate=(years(x+.02)-years(x-.02))/.04
    m=SC[k%len(SC)]+(12 if rate>25 else 0)
    tick(x,hz(m),.08+.07*min(1,rate/50),.25+.5*((k*7)%11)/10)
swell(8.4,2.6,.13,9000)
# 시간의 소리: 1초에 흐르는 년수(속도)를 그대로 음 높이로 — 빨라지면 올라가고, 도착하며 내려감
seg_=(t>=8.6)&(t<DONE+.05); ts=t[seg_]
rate=np.interp(ts,grid[1:],np.diff(yy)*4000)
f=110*2**(np.log2(1+rate)/2.3)
ph=2*np.pi*np.cumsum(f)/sr
amp=np.clip(rate/55,0,1)**.8*np.clip((DONE+.05-ts)/.12,0,1)
hum=(np.sin(ph)+.35*np.sin(2*ph)+.15*np.sin(3*ph))*amp
add(lp(hum,2500),ts[0],.11,.5,.5)
pad([38,50,57,62,65],8.6,11.0,.11,fc=1500)               # Dm
pad([34,46,53,58,62,65],11.0,13.6,.11,fc=1900)           # B♭
pad([36,48,55,60,64,67],13.6,DONE,.12,fc=2300)           # C (해소 직전의 끌림)
for x,m,p in [(11.31,81,.25),(12.87,84,.5),(13.63,88,.75)]: bell(m,x,.10,p); bell(m+7,x+.05,.04,1-p)   # 1903·1969·1989
ping(86,13.63,.10,.8)                                     # 보이저 2호
swell(14.2,1.6,.10,6000)
# ---------- 완주 15.79: D장조 ----------
impact(DONE-.01,.55,36,3.2)
pad([38,50,57,62,66,69,74,78],DONE,19.0,.15,fc=3200,att=.15,rel=1.6)
for j,m in enumerate([62,66,69,74,78,81,86,90]): bell(m,DONE+.04+j*.06,.07,.15+.7*j/7,1.8,.75)
# ---------- 결말 17.4–20 ----------
for x,m in [(17.45,74),(17.95,78),(18.3,81)]: bell(m,x,.08,.5,1.6,.75)

def ir(seed,sec=2.6):
    n=int(sec*sr); tt=np.arange(n)/sr; r=np.random.default_rng(seed).standard_normal(n)*np.exp(-tt*2.5); r=lp(r,5200); return r/np.sqrt((r**2).sum())
mix=out+np.stack([fftconvolve(wet[0],ir(1))[:N],fftconvolve(wet[1],ir(2))[:N]])*.9
mix=hp(mix,30); mix*=np.clip(t/.03,0,1)*np.clip((D-t)/1.6,0,1)
mix=np.tanh(mix*1.5)/np.tanh(1.5); mix*=10**(-1/20)/np.abs(mix).max()
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix.T*32767).astype('<i2').tobytes()); w.close()
print('지구 공전 틱 개수:',len(cross))
