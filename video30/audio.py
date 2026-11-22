# 배경음 합성: 장면별 화음 패드 + 주요 순간의 짧은 벨 소리 (numpy만 사용)
import numpy as np, wave, sys
sr=44100; D=60; t=np.arange(sr*D)/sr
out=np.zeros((2,len(t)))
def note(m): return 440*2**((m-69)/12)
# (시작, 끝, MIDI 음들)
chords=[(0,4.6,[52,59,64,68]),(4.6,13.6,[49,56,64,68]),(13.6,19.5,[45,57,61,64]),
        (19.5,42,[47,54,63,66]),(42,52.4,[49,56,61,64]),(52.4,60,[52,59,64,68,71])]
for a,b,ms in chords:
    env=np.clip((t-a+0.6)/1.2,0,1)*np.clip((b+0.6-t)/1.2,0,1)
    env=np.sin(env*np.pi/2)**2
    for i,m in enumerate(ms):
        f=note(m)
        for ch,det in ((0,-0.35),(1,0.35)):
            lfo=1+0.12*np.sin(2*np.pi*(0.11+0.03*i)*t+i+ch)
            out[ch]+=0.05*env*lfo*(np.sin(2*np.pi*(f+det)*t)+0.25*np.sin(2*np.pi*2*(f+det)*t))
def bell(t0,m,vol=0.16,pan=0.5):
    n=int(sr*2.2); i0=int(t0*sr); tt=np.arange(n)/sr; f=note(m)
    s=np.exp(-tt*3.2)*(np.sin(2*np.pi*f*tt)+0.4*np.exp(-tt*5)*np.sin(2*np.pi*2*f*tt)+0.2*np.exp(-tt*8)*np.sin(2*np.pi*3*f*tt))
    s*=np.clip(tt/0.004,0,1)
    n=min(n,len(t)-i0)
    out[0,i0:i0+n]+=vol*(1-pan)*2*s[:n]; out[1,i0:i0+n]+=vol*pan*2*s[:n]
for t0,m,p in [(0.3,76,.5),(9.6,80,.5),(17.1,83,.5),(19.95,85,.55),(24.85,88,.5),(33.5,87,.4),(35.55,83,.5),(39.1,80,.45),(39.9,85,.55),
               (50.0,85,.5),(55.8,88,.5),(56.1,92,.5),(56.4,95,.5)]:
    bell(t0,m,pan=p)
fade=np.clip(t/0.5,0,1)*np.clip((D-t)/1.5,0,1)
out*=fade; out*=0.8/np.abs(out).max()
pcm=(out.T*32767*0.55).astype('<i2')
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
