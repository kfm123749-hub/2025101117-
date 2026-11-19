# 「60초 상대성 이론」 오르간 편곡 — 직접 작곡한 곡 (기존 영화음악의 멜로디·화성 진행을 쓰지 않음)
#  · 파이프 오르간: 음전(스톱)별 배음을 더해 합성 + 건반을 누를 때의 '칩' 소리 + 성당 잔향
#  · 1초 간격의 느린 시계 째깍이 바탕에 깔리고, 시간 지연 장면에서는 화면 속 시계의 째깍으로 바뀜
#  · 빛 시계 장면의 '핑'(빛이 거울에 닿는 순간)은 그대로 유지 — 5번 vs 4번이 들려야 하므로
import numpy as np, wave, sys, json, math
from scipy.signal import butter, lfilter, fftconvolve
ev=json.load(open('events.json'))
sr=44100; D=60.0; N=int(sr*D); t=np.arange(N)/sr
rng=np.random.default_rng(6011)
org=np.zeros((2,N)); fx=np.zeros((2,N)); fxw=np.zeros((2,N))
hz=lambda m:440*2**((m-69)/12)
def lp(x,fc,o=2): b,a=butter(o,min(fc,sr*.45)/(sr/2)); return lfilter(b,a,x)
def hp(x,fc,o=2): b,a=butter(o,fc/(sr/2),'high'); return lfilter(b,a,x)
def bp(x,lo,hi): return lp(hp(x,lo),hi)
def put(buf,sig,t0,g=1.,pan=.5):
    i0=int(round(t0*sr))
    if i0>=N: return
    if i0<0: sig=sig[-i0:]; i0=0
    n=min(len(sig),N-i0); l,r=math.cos(pan*math.pi/2)*1.41,math.sin(pan*math.pi/2)*1.41
    buf[0,i0:i0+n]+=sig[:n]*g*l; buf[1,i0:i0+n]+=sig[:n]*g*r
def addfx(sig,t0,g=1.,pan=.5,w=.35): put(fx,sig,t0,g*(1-w*.5),pan); put(fxw,sig,t0,g*w,pan)

# ---------- 파이프 오르간 ----------
# 음전: (배수, 배음 세기들). 8'=제 음높이, 4'=한 옥타브 위, 2'=두 옥타브 위, 16'/32'=페달 저음
STOPS={'flute8':(1,[1,.06,.22,.03,.08,0,.03]),
       'princ8':(1,[1,.55,.32,.22,.15,.11,.08,.06,.045,.035]),
       'flute4':(2,[1,.05,.2,.02,.06]),
       'oct4':(2,[1,.45,.25,.15,.1,.07]),
       'fift2':(4,[1,.35,.18,.1]),
       'mix':(3,[1,.4,.2,.1]),
       'bourdon16':(.5,[1,.05,.3,.03,.1]),
       'sub32':(.25,[1,.12,.25])}
def pipe(m,t0,dur,reg,g,pan=.5,att=None,rel=.35):
    f0=hz(m); n=int((dur+rel)*sr); tt=np.arange(n)/sr
    a=att if att is not None else (.07 if f0>180 else .14)
    env=np.clip(tt/a,0,1)**1.6*np.clip((dur+rel-tt)/rel,0,1)
    s=np.zeros(n)
    for name,lev in reg.items():
        mult,harm=STOPS[name]; f=f0*mult*(1+rng.normal(0,.0005))
        for k,amp in enumerate(harm,1):
            if amp==0 or f*k>sr*.42: continue
            s+=lev*amp*np.sin(2*np.pi*f*k*tt+rng.random()*6.283)
    nc=int(.07*sr); ch=bp(rng.standard_normal(nc),min(2.5*f0,6000),min(7*f0,12000))*np.exp(-np.arange(nc)/sr*55)   # 칩
    s[:nc]+=ch*.25*sum(reg.values())
    s*=env/(1+sum(reg.values()))
    put(org,s,t0,g,pan)
def chord(ns,t0,dur,reg,g,att=None,spread=.3):
    for j,m in enumerate(ns): pipe(m,t0,dur,reg,g,.5+spread*((j%2)*2-1)*(.3+.7*j/max(1,len(ns)-1)),att)

SOFT={'flute8':1}; WARM={'flute8':1,'princ8':.55}; BRIGHT={'princ8':1,'flute8':.6,'oct4':.6}
FULL={'princ8':1,'flute8':.6,'oct4':.8,'fift2':.45,'mix':.5}
PED={'bourdon16':1,'flute8':.5}; PEDBIG={'sub32':.8,'bourdon16':1,'princ8':.5}

# (시작, 끝, 페달, 손건반 화음, 음전, 세기)
SECT=[
 (0.0,3.5,38,[69],SOFT,.55),                     # 훅: 낮은 D 위에 높은 A 하나
 (4.6,6.3,38,[58,62,65,70],SOFT,.8),             # 두 이론: B♭/D
 (6.3,8.0,36,[60,65,69,72],SOFT,.8),             # F/C
 (8.0,10.5,43,[55,58,62,67],WARM,.75),           # 빛의 속도: Gm
 (10.5,13.0,46,[58,62,65,70],WARM,.75),          # B♭
 (13.0,15.5,38,[57,62,65,69],SOFT,.55),          # 빛 시계: Dm (핑이 잘 들리도록 작게)
 (15.5,18.0,46,[58,62,65,70],SOFT,.55),          # B♭
 (18.0,20.5,41,[57,60,65,69],WARM,.75),          # F
 (20.5,23.0,48,[55,60,64,67],WARM,.75),          # C
 (23.0,25.0,43,[55,62,67,70],WARM,.7),           # 속도 그래프: Gm — 음전을 하나씩 더하며 상승
 (25.0,26.6,46,[58,65,70,74],{'flute8':1,'princ8':.8},.8),
 (26.6,28.2,48,[60,64,67,72],BRIGHT,.85),
 (28.2,30.0,45,[57,62,64,69],{**BRIGHT,'mix':.3},.9),   # Asus4 → 긴장
 (30.0,32.5,38,[57,62,65],{'flute8':1,'flute4':.5},.7), # 등가 원리: 가볍게
 (32.5,35.0,46,[58,62,65],{'flute8':1,'flute4':.5},.7),
 (36.0,38.5,34,[58,62,65,70,74],FULL,1.0),       # 휜 시공간: 별이 떨어지는 순간 전체 오르간
 (38.5,40.5,45,[57,60,65,69,72],FULL,.95),       # F/A
 (40.5,42.0,43,[55,58,62,65,70],BRIGHT,.9),      # Gm7
 (42.0,43.0,48,[55,60,64,67],WARM,.75),          # C
 (43.0,44.5,41,[57,60,65,69],SOFT,.6),           # 중력 시간 지연: 째깍이 잘 들리도록 작게
 (44.5,46.0,38,[57,62,65,69],SOFT,.6),
 (46.0,47.5,46,[58,62,65,70],SOFT,.6),
 (47.5,49.0,48,[55,60,65,67],SOFT,.6),
 (49.0,50.75,38,[57,62,65,69],WARM,.8),          # GPS: 다시 쌓아 올림
 (50.75,52.5,46,[58,62,65,70],WARM,.85),
 (52.5,54.25,41,[60,65,69,72],BRIGHT,.9),
 (54.25,56.0,45,[57,61,64,69],{**BRIGHT,'mix':.35},.95),   # A — 딸림화음
 (56.0,59.1,38,[62,66,69,74,78,81],FULL,1.05),   # 정리: D장조로 해소
]
for a,b,ped,ns,reg,g in SECT:
    big=a in (36.0,56.0)
    pipe(ped-12 if ped>40 else ped,a,b-a,PEDBIG if big else PED,g*(1.25 if big else .95),.5,att=.2 if big else None)
    chord(ns,a,b-a,reg,g,att=.35 if a==56.0 else None)
# 훅: '왜 그럴까요?' 직전에 부풀었다가 끊기는 화음
for j,m in enumerate([50,57,62,65,69]): pipe(m,2.4,1.15,{'princ8':1,'flute8':.6},.35+.1*j/4,.3+.1*j,att=.9)
chord([50,57,62,65,69,74],3.55,.75,FULL,.95)
pipe(26,3.55,.9,{'sub32':.8,'bourdon16':1},1.2)
# 별이 떨어지기 직전의 정적에서 32' 페달만 낮게 깔림
pipe(34,35.1,.95,{'sub32':1,'bourdon16':.6},.8,att=.6)

# 위 성부 선율 (직접 작곡: 화음 구성음 위의 긴 음)
MEL=[(4.9,1.4,74),(6.3,1.7,72),(8.2,1.2,70),(9.4,1.1,69),(10.5,1.3,74),(11.8,1.2,77),
     (18.0,2.5,77),(20.5,2.5,76),(23.2,1.8,74),(25.0,1.6,77),(26.6,1.6,79),(28.2,1.8,81),
     (30.2,2.3,69),(32.5,1.5,70),(34.0,.9,69),
     (36.0,1.25,77),(37.25,1.25,74),(38.5,2.0,72),(40.5,1.5,74),(42.0,1.0,76),
     (49.4,1.35,74),(50.75,1.75,77),(52.5,1.75,81),(54.25,.9,79),(55.15,.85,76),
     (56.0,1.6,78),(57.6,1.5,81)]
for x,d,m in MEL: pipe(m,x,d,{'princ8':.7,'flute8':.8,'oct4':.25},.62,.55)
# 분산화음(16분음표, 4' 플루트): 휜 시공간의 공전과 GPS 구간
def arp(t0,t1,chords,g=.32,step=.25):
    pat=[0,1,2,3,2,1,2,3]; k=0; x=t0
    while x<t1-1e-6:
        ns=[c for a,b,c in chords if a<=x<b]
        if ns:
            c=ns[0]; m=c[pat[k%8]%len(c)]+12; pipe(m,x,step*.9,{'flute4':1,'flute8':.3},g,.25+.5*((k*3)%8)/7,att=.02,rel=.12)
        x+=step; k+=1
arp(37.0,42.9,[(37,38.5,[58,62,65,70]),(38.5,40.5,[57,60,65,69]),(40.5,42,[55,58,62,65]),(42,43,[55,60,64,67])],.26)
arp(49.4,55.9,[(49,50.75,[57,62,65,69]),(50.75,52.5,[58,62,65,70]),(52.5,54.25,[60,65,69,72]),(54.25,56,[57,61,64,69])],.30)

# ---------- 시계 째깍 ----------
def clock(t0,g,pitch=1.,pan=.5):
    n=int(.16*sr); tt=np.arange(n)/sr
    s=bp(rng.standard_normal(n),1500,6500)*np.exp(-tt*320)*.9+np.sin(2*np.pi*1750*pitch*tt)*np.exp(-tt*70)*.35+np.sin(2*np.pi*430*pitch*tt)*np.exp(-tt*38)*.45
    addfx(s,t0,g,pan,.3)
for k,x in enumerate(ev['hookTicks']): clock(x,.07+.05*k/len(ev['hookTicks']),1+.25*k/len(ev['hookTicks']),.4+.2*(k%2))
BED=[(4.6,13.0),(18.0,23.0),(30.0,43.0),(49.0,56.0)]
for a,b in BED:
    x=a; k=0
    while x<b-1e-6: clock(x,.2,1.0 if k%2==0 else .78,.45 if k%2==0 else .55); x+=1.0; k+=1
x=56.0; d=1.0                                   # 끝: 째깍이 점점 느려지다 멈춤
while x<59.2: clock(x,.09*(1-.25*(x-56)/3.2),.78 if d>1.05 else 1.0,.5); x+=d; d*=1.32
for x in ev['earthTicks']: clock(x,.26,1.0,.35)            # 지구 시계
for x in ev['shipTicks']: clock(x,.34,.82,.65)             # 우주선 시계 (점점 뜸해짐)
for x in ev['farTicks']: clock(x,.26,1.05,.7)              # 중력이 약한 곳
for x in ev['nearTicks']: clock(x,.32,.8,.32)              # 중력이 강한 곳
# ---------- 빛 시계의 '핑' ----------
def ping(m,t0,g,pan):
    f=hz(m); n=int(1.6*sr); tt=np.arange(n)/sr
    s=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*9))*np.exp(-tt*5)*np.minimum(1,tt/.002); addfx(s,t0,g,pan,.5)
for x in ev['topHits']: ping(81,x,.15 if x>14.6+1e-6 else .1,.3)
for x in ev['botHits']: ping(76,x,.15 if x>14.6+1e-6 else .1,.7)
# ---------- 꼭 필요한 효과음만 작게 ----------
n=int(.5*sr); u=np.arange(n)/n; f=1800*(5200/1800)**u; addfx(np.sin(2*np.pi*np.cumsum(f)/sr)*np.sin(np.pi*u),9.0,.05,.3,.6)   # 빛 발사
n=int(.3*sr); tt=np.arange(n)/sr; addfx(lp(rng.standard_normal(n),300)*np.exp(-tt*14),32.3,.18,.5,.2)                        # 공이 바닥에
n=int(1.2*sr); tt=np.arange(n)/sr; addfx(np.sin(2*np.pi*np.cumsum(40*(1+np.exp(-tt*8)))/sr)*np.exp(-tt*2.5),36.0,.22,.5,.3)  # 별이 떨어짐

# ---------- 성당 잔향 ----------
def cathedral(seed,sec=6.5):
    r=np.random.default_rng(seed); n=int(sec*sr); tt=np.arange(n)/sr
    bright=lp(r.standard_normal(n),6000)*np.exp(-tt*3.2); dark=lp(r.standard_normal(n),1800)*np.exp(-tt*1.15)
    ir=.45*bright+dark; ir[:int(.03*sr)]=0
    for d,a in [(.017,.5),(.031,.35),(.047,.3),(.066,.22),(.083,.18)]: ir[int(d*sr)]+=a*r.choice([-1,1])*np.sqrt((ir**2).sum()/n)*40
    return ir/np.sqrt((ir**2).sum())
def room(seed,sec=2.0):
    r=np.random.default_rng(seed); n=int(sec*sr); tt=np.arange(n)/sr; ir=lp(r.standard_normal(n),5000)*np.exp(-tt*3); return ir/np.sqrt((ir**2).sum())
ow=np.stack([fftconvolve(org[0],cathedral(1))[:N],fftconvolve(org[1],cathedral(2))[:N]])
fw=np.stack([fftconvolve(fxw[0],room(3))[:N],fftconvolve(fxw[1],room(4))[:N]])
# 오르간 세기 곡선: 핑·째깍이 의미를 전달하는 구간에서는 한 발 물러남
gk=[(0,1),(12.6,1),(13.2,.6),(17.6,.6),(18.2,1),(22.8,1),(23.3,.55),(29.6,.55),(30.2,1),(42.8,1),(43.3,.45),(48.7,.45),(49.2,1),(60,1)]
gain=np.interp(t,[a for a,b in gk],[b for a,b in gk])
O=(org*.55+ow*.75)*gain; O/=np.percentile(np.abs(O),99.95)          # 오르간 버스: 최대치 ≈ 1
F=fx+fw*.8; F/=np.percentile(np.abs(F),99.95)                       # 째깍·핑 버스: 최대치 ≈ 1
mix=O*.42+F*.5                                                      # 째깍·핑이 오르간 위로 들리도록
mix=hp(mix,24); mix*=np.clip(t/.01,0,1)*np.clip((D-t)/1.4,0,1)
# 통합 음량을 쇼츠 기준(-14 LUFS 안팎)에 가깝게: RMS 기준으로 맞춘 뒤 순간 최대치만 부드럽게 눌러 줌
mix*=10**(-15.5/20)/np.sqrt((mix**2).mean())
mix=np.tanh(mix/.85)*.85
mix*=min(1,10**(-1/20)/np.abs(mix).max())
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix.T*32767).astype('<i2').tobytes()); w.close()
