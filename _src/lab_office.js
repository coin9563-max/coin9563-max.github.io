// LAB 09 — 오피스 빛 · 열
// 방위 · 창 비율 · 평면 깊이 · 차양 · 유리를 바꾸면, 단면의 주광률 분포와 주광 영역, 여름 설계일 시간별 냉방 부하,
// 겨울 난방 부하가 함께 다시 계산된다. 서울(위도 37.5°) 맑은 날 기준의 근사 계산.
(function(){
  const root=document.getElementById('lab-office'); if(!root) return;
  const ORI=[{n:'남',az:180},{n:'동',az:90},{n:'서',az:270},{n:'북',az:0}];
  const GL=[{n:'일반 복층',U:2.8,G:.70,T:.80},{n:'복층 로이',U:1.5,G:.40,T:.70},{n:'삼중 로이',U:.9,G:.30,T:.60}];
  const P={ori:0,H:3.6,wwr:55,D:12,oh:.9,gl:1,sill:.8};
  const app=root.querySelector('.app');
  app.innerHTML=`<div class="lctl"></div>
  <div class="nlv"><div class="cv sheet"><canvas class="sec"></canvas><p class="hint">빨간 차양 끝 = 차양 깊이 · 파란 창 머리 = 창 높이 · 뒤 벽 = 평면 깊이 (드래그)</p></div>
  <div class="cv sheet"><canvas class="ld"></canvas><p class="hint">여름 설계일(7월 21일) 시간별 냉방 부하 W/㎡ — 일사 · 전도 · 내부 발열</p></div></div><div class="nls"></div>`;
  const cS=app.querySelector('.sec'), cL=app.querySelector('.ld'), out=app.querySelector('.nls');
  const refresh=LabUI(app.querySelector('.lctl'),[
    {g:'외피',k:'방위',opts:ORI.map(o=>o.n+'향'),get:()=>P.ori,set:v=>P.ori=v},
    {g:'외피',k:'창 면적비 %',min:15,max:90,step:1,get:()=>P.wwr,set:v=>P.wwr=v},
    {g:'외피',k:'차양 깊이 m',min:0,max:2,step:.05,get:()=>P.oh,set:v=>P.oh=v},
    {g:'외피',k:'유리',opts:GL.map(g=>g.n),get:()=>P.gl,set:v=>P.gl=v},
    {g:'공간',k:'층고 m',min:2.8,max:4.8,step:.1,get:()=>P.H,set:v=>P.H=v},
    {g:'공간',k:'평면 깊이 m',min:5,max:20,step:.5,get:()=>P.D,set:v=>P.D=v},
  ],draw);
  const R=Math.PI/180, LAT=37.5*R;
  function sun(doy,h){const dec=23.44*R*Math.sin(2*Math.PI*(284+doy)/365),ha=(h-12)*15*R;
    const alt=Math.asin(Math.sin(LAT)*Math.sin(dec)+Math.cos(LAT)*Math.cos(dec)*Math.cos(ha));
    let az=Math.atan2(Math.sin(ha),Math.cos(ha)*Math.sin(LAT)-Math.tan(dec)*Math.cos(LAT))+Math.PI; return {alt,az};}
  function compute(){
    const g=GL[P.gl], o=ORI[P.ori], ceil=P.H-.9;                         // 천장 아래 (보 · 설비 0.9m)
    const wh=Math.max(.3,Math.min(ceil-P.sill,(P.wwr/100)*P.H)), head=P.sill+wh; // 폭 1m당 창 높이
    // 주광: BRE 평균 주광률 DF = T·Aw·θ / (A·(1−R²)),  θ = 차양이 가린 뒤 보이는 하늘 각
    const theta=90-Math.atan2(P.oh,wh/2+.15)/R*0.9, A=2*(P.D+P.H+P.D*P.H/8); // 폭 8m 실 기준, 폭 1m당 실내 표면
    const DFa=g.T*wh*theta/(A*.75)*1.0, hh=head;
    const xs=[],df=[]; let sum=0; for(let x=.25;x<=P.D;x+=.25){const v=Math.exp(-x/(1.15*hh));xs.push(x);df.push(v);sum+=v;}
    const nrm=DFa*df.length/sum; for(let i=0;i<df.length;i++)df[i]*=nrm;
    const lit=xs.filter((x,i)=>df[i]>=2).length*.25, litR=Math.min(1,lit/P.D);
    // 냉방: 시간별 (07~19시), 바닥 1㎡당
    const H=[],TO=t=>27+6*Math.sin((t-9)*Math.PI/12);                 // 외기 (최고 33℃ 15시)
    for(let t=6;t<=20;t+=.5){const s=sun(202,t);let Iv=0,sh=0;
      if(s.alt>0){const dni=900*Math.exp(-.16/Math.sin(s.alt)),dhi=110*Math.pow(Math.sin(s.alt),.6),gam=s.az-o.az*R,ci=Math.cos(s.alt)*Math.cos(gam);
        const prof=Math.atan2(Math.tan(s.alt),Math.max(.02,Math.cos(gam)));sh=ci>0?Math.min(1,P.oh*Math.tan(prof)/wh):0;
        Iv=Math.max(0,dni*ci)*(1-sh)+dhi*.5+(dni*Math.sin(s.alt)+dhi)*.2*.5;}
      const qs=g.G*wh*Iv/P.D, qc=(g.U*wh+.25*(P.H-wh))*(TO(t)-26)/P.D, qi=(t>=8&&t<=19)?(14+10*(1-.6*litR)):3;
      H.push({t,qs,qc:Math.max(0,qc),qi,tot:qs+Math.max(0,qc)+qi,sh});}
    const pk=H.reduce((a,b)=>b.tot>a.tot?b:a);
    const w=sun(355,12), ws=Math.atan2(Math.tan(w.alt),Math.cos(Math.PI-o.az*R)), shW=P.ori===3?1:Math.min(1,P.oh*Math.tan(Math.max(.01,ws))/wh);
    const heat=(g.U*wh+.25*(P.H-wh))*(20+11)/P.D+.5*.34*P.H*31;         // 겨울 −11℃, 환기 0.5회/h
    const s21=sun(202,12),sumSh=P.ori===0?Math.min(1,P.oh*Math.tan(s21.alt)/wh):null;
    const checks=[['주광 영역 ≥ 50%',litR>=.5],['평균 주광률 2~5%',DFa>=2&&DFa<=5],['냉방 피크 ≤ 60 W/㎡',pk.tot<=60],['겨울 해 들어옴',P.ori===3?false:shW<.5]];
    return {g,o,wh,head,ceil,xs,df,DFa,litR,lit,H,pk,heat,sumSh,shW,checks,theta};
  }
  let SS=null;
  function drawSec(Z){
    const [g,W,H]=LD.fit(cS), x0=-Math.max(2.2,P.oh+1), x1=P.D+.6, z0=-1.4, z1=P.H+1.2;
    const k=Math.min((W-30)/(x1-x0),(H-60)/(z1-z0)), ox=20-x0*k, oy=H/2+(z0+z1)/2*k, X=x=>ox+x*k, Y=z=>oy-z*k; SS={k,ox,oy};
    // 주광률 띠 (바닥 위)
    Z.xs.forEach((x,i)=>{const v=Math.min(1,Z.df[i]/6);g.fillStyle=`rgba(255,214,120,${.08+.6*v})`;g.fillRect(X(x-.25),Y(.9),.25*k+.5,.9*k);});
    // 슬래브 · 벽 · 천장
    g.fillStyle='#2a2a26'; g.fillRect(X(-.3),Y(0),(P.D+.6)*k,.3*k); g.fillRect(X(-.3),Y(P.H+.3),(P.D+.6)*k,.3*k);
    g.strokeStyle=LD.FAINT; g.setLineDash([3,3]); g.beginPath(); g.moveTo(X(0),Y(Z.ceil)); g.lineTo(X(P.D),Y(Z.ceil)); g.stroke(); g.setLineDash([]);
    g.strokeStyle=LD.INK; g.lineWidth=1.4; g.beginPath(); g.moveTo(X(0),Y(0)); g.lineTo(X(0),Y(P.sill)); g.moveTo(X(0),Y(Z.head)); g.lineTo(X(0),Y(P.H)); g.moveTo(X(P.D),Y(0)); g.lineTo(X(P.D),Y(P.H)); g.stroke();
    g.strokeStyle=LD.BLUE; g.lineWidth=2; g.beginPath(); g.moveTo(X(0),Y(P.sill)); g.lineTo(X(0),Y(Z.head)); g.stroke();
    // 차양
    g.strokeStyle=LD.INK; g.lineWidth=2.4; g.beginPath(); g.moveTo(X(0),Y(Z.head+.05)); g.lineTo(X(-P.oh),Y(Z.head+.05)); g.stroke();
    g.fillStyle=LD.RED; g.beginPath(); g.arc(X(-P.oh),Y(Z.head+.05),5,0,7); g.fill(); g.fillStyle=LD.BLUE; g.beginPath(); g.arc(X(0),Y(Z.head),4,0,7); g.fill();
    SS.hx=X(-P.oh); SS.hy=Y(Z.head+.05); SS.wx=X(0); SS.wy=Y(Z.head); SS.bx=X(P.D);
    // 햇빛: 여름 · 겨울 남중 (남향일 때 단면 그대로, 그 외엔 정오 단면 투영)
    [[202,'#ff6b4a','하지 무렵 12시'],[355,'#ffd678','동지 12시']].forEach(([d,c,lab])=>{const s=sun(d,12),gam=s.az-Z.o.az*R,cg=Math.cos(gam);if(s.alt<=0||cg<=.05)return;
      const pa=Math.atan2(Math.tan(s.alt),cg), tp=Math.tan(pa); g.strokeStyle=c; g.globalAlpha=.75; g.lineWidth=.8;
      for(let zz=P.sill+.05;zz<=Z.head-.02;zz+=Math.max(.2,(Z.head-P.sill)/5)){const xo=-(Z.head+.05-zz)/tp, sz=Z.head+1.4, sx=-(sz-zz)/tp;
        g.beginPath(); g.moveTo(X(sx),Y(sz));
        if(xo>-P.oh){g.lineTo(X(xo),Y(Z.head+.05));g.setLineDash([2,3]);}
        else {const fx=Math.min(P.D,zz/tp); g.lineTo(X(fx),Y(zz-fx*tp));}
        g.stroke(); g.setLineDash([]);}
      g.globalAlpha=1; LD.text(g,lab+' '+(pa/R).toFixed(0)+'°',8,16+(d>300?13:0),{c});});
    LD.dim(g,X(0),Y(-.35),X(P.D),Y(-.35),P.D.toFixed(1)+'m',10);
    LD.dim(g,X(0),Y(-.85),X(Math.max(.3,Z.lit)),Y(-.85),'주광 영역 '+Z.lit.toFixed(1)+'m',10,'#ffd678');
    LD.text(g,Z.o.n+'향 · 창 높이 '+Z.wh.toFixed(2)+'m',X(P.D)-6,Y(P.H)+14,{c:LD.INK,a:'right'});
  }
  function drawLoad(Z){
    const [g,W,H]=LD.fit(cL), m=34, x0=m+10, x1=W-14, y0=H-m, y1=18, mx=Math.max(80,Math.ceil(Z.pk.tot/20)*20);
    const X=t=>x0+(t-6)/14*(x1-x0), Y=v=>y0-v/mx*(y0-y1);
    for(let v=0;v<=mx;v+=20){g.strokeStyle=LD.FAINT;g.beginPath();g.moveTo(x0,Y(v));g.lineTo(x1,Y(v));g.stroke();LD.text(g,v,x0-6,Y(v)+3,{a:'right'});}
    for(let t=6;t<=20;t+=2)LD.text(g,t+'시',X(t),y0+14,{a:'center'});
    const area=(f,c)=>{g.beginPath();Z.H.forEach((h,i)=>{const v=f(h);i?g.lineTo(X(h.t),Y(v)):g.moveTo(X(h.t),Y(v));});for(let i=Z.H.length-1;i>=0;i--){const h=Z.H[i];g.lineTo(X(h.t),Y(f(h,1)));}g.closePath();g.fillStyle=c;g.fill();};
    area((h,b)=>b?0:h.qi,'rgba(138,138,128,.55)'); area((h,b)=>b?h.qi:h.qi+h.qc,'rgba(77,163,255,.55)'); area((h,b)=>b?h.qi+h.qc:h.tot,'rgba(255,107,74,.6)');
    g.strokeStyle=LD.RED; g.setLineDash([4,4]); g.beginPath(); g.moveTo(x0,Y(60)); g.lineTo(x1,Y(60)); g.stroke(); g.setLineDash([]); LD.text(g,'60 W/㎡',x1-4,Y(60)-4,{a:'right',c:LD.RED});
    g.fillStyle=LD.INK; g.beginPath(); g.arc(X(Z.pk.t),Y(Z.pk.tot),3.5,0,7); g.fill(); LD.text(g,'피크 '+Z.pk.tot.toFixed(0)+' W/㎡ · '+Math.floor(Z.pk.t)+':'+(Z.pk.t%1?'30':'00'),X(Z.pk.t),Y(Z.pk.tot)-8,{a:'center',c:LD.INK});
    [['일사',LD.RED],['전도',LD.BLUE],['내부 발열',LD.DIM]].forEach(([s,c],i)=>{g.fillStyle=c;g.fillRect(x0+8+i*84,y1+2,10,8);LD.text(g,s,x0+22+i*84,y1+10,{c});});
  }
  function stats(Z){
    LD.stats(out,[
      ['평균 주광률',Z.DFa.toFixed(1)+' %',Z.DFa<2||Z.DFa>5?'ng':''],['주광 영역 (DF ≥ 2%)',Math.round(Z.litR*100)+' %',Z.litR<.5?'ng':''],
      ['냉방 피크',Z.pk.tot.toFixed(0)+' W/㎡',Z.pk.tot>60?'ng':''],['피크 중 일사',Math.round(Z.pk.qs/Z.pk.tot*100)+' %'],
      ['난방 피크',Z.heat.toFixed(0)+' W/㎡'],['동지 정오 창 가림',P.ori===3?'—':Math.round(Z.shW*100)+' %'],['하지 정오 창 가림',Z.sumSh==null?'—':Math.round(Z.sumSh*100)+' %'],
      ['판정',Z.checks.filter(c=>c[1]).length+' / '+Z.checks.length+' OK'],['NG',Z.checks.filter(c=>!c[1]).map(c=>c[0]).join(', ')||'없음',Z.checks.some(c=>!c[1])?'ng':'']
    ],[0,1,2],`창을 키우면 주광 영역이 깊어지지만 일사로 냉방 피크가 오른다. 남향은 차양으로 여름 해만 막을 수 있고, 동 · 서향은 해가 낮아 차양이 잘 듣지 않는다. 주광은 BRE 평균 주광률식, 부하는 서울 7월 맑은 날 · 실내 26℃ · 내부 발열 24 W/㎡(주광 영역만큼 조명 감소) 기준 근사값.`);
  }
  function draw(){const Z=compute();drawSec(Z);drawLoad(Z);stats(Z);}
  let drag=null; const loc=e=>{const r=cS.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];};
  cS.addEventListener('pointerdown',e=>{const [x,y]=loc(e);drag=Math.hypot(x-SS.hx,y-SS.hy)<12?'o':Math.hypot(x-SS.wx,y-SS.wy)<12?'w':Math.abs(x-SS.bx)<8?'d':null;if(drag)cS.setPointerCapture(e.pointerId);});
  cS.addEventListener('pointermove',e=>{const [x,y]=loc(e);if(!drag){cS.style.cursor=Math.hypot(x-SS.hx,y-SS.hy)<12?'ew-resize':Math.hypot(x-SS.wx,y-SS.wy)<12?'ns-resize':Math.abs(x-SS.bx)<8?'ew-resize':'default';return;}
    if(drag==='o')P.oh=Math.max(0,Math.min(2,Math.round(-(x-SS.ox)/SS.k*20)/20));
    else if(drag==='w'){const z=(SS.oy-y)/SS.k;P.wwr=Math.max(15,Math.min(90,Math.round((z-P.sill)/P.H*100)));}
    else P.D=Math.max(5,Math.min(20,Math.round((x-SS.ox)/SS.k*2)/2));
    refresh();draw();});
  cS.addEventListener('pointerup',()=>drag=null);
  const wave=(t,a,b,sp,ph)=>a+(b-a)*(1-Math.cos(t*sp+(ph||0)))/2, q=(v,st)=>Math.round(v/st)*st;
  app.demo={step:t=>{P.wwr=q(wave(t,25,85,.45),1);P.oh=q(wave(t,0,1.6,.27,1),.05);P.ori=Math.floor(t/8)%4;draw();},stop:()=>refresh()};
  LabIO(app,{name:'office',state:()=>({P}),load:o=>{Object.assign(P,o.P||{});refresh();},redraw:draw});
  addEventListener('resize',draw); draw();
})();
