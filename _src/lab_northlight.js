// LAB 02 — 정북 일조사선 매스
// 대지 꼭짓점을 끌면, 정북 방향 일조 사선(건축법 시행령 제86조, 전용·일반주거지역)과
// 대지안의 공지 · 건폐율 · 용적률을 함께 걸어 허용 볼륨과 실제 가능한 연면적을 계산한다.
//   높이 10m 이하 부분: 정북 경계에서 1.5m 이상
//   높이 10m 초과 부분: 그 부분 높이의 1/2 이상
(function(){
  const root=document.getElementById('lab-northlight'); if(!root) return;
  const P={fh:3.3, maxF:15, bcr:60, far:250, sb:1.0, yaw:-0.78};
  let poly=[[3,8],[31,2],[36,26],[8,31]];
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv"><canvas class="top"></canvas><p class="hint">꼭짓점 드래그 · 변 더블클릭 = 점 추가 · 점 더블클릭 = 삭제</p></div>
  <div class="cv"><canvas class="iso"></canvas><p class="hint">드래그 = 회전</p></div></div>
  <div class="nls"></div>`;
  const cT=app.querySelector('.top'), cI=app.querySelector('.iso'), out=app.querySelector('.nls');
  LabUI(app.querySelector('.lctl'),[
    {g:'법규',k:'건폐율 %',min:20,max:80,step:5,get:()=>P.bcr,set:v=>P.bcr=v},
    {g:'법규',k:'용적률 %',min:100,max:500,step:10,get:()=>P.far,set:v=>P.far=v},
    {g:'법규',k:'대지안의 공지 m',min:0,max:3,step:.5,get:()=>P.sb,set:v=>P.sb=v},
    {g:'건물',k:'층고 m',min:2.8,max:4.5,step:.1,get:()=>P.fh,set:v=>P.fh=v},
    {g:'건물',k:'최고 층수',min:3,max:25,step:1,get:()=>P.maxF,set:v=>P.maxF=v},
  ],draw);

  // ---------- 기하
  const area=p=>Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-b[0]*a[1];},0))/2;
  function inside(x,y){let c=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const[a,b]=poly[i],[d,e]=poly[j];if((b>y)!==(e>y)&&x<(d-a)*(y-b)/(e-b)+a)c=!c;}return c;}
  function segD(x,y,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));return Math.hypot(x-a[0]-t*dx,y-a[1]-t*dy);}
  function edgeD(x,y){let m=1e9;for(let i=0;i<poly.length;i++)m=Math.min(m,segD(x,y,poly[i],poly[(i+1)%poly.length]));return m;}
  function northD(x,y){ // 정북(화면 위쪽) 방향으로 경계선까지 거리
    let best=1e9; for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];
      if((a[0]-x)*(b[0]-x)>0||a[0]===b[0]) continue; const t=(x-a[0])/(b[0]-a[0]), yi=a[1]+t*(b[1]-a[1]); if(yi<=y) best=Math.min(best,y-yi);} return best;}
  const hmax=d=>d<1.5?0:d<5?10:2*d;

  // ---------- 계산 (0.5m 격자)
  const C=0.5;
  function compute(){
    const xs=poly.map(p=>p[0]), ys=poly.map(p=>p[1]), cells=[];
    for(let x=Math.floor(Math.min(...xs));x<Math.max(...xs);x+=C) for(let y=Math.floor(Math.min(...ys));y<Math.max(...ys);y+=C){
      const cx=x+C/2, cy=y+C/2; if(!inside(cx,cy)||edgeD(cx,cy)<P.sb) continue;
      const d=northD(cx,cy), H=hmax(d), f=Math.min(P.maxF,Math.floor(H/P.fh));
      cells.push({x,y,d,f});
    }
    const site=area(poly), ca=C*C, foot=cells.filter(c=>c.f>0);
    const envGFA=foot.reduce((s,c)=>s+c.f*ca,0), legalFoot=site*P.bcr/100, legalGFA=site*P.far/100;
    // 건폐율 안에서: 높이 올릴 수 있는 칸부터 채운다
    const sorted=[...foot].sort((a,b)=>b.f-a.f); let fa=0, g=0; const used=new Set();
    for(const c of sorted){ if(fa+ca>legalFoot) break; fa+=ca; g+=c.f*ca; used.add(c); }
    // 용적률에 맞춰 층수를 깎는다: 사용 칸의 높이를 F층으로 자르고, 연면적이 법정 한도 안에 드는 가장 큰 F
    const U=[...used]; let F=Math.max(0,...U.map(c=>c.f));
    const gAt=F=>U.reduce((s,c)=>s+Math.min(c.f,F)*ca,0);
    while(F>0&&gAt(F)>legalGFA+0.01) F--;
    U.forEach(c=>c.m=Math.min(c.f,F)); cells.forEach(c=>{if(!used.has(c))c.m=0;});
    const gfa=gAt(F);
    const lim = g>=legalGFA-0.01 ? '용적률' : (fa>=legalFoot-ca ? '건폐율 + 일조사선' : '일조사선 · 대지안의 공지');
    const topF=Math.max(0,...foot.map(c=>c.f));
    return {cells,used,site,envGFA,legalFoot,legalGFA,fa,gfa,lim,topF,F};
  }

  // ---------- 그리기
  const ramp=f=>{if(f<=0)return '#2a2d27';const t=Math.min(1,f/Math.max(1,P.maxF));return `hsl(${88-t*40},${45+t*20}%,${28+t*38}%)`;};
  function fit(cv){const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1;cv.width=r.width*dpr;cv.height=r.height*dpr;const g=cv.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);return [g,r.width,r.height];}
  let T=null; // top view transform
  function drawTop(R){
    const [g,W,H]=fit(cT); g.clearRect(0,0,W,H);
    const xs=poly.map(p=>p[0]), ys=poly.map(p=>p[1]), x0=Math.min(...xs)-4, y0=Math.min(...ys)-4, w=Math.max(...xs)-x0+4, h=Math.max(...ys)-y0+4;
    const k=Math.min(W/w,H/h); T={k,ox:(W-w*k)/2-x0*k,oy:(H-h*k)/2-y0*k};
    const X=x=>T.ox+x*k, Y=y=>T.oy+y*k;
    R.cells.forEach(c=>{g.fillStyle=ramp(c.f);g.globalAlpha=R.used.has(c)?1:.45;g.fillRect(X(c.x),Y(c.y),C*k+.5,C*k+.5);}); g.globalAlpha=1;
    g.beginPath();poly.forEach((p,i)=>i?g.lineTo(X(p[0]),Y(p[1])):g.moveTo(X(p[0]),Y(p[1])));g.closePath();g.strokeStyle='#e6e4dc';g.lineWidth=1.5;g.stroke();
    g.font='11px "JetBrains Mono",monospace';g.fillStyle='#8a8a80';g.textAlign='center';
    poly.forEach((a,i)=>{const b=poly[(i+1)%poly.length];g.fillText(Math.hypot(b[0]-a[0],b[1]-a[1]).toFixed(1)+'m',X((a[0]+b[0])/2),Y((a[1]+b[1])/2)-6);});
    poly.forEach(p=>{g.beginPath();g.arc(X(p[0]),Y(p[1]),5,0,7);g.fillStyle='#b6d36b';g.fill();});
    g.fillStyle='#b6d36b';g.font='600 12px "JetBrains Mono",monospace';g.fillText('N ↑',W-24,18);
    g.textAlign='left';g.font='10px "JetBrains Mono",monospace';const L=[1,Math.ceil(P.maxF/3),Math.ceil(P.maxF*2/3),P.maxF];L.forEach((f,i)=>{g.fillStyle=ramp(f);g.fillRect(10+i*46,H-20,12,10);g.fillStyle='#8a8a80';g.fillText(f+'F',26+i*46,H-11);});
  }
  function drawIso(R){
    const [g,W,H]=fit(cI); g.clearRect(0,0,W,H);
    const xs=poly.map(p=>p[0]), ys=poly.map(p=>p[1]), cx=(Math.min(...xs)+Math.max(...xs))/2, cy=(Math.min(...ys)+Math.max(...ys))/2;
    const span=Math.max(Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys),R.topF*P.fh*1.2), k=Math.min(W,H)/span*.7;
    const co=Math.cos(P.yaw), si=Math.sin(P.yaw);
    const pr=(x,y,z)=>{x-=cx;y-=cy;const xr=x*co-y*si, yr=x*si+y*co;return [W/2+xr*k, H*.66+yr*k*.58-z*k*.8, yr];};
    // 대지
    g.beginPath();poly.forEach((p,i)=>{const q=pr(p[0],p[1],0);i?g.lineTo(q[0],q[1]):g.moveTo(q[0],q[1]);});g.closePath();g.fillStyle='#1c2117';g.fill();g.strokeStyle='#5d6b44';g.stroke();
    // 일조사선 볼륨 (건폐율 안 칸만 진하게)
    const hm=new Map(); R.cells.forEach(c=>{if(c.m>0)hm.set(c.x+','+c.y,c.m);});
    // 건폐율 밖 사선 볼륨은 윗면만 흐리게
    R.cells.filter(c=>c.f>c.m).forEach(c=>{const z=c.f*P.fh,t=[pr(c.x,c.y,z),pr(c.x+C,c.y,z),pr(c.x+C,c.y+C,z),pr(c.x,c.y+C,z)];g.beginPath();t.forEach((v,i)=>i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]));g.closePath();g.fillStyle='rgba(182,211,107,.10)';g.fill();});
    const list=R.cells.filter(c=>c.m>0).map(c=>({c,dep:pr(c.x+C/2,c.y+C/2,0)[2]})).sort((a,b)=>a.dep-b.dep);
    const faces=[[0,-1,'n'],[0,1,'s'],[1,0,'e'],[-1,0,'w']];
    for(const {c} of list){
      const z=c.m*P.fh, a=1;
      for(const [nx,ny] of faces){
        if(nx*si+ny*co<=0) continue; // 뒤쪽 면
        const nf=hm.get((c.x+nx*C)+','+(c.y+ny*C))||0; if(nf>=c.m) continue;
        const z0=nf*P.fh; let p1,p2;
        if(ny===-1){p1=[c.x,c.y];p2=[c.x+C,c.y];} else if(ny===1){p1=[c.x,c.y+C];p2=[c.x+C,c.y+C];} else if(nx===1){p1=[c.x+C,c.y];p2=[c.x+C,c.y+C];} else {p1=[c.x,c.y];p2=[c.x,c.y+C];}
        const q=[pr(p1[0],p1[1],z0),pr(p2[0],p2[1],z0),pr(p2[0],p2[1],z),pr(p1[0],p1[1],z)];
        g.beginPath();q.forEach((v,i)=>i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]));g.closePath();
        g.globalAlpha=a; g.fillStyle=g.strokeStyle=ny===1?'#8fa65a':nx!==0?'#6f8247':'#55633a'; g.lineWidth=.8; g.fill(); g.stroke();
        // 층 선
        g.strokeStyle='rgba(18,19,17,.35)';g.lineWidth=.6;g.beginPath();
        for(let f=nf+1;f<c.m;f++){const s=pr(p1[0],p1[1],f*P.fh),e=pr(p2[0],p2[1],f*P.fh);g.moveTo(s[0],s[1]);g.lineTo(e[0],e[1]);} g.stroke();
      }
      const t=[pr(c.x,c.y,z),pr(c.x+C,c.y,z),pr(c.x+C,c.y+C,z),pr(c.x,c.y+C,z)];
      g.beginPath();t.forEach((v,i)=>i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]));g.closePath();g.fillStyle=g.strokeStyle=ramp(c.m);g.lineWidth=.8;g.fill();g.stroke();
      g.globalAlpha=1;
    }
    const n=pr(cx,Math.min(...ys)-4,0), s=pr(cx,Math.min(...ys)-9,0);
    g.strokeStyle='#b6d36b';g.lineWidth=1.5;g.beginPath();g.moveTo(n[0],n[1]);g.lineTo(s[0],s[1]);g.stroke();g.fillStyle='#b6d36b';g.font='600 12px "JetBrains Mono",monospace';g.fillText('N',s[0]+4,s[1]);
  }
  function stats(R){
    const f=v=>v.toLocaleString('ko-KR',{maximumFractionDigits:0});
    const rows=[['대지면적',f(R.site)+' ㎡'],['법정 최대 건축면적',f(R.legalFoot)+' ㎡ ('+P.bcr+'%)'],['법정 최대 연면적',f(R.legalGFA)+' ㎡ ('+P.far+'%)'],
      ['사선 허용 볼륨',f(R.envGFA)+' ㎡ · 최고 '+R.topF+'층'],['계획 건축면적',f(R.fa)+' ㎡'],['계획 매스 최고 층수',R.F+'층 · '+(R.F*P.fh).toFixed(1)+' m'],
      ['실제 가능한 연면적',f(R.gfa)+' ㎡ ('+(R.gfa/R.site*100).toFixed(0)+'%)'],['결정 요인',R.lim]];
    out.innerHTML=rows.map(([a,b],i)=>`<div class="${i>=6?'hi':''}"><span>${a}</span><b>${b}</b></div>`).join('')+
      `<p class="note">정북 경계에서 1.5m 이상 떨어지면 10m까지, 그 위로는 높이의 절반만큼 떨어져야 한다. 왼쪽 흐린 칸은 건폐율 때문에 쓰지 못하는 부분, 오른쪽 옅은 면은 사선이 허용하는 최대 볼륨이고 진한 덩어리는 용적률까지 채운 계획 매스.</p>`;
  }
  function draw(){const R=compute();drawTop(R);drawIso(R);stats(R);}

  // ---------- 조작
  const W2=(e)=>{const r=cT.getBoundingClientRect();return [(e.clientX-r.left-T.ox)/T.k,(e.clientY-r.top-T.oy)/T.k];};
  let drag=-1;
  cT.addEventListener('pointerdown',e=>{const [x,y]=W2(e);drag=poly.findIndex(p=>Math.hypot(p[0]-x,p[1]-y)*T.k<12);if(drag>=0)cT.setPointerCapture(e.pointerId);});
  cT.addEventListener('pointermove',e=>{if(drag<0)return;const [x,y]=W2(e);poly[drag]=[Math.round(x*2)/2,Math.round(y*2)/2];draw();});
  cT.addEventListener('pointerup',()=>drag=-1);
  cT.addEventListener('dblclick',e=>{const [x,y]=W2(e);const vi=poly.findIndex(p=>Math.hypot(p[0]-x,p[1]-y)*T.k<12);
    if(vi>=0){if(poly.length>3)poly.splice(vi,1);} else {let bi=-1,bd=1e9;poly.forEach((a,i)=>{const d=segD(x,y,a,poly[(i+1)%poly.length]);if(d<bd){bd=d;bi=i;}}); if(bd*T.k<14) poly.splice(bi+1,0,[Math.round(x*2)/2,Math.round(y*2)/2]);} draw();});
  let rx=null; cI.addEventListener('pointerdown',e=>{rx=e.clientX;cI.setPointerCapture(e.pointerId);});
  cI.addEventListener('pointermove',e=>{if(rx===null)return;P.yaw+=(e.clientX-rx)*.01;rx=e.clientX;drawIso(compute());});
  cI.addEventListener('pointerup',()=>rx=null);
  addEventListener('resize',draw); draw();
})();
