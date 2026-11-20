// 화면과 소리가 함께 쓰는 시간축: 영상 t초에 흐른 '지구 년수' (해왕성 발견 1846.73년부터)
(function(root){
const NEP=164.79, START=1846.73;                     // 1846년 9월 23일 발견
const cl=x=>Math.min(1,Math.max(0,x)), io=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
function years(t){
  if(t<2.8)return .03*t;                             // 훅: 거의 멈춤
  if(t<7.4)return .084+(1-.084)*io(cl((t-2.8)/4.6)); // 지구 1바퀴
  if(t<8.6)return 1;                                 // 잠깐 정지: 해왕성은 2.2°
  if(t<11.0){const s=cl((t-8.6)/2.4);return Math.pow(40,s);}                      // 1년 → 40년 (가속)
  const s=cl((t-11.0)/4.8);return 40+(NEP-40)*(1-Math.pow(1-s,2.2));               // 40년 → 164.79년 (감속하며 도착)
}
const EVENTS=[[1903.96,'1903','첫 동력 비행'],[1969.55,'1969','달 착륙'],[1989.65,'1989','보이저 2호 방문']];
const api={years,NEP,START,EVENTS};
if(typeof module!=='undefined')module.exports=api;else root.TL=api;
})(this);
