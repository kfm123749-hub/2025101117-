# 배경음: 장면별 화음 패드 + 행성 도착마다 벨 (numpy만 사용)
import numpy as np, wave, sys
sr=44100; D=60; t=np.arange(sr*D)/sr; out=np.zeros((2,len(t)))
note=lambda m:440*2**((m-69)/12)
for a,b,ms in [(0,4.4,[38,50,57,62]),(4.4,20.4,[43,50,59,62]),(20.4,46,[40,52,59,64]),(46,54.5,[45,52,57,64]),(54.5,60,[38,50,57,62,66])]:
    env=np.sin(np.clip((t-a+.6)/1.2,0,1)*np.clip((b+.6-t)/1.2,0,1)*np.pi/2)**2
    for i,m in enumerate(ms):
        f=note(m)
        for ch,det in ((0,-.35),(1,.35)):
            out[ch]+=.05*env*(1+.12*np.sin(2*np.pi*(.11+.03*i)*t+i+ch))*(np.sin(2*np.pi*(f+det)*t)+.25*np.sin(4*np.pi*(f+det)*t))
def bell(t0,m,vol=.15,pan=.5,dec=3.2):
    tt=np.arange(int(sr*2.6))/sr; f=note(m); i0=int(t0*sr)
    s=np.exp(-tt*dec)*(np.sin(2*np.pi*f*tt)+.4*np.exp(-tt*5)*np.sin(4*np.pi*f*tt))*np.clip(tt/.004,0,1)
    n=min(len(s),len(t)-i0); out[0,i0:i0+n]+=vol*(1-pan)*2*s[:n]; out[1,i0:i0+n]+=vol*pan*2*s[:n]
for t0,m in [(.3,62),(1.0,74),(2.05,69),(5.0,76),(9.4,79),(15.6,62),(15.6,74),(21,88)]: bell(t0,m)
for i,t0 in enumerate([23,24.6,26.4,28.6,32.3,35.4,38.9,42.3]): bell(t0,[88,86,83,81,76,74,71,64][i],.16,.5,2.4)
for t0,m in [(44.3,76),(47.4,81),(48.9,78),(50.4,74),(55.4,62),(56.1,69),(56.1,74),(57.5,78)]: bell(t0,m)
out*=np.clip(t/.5,0,1)*np.clip((D-t)/1.5,0,1); out*=.8/np.abs(out).max()
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out.T*32767*.55).astype('<i2').tobytes()); w.close()
