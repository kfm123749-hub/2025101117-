// 갈턴 보드 시뮬레이션 (화면과 소리가 같은 데이터를 씀)
// 공은 핀 12줄을 지나며 매번 1/2 확률로 왼쪽·오른쪽 → 13칸 중 하나에 떨어짐
(function(root){
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
function simulate(){
  const R=12,N=1000,CX=540,DX=70,Y0=560,DY=40,BIN_BOTTOM=1560,BALL=5.4,COLS=6,G=2600;
  const rnd=mulberry32(20261114);
  const balls=[];
  for(let i=0;i<N;i++){
    const rel=i===0?0.55:3.0+9.0*Math.sqrt(i/(N-1));          // 첫 공은 혼자 천천히, 나머지는 점점 빠르게
    const step=i===0?0.17:0.075, drop=i===0?0.32:0.2;
    const ks=[0];for(let r=0;r<R;r++)ks.push(ks[r]+(rnd()<.5?0:1));
    const hits=[];for(let r=0;r<R;r++)hits.push(rel+drop+r*step);
    const exitT=rel+drop+R*step;
    balls.push({i,rel,step,drop,ks,hits,exitT,bin:ks[R],jit:(rnd()-.5)*6});
  }
  // 칸 안에서 쌓이는 순서 = 칸에 들어간 순서
  const order=[...balls].sort((a,b)=>a.exitT-b.exitT),cnt=Array(R+1).fill(0);
  for(const b of order){
    const s=cnt[b.bin]++;b.slot=s;
    const row=Math.floor(s/COLS),col=s%COLS;
    b.fx=CX+(b.bin-R/2)*DX+(col-(COLS-1)/2)*BALL*2.05+(row%2?BALL*.5:0);
    b.fy=BIN_BOTTOM-BALL-row*BALL*1.86;
    const y1=Y0+(R-1)*DY;b.fallT=Math.sqrt(2*Math.max(10,b.fy-y1)/G);b.landT=b.exitT+b.fallT;
  }
  return {R,N,CX,DX,Y0,DY,BIN_BOTTOM,BALL,G,balls,counts:cnt};
}
if(typeof module!=='undefined')module.exports={simulate};else root.GALTON=simulate();
})(this);
