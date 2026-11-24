// LAB 08 — 처마와 시선 · 바람
// 해측 처마 높이 · 지붕 경사 · 작업 자리를 바꾸면, 앉은 눈높이에서 하늘이 잘리는 각도와 바다가 남는 띠,
// 작업 자리 천장고, 처마 끝 풍속 · 들림 하중, 마을 지붕 경사와의 차이가 함께 다시 계산된다. (비어가는 마을 굴막 단면의 논리)
(function(){
  const root=document.getElementById('lab-eave'); if(!root) return;
  const P={He:1.9,a:22,D:9,xw:2.6,o:0.9,eye:1.1,hs:2.4,sh:5,V0:40,town:22};
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="sec"></canvas><p class="hint">빨간 처마 끝을 위아래로 = 처마 높이 · 앉은 사람을 좌우로 = 작업 자리</p></div>
  <div class="cv sheet"><canvas class="vw"></canvas><p class="hint">앉은 눈높이에서 바다 쪽으로 본 세로 시야 (−45° ~ +45°)</p></div></div><div class="nls"></div>`;
  const cS=app.querySelector('.sec'), cV=app.querySelector('.vw'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'지붕',k:'해측 처마 높이 m',min:1.3,max:3.6,step:.05,get:()=>P.He,set:v=>P.He=v},
    {g:'지붕',k:'지붕 경사 °',min:8,max:40,step:1,get:()=>P.a,set:v=>P.a=v},
    {g:'지붕',k:'처마 내밀기 m',min:0,max:2.5,step:.1,get:()=>P.o,set:v=>P.o=v},
    {g:'자리',k:'작업 자리 (처마선에서) m',min:.6,max:7,step:.1,get:()=>P.xw,set:v=>P.xw=v},
    {g:'자리',k:'눈높이',opts:['앉음 1.1m','선 자세 1.6m'],get:()=>P.eye>1.3?1:0,set:v=>P.eye=v?1.6:1.1},
    {g:'대지',k:'바다 위 바닥 높이 m',min:.8,max:6,step:.1,get:()=>P.hs,set:v=>P.hs=v},
    {g:'대지',k:'기본 풍속 m/s',min:26,max:46,step:1,get:()=>P.V0,set:v=>P.V0=v},
  ],draw);
  const R=Math.PI/180, deg=r=>r/R;
  function compute(){
    const t=Math.tan(P.a*R), ex=P.xw, ez=P.eye;
    const tipX=-P.o, tipZ=P.He-P.o*t;            // 처마 끝 (내밀기만큼 바다 쪽, 경사 따라 낮아짐)
    const thE=Math.atan2(tipZ-ez, ex-tipX);       // 처마 끝이 시야를 자르는 각 (위 +)
    const thQ=-Math.atan2(ez+0, ex+P.sh);         // 안벽 모서리 (바다가 보이기 시작하는 아래 한계)
    const seaTop=Math.min(0,thE), sea=Math.max(0,deg(seaTop-thQ)), sky=Math.max(0,deg(thE));
    const gaze=-20*R, glareTop=gaze+35*R, glare=Math.max(0,deg(Math.min(thE,glareTop)-Math.max(0,gaze)));
    const headroom=P.He+ex*t, back=P.He+P.D*t;
    const zr=Math.max(tipZ,1), Vz=P.V0*Math.pow(zr/10,.10)*1.0, q=.5*1.225*Vz*Vz/1000; // 해안 노풍도 D, 높이 보정
    const cpN=1.5+.8;                              // 처마 끝 윗면 흡인 + 아랫면 밀어올림 (내민 부분)
    const lift=q*cpN*Math.max(P.o,.3)/Math.cos(P.a*R)*(1+Math.max(0,tipZ-1.5)*.12);
    const dTown=P.a-P.town;
    const checks=[['하늘 보임 0°',sky<=.5],['바다 띠 ≥ 8°',sea>=8],['작업 자리 천장고 ≥ 2.1m',headroom>=2.1],['마을 경사 ±6°',Math.abs(dTown)<=6],['처마 끝 ≥ 1.2m (통행)',tipZ>=1.2]];
    return {t,tipX,tipZ,thE,thQ,sea,sky,glare,gaze,headroom,back,Vz,q,lift,dTown,checks};
  }
  let SS=null;
  function drawSec(Z){
    const [g,W,H]=LD.fit(cS), x0=-P.sh-9, x1=P.D+4, z0=-P.hs-1, z1=Math.max(Z.back,P.He)+1.6;
    const k=Math.min((W-40)/(x1-x0),(H-40)/(z1-z0)), ox=20-x0*k, oy=H-20+z0*k, X=x=>ox+x*k, Y=z=>oy-z*k;
    SS={k,ox,oy,X,Y};
    // 바다 · 안벽 · 바닥 · 뒤 마을 지형
    g.fillStyle='#1b2a33'; g.fillRect(X(x0),Y(-P.hs),(-P.sh-x0)*k,(P.hs+z0*-1)*k);
    g.strokeStyle=LD.BLUE; g.lineWidth=.8; g.beginPath(); g.moveTo(X(x0),Y(-P.hs)); g.lineTo(X(-P.sh),Y(-P.hs)); g.stroke();
    LD.path(g,[[X(-P.sh),Y(0)],[X(P.D+1),Y(0)],[X(P.D+1),Y(z0)],[X(-P.sh),Y(z0)]]); g.fillStyle='#2a2a26'; g.fill(); g.strokeStyle=LD.INK; g.lineWidth=1; g.stroke();
    // 마을 지붕선 (뒤쪽, 흐리게)
    g.strokeStyle=LD.FAINT; g.lineWidth=.8;
    for(let i=0;i<3;i++){const bx=P.D+.6+i*2.4,bz=Z.back*.0+1.2+i*1.3,tw=1.2*Math.tan(P.town*R);
      LD.path(g,[[X(bx),Y(bz-1.2)],[X(bx),Y(bz)],[X(bx+1.2),Y(bz+tw)],[X(bx+2.4),Y(bz)],[X(bx+2.4),Y(bz-1.2)]],false); g.stroke();}
    // 시선 부채: 바다 (파랑), 하늘 (빨강), 지붕에 막힘 (회색)
    const ex=X(P.xw), ey=Y(P.eye), Lr=(P.xw+P.sh+3)*k*1.4;
    for(let a=-40;a<=60;a+=2.5){const r=a*R, c=r>Z.thE?LD.FAINT:(r>0?LD.RED:(r>Z.thQ?LD.BLUE:'#555'));
      let len=Lr; if(r>Z.thE){len=Math.min(Lr,Math.hypot(P.xw-Z.tipX,Z.tipZ-P.eye)*k/Math.cos(r-Z.thE+1e-6)*.9);} if(r<=Z.thQ) len=Math.min(Lr,(P.eye/Math.max(.05,-Math.tan(r)))*k/Math.cos(r));
      g.strokeStyle=c; g.globalAlpha=r>Z.thE?.35:.55; g.lineWidth=.7; g.beginPath(); g.moveTo(ex,ey); g.lineTo(ex-Math.cos(r)*len,ey-Math.sin(r)*len); g.stroke();}
    g.globalAlpha=1;
    // 지붕 (얇은 막 + 서까래 선)
    const rx0=Z.tipX, rz0=Z.tipZ, rx1=P.D+.3, rz1=P.He+(P.D+.3)*Z.t;
    g.strokeStyle=LD.INK; g.lineWidth=2; g.beginPath(); g.moveTo(X(rx0),Y(rz0)); g.lineTo(X(rx1),Y(rz1)); g.stroke();
    g.lineWidth=1; g.beginPath(); g.moveTo(X(0),Y(0)); g.lineTo(X(0),Y(P.He)); g.moveTo(X(P.D),Y(0)); g.lineTo(X(P.D),Y(Z.back)); g.stroke();
    // 사람 (앉음/선 자세)
    g.fillStyle=LD.INK; g.beginPath(); g.arc(ex,ey-3,4,0,7); g.fill(); g.lineWidth=1.4; g.strokeStyle=LD.INK; g.beginPath();
    if(P.eye<1.3){g.moveTo(ex,ey+2); g.lineTo(ex+2,Y(.45)); g.lineTo(ex-10,Y(.45)); g.lineTo(ex-10,Y(0));} else {g.moveTo(ex,ey+2); g.lineTo(ex,Y(.85)); g.lineTo(ex-3,Y(0)); g.moveTo(ex,Y(.85)); g.lineTo(ex+3,Y(0));} g.stroke();
    // 처마 끝 핸들 · 치수
    g.fillStyle=LD.RED; g.beginPath(); g.arc(X(Z.tipX),Y(Z.tipZ),5,0,7); g.fill(); SS.hx=X(Z.tipX); SS.hy=Y(Z.tipZ); SS.px=ex; SS.py=ey;
    LD.dim(g,X(0),Y(0),X(0),Y(P.He),P.He.toFixed(2)+'m',-14);
    LD.dim(g,X(P.xw),Y(0),X(P.xw),Y(Z.headroom),Z.headroom.toFixed(2)+'m',14,Z.headroom>=2.1?LD.BLUE:LD.RED);
    LD.text(g,P.a+'°',X(P.D*.55),Y(P.He+P.D*.55*Z.t)-8,{c:LD.INK});
    // 바람 화살표 (처마 끝 풍속 비례)
    const wl=Z.Vz*1.1; g.strokeStyle='#cfc9b8'; g.lineWidth=1;
    for(let i=0;i<3;i++){const yy=Y(Z.tipZ)+(-8+i*8); g.beginPath(); g.moveTo(X(x0)+6,yy); g.lineTo(X(x0)+6+wl,yy); g.lineTo(X(x0)+wl,yy-3); g.stroke();}
    LD.text(g,'바람 '+Z.Vz.toFixed(1)+' m/s',X(x0)+6,Y(Z.tipZ)-14,{c:'#cfc9b8'});
    LD.text(g,'바다',X(x0)+6,Y(-P.hs)+14,{c:LD.BLUE});
  }
  function drawView(Z){
    const [g,W,H]=LD.fit(cV), m=24, top=m, bot=H-m, A=45*R, Y=r=>top+(A-r)/(2*A)*(bot-top), x0=m+40, x1=W-m;
    const band=(r0,r1,c)=>{const a=Math.max(-A,Math.min(A,r0)),b=Math.max(-A,Math.min(A,r1));if(b<=a)return;g.fillStyle=c;g.fillRect(x0,Y(b),x1-x0,Y(a)-Y(b));};
    band(Z.thE,A,'#3a342c');              // 지붕 아랫면
    band(0,Z.thE,'#d9dde0');               // 하늘
    band(Z.thQ,Math.min(0,Z.thE),'#2f5a73'); // 바다
    band(-A,Z.thQ,'#55524b');              // 안벽 · 바닥
    // 지붕 아랫면 서까래, 바다 물결
    g.strokeStyle='#5a5246'; g.lineWidth=1; for(let i=1;i<9;i++){const yy=Y(Z.thE)-(Y(Z.thE)-top)*Math.pow(i/9,1.6); if(yy>top&&Z.thE<A){g.beginPath();g.moveTo(x0,yy);g.lineTo(x1,yy);g.stroke();}}
    g.strokeStyle='#4f7c95'; for(let r=Z.thQ+1.5*R;r<Math.min(0,Z.thE);r+=1.8*R){const yy=Y(r);g.beginPath();for(let x=x0;x<x1;x+=6)g.lineTo(x,yy+Math.sin(x*.12+r*90)*1.2);g.stroke();}
    // 눈부심 구간 (시선 −20° 위 35° 안에 보이는 하늘)
    if(Z.glare>0){g.fillStyle='rgba(255,107,74,.35)';g.fillRect(x0,Y(Math.min(Z.thE,Z.gaze+35*R)),x1-x0,Y(Math.max(0,Z.gaze))-Y(Math.min(Z.thE,Z.gaze+35*R)));}
    // 눈금
    for(let a=-40;a<=40;a+=10){const yy=Y(a*R);g.strokeStyle=LD.FAINT;g.beginPath();g.moveTo(x0-6,yy);g.lineTo(x0,yy);g.stroke();LD.text(g,(a>0?'+':'')+a+'°',x0-10,yy+3,{a:'right'});}
    const lab=(r,s,c)=>{if(r<-A||r>A)return;const yy=Y(r);g.strokeStyle=c;g.lineWidth=1;g.beginPath();g.moveTo(x0,yy);g.lineTo(x1,yy);g.stroke();LD.text(g,s,x1-6,yy-4,{c:c,a:'right'});};
    lab(0,'수평선',LD.INK); lab(Z.thE,'처마 끝 '+deg(Z.thE).toFixed(1)+'°',LD.RED); lab(Z.thQ,'안벽 '+deg(Z.thQ).toFixed(1)+'°','#bbb');
    // 손끝 (작업면) 시선
    const gy=Y(Z.gaze); g.strokeStyle=LD.GREEN; g.setLineDash([4,4]); g.beginPath(); g.moveTo(x0,gy); g.lineTo(x1,gy); g.stroke(); g.setLineDash([]); LD.text(g,'손끝 시선 −20°',x0+6,gy-4,{c:LD.GREEN});
  }
  function stats(Z){
    LD.stats(out,[
      ['하늘 보임',Z.sky.toFixed(1)+'°',Z.sky>.5?'ng':''],['바다 띠',Z.sea.toFixed(1)+'°'],['눈부심 (시선 위 하늘)',Z.glare.toFixed(1)+'°',Z.glare>0?'ng':''],
      ['작업 자리 천장고',Z.headroom.toFixed(2)+' m',Z.headroom<2.1?'ng':''],['처마 끝 높이',Z.tipZ.toFixed(2)+' m'],['처마 끝 풍속',Z.Vz.toFixed(1)+' m/s'],
      ['처마 들림 하중',Z.lift.toFixed(2)+' kN/m'],['마을 경사와 차이',(Z.dTown>0?'+':'')+Z.dTown+'°',Math.abs(Z.dTown)>6?'ng':''],
      ['판정',Z.checks.filter(c=>c[1]).length+' / '+Z.checks.length+' OK'],['NG',Z.checks.filter(c=>!c[1]).map(c=>c[0]).join(', ')||'없음',Z.checks.some(c=>!c[1])?'ng':'']
    ],[0,1,9],'처마를 낮추면 하늘이 잘리고 바람을 받는 높이가 내려가지만, 작업 자리 천장고가 모자라면 경사를 세우거나 자리를 안쪽으로 옮겨야 한다. 풍속은 해안(노풍도 D) 높이 보정, 들림 하중은 내민 처마 윗면 흡인과 아랫면 밀어올림을 합친 근사값이다.');
  }
  function draw(){const Z=compute();drawSec(Z);drawView(Z);stats(Z);}
  // 조작
  let drag=null; const loc=(cv,e)=>{const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];};
  cS.addEventListener('pointerdown',e=>{const [x,y]=loc(cS,e);if(Math.hypot(x-SS.hx,y-SS.hy)<14)drag='e';else if(Math.hypot(x-SS.px,y-SS.py)<18)drag='p';if(drag)cS.setPointerCapture(e.pointerId);});
  cS.addEventListener('pointermove',e=>{const [x,y]=loc(cS,e);if(!drag){cS.style.cursor=Math.hypot(x-SS.hx,y-SS.hy)<14?'ns-resize':Math.hypot(x-SS.px,y-SS.py)<18?'ew-resize':'default';return;}
    if(drag==='e'){const z=(SS.oy-y)/SS.k+P.o*Math.tan(P.a*R);P.He=Math.max(1.3,Math.min(3.6,Math.round(z*20)/20));}
    else P.xw=Math.max(.6,Math.min(7,Math.round((x-SS.ox)/SS.k*10)/10));
    refresh();draw();});
  cS.addEventListener('pointerup',()=>drag=null);
  const wave=(t,a,b,sp,ph)=>a+(b-a)*(1-Math.cos(t*sp+(ph||0)))/2, q=(v,st)=>Math.round(v/st)*st;
  app.demo={step:t=>{P.He=q(wave(t,1.4,3.2,.5),.05);P.a=q(wave(t,12,34,.23,1.3),1);P.xw=q(wave(t,1.2,4.5,.17,2),.1);draw();},stop:()=>refresh()};
  LabIO(app,{name:'eave',state:()=>({P}),load:o=>{Object.assign(P,o.P||{});refresh();},redraw:draw});
  addEventListener('resize',draw); draw();
})();
