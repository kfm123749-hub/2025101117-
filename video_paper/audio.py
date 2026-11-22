# 배경음: 접을 때마다 음이 올라가는 틱 + 점점 커지는 패드 + 도착 화음 (numpy만 사용)
import numpy as np, wave, sys
sr=44100; D=60; t=np.arange(sr*D)/sr; out=np.zeros((2,len(t)))
note=lambda m:440*2**((m-69)/12)
T0=4.6; D2=32/34; TEND=T0+8+32
def add(i0,sig,vol,pan=.5):
    n=min(len(sig),len(t)-i0)
    out[0,i0:i0+n]+=vol*(1-pan)*2*sig[:n]; out[1,i0:i0+n]+=vol*pan*2*sig[:n]
def bell(t0,m,vol=.15,pan=.5,dec=3.2,dur=2.2):
    tt=np.arange(int(sr*dur))/sr; f=note(m)
    s=np.exp(-tt*dec)*(np.sin(2*np.pi*f*tt)+.4*np.exp(-tt*5)*np.sin(4*np.pi*f*tt)+.2*np.exp(-tt*8)*np.sin(6*np.pi*f*tt))
    add(int(t0*sr),s*np.clip(tt/.004,0,1),vol,pan)
# 접기 틱: 반음씩 42번 상승
for k in range(1,43):
    tk=T0+k-.5 if k<=8 else T0+8+(k-8-.5)*D2
    bell(tk,45+k,vol=.07+.0022*k,pan=.5+.18*(-1)**k,dec=7,dur=.9)
# 패드: 접는 동안 서서히 커짐
env=np.clip((t-3.6)/3,0,1)*(.35+.65*np.clip((t-T0)/(TEND-T0),0,1))*np.clip((TEND+.15-t)/.3,0,1)
for i,m in enumerate([38,45,50,57]):
    f=note(m)
    for ch,det in ((0,-.3),(1,.3)):
        out[ch]+=.05*env*(1+.1*np.sin(2*np.pi*(.09+.02*i)*t+i))*(np.sin(2*np.pi*(f+det)*t)+.3*np.sin(4*np.pi*(f+det)*t))
# 훅과 도착, 마무리
for t0,m in [(.3,62),(1.05,69),(2.05,74)]: bell(t0,m,.1)
for m in (50,62,69,74,78,81): bell(TEND,m,.11,dec=1.1,dur=5.5)
for t0,ms in [(50.0,(57,69,76)),(52.3,(59,71,78)),(55.8,(50,62,66,69,74)),(56.7,(81,))]:
    for m in ms: bell(t0,m,.09,dec=1.4,dur=4)
out*=np.clip(t/.4,0,1)*np.clip((D-t)/1.5,0,1); out*=.8/np.abs(out).max()
pcm=(out.T*32767*.6).astype('<i2')
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
