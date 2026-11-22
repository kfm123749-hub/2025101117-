# 「60초 상대성 이론」 음악 — 화면과 같은 이벤트(events.json)에 맞춰 직접 작곡·합성 (numpy, scipy)
#  · 빛 시계: 빛이 거울에 닿을 때마다 '핑' — 멈춘 시계(왼쪽·높은 음) 5번, 움직이는 시계(오른쪽·낮은 음) 4번이 그대로 들림
#  · 속도 그래프: 지구 시계와 우주선 시계의 '째깍' — 우주선 쪽이 점점 뜸해짐, 속도에 따라 올라가는 음
#  · 중력 시간 지연: 먼 시계(빠름)와 가까운 시계(느림)의 '째깍'
#  · 조성: D단조의 질문 → 장면마다 화음이 바뀌고 → 마지막에 D장조로 해소
import numpy as np, wave, sys, json, math
from scipy.signal import butter, lfilter, fftconvolve
ev=json.load(open('events.json'))
sr=44100; D=60.0; N=int(sr*D); t=np.arange(N)/sr
rng=np.random.default_rng(1915)
out=np.zeros((2,N)); wet=np.zeros((2,N))
hz=lambda m:440*2**((m-69)/12)
def lp(x,fc,o=2): b,a=butter(o,min(fc,sr*.45)/(sr/2)); return lfilter(b,a,x)
def hp(x,fc,o=2): b,a=butter(o,fc/(sr/2),'high'); return lfilter(b,a,x)
def add(sig,t0,g=1.,pan=.5,w=.4):
    i0=int(round(t0*sr))
    if i0>=N: return
    if i0<0: sig=sig[-i0:]; i0=0
    n=min(len(sig),N-i0); s=sig[:n]*g; l,r=math.cos(pan*math.pi/2)*1.41,math.sin(pan*math.pi/2)*1.41
    out[0,i0:i0+n]+=s*l*(1-w*.5); out[1,i0:i0+n]+=s*r*(1-w*.5); wet[0,i0:i0+n]+=s*l*w; wet[1,i0:i0+n]+=s*r*w
def varlp(x,fc):
    y=np.zeros(len(x)); zi=np.zeros(2); ch=512
    for j in range(0,len(x),ch):
        b,a=butter(2,float(np.clip(fc[min(j,len(fc)-1)],60,sr*.4))/(sr/2)); y[j:j+ch],zi=lfilter(b,a,x[j:j+ch],zi=zi)
    return y
def pad(notes,a,b,g,fc=1800,att=.8,rel=1.2):
    i0,i1=int(max(0,a-att*.4)*sr),int(min(D,b+rel)*sr); tt=t[i0:i1]-a; n=len(tt)
    env=np.clip((tt+att*.4)/att,0,1)*np.clip((b-a+rel-tt)/rel,0,1); env=np.sin(env*np.pi/2)**2
    for j,m in enumerate(notes):
        f=hz(m); s=np.zeros(n)
        for d in (-.0035,0,.0035):
            ph=f*(1+d)*tt+rng.random(); s+=(2*(ph%1)-1)*.5+np.sin(2*np.pi*ph)*.5
        add(lp(s,fc)*env/3,max(0,a-att*.4),g*1.35,.5+.32*((j%2)*2-1)*(.4+.6*j/len(notes)),.6)
def bell(m,t0,g=.1,pan=.5,dec=2.0,w=.65,ratio=3.5):
    f=hz(m); n=int(4*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt+1.3*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt))*np.exp(-tt*dec)*np.minimum(1,tt/.003); add(s,t0,g,pan,w)
def ping(m,t0,g=.1,pan=.5,dec=5):                    # 빛이 거울에 닿는 소리
    f=hz(m); n=int(1.6*sr); tt=np.arange(n)/sr
    s=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*9))*np.exp(-tt*dec)*np.minimum(1,tt/.002); add(s,t0,g*1.6,pan,.55)
def tick(t0,f,g,pan=.5,dec=70):
    n=int(.08*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt)*np.exp(-tt*dec)+hp(rng.standard_normal(n),4000)*np.exp(-tt*200)*.3; add(s,t0,g*1.7,pan,.35)
def impact(t0,g=.4,f0=44,dur=2.4):
    n=int(dur*sr); tt=np.arange(n)/sr; f=f0*(1+1.2*np.exp(-tt*9)); ph=2*np.pi*np.cumsum(f)/sr
    add((np.sin(ph)*np.exp(-tt*2.2)+lp(rng.standard_normal(n),800)*np.exp(-tt*12)*.4)*np.minimum(1,tt/.003),t0,g*.6,.5,.35)
def swell(t0,dur,g=.1,f_end=6000,p=2.2):
    n=int(dur*sr); x=rng.standard_normal(n); u=np.arange(n)/n
    add(varlp(x,200+f_end*u**2)*u**p,t0,g,.5,.6)
def glide(t0,dur,f0,f1,g,pan=.5,shape=None):
    n=int(dur*sr); u=np.arange(n)/n; f=f0*(f1/f0)**u if shape is None else shape(u)
    ph=2*np.pi*np.cumsum(f)/sr; env=np.sin(np.pi*u)**1.2
    add((np.sin(ph)+.25*np.sin(2*ph))*env,t0,g,pan,.6)

# ---------- 화음 진행 ----------
for a,b,ns,fc in [(0,4.6,[38,50,57,60,65],900),(4.6,8,[41,53,57,60,64,69],2000),(8,13,[45,52,57,60,64],1700),
                  (13,17.6,[41,53,60,64,67],1800),(17.6,23,[36,48,55,62,64,67],2200),(23,30,[38,50,57,62,65,69],1900),
                  (30,35,[34,46,53,58,62,65],1900),(35,43,[31,43,50,55,58,62],1300),(43,49,[39,51,58,62,65,70],1900),
                  (49,53,[36,48,55,60,64,67],2300),(53,56,[43,55,59,62,67,71],2500),(56,60,[38,50,57,62,66,69,74],3200)]:
    pad(ns,a,b,.085 if a else .07,fc=fc)

# ---------- 0. 훅: 하루가 빨리 감기고, 오차 경고음이 커짐 ----------
for k,x in enumerate(ev['hookTicks']): tick(x,1500+12*k,.05+.03*k/len(ev['hookTicks']),.35+.3*(k%2))
seg=(t>=.4)&(t<3.7); ts=t[seg]; u=(ts-.4)/3.3
f=330*2**(u*1.6); ph=2*np.pi*np.cumsum(f)/sr; ph2=2*np.pi*np.cumsum(f*1.06)/sr
add((np.sin(ph)+np.sin(ph2))*.5*u**1.5*np.clip((3.7-ts)/.08,0,1),ts[0],.07,.5,.4)
impact(3.55,.42,40,2.4); bell(74,3.57,.08,.5,1.6)
# ---------- 1. 두 이론 ----------
swell(3.9,.75,.08)
bell(81,5.0,.10,.35,1.8); bell(88,5.03,.04,.3,1.8)     # 특수
bell(74,5.6,.10,.65,1.6); bell(69,5.63,.06,.7,1.6)     # 일반
# ---------- 2. 빛의 속도 ----------
sh=(t>=8)&(t<13.2); ts=t[sh]; x=(-160+210*(ts-8))/1080
hum=np.zeros(len(ts))
for m,g in [(38,1),(45,.5)]:
    ph=hz(m)*ts; hum+=g*((2*(ph%1)-1)*.6+np.sin(2*np.pi*ph)*.4)
hum=lp(hum,500)*np.clip((ts-8)/.6,0,1)*np.clip((13.2-ts)/.5,0,1)
pans=np.clip(x,0,1); l=np.cos(pans*np.pi/2)*1.41; r=np.sin(pans*np.pi/2)*1.41; i0=int(8*sr)
out[0,i0:i0+len(ts)]+=hum*l*.05; out[1,i0:i0+len(ts)]+=hum*r*.05
glide(9.0,.5,1800,5200,.045,.3); bell(93,9.0,.05,.4,3.5)                 # 빛 발사
n=int(.35*sr); tt=np.arange(n)/sr; add(np.sign(np.sin(2*np.pi*110*tt))*np.exp(-tt*6)*.6,10.27,.06,.5,.2)   # 1.5c ? 땡
bell(81,10.52,.12,.5,1.8); bell(88,10.55,.05,.55,1.8)                  # 그대로 c
for k,xx in enumerate([11.0,11.25]): bell([76,81][k],xx,.07,.3+.4*k,1.8)
swell(12.4,.8,.06)
# ---------- 3. 빛 시계 ----------
run0=14.6
for x in ev['topHits']: ping(81,x,.11 if x>run0+1e-6 else .07,.3)
for x in ev['botHits']: ping(76,x,.11 if x>run0+1e-6 else .07,.7)
impact(17.6,.18,52,1.4)
for k,(x,m) in enumerate([(17.95,69),(18.35,72),(18.75,76)]): bell(m,x,.07,.4+.1*k,1.6)
bell(84,19.5,.11,.5,1.6); bell(91,19.53,.04,.6,1.8)
bell(88,20.6,.09,.5,1.6)
swell(22.2,.8,.07)
# ---------- 4. 속도 그래프 ----------
for x in ev['earthTicks']: tick(x,2300,.08,.3)
for x in ev['shipTicks']: tick(x,1500,.10,.7,50)
def beta(x):
    ks=[[23.6,0],[24.6,.5],[25.2,.5],[26.0,math.sqrt(3)/2],[26.6,math.sqrt(3)/2],[27.6,.99],[29.6,.99]]
    if x<=ks[0][0]: return 0
    for (a,va),(b,vb) in zip(ks,ks[1:]):
        if x<=b: s=(x-a)/(b-a); s=4*s**3 if s<.5 else 1-(-2*s+2)**3/2; return va+(vb-va)*s
    return .99
sg=(t>=23.6)&(t<29.8); ts=t[sg]; bb=np.array([beta(x) for x in ts[::100]]); bb=np.interp(np.arange(len(ts)),np.arange(0,len(ts),100)[:len(bb)],bb)
gam=1/np.sqrt(1-np.minimum(bb,.995)**2); f=220*gam**.85
ph=2*np.pi*np.cumsum(f)/sr; env=np.clip((ts-23.6)/.6,0,1)*np.clip((29.8-ts)/.4,0,1)*(.5+.5*np.clip(np.log(gam)/2,0,1))
add((np.sin(ph)+.3*np.sin(2*ph)+.12*np.sin(3*ph))*env,ts[0],.045,.5,.6)
for x,m in [(24.6,79),(26.0,83),(27.6,88)]: bell(m,x,.09,.6,1.7)
swell(29.1,.8,.08)
# ---------- 5. 등가 원리 ----------
rk=(t>=30.2)&(t<34.9); ts=t[rk]; nz=lp(rng.standard_normal(len(ts)),350)*np.clip((ts-30.2)/.6,0,1)*np.clip((34.9-ts)/.5,0,1)
i0=int(30.2*sr); out[0,i0:i0+len(ts)]+=nz*.25*.5; out[1,i0:i0+len(ts)]+=nz*.25*1.3
tick(31.3,900,.05,.5,40)
impact(32.3,.22,70,.8); bell(76,32.3,.08,.3,2.2); bell(76,32.32,.08,.7,2.2)
bell(83,32.6,.10,.5,1.6); bell(90,32.63,.04,.5,1.8)
# ---------- 6. 휜 시공간 ----------
glide(35.2,.85,1400,300,.05,.5)                                      # 별이 떨어짐
impact(36.0,.55,34,3.0)
glide(36.0,1.1,110,55,.10,.5)                                        # 시공간이 꺼짐
for k in range(4): bell([67,70,74,77][k%4],37.0+k*1.7,.06,.3+.4*(k%2),1.6)   # 행성의 공전
glide(39.8,2.3,1100,1100,.04,.5,shape=lambda u:1100*2**(-.35*np.exp(-((u-.55)/.18)**2)))  # 빛이 휘는 순간 음도 휜다
bell(86,41.7,.08,.7,1.8)
swell(42.3,.8,.07)
# ---------- 7. 중력 시간 지연 ----------
for x in ev['farTicks']: tick(x,2400,.08,.72)
for x in ev['nearTicks']: tick(x,1000,.11,.32,45)
bell(82,46.3,.08,.5,1.7)
swell(48.3,.8,.08)
# ---------- 8. GPS ----------
for k in range(9):
    x=49.4+k*.4*3
    for j in range(3):
        n=int(.06*sr); tt=np.arange(n)/sr; add(np.sign(np.sin(2*np.pi*1650*tt))*np.exp(-tt*40)*.35,x+j*.09,.03,.55,.4)
bell(81,50.0,.10,.3,1.6); bell(74,51.0,.11,.7,1.6); bell(86,52.0,.10,.5,1.6); bell(79,52.02,.06,.5,1.6)
impact(52.85,.32,44,2.2); bell(88,52.9,.09,.5,1.8)
bell(84,53.05,.06,.4,1.6)
swell(55.3,.7,.08)
# ---------- 9. 정리 ----------
bell(81,56.2,.10,.35,1.6); bell(74,56.8,.10,.65,1.6)
impact(57.6,.4,37,3.2)
for j,m in enumerate([62,66,69,74,78,81,86]): bell(m,57.62+j*.07,.06,.2+.6*j/6,1.4,.75)

def ir(seed,sec=2.6):
    n=int(sec*sr); tt=np.arange(n)/sr; r=np.random.default_rng(seed).standard_normal(n)*np.exp(-tt*2.4); r=lp(r,5200); return r/np.sqrt((r**2).sum())
mix=out+np.stack([fftconvolve(wet[0],ir(1))[:N],fftconvolve(wet[1],ir(2))[:N]])*.85
mix=hp(mix,28); mix*=np.clip(t/.01,0,1)*np.clip((D-t)/1.8,0,1)
mix=np.tanh(mix*1.5)/np.tanh(1.5); mix*=10**(-1/20)/np.abs(mix).max()
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix.T*32767).astype('<i2').tobytes()); w.close()
