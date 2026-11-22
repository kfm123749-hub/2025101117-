// 「60초 상대성 이론」 공용 시간축 — 화면(index.html)과 소리(score.py)가 같은 값을 씀
(function(root){
const cl=x=>Math.min(1,Math.max(0,x)),io=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
function kf(t,ks){if(t<=ks[0][0])return ks[0][1];for(let i=1;i<ks.length;i++)if(t<=ks[i][0]){const [a,va]=ks[i-1],[b,vb]=ks[i];return va+(vb-va)*io((t-a)/(b-a));}return ks[ks.length-1][1];}
const S={hook:0,title:4.6,c:8,clock:13,gamma:23,eq:30,curve:35,gtd:43,gps:49,end:56};
// 빛 시계: 멈춘 시계 한 번 건너는 데 0.6초, 빛 속도의 60%로 움직이는 시계는 0.75초 (γ = 1.25)
const LC={ph0:13.4,run0:14.6,run1:17.6,tau0:.6,tau1:.75};
// 속도 그래프: β(t)
const beta=t=>kf(t,[[23.6,0],[24.6,.5],[25.2,.5],[26.0,Math.sqrt(3)/2],[26.6,Math.sqrt(3)/2],[27.6,.99],[29.6,.99]]);
const gamma=b=>1/Math.sqrt(1-b*b);
// 중력 시간 지연(과장): 가까운 시계 0.55배
const GTD={t0:43.9,far:.5,near:.5/.55};
const ev={hookTicks:[],topHits:[],botHits:[],earthTicks:[],shipTicks:[],farTicks:[],nearTicks:[]};
{let x=.35,dt=.24;while(x<3.5){ev.hookTicks.push(+x.toFixed(3));x+=dt;dt=Math.max(.045,dt*.9);}}
for(let k=1;;k++){const x=LC.ph0+k*LC.tau0;if(x>LC.run1+1e-6)break;ev.topHits.push(+x.toFixed(3));}
for(let k=1;;k++){const x=LC.ph0+k*LC.tau0;if(x>LC.run0+1e-6)break;ev.botHits.push(+x.toFixed(3));}
for(let k=1;;k++){const x=LC.run0+k*LC.tau1;if(x>LC.run1+1e-6)break;ev.botHits.push(+x.toFixed(3));}
// 우주선 시계의 누적 위상 (1/γ 로 흐름)
const SP=[];{let p=0;for(let i=0;i<=8000;i++){const x=23.6+i/1000;SP.push(p);p+=1/1000/gamma(Math.min(.995,beta(x)));}}
const shipPhase=t=>t<=23.6?0:SP[Math.min(SP.length-1,Math.round((t-23.6)*1000))];
for(let x=23.6+.5;x<29.6;x+=.5)ev.earthTicks.push(+x.toFixed(3));
for(let k=1;;k++){let lo=23.6,hi=31.6,goal=k*.5;if(shipPhase(29.6)<goal)break;for(let i=0;i<40;i++){const m=(lo+hi)/2;shipPhase(m)<goal?lo=m:hi=m;}ev.shipTicks.push(+lo.toFixed(3));}
for(let x=GTD.t0;x<48.8;x+=GTD.far)ev.farTicks.push(+x.toFixed(3));
for(let x=GTD.t0;x<48.8;x+=GTD.near)ev.nearTicks.push(+x.toFixed(3));
const api={S,LC,beta,gamma,shipPhase,GTD,ev,kf};
if(typeof module!=='undefined')module.exports=api;else root.TL=api;
})(this);
