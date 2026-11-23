// LAB 04 — 계단 설계
// 층고를 끌어 올리면 단 수 · 단높이 · 디딤판 · 계단참이 다시 잡히고, 용도별 법규(건축물의 피난·방화구조 등의 기준에 관한 규칙 제15조,
// 공동주택은 주택건설기준 등에 관한 규정)와 보행 공식(2R+T ≈ 63cm)으로 OK/NG를 판정한다.
(function(){
  const root=document.getElementById('lab-stair'); if(!root) return;
  const USE=[
    {n:'일반 (기타 건축물)',R:20,T:24,W:60},
    {n:'공동주택',R:18,T:26,W:120},
    {n:'판매 · 집회 · 문화',R:18,T:26,W:120},
    {n:'중 · 고등학교',R:18,T:26,W:150},
    {n:'초등학교',R:16,T:26,W:150},
  ];
  const P={H:3.6,W:120,use:1,type:1,rt:17};
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="sec"></canvas><p class="hint">위층 바닥의 파란 점을 위아래로 드래그 = 층고</p></div>
  <div class="cv sheet"><canvas class="pl"></canvas><p class="hint">파란 점을 좌우로 드래그 = 계단 폭</p></div></div><div class="nls"></div>`;
  const cS=app.querySelector('.sec'), cP=app.querySelector('.pl'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'법규',k:'용도',opts:USE.map(u=>u.n),get:()=>P.use,set:v=>P.use=v},
    {g:'계단',k:'형식',opts:['직선 계단','ㄷ자 (반층참)'],get:()=>P.type,set:v=>P.type=v},
    {g:'계단',k:'목표 단높이 cm',min:14,max:20,step:.5,get:()=>P.rt,set:v=>P.rt=v},
  ],draw);

  function compute(){
    const U=USE[P.use], Hc=P.H*100, rmax=Math.min(U.R,P.rt);
    const n=Math.ceil(Hc/rmax-1e-9), R=Hc/n;
    const T=Math.max(U.T,Math.min(32,Math.round((63-2*R)*2)/2));
    let f=Math.max(P.type?2:1,Math.ceil(P.H/3-1e-9)); if(P.type&&f%2) f++;
    const per=[]; for(let i=0;i<f;i++) per.push(Math.floor(n/f)+(i<n%f?1:0));
    const land=Math.max(120,P.W), runs=per.map(r=>(r-1)*T);
    const planL = P.type ? Math.max(...runs)+land : runs.reduce((a,b)=>a+b,0)+(f-1)*land;
    const planW = P.type ? 2*P.W+10 : P.W;
    const blondel=2*R+T, maxFlightH=Math.max(...per)*R;
    const checks=[
      ['단높이 ≤ '+U.R,R<=U.R+1e-6],['단너비 ≥ '+U.T,T>=U.T],['계단 폭 ≥ '+U.W,P.W>=U.W],
      ['2R+T 60~66',blondel>=60&&blondel<=66],['3m마다 계단참',maxFlightH<=300+1e-6]];
    return {U,n,R,T,f,per,land,runs,planL,planW,blondel,checks,ang:Math.atan(R/T)*180/Math.PI};
  }

  let SS=null, SP=null;
  function drawSec(Z){
    const [g,W,H]=LD.fit(cS), Hc=P.H*100;
    // 단면: 직선은 전체 펼침, ㄷ자는 첫 비행 + 참 + 둘째 비행(뒤쪽, 흐리게)
    const L = P.type ? Math.max(...Z.runs)+Z.land : Z.planL;
    const k=Math.min((W-110)/L,(H-70)/(Hc+60)), ox=60, oy=H-34;
    SS={k,ox,oy}; const X=x=>ox+x*k, Y=z=>oy-z*k;
    // 바닥 슬래브
    g.fillStyle='#2a2a26'; g.fillRect(X(-40),Y(0),(L+80)*k,18*k+2); g.fillRect(X(P.type?-40:L-10),Y(Hc),(P.type?Z.runs[0]+60:90)*k,18*k+2);
    let x=0,z=0, pts=[[X(0),Y(0)]], ghost=[];
    Z.per.forEach((r,fi)=>{
      const dir = P.type ? (fi%2?-1:1) : 1, line=[];
      for(let i=0;i<r;i++){ z+=Z.R; line.push([x,z-Z.R],[x,z]); if(i<r-1) x+=dir*Z.T; }
      const pp=line.map(p=>[X(p[0]),Y(p[1])]);
      if(P.type&&fi%2){ghost.push(pp);} else pts.push(...pp);
      if(fi<Z.per.length-1){ const lx=x+dir*Z.land; if(!(P.type&&fi%2)) pts.push([X(lx),Y(z)]); else ghost[ghost.length-1].push([X(lx),Y(z)]); if(!P.type) x=lx; }
    });
    // 계단 몸체 (포셰)
    g.lineWidth=1.2; g.strokeStyle=LD.INK;
    LD.path(g,pts,false); g.stroke();
    ghost.forEach(pp=>{g.setLineDash([4,3]);g.strokeStyle=LD.DIM;LD.path(g,pp,false);g.stroke();g.setLineDash([]);});
    // 기울기 선 + 헤드룸 2.1m
    const fr=Z.per[0], x1=(fr-1)*Z.T, z1=fr*Z.R;
    g.strokeStyle='rgba(77,163,255,.5)';g.setLineDash([2,3]);g.beginPath();g.moveTo(X(0),Y(0+210));g.lineTo(X(x1),Y(z1+210));g.stroke();g.setLineDash([]);
    LD.text(g,'헤드룸 2.1m',X(x1*0.25),Y(Z.R*fr*0.25+210)-6,{c:LD.BLUE});
    // 단 치수 (빨강)
    const sx=X(Z.T), sz=Y(2*Z.R);
    g.strokeStyle=LD.RED;g.lineWidth=1.4;g.beginPath();g.moveTo(X(Z.T),Y(Z.R));g.lineTo(X(Z.T),Y(2*Z.R));g.lineTo(X(2*Z.T),Y(2*Z.R));g.stroke();
    LD.text(g,`R ${Z.R.toFixed(1)}`,sx-6,(Y(Z.R)+Y(2*Z.R))/2+3,{c:LD.RED,a:'right'}); LD.text(g,`T ${Z.T}`,(X(Z.T)+X(2*Z.T))/2,sz-6,{c:LD.RED,a:'center'});
    // 층고 치수 + 핸들
    LD.dim(g,X(L)+30,Y(0),X(L)+30,Y(Hc),`H ${P.H.toFixed(2)}m`,-14);
    LD.text(g,'FL ±0',X(-40),Y(0)+14); LD.text(g,`FL +${P.H.toFixed(2)}`,X(P.type?-40:L-10),Y(Hc)-6);
    const hx=P.type?X(-40)+10:X(L)+10; g.beginPath();g.arc(hx,Y(Hc),6,0,7);g.fillStyle=LD.BG;g.fill();g.strokeStyle=LD.BLUE;g.lineWidth=2;g.stroke();
    SS.hx=hx; SS.hy=Y(Hc);
    LD.text(g,`${Z.n}단 · 경사 ${Z.ang.toFixed(1)}°`,12,18,{c:LD.INK,size:11});
  }
  function drawPlan(Z){
    const [g,W,H]=LD.fit(cP);
    const k=Math.min((W-90)/Z.planL,(H-80)/Z.planW), ox=(W-Z.planL*k)/2, oy=(H-Z.planW*k)/2;
    SP={k,ox,oy}; const X=x=>ox+x*k, Y=y=>oy+y*k;
    g.strokeStyle=LD.INK; g.lineWidth=1.4; g.strokeRect(X(0),Y(0),Z.planL*k,Z.planW*k);
    const tread=(x0,y0,w,n,dir)=>{g.strokeStyle=LD.INK;g.lineWidth=.7;g.beginPath();for(let i=0;i<=n;i++){const x=x0+dir*i*Z.T;g.moveTo(X(x),Y(y0));g.lineTo(X(x),Y(y0+w));}g.stroke();};
    const land=(x0,y0,w,h)=>{g.save();g.beginPath();g.rect(X(x0),Y(y0),w*k,h*k);g.clip();g.fillStyle='rgba(255,255,255,.04)';g.fillRect(X(x0),Y(y0),w*k,h*k);g.strokeStyle=LD.FAINT;g.lineWidth=.6;g.beginPath();for(let s=-h*k;s<w*k;s+=8){g.moveTo(X(x0)+s,Y(y0)+h*k);g.lineTo(X(x0)+s+h*k,Y(y0));}g.stroke();g.restore();g.strokeStyle=LD.INK;g.lineWidth=.8;g.strokeRect(X(x0),Y(y0),w*k,h*k);};
    let arrow=[];
    if(P.type){
      const r0=Z.runs[0], r1=Z.runs[1]||r0, L0=Z.planL-Z.land;
      tread(0,Z.planW-P.W,P.W,Z.per[0]-1,1); tread(L0,0,P.W,(Z.per[1]||1)-1,-1);
      land(L0,0,Z.land,Z.planW);
      g.strokeStyle=LD.INK;g.lineWidth=1;g.beginPath();g.moveTo(X(0),Y(P.W+5));g.lineTo(X(L0),Y(P.W+5));g.stroke();
      arrow=[[0+Z.T/2,Z.planW-P.W/2],[L0+Z.land/2,Z.planW-P.W/2],[L0+Z.land/2,P.W/2],[L0-r1+Z.T/2,P.W/2]];
    } else {
      let x=0; Z.per.forEach((r,i)=>{tread(x,0,P.W,r-1,1); x+=(r-1)*Z.T; if(i<Z.per.length-1){land(x,0,Z.land,P.W); x+=Z.land;}});
      arrow=[[Z.T/2,P.W/2],[Z.planL-Z.T/2,P.W/2]];
    }
    g.strokeStyle=LD.RED;g.lineWidth=1.2;LD.path(g,arrow.map(p=>[X(p[0]),Y(p[1])]),false);g.stroke();
    const e=arrow[arrow.length-1], e0=arrow[arrow.length-2], a=Math.atan2(e[1]-e0[1],e[0]-e0[0]);
    g.beginPath();g.moveTo(X(e[0]),Y(e[1]));g.lineTo(X(e[0])-9*Math.cos(a-.4),Y(e[1])-9*Math.sin(a-.4));g.moveTo(X(e[0]),Y(e[1]));g.lineTo(X(e[0])-9*Math.cos(a+.4),Y(e[1])-9*Math.sin(a+.4));g.stroke();
    g.beginPath();g.arc(X(arrow[0][0]),Y(arrow[0][1]),3,0,7);g.fillStyle=LD.RED;g.fill(); LD.text(g,'UP',X(arrow[0][0])+6,Y(arrow[0][1])-6,{c:LD.RED});
    LD.dim(g,X(0),Y(Z.planW),X(Z.planL),Y(Z.planW),`${(Z.planL/100).toFixed(2)} m`,22);
    LD.dim(g,X(0),Y(0),X(0),Y(Z.planW),`${(Z.planW/100).toFixed(2)} m`,22);
    // 폭 핸들: 첫 비행 바깥 변
    const hy=P.type?Y(Z.planW):Y(P.W), hx=X(Z.T*1.5); g.beginPath();g.arc(hx,hy,6,0,7);g.fillStyle=LD.BG;g.fill();g.strokeStyle=LD.BLUE;g.lineWidth=2;g.stroke();
    SP.hx=hx;SP.hy=hy;
    LD.text(g,`계단실 ${(Z.planL/100).toFixed(2)} × ${(Z.planW/100).toFixed(2)} m · 폭 ${P.W}cm · 참 ${Z.land}cm`,12,18,{c:LD.INK,size:11});
  }
  function stats(Z){
    LD.stats(out,[
      ['층고',P.H.toFixed(2)+' m'],['단 수',Z.n+'단 · '+Z.f+'비행'],['단높이 R',Z.R.toFixed(1)+' cm'],['단너비 T',Z.T+' cm'],
      ['2R + T',Z.blondel.toFixed(1)+' cm'],['계단실',(Z.planL/100).toFixed(2)+' × '+(Z.planW/100).toFixed(2)+' m'],
      ['법규 · 보행',Z.checks.filter(c=>c[1]).length+' / '+Z.checks.length+' OK'],['NG',Z.checks.filter(c=>!c[1]).map(c=>c[0]).join(', ')||'없음',Z.checks.some(c=>!c[1])?'ng':'']
    ],[6,7],`${Z.U.n}: 단높이 ${Z.U.R}cm 이하 · 단너비 ${Z.U.T}cm 이상 · 폭 ${Z.U.W}cm 이상, 높이 3m를 넘으면 3m 이내마다 너비 120cm 이상의 계단참. 2R+T는 걷기 편한 범위(블롱델 공식)로 법규가 아니라 권장값.`);
  }
  function draw(){const Z=compute();drawSec(Z);drawPlan(Z);stats(Z);}

  // 조작
  let dS=false,dP=false;
  const loc=(cv,e)=>{const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];};
  cS.addEventListener('pointerdown',e=>{const [x,y]=loc(cS,e);if(Math.hypot(x-SS.hx,y-SS.hy)<14){dS=true;cS.setPointerCapture(e.pointerId);}});
  cS.addEventListener('pointermove',e=>{const [x,y]=loc(cS,e);if(!dS){cS.style.cursor=Math.hypot(x-SS.hx,y-SS.hy)<14?'ns-resize':'default';return;}
    P.H=Math.max(2.4,Math.min(6,Math.round((SS.oy-y)/SS.k/5)*5/100));draw();});
  cS.addEventListener('pointerup',()=>dS=false);
  cP.addEventListener('pointerdown',e=>{const [x,y]=loc(cP,e);if(Math.hypot(x-SP.hx,y-SP.hy)<14){dP=true;cP.setPointerCapture(e.pointerId);}});
  cP.addEventListener('pointermove',e=>{const [x,y]=loc(cP,e);if(!dP){cP.style.cursor=Math.hypot(x-SP.hx,y-SP.hy)<14?'ns-resize':'default';return;}
    const yy=(y-SP.oy)/SP.k; P.W=Math.max(60,Math.min(240,Math.round((P.type?(yy-10)/2:yy)/5)*5));draw();});
  cP.addEventListener('pointerup',()=>dP=false);
  LabIO(app,{name:'stair',state:()=>({P}),load:o=>{Object.assign(P,o.P||{});refresh();},redraw:draw});
  addEventListener('resize',draw); draw();
})();
