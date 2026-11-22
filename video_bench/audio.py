# 배경음: 장면별 화음 패드 + 주요 순간의 벨 (numpy만 사용)
import numpy as np, wave, sys
sr=44100; D=60; t=np.arange(sr*D)/sr; out=np.zeros((2,len(t)))
note=lambda m:440*2**((m-69)/12)
for a,b,ms in [(0,4.5,[50,57,62,66]),(4.5,14,[47,54,62,66]),(14,27,[43,55,59,62]),(27,41,[45,52,61,64]),(41,52,[47,54,59,62]),(52,60,[50,57,62,66,69])]:
    env=np.sin(np.clip((t-a+.6)/1.2,0,1)*np.clip((b+.6-t)/1.2,0,1)*np.pi/2)**2
    for i,m in enumerate(ms):
        f=note(m)
        for ch,det in ((0,-.35),(1,.35)):
            out[ch]+=.05*env*(1+.12*np.sin(2*np.pi*(.11+.03*i)*t+i+ch))*(np.sin(2*np.pi*(f+det)*t)+.25*np.sin(4*np.pi*(f+det)*t))
def bell(t0,m,vol=.15,pan=.5):
    tt=np.arange(int(sr*2.2))/sr; f=note(m); i0=int(t0*sr)
    s=np.exp(-tt*3.2)*(np.sin(2*np.pi*f*tt)+.4*np.exp(-tt*5)*np.sin(4*np.pi*f*tt))*np.clip(tt/.004,0,1)
    n=min(len(s),len(t)-i0); out[0,i0:i0+n]+=vol*(1-pan)*2*s[:n]; out[1,i0:i0+n]+=vol*pan*2*s[:n]
for t0,m in [(.3,74),(1.2,81),(2.1,78),(10.1,83),(15.3,76),(17.0,83),(19.7,86),(28.4,74),(29.9,78),(31.4,81),(32.6,86),
             (42.1,81),(43.25,78),(44.4,74),(45.55,69),(52.9,74),(53.95,78),(55.0,81),(56.6,86)]: bell(t0,m)
out*=np.clip(t/.5,0,1)*np.clip((D-t)/1.5,0,1); out*=.8/np.abs(out).max()
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out.T*32767*.55).astype('<i2').tobytes()); w.close()
