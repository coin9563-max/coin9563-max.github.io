// LAB 06 — 일조 시간 (동지 기준)
// 건물을 끌어 옮기면 대지 위 1m 격자마다 09~15시 동안 해가 드는 시간을 계산한다(광선-상자 교차).
// 공동주택 일조 기준(동지 09~15시 중 연속 2시간 이상 또는 08~16시 중 총 4시간 이상)을 체크한다.
(function(){
  const root=document.getElementById('lab-sun'); if(!root) return;
  const DAYS=[{n:'동지 (12/22)',d:-23.44},{n:'춘·추분',d:0},{n:'하지 (6/21)',d:23.44}];
  const P={lat:37.5,day:0,t:12,sel:0,step:10};
  let B=[{x:8,y:6,w:34,d:11,h:27},{x:12,y:30,w:12,d:10,h:12},{x:34,y:34,w:16,d:12,h:18}];
  const S=60; // 대지 60×60m
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="map"></canvas><p class="hint">건물 드래그 = 이동 · 파란 모서리 = 크기 · 빈 곳 더블클릭 = 건물 추가</p></div>
  <div class="cv sheet"><canvas class="sh"></canvas><p class="hint">선택 시각의 그림자 · 태양 궤적</p></div></div><div class="nls"></div>`;
  const cM=app.querySelector('.map'), cS=app.querySelector('.sh'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'태양',k:'날짜',opts:DAYS.map(d=>d.n),get:()=>P.day,set:v=>P.day=v},
    {g:'태양',k:'위도 °',min:33,max:38.5,step:.1,get:()=>P.lat,set:v=>P.lat=v},
    {g:'태양',k:'그림자 시각',min:8,max:16,step:.25,get:()=>P.t,set:v=>P.t=v,fmt:v=>{const h=Math.floor(v),m=Math.round((v-h)*60);return h+':'+String(m).padStart(2,'0');}},
    {g:'선택 건물',k:'높이 m',min:3,max:60,step:1,get:()=>B[P.sel]?B[P.sel].h:0,set:v=>{if(B[P.sel])B[P.sel].h=v;}},
  ],()=>{calc();draw();});

  function sun(t){ // t: 진태양시(시)
    const f=P.lat*Math.PI/180, d=DAYS[P.day].d*Math.PI/180, H=(t-12)*15*Math.PI/180;
    const alt=Math.asin(Math.sin(f)*Math.sin(d)+Math.cos(f)*Math.cos(d)*Math.cos(H));
    const az=Math.atan2(Math.sin(H),Math.cos(H)*Math.sin(f)-Math.tan(d)*Math.cos(f)); // 남쪽 기준, 서쪽 +
    return {alt,az,dx:-Math.sin(az),dy:Math.cos(az),tz:Math.tan(alt)};
  }
  function lit(x,y,s){ // 지면 점 (x,y)에서 해 쪽으로 쏜 광선이 건물에 막히는가
    if(s.alt<=0) return false;
    for(const b of B){ let t0=0,t1=1e9;
      for(const [p,dd,lo,hi] of [[x,s.dx,b.x,b.x+b.w],[y,s.dy,b.y,b.y+b.d]]){
        if(Math.abs(dd)<1e-9){ if(p<lo||p>hi){t0=1e9;break;} continue; }
        let a=(lo-p)/dd, c=(hi-p)/dd; if(a>c)[a,c]=[c,a]; t0=Math.max(t0,a); t1=Math.min(t1,c); }
      if(t0<t1 && t1>0 && Math.max(t0,0)*s.tz<b.h) return false; }
    return true;
  }
  const inB=(x,y)=>B.some(b=>x>b.x&&x<b.x+b.w&&y>b.y&&y<b.y+b.d);
  let G=null;
  function calc(){
    const ts=[]; for(let t=8;t<=16+1e-9;t+=P.step/60) ts.push(t);
    const suns=ts.map(sun), cont=new Float32Array(S*S), tot=new Float32Array(S*S), dt=P.step/60;
    for(let j=0;j<S;j++)for(let i=0;i<S;i++){const x=i+.5,y=j+.5,k=j*S+i; if(inB(x,y)){cont[k]=-1;continue;}
      let run=0,best=0,sum=0; ts.forEach((t,n)=>{const l=lit(x,y,suns[n]); if(l)sum+=dt; if(t>=9-1e-9&&t<=15+1e-9){ if(l){run+=dt;best=Math.max(best,run);} else run=0; }});
      cont[k]=best; tot[k]=sum; }
    let open=0,ok2=0,ok4=0; for(let k=0;k<S*S;k++){ if(cont[k]<0) continue; open++; if(cont[k]>=2-1e-6)ok2++; if(tot[k]>=4-1e-6)ok4++; }
    G={cont,tot,open,ok2,ok4};
  }
  const col=v=>{ if(v<0) return null; const t=Math.min(1,v/6); // 0h 어두운 남색 → 6h 따뜻한 노랑
    const r=Math.round(28+t*(240-28)), g=Math.round(30+t*(196-30)), b=Math.round(48+t*(90-48)); return `rgb(${r},${g},${b})`; };
  let TM=null;
  function drawMap(){
    const [g,W,H]=LD.fit(cM), k=Math.min(W-60,H-70)/S, ox=(W-S*k)/2+10, oy=(H-S*k)/2-6; TM={k,ox,oy};
    for(let j=0;j<S;j++)for(let i=0;i<S;i++){const v=G.cont[j*S+i]; if(v<0) continue; g.fillStyle=col(v); g.fillRect(ox+i*k,oy+j*k,k+.6,k+.6);}
    // 2시간 경계선
    g.strokeStyle=LD.RED;g.lineWidth=1.4;g.beginPath();
    for(let j=0;j<S;j++)for(let i=0;i<S;i++){const a=G.cont[j*S+i]; if(a<0) continue; const A=a>=2-1e-6;
      if(i+1<S){const b=G.cont[j*S+i+1]; if(b>=0&&(b>=2-1e-6)!==A){g.moveTo(ox+(i+1)*k,oy+j*k);g.lineTo(ox+(i+1)*k,oy+(j+1)*k);}}
      if(j+1<S){const b=G.cont[(j+1)*S+i]; if(b>=0&&(b>=2-1e-6)!==A){g.moveTo(ox+i*k,oy+(j+1)*k);g.lineTo(ox+(i+1)*k,oy+(j+1)*k);}}}
    g.stroke();
    B.forEach((b,i)=>{g.fillStyle='#1e1e1b';g.fillRect(ox+b.x*k,oy+b.y*k,b.w*k,b.d*k);g.strokeStyle=i===P.sel?LD.BLUE:LD.INK;g.lineWidth=i===P.sel?2:1.2;g.strokeRect(ox+b.x*k,oy+b.y*k,b.w*k,b.d*k);
      LD.text(g,`${b.h}m`,ox+(b.x+b.w/2)*k,oy+(b.y+b.d/2)*k+4,{c:LD.INK,a:'center',size:11});
      g.beginPath();g.arc(ox+(b.x+b.w)*k,oy+(b.y+b.d)*k,4.5,0,7);g.fillStyle=LD.BG;g.fill();g.strokeStyle=LD.BLUE;g.lineWidth=2;g.stroke();});
    g.strokeStyle=LD.FAINT;g.lineWidth=1;g.strokeRect(ox,oy,S*k,S*k);
    // 범례
    for(let h=0;h<=6;h++){g.fillStyle=col(h);g.fillRect(ox+h*26,oy+S*k+12,24,8);LD.text(g,h+'h',ox+h*26+12,oy+S*k+32,{a:'center'});}
    LD.text(g,'— 연속 2시간 경계',ox+S*k,oy+S*k+20,{c:LD.RED,a:'right'});
    LD.text(g,'N ↑',ox+S*k-4,oy-4,{c:LD.INK,a:'right'}); LD.text(g,`연속 일조 (09–15시) · ${DAYS[P.day].n}`,12,16,{c:LD.INK,size:11});
  }
  function drawShadow(){
    const [g,W,H]=LD.fit(cS), s=sun(P.t), k=Math.min(W-60,H-50)/S, ox=(W-S*k)/2+10, oy=(H-S*k)/2+6;
    g.fillStyle='#3a3833';g.fillRect(ox,oy,S*k,S*k);
    if(s.alt>0){ const L=1/s.tz; g.fillStyle='rgba(10,10,12,.78)';
      B.forEach(b=>{const sx=-s.dx*b.h*L, sy=-s.dy*b.h*L, c=[[b.x,b.y],[b.x+b.w,b.y],[b.x+b.w,b.y+b.d],[b.x,b.y+b.d]];
        // 상자 그림자 = 바닥 사각형과 옮긴 사각형의 볼록 껍질
        const pts=c.concat(c.map(p=>[p[0]+sx,p[1]+sy])).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
        const cr=(o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]); const lo=[],up=[];
        pts.forEach(p=>{while(lo.length>1&&cr(lo[lo.length-2],lo[lo.length-1],p)<=0)lo.pop();lo.push(p);});
        pts.slice().reverse().forEach(p=>{while(up.length>1&&cr(up[up.length-2],up[up.length-1],p)<=0)up.pop();up.push(p);});
        const hull=lo.slice(0,-1).concat(up.slice(0,-1)); g.save();g.beginPath();g.rect(ox,oy,S*k,S*k);g.clip();LD.path(g,hull.map(p=>[ox+p[0]*k,oy+p[1]*k]));g.fill();g.restore();});
    } else { g.fillStyle='rgba(0,0,0,.6)';g.fillRect(ox,oy,S*k,S*k); }
    B.forEach(b=>{g.fillStyle='#55534c';g.fillRect(ox+b.x*k,oy+b.y*k,b.w*k,b.d*k);g.strokeStyle=LD.INK;g.lineWidth=1;g.strokeRect(ox+b.x*k,oy+b.y*k,b.w*k,b.d*k);});
    g.strokeStyle=LD.FAINT;g.strokeRect(ox,oy,S*k,S*k);
    // 태양 궤적 (작은 원형 차트, 오른쪽 위)
    const R=46, cx=W-R-16, cy=R+28; g.strokeStyle=LD.FAINT;g.lineWidth=.8;g.beginPath();g.arc(cx,cy,R,0,7);g.stroke();g.beginPath();g.arc(cx,cy,R*2/3,0,7);g.arc(cx,cy,R/3,0,7);g.stroke();
    LD.text(g,'S',cx,cy+R+12,{a:'center'});LD.text(g,'N',cx,cy-R-4,{a:'center'});
    const pp=t=>{const q=sun(t),r=R*(1-Math.max(0,q.alt)/(Math.PI/2));return [cx-Math.sin(q.az)*r,cy+Math.cos(q.az)*r,q.alt];};
    g.strokeStyle='#e0a15a';g.lineWidth=1.2;g.beginPath();let st=false;for(let t=4;t<=20;t+=.1){const p=pp(t);if(p[2]<0){st=false;continue;}st?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]);st=true;}g.stroke();
    const p=pp(P.t); if(p[2]>0){g.beginPath();g.arc(p[0],p[1],4,0,7);g.fillStyle=LD.RED;g.fill();}
    const hh=Math.floor(P.t),mm=Math.round((P.t-hh)*60);
    LD.text(g,`${hh}:${String(mm).padStart(2,'0')} · 고도 ${(s.alt*180/Math.PI).toFixed(1)}° · 방위 ${(s.az*180/Math.PI).toFixed(0)}°`,12,16,{c:LD.INK,size:11});
  }
  function stats(){
    const pc=v=>(v/G.open*100).toFixed(0)+'%'; const s=sun(12);
    LD.stats(out,[['날짜 · 위도',DAYS[P.day].n+' · '+P.lat.toFixed(1)+'°'],['남중 고도',(s.alt*180/Math.PI).toFixed(1)+'°'],['빈 땅',G.open+' ㎡'],['건물',B.length+'동'],
      ['연속 2시간 이상',G.ok2+' ㎡ ('+pc(G.ok2)+')'],['총 4시간 이상 (08–16)',G.ok4+' ㎡ ('+pc(G.ok4)+')'],['연속 2시간 미만',(G.open-G.ok2)+' ㎡',G.open-G.ok2>G.open*.5?'ng':''],['선택 건물',B[P.sel]?`${B[P.sel].w}×${B[P.sel].d}m · ${B[P.sel].h}m`:'-']],[4,5],
      '1m 격자마다 해 쪽으로 광선을 쏘아 건물 상자에 막히는지 10분 간격으로 본다. 진태양시 기준이며 지형 · 수목 · 인접 대지 밖 건물은 없다. 공동주택 일조 기준(동지 09~15시 연속 2시간 또는 08~16시 총 4시간)은 창 위치에서 판정하므로 여기 지면 값은 배치 스터디용.');
  }
  function draw(){drawMap();drawShadow();stats();}

  const W2=e=>{const r=cM.getBoundingClientRect();return [(e.clientX-r.left-TM.ox)/TM.k,(e.clientY-r.top-TM.oy)/TM.k];};
  let drag=null;
  cM.addEventListener('pointerdown',e=>{const [x,y]=W2(e);
    let i=B.findIndex(b=>Math.hypot(b.x+b.w-x,b.y+b.d-y)*TM.k<10); if(i>=0){drag={i,mode:'size'};}
    else{i=B.findIndex(b=>x>b.x&&x<b.x+b.w&&y>b.y&&y<b.y+b.d); if(i>=0)drag={i,mode:'move',dx:x-B[i].x,dy:y-B[i].y};}
    if(drag){P.sel=drag.i;refresh();cM.setPointerCapture(e.pointerId);draw();}});
  cM.addEventListener('pointermove',e=>{if(!drag)return;const [x,y]=W2(e),b=B[drag.i];
    if(drag.mode==='move'){b.x=Math.max(0,Math.min(S-b.w,Math.round(x-drag.dx)));b.y=Math.max(0,Math.min(S-b.d,Math.round(y-drag.dy)));}
    else{b.w=Math.max(4,Math.min(S-b.x,Math.round(x-b.x)));b.d=Math.max(4,Math.min(S-b.y,Math.round(y-b.y)));}
    P.step=30;calc();draw();});
  cM.addEventListener('pointerup',()=>{if(drag){drag=null;P.step=10;calc();draw();}});
  cM.addEventListener('dblclick',e=>{const [x,y]=W2(e);if(inB(x,y))return;B.push({x:Math.round(x)-5,y:Math.round(y)-4,w:10,d:8,h:9});P.sel=B.length-1;refresh();calc();draw();});
  LabIO(app,{name:'sun-hours',state:()=>({P,B}),load:o=>{Object.assign(P,o.P||{});if(o.B)B=o.B;refresh();},redraw:()=>{calc();draw();},
    dxf:()=>B.map(b=>({layer:'BUILDING',pts:[[b.x,b.y],[b.x+b.w,b.y],[b.x+b.w,b.y+b.d],[b.x,b.y+b.d]],z:b.h}))});
  addEventListener('resize',draw); calc(); draw();
})();
