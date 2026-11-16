# 「침착함은 순서다」 음악 — 화면과 같은 시간축(events.json: 흥분도 A, 호흡, 심장 박동)으로 작곡·합성
#  · 심장 박동: 132 → 61 bpm 으로 느려지며 점점 작아짐
#  · 불협화음 드론과 떨림: 흥분도에 비례 → 사라짐
#  · 숨소리(걸러낸 잡음)와 안내음: 화면의 원과 똑같이 4초 들이쉬고 6초 내쉼
#  · 화음: D단조의 긴장에서 F장조의 고요로
import numpy as np, wave, sys, json, math
from scipy.signal import butter, lfilter, fftconvolve
ev=json.load(open('events.json')); TT=ev['T']
sr=44100; D=60.0; N=int(sr*D); t=np.arange(N)/sr
rng=np.random.default_rng(4646)
A=np.interp(t,np.arange(6001)/100,ev['A']); BR=np.interp(t,np.arange(6001)/100,ev['breath'])
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
def varlp(x,fc):                       # 시간에 따라 변하는 저역 필터
    y=np.zeros(len(x)); zi=np.zeros(2); ch=512
    for j in range(0,len(x),ch):
        b,a=butter(2,float(np.clip(fc[j],80,sr*.4))/(sr/2)); y[j:j+ch],zi=lfilter(b,a,x[j:j+ch],zi=zi)
    return y
def pad(notes,a,b,g,fc=1600,att=1.0,rel=1.4):
    i0,i1=int(max(0,a-att*.4)*sr),int(min(D,b+rel)*sr); tt=t[i0:i1]-a; n=len(tt)
    env=np.clip((tt+att*.4)/att,0,1)*np.clip((b-a+rel-tt)/rel,0,1); env=np.sin(env*np.pi/2)**2
    for j,m in enumerate(notes):
        f=hz(m); s=np.zeros(n)
        for d in (-.0035,0,.0035):
            ph=f*(1+d)*tt+rng.random(); s+=(2*(ph%1)-1)*.5+np.sin(2*np.pi*ph)*.5
        add(lp(s,fc)*env/3,max(0,a-att*.4),g,.5+.32*((j%2)*2-1)*(.4+.6*j/len(notes)),.6)
def bell(m,t0,g=.1,pan=.5,dec=2.0,w=.65,ratio=3.5,dur=4):
    f=hz(m); n=int(dur*sr); tt=np.arange(n)/sr
    s=np.sin(2*np.pi*f*tt+1.4*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt))*np.exp(-tt*dec)*np.minimum(1,tt/.004); add(s,t0,g,pan,w)
def soft(m,t0,g=.1,pan=.5,dec=1.6):     # 둥근 음 (마림바 느낌)
    f=hz(m); n=int(3.5*sr); tt=np.arange(n)/sr
    s=(np.sin(2*np.pi*f*tt)+.25*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*14))*np.exp(-tt*dec)*np.minimum(1,tt/.006); add(s,t0,g,pan,.6)
def impact(t0,g=.5,f0=42,dur=2.6):
    n=int(dur*sr); tt=np.arange(n)/sr; f=f0*(1+1.3*np.exp(-tt*9)); ph=2*np.pi*np.cumsum(f)/sr
    s=np.sin(ph)*np.exp(-tt*2.1)+lp(rng.standard_normal(n),900)*np.exp(-tt*11)*.5; add(s*np.minimum(1,tt/.002),t0,g,.5,.35)
def tick(t0,f,g,pan=.5,dec=60):
    n=int(.09*sr); tt=np.arange(n)/sr; add(np.sin(2*np.pi*f*tt)*np.exp(-tt*dec),t0,g,pan,.4)
def swell(t0,dur,g=.1,f_end=6000,rev=False):
    n=int(dur*sr); x=rng.standard_normal(n); u=np.arange(n)/n
    if rev: u=1-u
    add(varlp(x,200+f_end*u**2.2)*u**2.2,t0,g,.5,.6)

# ---------- 심장 박동 ----------
for tb in ev['beats']:
    a=float(np.interp(tb,t[::441],A[::441])); vol=.09+.5*a**1.3
    n=int(.34*sr); tt=np.arange(n)/sr
    lub=np.sin(2*np.pi*np.cumsum(46+34*np.exp(-tt*30))/sr)*np.exp(-tt*13)
    dub=np.sin(2*np.pi*np.cumsum(58+30*np.exp(-tt*34))/sr)*np.exp(-tt*17)
    add(lub*np.minimum(1,tt/.003),tb,vol,.5,.12); add(dub*np.minimum(1,tt/.003),tb+.16,vol*.6,.5,.12)

# ---------- 긴장: 불협화음 드론 + 떨림 + 귀울림 ----------
ten=np.zeros(N)
for m,g in [(38,.9),(51,.5),(63,.55),(64,.55),(70,.4),(71,.4)]:
    f=hz(m); ph=f*t+rng.random(); ten+=g*((2*(ph%1)-1)*.6+np.sin(2*np.pi*ph)*.4)
ten=lp(ten,1500)*(A**2.1)*(1-.45*A*(.5+.5*np.sin(2*np.pi*9.3*t)))
add(ten,0,.055,.5,.5)
add(np.sin(2*np.pi*3150*t)*(A**4)*(.6+.4*np.sin(2*np.pi*.7*t)),0,.012,.5,.3)             # 귀울림
crk=hp(rng.standard_normal(N),2500)*(rng.random(N)>.9995).astype(float)
crk=lfilter([1],[1,-.992],crk)*(A**2)
add(lp(crk,6000),0,.05,.5,.5)

# ---------- 숨소리 + 안내음 ----------
nz=rng.standard_normal(N); dbr=np.gradient(BR)*sr                                         # 호흡 속도(+들숨, −날숨)
amp=np.clip(np.abs(dbr)/.42,0,1)**.8; amp=lp(amp,6)
fc=np.where(dbr>0,500+2300*BR,350+1500*BR)
breathN=varlp(nz,fc)*amp
g_b=np.where(t<TT['in1'],.05,np.where(t<TT['label'],.20,.05))
add(hp(breathN,150)*g_b,0,1.0,.5,.55)
gm=(t>=TT['in1']-.3)&(t<TT['label']+.6); tg=t[gm]
fg=hz(57)*2**(BR[gm]*7/12)                                                                 # 들숨에 5도 오르고 날숨에 내려옴
envg=np.clip((tg-(TT['in1']-.3))/.8,0,1)*np.clip((TT['label']+.6-tg)/1.2,0,1)
phg=2*np.pi*np.cumsum(fg)/sr
add((np.sin(phg)+.3*np.sin(2*phg)+.1*np.sin(3*phg))*envg*(.5+.5*BR[gm]),tg[0],.05,.5,.7)
for k in range(20):                                                                        # 1초마다 부드러운 박
    x=TT['in1']+k; inh=(k<4) or (10<=k<14)
    soft(81 if inh else 77,x+.01,.035 if k%10 not in (0,4) else .06,.5,5)

# ---------- 화음 ----------
CH=[(20,26,[34,46,53,57,62,65],1400),(26,30,[36,48,55,60,64,67],1700),(30,36,[41,53,57,60,64,67],1900),
    (36,38.6,[38,50,57,60,65],1300),(38.6,41.8,[34,46,53,58,62,65],2000),(41.8,45,[36,48,55,60,64,67],2100),
    (45,48.2,[45,52,57,60,64],1500),(48.2,50.6,[41,53,57,60,65,69],2300),(50.6,53,[40,52,55,60,64,67],2300),
    (53,57.1,[34,46,53,58,62,65,69],2400),(57.1,60,[41,48,53,57,60,65,69,72],3000)]
for a,b,ns,fcut in CH:
    gch=.05+.115*(1-float(np.interp((a+b)/2,t[::441],A[::441])))
    pad(ns,a,b,gch,fc=fcut)

# ---------- 장면별 소리 ----------
impact(0.0,.5,40,2.4); impact(1.1,.22,48,1.2); bell(62,2.5,.07,.5,1.6,.7)                   # 훅
swell(4.2,.9,.07)
for k,x in enumerate([6.6,7.1,7.6]): tick(x,1500+300*k,.035,.3+.2*k)                       # 그래프 라벨
bell(75,8.4,.07,.72,2.6); bell(76,8.42,.07,.78,2.6)                                         # '지금 여기' (반음 부딪힘)
gl=np.arange(int(1.3*sr))/sr; fgl=hz(62)*2**(gl/1.3*7/12)
add(np.sin(2*np.pi*np.cumsum(fgl)/sr)*np.sin(np.pi*gl/1.3)**1.5,10.2,.06,.55,.7)             # 화살표
bell(74,11.4,.11,.45,1.8); bell(81,11.45,.06,.55,1.8)                                       # 목표(완전5도)
swell(12.2,1.0,.08)
swell(38.3,.5,.06,5000)                                                                    # 이름표로 모임
soft(81,39.45,.12,.45,2.2); bell(89,39.47,.05,.6,2.4)
for k in range(1,11): tick(39.5+.14*k,2100+rng.random()*300,.03,.4+.2*rng.random(),120)     # 타자 소리
bell(77,41.2,.06,.5,1.8)
rs=lp(hp(rng.standard_normal(int(3*sr)),900),3500); ur=np.arange(len(rs))/len(rs)
add(rs*np.sin(np.pi*ur)*(.6+.4*np.sin(2*np.pi*7*ur*3)),45.2,.035,.5,.5)                       # 엉킨 실
swell(47.6,.7,.08,7000)
soft(84,49.05,.14,.3,1.8); bell(91,49.08,.06,.4,2.0); impact(49.05,.22,52,1.6)              # 지금 할 한 가지
swell(52.3,.8,.07)
for j,m in enumerate([53,57,60,65,69,72,77]): soft(m,53.1+j*.13,.07,.2+.6*j/6,1.6)           # 원으로 돌아옴
for x,m,pn in [(54.3,77,.4),(55.2,81,.5),(56.1,84,.6)]: soft(m,x,.11,pn,1.5); bell(m+12,x+.02,.035,1-pn,2.0)
impact(57.1,.34,41,3.0)
for j,m in enumerate([65,69,72,77,81]): bell(m,57.15+j*.07,.06,.25+.5*j/4,1.5,.75)

def ir(seed,sec=3.0):
    n=int(sec*sr); tt=np.arange(n)/sr; r=np.random.default_rng(seed).standard_normal(n)*np.exp(-tt*2.2); r=lp(r,5000); return r/np.sqrt((r**2).sum())
mix=out+np.stack([fftconvolve(wet[0],ir(1))[:N],fftconvolve(wet[1],ir(2))[:N]])*.9
mix=hp(mix,28); mix*=np.clip(t/.02,0,1)*np.clip((D-t)/2.4,0,1)
mix=np.tanh(mix*1.5)/np.tanh(1.5); mix*=10**(-1/20)/np.abs(mix).max()
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix.T*32767).astype('<i2').tobytes()); w.close()
