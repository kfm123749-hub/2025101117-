// 「침착함은 순서다」 공용 시간축 — 화면(index.html)과 소리(score.py)가 같은 값을 씀
//  A(t)      : 흥분도 1(패닉) → 0(침착)
//  breath(t) : 호흡 0(다 내쉼) ~ 1(가득 들이쉼)
//  beats     : 심장 박동 시각 (흥분도가 낮아질수록 느려짐)
(function(root){
const cl=x=>Math.min(1,Math.max(0,x)), sm=x=>x*x*(3-2*x);
function kf(t,ks){if(t<=ks[0][0])return ks[0][1];for(let i=1;i<ks.length;i++)if(t<=ks[i][0]){const [a,va]=ks[i-1],[b,vb]=ks[i];return va+(vb-va)*sm((t-a)/(b-a));}return ks[ks.length-1][1];}
const T={why:5,breath:13,in1:16,ex1:20,in2:26,ex2:30,label:36,box:38.6,step:45,collapse:48.2,close:53,end:60};
const A=t=>kf(t,[[0,1],[5,1],[6.2,.9],[13,.85],[16,.8],[20,.74],[26,.46],[30,.42],[36,.2],[38.4,.26],[39.6,.12],[45,.11],[47.8,.15],[49.2,.06],[53,.05],[56,.02],[60,.02]]);
const cosE=(a,b,s)=>a+(b-a)*(1-Math.cos(Math.PI*cl(s)))/2;
function breath(t){
  if(t<T.in1)return .2+.07*(1-cl((t-14.2)/1.6))*Math.sin(2*Math.PI*.8*t);     // 얕고 빠른 숨
  if(t<T.ex1)return cosE(.2,1,(t-T.in1)/4);
  if(t<T.in2)return cosE(1,0,(t-T.ex1)/6);
  if(t<T.ex2)return cosE(0,1,(t-T.in2)/4);
  if(t<T.label)return cosE(1,.05,(t-T.ex2)/6);
  if(t<T.close)return .05;
  return .22+.16*(1-Math.cos(2*Math.PI*(t-T.close)/8.5))/2;                    // 마지막: 고요한 숨
}
const bpm=t=>60+72*Math.pow(A(t),1.1);
const beats=[];{let ph=.85;for(let t=0;t<60;t+=.001){ph+=bpm(t)/60*.001;if(ph>=1){ph-=1;beats.push(+t.toFixed(3));}}}
const api={T,A,breath,bpm,beats};
if(typeof module!=='undefined')module.exports=api;else root.TL=api;
})(this);
