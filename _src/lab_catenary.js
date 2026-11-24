// LAB 07 — 현수선 형태 찾기 (Form finding)
// 그물을 대지 경계에 매달고 자중으로 늘어뜨린 뒤(힘 밀도법 반복 이완), 뒤집어 압축만 받는 셸을 얻는다.
// MOSSCAPE 흙 셸에서 numpy로 짠 동적 이완 코드를 웹으로 옮긴 것.
(function(){
  const root=document.getElementById('lab-catenary'); if(!root) return;
  const {INK,DIM,FAINT,RED,BLUE,MONO}=LD;
  const P={n:18,rise:.32,t:.3,yaw:-0.75,flip:1};
  let poly=[[2,6],[6,1.5],[13,1],[18,4.5],[18.5,11],[13,15],[5,14],[1.5,10.5]];
  let holes=[[10,8,1.4]];
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="pl"></canvas><p class="hint">파란 점 = 지점(경계) 드래그 · 빨간 원 = 천창 드래그 · 빈 곳 더블클릭 = 천창 추가/삭제</p></div>
  <div class="cv sheet"><canvas class="iso"></canvas><p class="hint">좌우로 드래그 = 회전</p></div></div><div class="nls"></div>`;
  const cP=app.querySelector('.pl'), cI=app.querySelector('.iso'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'그물',k:'그물 밀도',min:10,max:30,step:1,get:()=>P.n,set:v=>P.n=v},
    {g:'셸',k:'높이/경간',min:.15,max:.6,step:.01,get:()=>P.rise,set:v=>P.rise=v},
    {g:'셸',k:'흙 두께 m',min:.15,max:.6,step:.05,get:()=>P.t,set:v=>P.t=v},
  ],()=>{build();});

  const inside=(x,y,p)=>{let c=false;for(let i=0,j=p.length-1;i<p.length;j=i++){const a=p[i],b=p[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;};
  let M=null, it=0, anim=0, run=false; // M: 그물 (노드 · 고정 · 이웃 · 셀)
  function build(){
    const xs=poly.map(p=>p[0]),ys=poly.map(p=>p[1]),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
    const span=Math.max(x1-x0,y1-y0),h=span/P.n,nx=Math.ceil((x1-x0)/h)+1,ny=Math.ceil((y1-y0)/h)+1,id=new Int32Array(nx*ny).fill(-1),N=[];
    for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const x=x0+i*h,y=y0+j*h;if(!inside(x,y,poly))continue;if(holes.some(o=>Math.hypot(x-o[0],y-o[1])<o[2]))continue;id[j*nx+i]=N.length;N.push({x,y,i,j,z:0,fix:false,nb:[],edge:false});}
    N.forEach(o=>{[[1,0],[-1,0],[0,1],[0,-1]].forEach(([a,b])=>{const ii=o.i+a,jj=o.j+b,k=(ii>=0&&ii<nx&&jj>=0&&jj<ny)?id[jj*nx+ii]:-1;if(k>=0)o.nb.push(k);else{
      // 이웃이 비었을 때: 바깥 경계면 지점(고정), 천창 쪽이면 자유단
      const x=x0+ii*h,y=y0+jj*h; if(!inside(x,y,poly)) o.fix=true; else o.edge=true;}});});
    const cells=[];for(let j=0;j<ny-1;j++)for(let i=0;i<nx-1;i++){const a=id[j*nx+i],b=id[j*nx+i+1],c=id[(j+1)*nx+i+1],d=id[(j+1)*nx+i];if(a>=0&&b>=0&&c>=0&&d>=0)cells.push([a,b,c,d]);}
    M={N,cells,h,span,x0,x1,y0,y1}; it=0; anim=performance.now(); P.flip=0; if(!run){run=true;requestAnimationFrame(tick);}
  }
  // 힘 밀도법: z_i = (Σz_j + w)/k — 자중 w로 아래로 늘어진다. 반복할수록 수렴.
  function relax(n){const N=M.N,w=-M.h*M.h*.06;for(let s=0;s<n;s++){for(const o of N){if(o.fix||!o.nb.length)continue;let sz=0;for(const k of o.nb)sz+=N[k].z;
    // 천창 가장자리(자유단)는 이웃이 적어 더 처지므로 고리 보 역할로 살짝 묶는다
    o.z=(sz+w)/(o.nb.length+(o.edge?.15:0));}}it+=n;}
  function zs(){let m=0;M.N.forEach(o=>m=Math.min(m,o.z));return m;} // 가장 깊은 처짐 (음수)

  function tick(){if(!M)return;const done=it>=900;if(!done)relax(30);const t=(performance.now()-anim)/1000;
    if(done&&P.flip<1){P.flip=Math.min(1,P.flip+.06);} draw(); if(!done||P.flip<1) requestAnimationFrame(tick); else run=false;}

  let T={};
  function drawPlan(){const [g,W,H]=LD.fit(cP),pad=26,k=Math.min((W-2*pad)/(M.x1-M.x0+2),(H-2*pad-20)/(M.y1-M.y0+2)),ox=pad+(W-2*pad-(M.x1-M.x0)*k)/2-M.x0*k,oy=pad+10-M.y0*k+((H-2*pad-20)-(M.y1-M.y0)*k)/2;
    T={k,ox,oy};const G=(x,y)=>[ox+x*k,oy+y*k];const d=zs()||-1,h2=M.h*k/2;
    M.N.forEach(o=>{const v=o.z/d,[x,y]=G(o.x,o.y);g.fillStyle=`rgba(${Math.round(60+180*v)},${Math.round(58+150*v)},${Math.round(52+80*v)},.9)`;g.fillRect(x-h2,y-h2,h2*2+.5,h2*2+.5);});
    // 등고선 대신 그물선
    g.strokeStyle='rgba(21,21,19,.55)';g.lineWidth=.6;M.N.forEach((o,i)=>o.nb.forEach(k2=>{if(k2>i){const a=G(o.x,o.y),b=G(M.N[k2].x,M.N[k2].y);g.beginPath();g.moveTo(a[0],a[1]);g.lineTo(b[0],b[1]);g.stroke();}}));
    LD.path(g,poly.map(p=>G(p[0],p[1])));g.strokeStyle=INK;g.lineWidth=1.4;g.stroke();
    M.N.forEach(o=>{if(o.fix){const [x,y]=G(o.x,o.y);g.fillStyle=RED;g.fillRect(x-1.5,y-1.5,3,3);}});
    holes.forEach(o=>{const [x,y]=G(o[0],o[1]);g.beginPath();g.arc(x,y,o[2]*k,0,7);g.strokeStyle=RED;g.setLineDash([3,3]);g.lineWidth=1;g.stroke();g.setLineDash([]);g.beginPath();g.arc(x,y,4,0,7);g.fillStyle=RED;g.fill();});
    poly.forEach(p=>{const [x,y]=G(p[0],p[1]);g.beginPath();g.arc(x,y,5,0,7);g.fillStyle='#151513';g.fill();g.strokeStyle=BLUE;g.lineWidth=2;g.stroke();});
    const a=G(M.x0,M.y1+.9),b=G(M.x1,M.y1+.9);LD.dim(g,a[0],a[1],b[0],b[1],(M.x1-M.x0).toFixed(1)+' m',6);
    LD.text(g,P.flip<1?(it<900?'HANG  · 이완 '+it+'회':'FLIP  · 뒤집는 중'):'SHELL · 압축만 받는 형태',12,16,{c:P.flip<1?'#e0a15a':INK});
    LD.text(g,'■ 지점(고정)',12,H-10,{c:RED});
  }
  function drawIso(){const [g,W,H]=LD.fit(cI);const cx=(M.x0+M.x1)/2,cy=(M.y0+M.y1)/2,co=Math.cos(P.yaw),si=Math.sin(P.yaw),k=Math.min(W,H)/(M.span*1.55);
    const fl=P.flip, d=zs()||-1, s=P.rise*M.span/-d, zz=o=>o.z*s*(2*fl-1)*-1; // 처음엔 아래로(늘어짐), 뒤집히면 위로
    const pr=(x,y,z)=>{const X=(x-cx)*co-(y-cy)*si,Y=(x-cx)*si+(y-cy)*co;return [W/2+X*k,H*.62+Y*k*.5-z*k,Y];};
    // 바닥 경계
    LD.path(g,poly.map(p=>pr(p[0],p[1],0)));g.strokeStyle=FAINT;g.lineWidth=1;g.stroke();
    const Lx=-.5,Ly=-.6,Lz=.62;
    M.cells.map(c=>{const p=c.map(i=>M.N[i]),q=p.map(o=>pr(o.x,o.y,zz(o)));
      const ux=p[2].x-p[0].x,uy=p[2].y-p[0].y,uz=zz(p[2])-zz(p[0]),vx=p[3].x-p[1].x,vy=p[3].y-p[1].y,vz=zz(p[3])-zz(p[1]);
      let nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;const L=Math.hypot(nx,ny,nz)||1;if(nz<0){nx=-nx;ny=-ny;nz=-nz;}
      const sh=Math.max(0,(nx*Lx+ny*Ly+nz*Lz)/L);return {q,dep:q.reduce((a,b)=>a+b[2],0),sh};})
     .sort((a,b)=>a.dep-b.dep).forEach(c=>{LD.path(g,c.q);const v=Math.round(40+150*c.sh);g.fillStyle=`rgb(${v},${v-4},${v-12})`;g.fill();g.strokeStyle='rgba(230,227,218,.35)';g.lineWidth=.5;g.stroke();});
    let top=null;M.N.forEach(o=>{if(!top||zz(o)>zz(top))top=o;});
    if(fl>=1&&top){const p=pr(top.x,top.y,zz(top)),b=pr(top.x,top.y,0);g.setLineDash([3,3]);g.strokeStyle=BLUE;g.beginPath();g.moveTo(b[0],b[1]);g.lineTo(p[0],p[1]);g.stroke();g.setLineDash([]);LD.text(g,'▲ '+zz(top).toFixed(2)+' m',p[0]+8,p[1]-4,{c:BLUE});}
    LD.text(g,fl<1?'자중으로 늘어진 그물':'뒤집은 셸 (흙 두께 '+P.t.toFixed(2)+' m)',12,16,{c:DIM});
  }
  function stats(){const d=zs()||-1,s=P.rise*M.span/-d;let area=0,plan=0;M.cells.forEach(c=>{const p=c.map(i=>M.N[i]);const a=(o,b,cc)=>{const ux=b.x-o.x,uy=b.y-o.y,uz=(b.z-o.z)*s,vx=cc.x-o.x,vy=cc.y-o.y,vz=(cc.z-o.z)*s;return Math.hypot(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx)/2;};area+=a(p[0],p[1],p[2])+a(p[0],p[2],p[3]);plan+=M.h*M.h;});
    const vol=area*P.t,wt=vol*1.8,rise=-d*s;
    LD.stats(out,[['경간',M.span.toFixed(1)+' m'],['높이',rise.toFixed(2)+' m'],['높이/경간',(rise/M.span).toFixed(2),rise/M.span<.2?'ng':''],['바닥 면적',plan.toFixed(0)+' ㎡'],['셸 면적',area.toFixed(0)+' ㎡'],
      ['흙 물량',vol.toFixed(1)+' ㎥'],['무게',wt.toFixed(0)+' t'],['그물 노드',M.N.length+'개'],['천창',holes.length+'개'],['상태',P.flip>=1?'압축 셸':'이완 중']],[5,6],
      '그물을 경계에 매달아 자중으로 늘어뜨리면 장력만 받는 형태가 나온다. 이를 뒤집으면 같은 하중에 압축만 받는 셸이 된다(현수선 원리, Gaudí · Isler). 높이/경간이 0.2보다 낮으면 수평 추력이 커져 흙 셸로는 불리하다.');}
  function draw(){if(!M)return;drawPlan();drawIso();stats();}

  // 조작: 지점 · 천창 드래그, 더블클릭 = 천창 추가/삭제, 아이소 회전
  let drag=null,rot=null;
  const loc=(cv,e)=>{const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];};
  const W2=(x,y)=>[(x-T.ox)/T.k,(y-T.oy)/T.k];
  cP.addEventListener('pointerdown',e=>{const [x,y]=loc(cP,e);
    const vi=poly.findIndex(p=>Math.hypot(T.ox+p[0]*T.k-x,T.oy+p[1]*T.k-y)<10);if(vi>=0){drag={t:'v',i:vi};}
    else{const hi=holes.findIndex(o=>Math.hypot(T.ox+o[0]*T.k-x,T.oy+o[1]*T.k-y)<12);if(hi>=0)drag={t:'h',i:hi};}
    if(drag)cP.setPointerCapture(e.pointerId);});
  cP.addEventListener('pointermove',e=>{const [x,y]=loc(cP,e);if(!drag){const on=poly.some(p=>Math.hypot(T.ox+p[0]*T.k-x,T.oy+p[1]*T.k-y)<10)||holes.some(o=>Math.hypot(T.ox+o[0]*T.k-x,T.oy+o[1]*T.k-y)<12);cP.style.cursor=on?'move':'default';return;}
    const [wx,wy]=W2(x,y);if(drag.t==='v')poly[drag.i]=[Math.round(wx*10)/10,Math.round(wy*10)/10];else{holes[drag.i][0]=wx;holes[drag.i][1]=wy;}build();});
  cP.addEventListener('pointerup',()=>drag=null);
  cP.addEventListener('dblclick',e=>{const [x,y]=loc(cP,e),[wx,wy]=W2(x,y);const hi=holes.findIndex(o=>Math.hypot(o[0]-wx,o[1]-wy)<o[2]);
    if(hi>=0)holes.splice(hi,1);else if(inside(wx,wy,poly))holes.push([wx,wy,1.1]);build();});
  cI.addEventListener('pointerdown',e=>{rot=[e.clientX,P.yaw];cI.setPointerCapture(e.pointerId);});
  cI.addEventListener('pointermove',e=>{if(!rot)return;P.yaw=rot[1]+(e.clientX-rot[0])*.01;draw();});
  cI.addEventListener('pointerup',()=>rot=null);

  // 자동 시연: 경계 한 점과 천창이 움직이고, 높이/경간이 바뀐다
  const base=poly.map(p=>p.slice());let dk=-1;
  app.demo={step:t=>{const k=Math.floor(t/3.2);P.yaw=-0.75+0.5*Math.sin(t*.25);
    if(k!==dk){dk=k;poly=base.map((p,i)=>i===k%base.length?[p[0]+(p[0]-10)*.25,p[1]+(p[1]-8)*.25]:p.slice());holes=[[10+3*Math.sin(k),8+2*Math.cos(k*1.3),1.2+.5*(k%2)]];P.rise=[.32,.45,.25,.38][k%4];build();}
    else draw();},stop:()=>refresh()};
  LabIO(app,{name:'form-finding',poly:{get:()=>poly,set:v=>poly=v},state:()=>({P,poly,holes}),load:o=>{Object.assign(P,o.P||{});if(o.poly)poly=o.poly;if(o.holes)holes=o.holes;refresh();},redraw:build,
    dxf:()=>{const d=zs()||-1,s=P.rise*M.span/-d,E=[{layer:'BOUNDARY',pts:poly}];M.N.forEach((o,i)=>o.nb.forEach(k=>{if(k>i){const b=M.N[k];E.push({layer:'SHELL',closed:false,pts:[[o.x,o.y,-o.z*s],[b.x,b.y,-b.z*s]]});}}));return E;}});
  addEventListener('resize',draw); build();
})();
