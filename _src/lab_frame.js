// LAB 03 — 구조 그리드 → 골조
// 평면에서 그리드 축을 끌어 스팬을 바꾸면 기둥 · 보 · 슬래브가 생기고, 개략 부재 크기와 물량이 나온다.
// 부재 크기는 계획 단계의 경험식(스팬비)이다. 실제 설계는 구조 계산으로 정한다.
(function(){
  const root=document.getElementById('lab-frame'); if(!root) return;
  const SYS=[
    {n:'철근콘크리트 라멘',beam:12,bw:.5,slab:'t=max(150, L/28)',col:N=>Math.max(400,Math.ceil(Math.sqrt(N*1000/(0.3*24))/50)*50),sl:L=>Math.max(150,Math.ceil(L*1000/28/10)*10),dens:'RC'},
    {n:'철골 (H형강)',beam:20,bw:.4,slab:'데크 t=150',col:N=>Math.max(300,Math.ceil(Math.sqrt(N*1000/(0.6*235))*1.6/50)*50),sl:()=>150,dens:'S'},
    {n:'목구조 (집성재)',beam:15,bw:.45,slab:'CLT t=150~210',col:N=>Math.max(240,Math.ceil(Math.sqrt(N*1000/(0.5*20))/30)*30),sl:L=>L>5?210:150,dens:'W'},
  ];
  const P={sys:0, nf:3, fh:3.6, ex:2.2, load:12, yaw:-0.7};
  let sx=[7.2,7.2,7.2], sy=[6,6];
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="top"></canvas><p class="hint">축선 드래그 = 스팬 변경 · 칸 안 더블클릭 = 축 추가 · 축 더블클릭 = 삭제</p></div>
  <div class="cv sheet"><canvas class="iso"></canvas><p class="hint">드래그 = 회전</p></div></div>
  <div class="nls"></div>`;
  const cT=app.querySelector('.top'), cI=app.querySelector('.iso'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'구조',k:'구조 방식',opts:SYS.map(s=>s.n),get:()=>P.sys,set:v=>P.sys=v},
    {g:'구조',k:'층 하중 kN/㎡',min:6,max:20,step:1,get:()=>P.load,set:v=>P.load=v},
    {g:'건물',k:'층수',min:1,max:8,step:1,get:()=>P.nf,set:v=>P.nf=v},
    {g:'건물',k:'층고 m',min:3,max:5,step:.1,get:()=>P.fh,set:v=>P.fh=v},
    {g:'보기',k:'분해 간격 m',min:0,max:6,step:.2,get:()=>P.ex,set:v=>P.ex=v},
  ],draw);

  const cum=a=>a.reduce((r,v)=>(r.push(r[r.length-1]+v),r),[0]);
  function compute(){
    const S=SYS[P.sys], X=cum(sx), Y=cum(sy), Lx=X[X.length-1], Ly=Y[Y.length-1];
    const Lmax=Math.max(...sx,...sy), d=Math.ceil(Lmax*1000/S.beam/50)*50, b=Math.max(S.dens==='W'?150:200,Math.ceil(d*S.bw/50)*50);
    // 가장 불리한 내부 기둥: 부담 면적 × 하중 × 층수
    let trib=0; for(let i=0;i<X.length;i++)for(let j=0;j<Y.length;j++){const ax=((sx[i-1]||0)+(sx[i]||0))/2, ay=((sy[j-1]||0)+(sy[j]||0))/2; trib=Math.max(trib,ax*ay);}
    const N=trib*P.load*P.nf, c=S.col(N), t=S.sl(Math.min(Math.max(...sx),Math.max(...sy)));
    const nc=X.length*Y.length*P.nf, nb=((X.length)*(Y.length-1)+(Y.length)*(X.length-1))*P.nf;
    const bl=(Lx*Y.length+Ly*X.length)*P.nf, A=Lx*Ly*P.nf;
    const vol=nc*(c/1000)**2*P.fh + bl*(b/1000)*(d/1000) + A*t/1000;
    const q = S.dens==='RC' ? `콘크리트 ${vol.toFixed(0)} ㎥` : S.dens==='S' ? `강재 약 ${((nc*P.fh*(c*1.2/1000*60)+bl*(d/1000*120))/1000).toFixed(0)} t` : `목재 ${(nc*(c/1000)**2*P.fh+bl*(b/1000)*(d/1000)+A*t/1000).toFixed(0)} ㎥`;
    return {S,X,Y,Lx,Ly,d,b,c,t,N,trib,nc,nb,bl,A,q};
  }

  const INK='#e6e3da', RED='#ff6b4a', BLUE='#4da3ff', MONO='"JetBrains Mono",ui-monospace,monospace';
  function fit(cv){const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1;cv.width=r.width*dpr;cv.height=r.height*dpr;const g=cv.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);g.lineJoin='round';return [g,r.width,r.height];}
  const path=(g,pts)=>{g.beginPath();pts.forEach((v,i)=>i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]));g.closePath();};
  let T=null;
  function drawTop(R){
    const [g,W,H]=fit(cT); g.fillStyle='#151513'; g.fillRect(0,0,W,H);
    const pad=46, k=Math.min((W-pad*2)/R.Lx,(H-pad*2-14)/R.Ly); T={k,ox:(W-R.Lx*k)/2,oy:(H-14-R.Ly*k)/2};
    const X=x=>T.ox+x*k, Y=y=>T.oy+y*k;
    g.fillStyle='rgba(255,255,255,.03)';g.fillRect(X(0),Y(0),R.Lx*k,R.Ly*k);
    // 보
    const bw=Math.max(2,R.b/1000*k);
    g.fillStyle='#3a3a35';R.X.forEach(x=>g.fillRect(X(x)-bw/2,Y(0),bw,R.Ly*k));R.Y.forEach(y=>g.fillRect(X(0),Y(y)-bw/2,R.Lx*k,bw));
    // 축선 (일점쇄선)
    g.setLineDash([10,3,2,3]);g.strokeStyle='#5a5a54';g.lineWidth=.7;
    R.X.forEach(x=>{g.beginPath();g.moveTo(X(x),Y(0)-26);g.lineTo(X(x),Y(R.Ly)+8);g.stroke();});
    R.Y.forEach(y=>{g.beginPath();g.moveTo(X(0)-26,Y(y));g.lineTo(X(R.Lx)+8,Y(y));g.stroke();}); g.setLineDash([]);
    // 기둥
    const cw=Math.max(4,R.c/1000*k);
    R.X.forEach(x=>R.Y.forEach(y=>{g.fillStyle=INK;g.fillRect(X(x)-cw/2,Y(y)-cw/2,cw,cw);}));
    // 축 기호 + 치수
    g.font=`11px ${MONO}`;g.textAlign='center';
    R.X.forEach((x,i)=>{g.beginPath();g.arc(X(x),Y(0)-34,9,0,7);g.fillStyle='#151513';g.fill();g.strokeStyle=INK;g.lineWidth=1;g.stroke();g.fillStyle=INK;g.fillText('X'+(i+1),X(x),Y(0)-30);});
    R.Y.forEach((y,i)=>{g.beginPath();g.arc(X(0)-34,Y(y),9,0,7);g.fillStyle='#151513';g.fill();g.strokeStyle=INK;g.stroke();g.fillStyle=INK;g.fillText(String.fromCharCode(65+i),X(0)-34,Y(y)+4);});
    g.fillStyle=BLUE;
    sx.forEach((v,i)=>g.fillText(v.toFixed(1),X((R.X[i]+R.X[i+1])/2),Y(R.Ly)+22));
    sy.forEach((v,i)=>{g.save();g.translate(X(R.Lx)+22,Y((R.Y[i]+R.Y[i+1])/2));g.rotate(-Math.PI/2);g.fillText(v.toFixed(1),0,4);g.restore();});
    g.fillStyle=INK;g.fillText(`${R.Lx.toFixed(1)} × ${R.Ly.toFixed(1)} m`,W/2,H-10);
    // 대표 부재 태그
    if(R.X.length>1&&R.Y.length>1){const bx=X((R.X[0]+R.X[1])/2), by=Y(R.Y[0]);g.strokeStyle=RED;g.lineWidth=2;g.beginPath();g.moveTo(X(R.X[0]),by);g.lineTo(X(R.X[1]),by);g.stroke();
      g.fillStyle=RED;g.textAlign='left';g.fillText(`B1 ${R.b}×${R.d}`,bx+6,by-8);
      const cx=X(R.X[1]),cy=Y(R.Y[1]);g.strokeRect(cx-cw/2-3,cy-cw/2-3,cw+6,cw+6);g.fillText(`C1 ${R.c}×${R.c}`,cx+cw/2+6,cy+cw/2+12);}
  }
  function drawIso(R){
    const [g,W,H]=fit(cI); g.fillStyle='#151513'; g.fillRect(0,0,W,H);
    const span=Math.max(R.Lx,R.Ly), Ht=P.nf*(P.fh+P.ex);
    const k=Math.min(W/(span*1.5),(H-50)/(span*.75+Ht*.85));
    const co=Math.cos(P.yaw), si=Math.sin(P.yaw);
    const pr=(x,y,z)=>{x-=R.Lx/2;y-=R.Ly/2;const xr=x*co-y*si, yr=x*si+y*co;return [W/2+xr*k, H-30-span*.38*k+yr*k*.55-z*k*.85, yr];};
    function box(x0,y0,z0,x1,y1,z1,top,side,stroke){
      const F=[[[x0,y0],[x1,y0],0,-1],[[x1,y1],[x0,y1],0,1],[[x1,y0],[x1,y1],1,0],[[x0,y1],[x0,y0],-1,0]];
      for(const [a,b,nx,ny] of F){const f=nx*si+ny*co; if(f<=0) continue; path(g,[pr(a[0],a[1],z0),pr(b[0],b[1],z0),pr(b[0],b[1],z1),pr(a[0],a[1],z1)]);
        const v=Math.round(side-28*Math.abs(nx*co-ny*si));g.fillStyle=`rgb(${v-200},${v-200},${v-203})`;g.fill();g.strokeStyle=stroke||INK;g.lineWidth=.7;g.stroke();}
      path(g,[pr(x0,y0,z1),pr(x1,y0,z1),pr(x1,y1,z1),pr(x0,y1,z1)]);g.fillStyle=top;g.fill();g.strokeStyle=stroke||INK;g.lineWidth=.7;g.stroke();
    }
    const dep=(x,y)=>x*si+y*co;
    const c=R.c/1000, b=R.b/1000, d=R.d/1000, t=R.t/1000;
    for(let f=0;f<P.nf;f++){
      const z0=f*(P.fh+P.ex), zt=z0+P.fh; // 층 바닥 ~ 슬래브 윗면
      const cols=[];R.X.forEach(x=>R.Y.forEach(y=>cols.push([x,y])));
      cols.sort((p,q)=>dep(p[0],p[1])-dep(q[0],q[1])).forEach(([x,y],i)=>{const hl=f===0&&x===R.X[1]&&y===R.Y[1];box(x-c/2,y-c/2,z0,x+c/2,y+c/2,zt-t-d,hl?'#4a2620':'#151513',hl?240:250,hl?RED:INK);});
      const beams=[];
      R.Y.forEach(y=>{for(let i=0;i<R.X.length-1;i++)beams.push([R.X[i],y-b/2,R.X[i+1],y+b/2,i===0&&y===R.Y[0]]);});
      R.X.forEach(x=>{for(let j=0;j<R.Y.length-1;j++)beams.push([x-b/2,R.Y[j],x+b/2,R.Y[j+1],false]);});
      beams.sort((p,q)=>dep((p[0]+p[2])/2,(p[1]+p[3])/2)-dep((q[0]+q[2])/2,(q[1]+q[3])/2)).forEach(([a,bb,cc,dd,hl])=>box(a,bb,zt-t-d,cc,dd,zt-t,hl&&f===P.nf-1?'#4a2620':'#262622',hl&&f===P.nf-1?240:246,hl&&f===P.nf-1?RED:INK));
      const lift=Math.min(P.ex*.45,1.4); box(-c/2-.15,-c/2-.15,zt-t+lift,R.Lx+c/2+.15,R.Ly+c/2+.15,zt+lift,'#1e1e1b',250);
      // 층 표기
      const q=pr(R.Lx+c/2+.15,-c/2-.15,zt+lift); g.fillStyle='#8a8a80';g.font=`10px ${MONO}`;g.textAlign='left';g.fillText(`${f+1}F  +${((f+1)*P.fh).toFixed(1)}`,q[0]+8,q[1]+3);
    }
    g.fillStyle=RED;g.font=`10px ${MONO}`;g.textAlign='left';g.fillText(`■ C1 ${R.c}×${R.c}   ■ B1 ${R.b}×${R.d}   t=${R.t}`,12,H-12);
  }
  function stats(R){
    const f=v=>v.toLocaleString('ko-KR',{maximumFractionDigits:0});
    const rows=[['구조 방식',R.S.n],['최대 스팬',Math.max(...sx,...sy).toFixed(1)+' m'],['보 춤 (L/'+R.S.beam+')',R.b+' × '+R.d+' mm'],['슬래브',R.t+' mm'],
      ['최대 부담 면적',R.trib.toFixed(1)+' ㎡'],['기둥 축력 (개략)',f(R.N)+' kN → '+R.c+'□'],['부재 수',`기둥 ${R.nc} · 보 ${R.nb}`],['연면적 · 물량',f(R.A)+' ㎡ · '+R.q]];
    out.innerHTML=rows.map(([a,b],i)=>`<div class="${i>=5?'hi':''}"><span>${a}</span><b>${b}</b></div>`).join('')+
      `<p class="note">보 춤은 스팬비(RC L/12, 철골 L/20, 집성재 L/15), 기둥은 가장 큰 부담 면적 × 층 하중 × 층수로 잡은 계획용 개략치. 스팬을 늘리면 기둥 수는 줄지만 보 춤과 층고 손실이 커지는 걸 확인하는 용도.</p>`;
  }
  function draw(){const R=compute();drawTop(R);drawIso(R);stats(R);}

  // ---------- 조작: 축선 드래그
  const W2=e=>{const r=cT.getBoundingClientRect();return [(e.clientX-r.left-T.ox)/T.k,(e.clientY-r.top-T.oy)/T.k];};
  function hit(x,y){const X=cum(sx),Y=cum(sy);let best=null,bd=10/T.k;
    X.forEach((v,i)=>{const d=Math.abs(x-v);if(d<bd&&i>0){bd=d;best=['x',i];}});Y.forEach((v,i)=>{const d=Math.abs(y-v);if(d<bd&&i>0){bd=d;best=['y',i];}});return best;}
  let drag=null;
  cT.addEventListener('pointerdown',e=>{const [x,y]=W2(e);drag=hit(x,y);if(drag)cT.setPointerCapture(e.pointerId);});
  cT.addEventListener('pointermove',e=>{const [x,y]=W2(e);
    if(!drag){const h=hit(x,y);cT.style.cursor=h?(h[0]==='x'?'ew-resize':'ns-resize'):'crosshair';return;}
    const [ax,i]=drag, A=ax==='x'?sx:sy, C=cum(A), v=ax==='x'?x:y;
    const nv=Math.round((v-C[i-1])*10)/10; if(nv<2.4||nv>15) return;
    if(i<A.length){const tot=A[i-1]+A[i]; if(tot-nv<2.4) return; A[i]=Math.round((tot-nv)*10)/10;} A[i-1]=nv; draw();});
  cT.addEventListener('pointerup',()=>drag=null);
  cT.addEventListener('dblclick',e=>{const [x,y]=W2(e);const h=hit(x,y);
    if(h){const [ax,i]=h,A=ax==='x'?sx:sy; if(A.length>1){ if(i<A.length){A[i-1]+=A[i];A.splice(i,1);} else A.pop(); }}
    else{const X=cum(sx),Y=cum(sy);const i=X.findIndex(v=>v>x),j=Y.findIndex(v=>v>y);
      if(i>0&&j>0){const dx=Math.min(x-X[i-1],X[i]-x)/sx[i-1], dy=Math.min(y-Y[j-1],Y[j]-y)/sy[j-1];
        if(dx>=dy&&sx[i-1]>=4.8){const a=Math.round((x-X[i-1])*10)/10;sx.splice(i-1,1,a,Math.round((sx[i-1]-a)*10)/10);}
        else if(sy[j-1]>=4.8){const a=Math.round((y-Y[j-1])*10)/10;sy.splice(j-1,1,a,Math.round((sy[j-1]-a)*10)/10);}}}
    draw();});
  let rx=null; cI.addEventListener('pointerdown',e=>{rx=e.clientX;cI.setPointerCapture(e.pointerId);});
  cI.addEventListener('pointermove',e=>{if(rx===null)return;P.yaw+=(e.clientX-rx)*.01;rx=e.clientX;drawIso(compute());});
  cI.addEventListener('pointerup',()=>rx=null);
  // 자동 시연
  const wave=(t,a,b,sp,ph)=>a+(b-a)*(1-Math.cos(t*sp+(ph||0)))/2, q=(v,st)=>Math.round(v/st)*st;
  app.demo={step:t=>{P.ex=wave(t,0,5,.8);P.nf=Math.round(wave(t,2,5,.27,2));P.yaw=-0.7+0.4*Math.sin(t*.25);draw();},stop:()=>refresh()};
  LabIO(app,{name:'structural-frame',state:()=>({P,sx,sy}),load:o=>{Object.assign(P,o.P||{});if(o.sx)sx=o.sx;if(o.sy)sy=o.sy;refresh();},redraw:draw,
    dxf:()=>{const R=compute(),E=[],c=R.c/1000;
      R.X.forEach(x=>E.push({layer:'GRID',closed:false,pts:[[x,-2],[x,R.Ly+2]]}));R.Y.forEach(y=>E.push({layer:'GRID',closed:false,pts:[[-2,y],[R.Lx+2,y]]}));
      R.X.forEach(x=>R.Y.forEach(y=>E.push({layer:'COLUMN',pts:[[x-c/2,y-c/2],[x+c/2,y-c/2],[x+c/2,y+c/2],[x-c/2,y+c/2]]})));
      for(let f=1;f<=P.nf;f++){const z=f*P.fh;R.X.forEach(x=>E.push({layer:'BEAM',closed:false,z,pts:[[x,0],[x,R.Ly]]}));R.Y.forEach(y=>E.push({layer:'BEAM',closed:false,z,pts:[[0,y],[R.Lx,y]]}));}
      return E;}});
  addEventListener('resize',draw); draw();
})();
