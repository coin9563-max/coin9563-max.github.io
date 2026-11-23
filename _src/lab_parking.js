// LAB 05 — 주차 배치
// 대지 꼭짓점을 끌면, 주차 모듈(구획 5.0 + 차로 6.0 + 구획 5.0)을 여러 각도 · 오프셋 · 연결 차로 위치로 깔아 보고
// 가장 많이 들어가는 안을 고른다. 법정 주차대수(용도별 시설면적당 1대)와 비교한다.
(function(){
  const root=document.getElementById('lab-parking'); if(!root) return;
  const USE=[{n:'업무시설',a:150},{n:'근린생활시설',a:134},{n:'판매시설',a:150},{n:'숙박시설',a:200}];
  const P={sw:2.5,sl:5.0,aw:6.0,use:0,gfa:4000,sb:1.0};
  let poly=[[4,6],[52,2],[57,34],[30,44],[6,36]];
  let best=null;
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="top"></canvas><p class="hint">꼭짓점 드래그 · 변 더블클릭 = 점 추가 · 점 더블클릭 = 삭제</p></div>
  <div class="cv sheet"><canvas class="gr"></canvas><p class="hint">각도별 최대 대수 (탐색 결과) · 막대를 누르면 그 각도로</p></div></div><div class="nls"></div>`;
  const cT=app.querySelector('.top'), cG=app.querySelector('.gr'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'주차',k:'구획 폭 m',min:2.3,max:2.6,step:.1,get:()=>P.sw,set:v=>P.sw=v},
    {g:'주차',k:'구획 길이 m',min:5,max:5.2,step:.1,get:()=>P.sl,set:v=>P.sl=v},
    {g:'주차',k:'차로 폭 m',min:5,max:7,step:.5,get:()=>P.aw,set:v=>P.aw=v},
    {g:'주차',k:'경계 이격 m',min:0,max:3,step:.5,get:()=>P.sb,set:v=>P.sb=v},
    {g:'법정 대수',k:'용도',opts:USE.map(u=>u.n),get:()=>P.use,set:v=>P.use=v},
    {g:'법정 대수',k:'시설면적 ㎡',min:500,max:20000,step:100,get:()=>P.gfa,set:v=>P.gfa=v},
  ],()=>{search();draw();});

  const area=p=>Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-b[0]*a[1];},0))/2;
  function inside(x,y,p){let c=false;for(let i=0,j=p.length-1;i<p.length;j=i++){const[a,b]=p[i],[d,e]=p[j];if((b>y)!==(e>y)&&x<(d-a)*(y-b)/(e-b)+a)c=!c;}return c;}
  const segD=(x,y,a,b)=>{const dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));return Math.hypot(x-a[0]-t*dx,y-a[1]-t*dy);};
  const edgeD=(x,y,p)=>{let m=1e9;for(let i=0;i<p.length;i++)m=Math.min(m,segD(x,y,p[i],p[(i+1)%p.length]));return m;};
  const ok=(x,y,p)=>inside(x,y,p)&&edgeD(x,y,p)>=P.sb-1e-9;

  // 한 각도 · 오프셋 · 연결 차로 위치에서 배치
  function layout(th,oy,cx){
    const c=Math.cos(th),s=Math.sin(th);
    const lp=poly.map(([x,y])=>[x*c+y*s,-x*s+y*c]); // 지역 좌표 (차로가 가로)
    const xs=lp.map(p=>p[0]),ys=lp.map(p=>p[1]),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
    const M=P.sl*2+P.aw, stalls=[], aisles=[];
    const rectOK=(a,b,w,h)=>ok(a,b,lp)&&ok(a+w,b,lp)&&ok(a,b+h,lp)&&ok(a+w,b+h,lp)&&ok(a+w/2,b+h/2,lp);
    const conX=x0+cx;
    for(let y=y0+oy-M;y<y1;y+=M){
      const ay=y+P.sl; // 차로 시작
      // 차로: 지나갈 수 있는 구간
      let segs=[],cur=null;
      for(let x=x0;x<=x1;x+=1){const g=rectOK(x,ay,1,P.aw);if(g){if(!cur)cur=[x,x+1];else cur[1]=x+1;}else if(cur){segs.push(cur);cur=null;}}
      if(cur)segs.push(cur);
      segs=segs.filter(s=>s[1]-s[0]>=P.sw*3);
      segs.forEach(sg=>{aisles.push([sg[0],ay,sg[1]-sg[0],P.aw]);
        for(const row of [[y,0],[ay+P.aw,1]]){
          for(let x=sg[0];x+P.sw<=sg[1]+1e-9;x+=P.sw){
            if(x+P.sw>conX&&x<conX+P.aw) continue; // 연결 차로 자리
            if(rectOK(x,row[0],P.sw,P.sl)) stalls.push([x,row[0],P.sw,P.sl,row[1]]);
          }}});
    }
    // 연결 차로 (세로)
    let con=null; {const ys2=aisles.map(a=>a[1]);if(ys2.length>1){const ya=Math.min(...ys2),yb=Math.max(...ys2)+P.aw;con=[conX,ya,P.aw,yb-ya];}}
    return {th,stalls,aisles,con,n:stalls.length};
  }
  let curTh=null;
  function search(){
    const res=[]; let top=null;
    for(let d=0;d<180;d+=5){const th=d*Math.PI/180; let bt=null;
      for(let oy=0;oy<P.sl*2+P.aw;oy+=2) for(let cx=2;cx<62;cx+=10){const r=layout(th,oy,cx); if(!bt||r.n>bt.n) bt=r;}
      res.push(bt); if(!top||bt.n>top.n) top=bt;}
    best={res,top}; curTh=top.th;
  }
  function current(){ return best.res.find(r=>Math.abs(r.th-curTh)<1e-6)||best.top; }

  let T=null;
  function drawTop(){
    const [g,W,H]=LD.fit(cT), L=current();
    const xs=poly.map(p=>p[0]),ys=poly.map(p=>p[1]),x0=Math.min(...xs)-4,y0=Math.min(...ys)-4,w=Math.max(...xs)-x0+4,h=Math.max(...ys)-y0+4;
    const k=Math.min(W/w,(H-24)/h); T={k,ox:(W-w*k)/2-x0*k,oy:(H-24-h*k)/2-y0*k};
    const c=Math.cos(L.th),s=Math.sin(L.th), G=(x,y)=>{const wx=x*c-y*s,wy=x*s+y*c;return [T.ox+wx*k,T.oy+wy*k];};
    const R=(x,y,w2,h2)=>[G(x,y),G(x+w2,y),G(x+w2,y+h2),G(x,y+h2)];
    LD.path(g,poly.map(p=>[T.ox+p[0]*k,T.oy+p[1]*k]));g.fillStyle='rgba(255,255,255,.025)';g.fill();
    // 차로
    g.fillStyle='rgba(224,161,90,.10)';
    L.aisles.concat(L.con?[L.con]:[]).forEach(a=>{LD.path(g,R(...a));g.fill();});
    g.strokeStyle='rgba(224,161,90,.75)';g.setLineDash([6,4]);g.lineWidth=.8;
    L.aisles.forEach(a=>{LD.path(g,[G(a[0],a[1]+a[3]/2),G(a[0]+a[2],a[1]+a[3]/2)],false);g.stroke();});
    if(L.con){const a=L.con;LD.path(g,[G(a[0]+a[2]/2,a[1]),G(a[0]+a[2]/2,a[1]+a[3])],false);g.stroke();} g.setLineDash([]);
    // 구획 (장애인 구획: 연결 차로에 가까운 앞쪽 몇 칸)
    const need=Math.max(1,Math.ceil(L.n*0.03));
    const acc=new Set(L.con?L.stalls.map((q,i)=>[i,Math.abs(q[0]+q[2]/2-(L.con[0]+L.con[2]/2))+Math.abs(q[1]-L.con[1])*0.2]).sort((a,b)=>a[1]-b[1]).slice(0,need).map(a=>a[0]):[]);
    L.stalls.forEach((q,i)=>{LD.path(g,R(...q.slice(0,4)));if(acc.has(i)){g.fillStyle='rgba(77,163,255,.25)';g.fill();g.strokeStyle=LD.BLUE;}else g.strokeStyle=LD.INK;g.lineWidth=.8;g.stroke();});
    LD.path(g,poly.map(p=>[T.ox+p[0]*k,T.oy+p[1]*k]));g.strokeStyle=LD.INK;g.lineWidth=1.6;g.stroke();
    poly.forEach((a,i)=>{const b=poly[(i+1)%poly.length];LD.text(g,Math.hypot(b[0]-a[0],b[1]-a[1]).toFixed(1)+'m',T.ox+(a[0]+b[0])/2*k,T.oy+(a[1]+b[1])/2*k-6,{a:'center'});});
    poly.forEach(p=>{g.beginPath();g.arc(T.ox+p[0]*k,T.oy+p[1]*k,5,0,7);g.fillStyle=LD.BG;g.fill();g.strokeStyle=LD.BLUE;g.lineWidth=2;g.stroke();});
    LD.text(g,`${L.n}대 · 장애인 ${need}대 · 각도 ${Math.round(L.th*180/Math.PI)}°`,12,18,{c:LD.INK,size:11});
    LD.text(g,'□ 일반  ■ 장애인  --- 차로',12,H-8);
  }
  let GB=null;
  function drawGraph(){
    const [g,W,H]=LD.fit(cG), res=best.res, mx=Math.max(1,...res.map(r=>r.n));
    const l=40,r=14,t=34,b=34, bw=(W-l-r)/res.length; GB={l,bw,t,b,H};
    g.strokeStyle=LD.FAINT;g.lineWidth=.6;for(let i=0;i<=4;i++){const y=t+(H-t-b)*i/4;g.beginPath();g.moveTo(l,y);g.lineTo(W-r,y);g.stroke();LD.text(g,Math.round(mx*(1-i/4)),l-6,y+3,{a:'right'});}
    res.forEach((q,i)=>{const h=(H-t-b)*q.n/mx, on=Math.abs(q.th-curTh)<1e-6, top=q===best.top;
      g.fillStyle=on?LD.RED:top?LD.GREEN:'#4a4a44';g.fillRect(l+i*bw+1,H-b-h,bw-2,h);
      if(i%6===0)LD.text(g,(i*5)+'°',l+i*bw+bw/2,H-b+14,{a:'center'});});
    LD.text(g,`최대 ${best.top.n}대 @ ${Math.round(best.top.th*180/Math.PI)}° · 각도 36 × 오프셋 × 연결 차로 위치 탐색`,12,18,{c:LD.INK,size:11});
    LD.text(g,'■ 선택  ■ 최대',W-120,H-8);
  }
  function stats(){
    const L=current(), U=USE[P.use], need=Math.ceil(P.gfa/U.a), site=area(poly), pa=L.n?site/L.n:0;
    LD.stats(out,[['대지면적',Math.round(site).toLocaleString()+' ㎡'],['배치 대수',L.n+'대'],['장애인 구획 (3%)',Math.max(1,Math.ceil(L.n*0.03))+'대'],['대당 면적',pa.toFixed(1)+' ㎡'],
      ['법정 대수',`${need}대 (${U.n} ${U.a}㎡당 1대)`],['충족',L.n>=need?'OK':'부족 '+(need-L.n)+'대',L.n>=need?'':'ng'],['탐색 최대',best.top.n+'대 @ '+Math.round(best.top.th*180/Math.PI)+'°'],['구획 · 차로',`${P.sw}×${P.sl} · ${P.aw}m`]],
      [1,5],'직각주차 모듈(구획+차로+구획)을 5° 간격 36개 각도, 오프셋, 세로 연결 차로 위치를 바꿔 가며 깔고 가장 많이 들어가는 안을 고른다. 법정 대수는 지자체 조례마다 달라 대표값을 썼고, 램프 · 기계식 · 출입구 위치는 반영하지 않았다.');
  }
  function draw(){drawTop();drawGraph();stats();}

  const W2=e=>{const r=cT.getBoundingClientRect();return [(e.clientX-r.left-T.ox)/T.k,(e.clientY-r.top-T.oy)/T.k];};
  let drag=-1;
  cT.addEventListener('pointerdown',e=>{const [x,y]=W2(e);drag=poly.findIndex(p=>Math.hypot(p[0]-x,p[1]-y)*T.k<12);if(drag>=0)cT.setPointerCapture(e.pointerId);});
  cT.addEventListener('pointermove',e=>{if(drag<0)return;const [x,y]=W2(e);poly[drag]=[Math.round(x*2)/2,Math.round(y*2)/2];
    // 드래그 중에는 현재 각도만 다시 계산
    let bt=null;for(let oy=0;oy<P.sl*2+P.aw;oy+=2)for(let cx=2;cx<62;cx+=10){const r=layout(curTh,oy,cx);if(!bt||r.n>bt.n)bt=r;}
    const i=best.res.findIndex(r=>Math.abs(r.th-curTh)<1e-6); best.res[i]=bt; drawTop(); stats();});
  cT.addEventListener('pointerup',()=>{if(drag>=0){drag=-1;search();draw();}});
  cT.addEventListener('dblclick',e=>{const [x,y]=W2(e);const vi=poly.findIndex(p=>Math.hypot(p[0]-x,p[1]-y)*T.k<12);
    if(vi>=0){if(poly.length>3)poly.splice(vi,1);} else {let bi=-1,bd=1e9;poly.forEach((a,i)=>{const d=segD(x,y,a,poly[(i+1)%poly.length]);if(d<bd){bd=d;bi=i;}}); if(bd*T.k<14) poly.splice(bi+1,0,[Math.round(x*2)/2,Math.round(y*2)/2]);} search();draw();});
  cG.addEventListener('click',e=>{const r=cG.getBoundingClientRect(),i=Math.floor((e.clientX-r.left-GB.l)/GB.bw);if(i>=0&&i<best.res.length){curTh=best.res[i].th;draw();}});
  LabIO(app,{name:'parking',poly:{get:()=>poly,set:v=>poly=v},state:()=>({P,poly}),load:o=>{Object.assign(P,o.P||{});if(o.poly)poly=o.poly;refresh();},redraw:()=>{search();draw();},
    dxf:()=>{const L=current(),c=Math.cos(L.th),s=Math.sin(L.th),G=(x,y)=>[x*c-y*s,x*s+y*c],E=[{layer:'SITE',pts:poly}];
      L.stalls.forEach(q=>E.push({layer:'STALL',pts:[G(q[0],q[1]),G(q[0]+q[2],q[1]),G(q[0]+q[2],q[1]+q[3]),G(q[0],q[1]+q[3])]}));
      L.aisles.forEach(a=>E.push({layer:'AISLE',closed:false,pts:[G(a[0],a[1]+a[3]/2),G(a[0]+a[2],a[1]+a[3]/2)]}));
      if(L.con){const a=L.con;E.push({layer:'AISLE',closed:false,pts:[G(a[0]+a[2]/2,a[1]),G(a[0]+a[2]/2,a[1]+a[3])]});}return E;}});
  addEventListener('resize',draw); search(); draw();
})();
