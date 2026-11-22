// 「생성형 AI 10년」 공용 시간표 — 화면(index.html)과 음악(score.py)이 같은 값을 씀
(function(root){
const cl=x=>Math.min(1,Math.max(0,x)),io=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
function kf(t,ks){if(t<=ks[0][0])return ks[0][1];for(let i=1;i<ks.length;i++)if(t<=ks[i][0]){const [a,va]=ks[i-1],[b,vb]=ks[i];return va+(vb-va)*io((t-a)/(b-a));}return ks[ks.length-1][1];}
const S={hook:0,scale:4.6,chat:12.6,modal:21.6,cost:33,adopt:41,limit:49,twist:54,end:60};
// 훅: 픽셀 해상도 단계 (시각, 한 변의 픽셀 수)
const FACE=[[0,18],[1.75,24],[1.95,32],[2.15,48],[2.35,64],[2.55,96],[2.75,160],[2.95,512]];
const faceN=t=>{let n=FACE[0][1];for(const [a,v] of FACE)if(t>=a)n=v;return n;};
// 1장: 카메라 확대 배율
const zoom=t=>Math.exp(kf(t,[[4.6,Math.log(18)],[6.0,Math.log(18)],[7.4,Math.log(5)],[9.0,Math.log(5)],[10.5,0]]));
// 2장: 경과 개월 수 (처음엔 천천히)
const R0=13.3,R1=17.3,months=t=>30*Math.pow(cl((t-R0)/(R1-R0)),2),finish=m=>R0+(R1-R0)*Math.sqrt(m/30);
// 3장: 글자 입력
const PROMPT='A small sailboat on a sunset sea',REPLY=['Under an orange sky,','a little sailboat drifts slowly on.'];
const typeT=k=>22.0+1.0*k/PROMPT.length, replyT=k=>23.05+.8*k/(REPLY[0].length+REPLY[1].length);
const MODES=[21.6,24.0,26.6,29.4,31.0];
// 4장: 동전
let s=280;const rnd=()=>(s=(s*16807)%2147483647)/2147483647;
const COIN=[...Array(280)].map(()=>({a:33.35+1.15*rnd(),c:36.3+.55*rnd()}));
// 5장: 사람 아이콘 53개가 켜지는 시각
const LIT=[...Array(53)].map((_,k)=>41.6+2.8*Math.pow(k/52,.85));
const api={S,FACE,faceN,zoom,months,finish,PROMPT,REPLY,typeT,replyT,MODES,COIN,LIT,kf};
if(typeof module!=='undefined')module.exports=api;else root.TL=api;
})(this);
