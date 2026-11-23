// LAB 02 — 정북 일조사선 매스
// 대지 꼭짓점을 끌면 정북 일조사선(건축법 시행령 제86조, 전용·일반주거지역) · 대지안의 공지 · 건폐율 · 용적률을
// 함께 걸어 층별 바닥판을 다각형으로 계산한다.
//   높이 10m 이하 부분: 정북 경계에서 1.5m 이상 / 10m 초과 부분: 그 높이의 1/2 이상
// 층 f의 허용 영역 = 대지 ∩ (대지를 남쪽으로 r만큼 민 것) ∩ (대지를 공지만큼 안으로 줄인 것)
(function(){
  const root=document.getElementById('lab-northlight'); if(!root) return;
  const P={fh:3.3, maxF:15, bcr:60, far:250, sb:1.0, yaw:-0.62};
  let poly=[[3,8],[31,2],[36,26],[8,31]];
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="top"></canvas><p class="hint">꼭짓점 드래그 · 변 더블클릭 = 점 추가 · 점 더블클릭 = 삭제</p></div>
  <div class="cv sheet"><canvas class="iso"></canvas><p class="hint">드래그 = 회전</p></div></div>
  <div class="nls"></div>`;
  const cT=app.querySelector('.top'), cI=app.querySelector('.iso'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'법규',k:'건폐율 %',min:20,max:80,step:5,get:()=>P.bcr,set:v=>P.bcr=v},
    {g:'법규',k:'용적률 %',min:100,max:500,step:10,get:()=>P.far,set:v=>P.far=v},
    {g:'법규',k:'대지안의 공지 m',min:0,max:3,step:.5,get:()=>P.sb,set:v=>P.sb=v},
    {g:'건물',k:'층고 m',min:2.8,max:4.5,step:.1,get:()=>P.fh,set:v=>P.fh=v},
    {g:'건물',k:'최고 층수',min:3,max:25,step:1,get:()=>P.maxF,set:v=>P.maxF=v},
  ],draw);

  // ---------- 다각형 연산
  const area=p=>p.length<3?0:Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-b[0]*a[1];},0))/2;
  const sgn=p=>p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-b[0]*a[1];},0)>0?1:-1;
  function clipHalf(sub,a,b,off,s){ // 변 a→b의 안쪽 반평면, off만큼 더 안으로
    const dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy);
    const nx=-dy/L*s, ny=dx/L*s;
    const f=p=>(p[0]-a[0])*nx+(p[1]-a[1])*ny-off, out=[];
    for(let i=0;i<sub.length;i++){const P1=sub[i],P2=sub[(i+1)%sub.length],f1=f(P1),f2=f(P2);
      if(f1>=0) out.push(P1); if((f1>=0)!==(f2>=0)){const t=f1/(f1-f2); out.push([P1[0]+t*(P2[0]-P1[0]),P1[1]+t*(P2[1]-P1[1])]);}}
    return out;
  }
  function clipPoly(sub,clip,off){const s=sgn(clip);for(let i=0;i<clip.length&&sub.length;i++) sub=clipHalf(sub,clip[i],clip[(i+1)%clip.length],off,s); return sub;}
  function clipY(sub,yc){const out=[];for(let i=0;i<sub.length;i++){const a=sub[i],b=sub[(i+1)%sub.length],fa=a[1]-yc,fb=b[1]-yc;
    if(fa>=0)out.push(a); if((fa>=0)!==(fb>=0)){const t=fa/(fa-fb);out.push([a[0]+t*(b[0]-a[0]),yc]);}} return out;}
  const req=h=>h<=10?1.5:h/2;
  function plate(f){ // f층 윗면 높이(f*fh)에서의 허용 바닥판
    const r=req(f*P.fh), sh=poly.map(p=>[p[0],p[1]+r]);
    return clipPoly(clipPoly(poly.map(p=>p.slice()),sh,0),poly,P.sb);
  }

  // ---------- 계산
  function compute(){
    const site=area(poly), legalFoot=site*P.bcr/100, legalGFA=site*P.far/100, env=[];
    for(let f=1;f<=P.maxF;f++){const pl=plate(f); if(area(pl)<4) break; env.push(pl);}
    const envGFA=env.reduce((s,p)=>s+area(p),0), topF=env.length;
    // 건폐율: 1층 영역의 북쪽을 잘라 법정 건축면적에 맞춘다 (북쪽이 사선에 가장 불리하므로)
    let foot=env[0]||[], yc=null;
    if(area(foot)>legalFoot){const ys=foot.map(p=>p[1]);let lo=Math.min(...ys),hi=Math.max(...ys);
      for(let i=0;i<40;i++){const m=(lo+hi)/2; if(area(clipY(foot,m))>legalFoot) lo=m; else hi=m;} yc=hi; foot=clipY(foot,yc);}
    // 용적률: 아래층부터 쌓아 법정 연면적을 넘기 직전까지
    const mass=[]; let gfa=0;
    for(const pl of env){const p=yc===null?pl:clipY(pl,yc), a=area(p); if(a<4||gfa+a>legalGFA+0.01) break; mass.push(p); gfa+=a;}
    const lim = mass.length<env.length && envGFA>legalGFA ? (yc!==null?'용적률 + 건폐율':'용적률') : (yc!==null?'건폐율 + 일조사선':'일조사선 · 대지안의 공지');
    return {site,legalFoot,legalGFA,env,envGFA,topF,foot,mass,gfa,lim,F:mass.length};
  }

  // ---------- 그리기 (흰 도면 시트)
  const INK='#e6e3da', RED='#ff6b4a', BLUE='#4da3ff', MONO='"JetBrains Mono",ui-monospace,monospace';
  function fit(cv){const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1;cv.width=r.width*dpr;cv.height=r.height*dpr;const g=cv.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);g.lineJoin='round';return [g,r.width,r.height];}
  const path=(g,pts)=>{g.beginPath();pts.forEach((v,i)=>i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]));g.closePath();};
  let T=null;
  function drawTop(R){
    const [g,W,H]=fit(cT); g.fillStyle='#151513'; g.fillRect(0,0,W,H);
    const xs=poly.map(p=>p[0]), ys=poly.map(p=>p[1]), x0=Math.min(...xs)-5, y0=Math.min(...ys)-6, w=Math.max(...xs)-x0+5, h=Math.max(...ys)-y0+5;
    const k=Math.min(W/w,(H-30)/h); T={k,ox:(W-w*k)/2-x0*k,oy:(H-30-h*k)/2-y0*k};
    const M=p=>[T.ox+p[0]*k,T.oy+p[1]*k];
    if(R.foot.length){path(g,R.foot.map(M));g.fillStyle='rgba(255,107,74,.12)';g.fill();g.strokeStyle=RED;g.lineWidth=1.4;g.stroke();}
    g.lineWidth=.6; R.env.forEach((pl,i)=>{path(g,pl.map(M));g.strokeStyle=i%5===4?'#8a8a80':'#3a3a35';g.stroke();});
    g.font=`10px ${MONO}`;g.fillStyle='#888';g.textAlign='left';
    R.env.forEach((pl,i)=>{if(i%5!==4&&i!==R.env.length-1)return;const top=pl.reduce((a,b)=>b[1]<a[1]?b:a);const q=M(top);g.fillText((i+1)+'F',q[0]+3,q[1]-3);});
    path(g,poly.map(M));g.strokeStyle=INK;g.lineWidth=1.6;g.stroke();
    const inset=clipPoly(poly.map(p=>p.slice()),poly,P.sb); if(P.sb>0&&inset.length){g.setLineDash([4,3]);path(g,inset.map(M));g.strokeStyle='#6a6a63';g.lineWidth=.8;g.stroke();g.setLineDash([]);}
    g.fillStyle=INK;g.textAlign='center';g.font=`11px ${MONO}`;
    const s=sgn(poly);
    poly.forEach((a,i)=>{const b=poly[(i+1)%poly.length],m=M([(a[0]+b[0])/2,(a[1]+b[1])/2]);const dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy);
      const nx=dy/L*s, ny=-dx/L*s; // 바깥 법선
      g.fillText(L.toFixed(1),m[0]+nx*14,m[1]+ny*14+4);});
    poly.forEach(p=>{const q=M(p);g.beginPath();g.arc(q[0],q[1],5,0,7);g.fillStyle='#151513';g.fill();g.strokeStyle=BLUE;g.lineWidth=2;g.stroke();});
    g.strokeStyle=INK;g.lineWidth=1;g.beginPath();g.moveTo(W-26,44);g.lineTo(W-26,16);g.moveTo(W-31,22);g.lineTo(W-26,16);g.lineTo(W-21,22);g.stroke();
    g.fillStyle=INK;g.font=`600 11px ${MONO}`;g.fillText('N',W-26,58);
    g.textAlign='left';g.font=`10px ${MONO}`;g.fillStyle='#8a8a80';
    g.fillText('— 대지  ··· 공지선  — 층별 허용선',12,H-12); g.fillStyle=RED; g.fillText('■ 계획 건축면적',12,H-26);
  }
  function drawIso(R){
    const [g,W,H]=fit(cI); g.fillStyle='#151513'; g.fillRect(0,0,W,H);
    const xs=poly.map(p=>p[0]), ys=poly.map(p=>p[1]), cx=(Math.min(...xs)+Math.max(...xs))/2, cy=(Math.min(...ys)+Math.max(...ys))/2;
    const span=Math.max(Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)), hz=R.topF*P.fh;
    const k=Math.min(W/(span*1.35),(H-40)/(span*.8+hz*.82));
    const co=Math.cos(P.yaw), si=Math.sin(P.yaw);
    const pr=(x,y,z)=>{x-=cx;y-=cy;const xr=x*co-y*si, yr=x*si+y*co;return [W/2+xr*k, H-34-span*.4*k+yr*k*.55-z*k*.82, yr];};
    path(g,poly.map(p=>pr(p[0],p[1],0)));g.fillStyle='#1c1c19';g.fill();g.strokeStyle=INK;g.lineWidth=1.2;g.stroke();
    g.setLineDash([3,3]);g.strokeStyle='rgba(77,163,255,.55)';g.lineWidth=.7;
    R.env.forEach((pl,i)=>{path(g,pl.map(p=>pr(p[0],p[1],(i+1)*P.fh)));g.stroke();}); g.setLineDash([]);
    R.mass.forEach((pl,i)=>{
      const z0=i*P.fh, z1=(i+1)*P.fh, s=sgn(pl), walls=[];
      for(let j=0;j<pl.length;j++){const a=pl[j],b=pl[(j+1)%pl.length],dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy); if(L<1e-6) continue;
        const nx=dy/L*s, ny=-dx/L*s; const facing=nx*si+ny*co; if(facing<=1e-6) continue;
        walls.push({a,b,d:pr((a[0]+b[0])/2,(a[1]+b[1])/2,0)[2],v:Math.round(212+40*Math.abs(nx*co-ny*si))});}
      walls.sort((p,q)=>p.d-q.d).forEach(w=>{path(g,[pr(w.a[0],w.a[1],z0),pr(w.b[0],w.b[1],z0),pr(w.b[0],w.b[1],z1),pr(w.a[0],w.a[1],z1)]);
        g.fillStyle=`rgb(${w.v-195},${w.v-195},${w.v-198})`;g.fill();g.strokeStyle=INK;g.lineWidth=.9;g.stroke();});
      path(g,pl.map(p=>pr(p[0],p[1],z1)));g.fillStyle='#1e1e1b';g.fill();g.strokeStyle=INK;g.lineWidth=1;g.stroke();
    });
    if(R.mass.length){const pl=R.mass[R.mass.length-1],q=pl.reduce((a,b)=>pr(b[0],b[1],0)[0]>pr(a[0],a[1],0)[0]?b:a),t=pr(q[0],q[1],R.F*P.fh);
      const lab=`▼ +${(R.F*P.fh).toFixed(1)}  ${R.F}F`; g.font=`11px ${MONO}`; const tw=g.measureText(lab).width, L=t[0]+40+tw>W-8;
      const x1=L?t[0]-6:t[0]+6, x2=L?t[0]-36:t[0]+36;
      g.strokeStyle=RED;g.lineWidth=.8;g.beginPath();g.moveTo(x1,t[1]);g.lineTo(x2,t[1]);g.stroke();
      g.fillStyle=RED;g.textAlign=L?'right':'left';g.fillText(lab,L?x2-4:x2+4,t[1]+4);}
    g.fillStyle='#8a8a80';g.font=`10px ${MONO}`;g.textAlign='left';g.fillText('--- 사선 허용 볼륨   □ 계획 매스',12,H-12);
  }
  function stats(R){
    const f=v=>v.toLocaleString('ko-KR',{maximumFractionDigits:0});
    const rows=[['대지면적',f(R.site)+' ㎡'],['법정 최대 건축면적',f(R.legalFoot)+' ㎡ ('+P.bcr+'%)'],['법정 최대 연면적',f(R.legalGFA)+' ㎡ ('+P.far+'%)'],
      ['사선 허용 볼륨',f(R.envGFA)+' ㎡ · '+R.topF+'층'],['계획 건축면적',f(area(R.foot))+' ㎡'],['계획 매스',R.F+'층 · '+(R.F*P.fh).toFixed(1)+' m'],
      ['실제 가능한 연면적',f(R.gfa)+' ㎡ ('+(R.gfa/R.site*100).toFixed(0)+'%)'],['결정 요인',R.lim]];
    out.innerHTML=rows.map(([a,b],i)=>`<div class="${i>=6?'hi':''}"><span>${a}</span><b>${b}</b></div>`).join('')+
      `<p class="note">정북 경계에서 높이 10m까지는 1.5m, 그 위는 높이의 절반만큼 떨어져야 한다. 회색 선이 층별 허용선(사선), 붉은 면은 건폐율 안에서 쓰는 바닥, 매스는 용적률을 넘기 직전 층까지 쌓은 것. 볼록한 대지 기준이며 도로사선 · 완화 규정은 넣지 않았다.</p>`;
  }
  function draw(){const R=compute();drawTop(R);drawIso(R);stats(R);}

  // ---------- 조작
  const W2=e=>{const r=cT.getBoundingClientRect();return [(e.clientX-r.left-T.ox)/T.k,(e.clientY-r.top-T.oy)/T.k];};
  const segD=(x,y,a,b)=>{const dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));return Math.hypot(x-a[0]-t*dx,y-a[1]-t*dy);};
  let drag=-1;
  cT.addEventListener('pointerdown',e=>{const [x,y]=W2(e);drag=poly.findIndex(p=>Math.hypot(p[0]-x,p[1]-y)*T.k<12);if(drag>=0)cT.setPointerCapture(e.pointerId);});
  cT.addEventListener('pointermove',e=>{if(drag<0)return;const [x,y]=W2(e);poly[drag]=[Math.round(x*2)/2,Math.round(y*2)/2];draw();});
  cT.addEventListener('pointerup',()=>drag=-1);
  cT.addEventListener('dblclick',e=>{const [x,y]=W2(e);const vi=poly.findIndex(p=>Math.hypot(p[0]-x,p[1]-y)*T.k<12);
    if(vi>=0){if(poly.length>3)poly.splice(vi,1);} else {let bi=-1,bd=1e9;poly.forEach((a,i)=>{const d=segD(x,y,a,poly[(i+1)%poly.length]);if(d<bd){bd=d;bi=i;}}); if(bd*T.k<14) poly.splice(bi+1,0,[Math.round(x*2)/2,Math.round(y*2)/2]);} draw();});
  let rx=null; cI.addEventListener('pointerdown',e=>{rx=e.clientX;cI.setPointerCapture(e.pointerId);});
  cI.addEventListener('pointermove',e=>{if(rx===null)return;P.yaw+=(e.clientX-rx)*.01;rx=e.clientX;drawIso(compute());});
  cI.addEventListener('pointerup',()=>rx=null);
  LabIO(app,{name:'northlight-envelope',poly:{get:()=>poly,set:v=>poly=v},state:()=>({P,poly}),load:o=>{Object.assign(P,o.P||{});if(o.poly)poly=o.poly;refresh();},redraw:draw,
    dxf:()=>{const R=compute(),E=[{layer:'SITE',pts:poly},{layer:'FOOTPRINT',pts:R.foot}];
      R.env.forEach((pl,i)=>E.push({layer:'ENVELOPE',pts:pl,z:(i+1)*P.fh}));
      R.mass.forEach((pl,i)=>{E.push({layer:'MASS',pts:pl,z:i*P.fh},{layer:'MASS',pts:pl,z:(i+1)*P.fh});pl.forEach(p=>E.push({layer:'MASS',closed:false,pts:[[p[0],p[1],i*P.fh],[p[0],p[1],(i+1)*P.fh]]}));});return E;}});
  addEventListener('resize',draw); draw();
})();
