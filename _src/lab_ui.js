// 실험 앱 공통: 슬라이더 패널 만들기 + 임베드(모달) 모드
(function(){
  if(/[?&]embed/.test(location.search)) document.documentElement.classList.add('embed');
  window.LabUI=function(box,ctl,onChange){
    const groups={}; ctl.forEach((c,i)=>{c.i=i;(groups[c.g]=groups[c.g]||[]).push(c);});
    box.innerHTML=Object.entries(groups).map(([g,cs])=>`<fieldset><legend>${g}</legend>${cs.map(c=>c.opts
      ?`<label><span>${c.k}</span><select data-k="${c.i}">${c.opts.map((o,j)=>`<option value="${j}" ${j==c.get()?'selected':''}>${o}</option>`).join('')}</select><output></output></label>`
      :`<label><span>${c.k}</span><input type="range" min="${c.min}" max="${c.max}" step="${c.step}" value="${c.get()}" data-k="${c.i}"><output>${c.fmt?c.fmt(c.get()):c.get()}</output></label>`).join('')}</fieldset>`).join('');
    let tm=null;
    box.addEventListener('input',e=>{const i=e.target.dataset.k; if(i===undefined) return; const c=ctl[i], v=parseFloat(e.target.value); c.set(v);
      if(!c.opts) e.target.nextElementSibling.textContent=c.fmt?c.fmt(v):v; clearTimeout(tm); tm=setTimeout(onChange,40);});
    return function(){box.querySelectorAll('[data-k]').forEach(el=>{const c=ctl[el.dataset.k];el.value=c.get();if(!c.opts)el.nextElementSibling.textContent=c.fmt?c.fmt(c.get()):c.get();});};
  };
  window.LabRng=function(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}};
})();
// 공통 그리기 도구 (어두운 도면 시트)
window.LD={INK:'#e6e3da',DIM:'#8a8a80',FAINT:'#3a3a35',BG:'#151513',RED:'#ff6b4a',BLUE:'#4da3ff',GREEN:'#9fd36b',MONO:'"JetBrains Mono",ui-monospace,monospace',
  fit:function(cv){var r=cv.getBoundingClientRect(),d=devicePixelRatio||1;cv.width=r.width*d;cv.height=r.height*d;var g=cv.getContext('2d');g.setTransform(d,0,0,d,0,0);g.lineJoin='round';g.fillStyle='#151513';g.fillRect(0,0,r.width,r.height);return [g,r.width,r.height];},
  path:function(g,p,close){g.beginPath();p.forEach(function(v,i){i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]);});if(close!==false)g.closePath();},
  text:function(g,s,x,y,o){o=o||{};g.font=(o.w||'')+' '+(o.size||10)+'px '+LD.MONO;g.fillStyle=o.c||LD.DIM;g.textAlign=o.a||'left';g.fillText(s,x,y);},
  dim:function(g,x1,y1,x2,y2,label,off,c){c=c||LD.BLUE;var dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy)||1,nx=-dy/L*off,ny=dx/L*off;g.strokeStyle=c;g.lineWidth=.7;g.beginPath();
    g.moveTo(x1,y1);g.lineTo(x1+nx*1.15,y1+ny*1.15);g.moveTo(x2,y2);g.lineTo(x2+nx*1.15,y2+ny*1.15);g.moveTo(x1+nx,y1+ny);g.lineTo(x2+nx,y2+ny);g.stroke();
    var mx=(x1+x2)/2+nx*1.6,my=(y1+y2)/2+ny*1.6;g.save();g.translate(mx,my);var a=Math.atan2(dy,dx);if(a>Math.PI/2||a<-Math.PI/2)a+=Math.PI;g.rotate(a);LD.text(g,label,0,3,{c:c,a:'center'});g.restore();},
  stats:function(el,rows,hi,note){el.innerHTML=rows.map(function(r,i){return '<div class="'+(hi&&hi.indexOf(i)>=0?'hi':'')+(r[2]==='ng'?' ng':'')+'"><span>'+r[0]+'</span><b>'+r[1]+'</b></div>';}).join('')+(note?'<p class="note">'+note+'</p>':'');}
};

// 실사용 도구줄: 좌표 · DXF 입력, PNG · CSV · DXF 내보내기, 링크로 조건 저장
window.LabIO=function(app,o){
  const bar=document.createElement('div'); bar.className='lio';
  bar.innerHTML=(o.poly?`<details class="lin"><summary>대지 입력</summary><p>꼭짓점 좌표를 한 줄에 하나씩 <code>x, y</code> (m, 북쪽이 +y). 또는 DXF의 닫힌 폴리라인을 올리세요.</p><textarea rows="6"></textarea><div><button type="button" class="ap">좌표 적용</button><label class="up">DXF 열기<input type="file" accept=".dxf"></label><span class="msg"></span></div></details>`:'')+
    `<button type="button" data-x="png">PNG</button><button type="button" data-x="csv">CSV</button>${o.dxf?'<button type="button" data-x="dxf">DXF</button>':''}<button type="button" data-x="link">링크 복사</button>`;
  app.appendChild(bar);
  const name=o.name||'lab', msg=bar.querySelector('.msg');
  const save=(blob,fn)=>{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=fn;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},500);};
  const flash=(b,t)=>{const o2=b.textContent;b.textContent=t;setTimeout(()=>b.textContent=o2,1400);};
  // 좌표 ↔ 내부 좌표 (내부는 y가 아래로 = 남쪽)
  const toText=p=>p.map(q=>`${q[0].toFixed(2)}, ${(-q[1]).toFixed(2)}`).join('\n');
  function setPoly(pts){ if(pts.length<3){msg.textContent='점이 3개 이상 필요해요';return;}
    const xs=pts.map(p=>p[0]),ys=pts.map(p=>-p[1]),mx=Math.min(...xs),my=Math.min(...ys);
    o.poly.set(pts.map(p=>[Math.round((p[0]-mx+3)*100)/100,Math.round((-p[1]-my+3)*100)/100])); msg.textContent=pts.length+'개 점 적용'; o.redraw(); }
  if(o.poly){
    const ta=bar.querySelector('textarea'); bar.querySelector('.lin').addEventListener('toggle',()=>{ta.value=toText(o.poly.get());});
    bar.querySelector('.ap').onclick=()=>{const pts=ta.value.split(/\n/).map(l=>l.split(/[,\s\t]+/).filter(Boolean).map(Number)).filter(a=>a.length>=2&&a.every(isFinite)).map(a=>[a[0],a[1]]);setPoly(pts);};
    bar.querySelector('input[type=file]').onchange=e=>{const f=e.target.files[0];if(!f)return;f.text().then(t=>{
      const L=t.split(/\r?\n/).map(s=>s.trim()), polys=[]; let cur=null;
      for(let i=0;i<L.length-1;i+=2){const c=L[i],v=L[i+1];
        if(c==='0'){ if(cur&&cur.length>2) polys.push(cur); cur=(v==='LWPOLYLINE'||v==='POLYLINE')?[]:(v==='VERTEX'&&cur?cur:null); if(v==='VERTEX'&&polys.length&&!cur){} }
        else if(cur&&c==='10') cur.push([+v,0]); else if(cur&&c==='20'&&cur.length) cur[cur.length-1][1]=+v; }
      if(cur&&cur.length>2) polys.push(cur);
      if(!polys.length){msg.textContent='닫힌 폴리라인을 찾지 못했어요';return;}
      const ar=p=>Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-b[0]*a[1];},0))/2;
      let P=polys.sort((a,b)=>ar(b)-ar(a))[0]; const ext=Math.max(...P.map(p=>Math.abs(p[0])),...P.map(p=>Math.abs(p[1])));
      const xs=P.map(p=>p[0]),ys=P.map(p=>p[1]),span=Math.max(Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys));
      if(span>1000) P=P.map(p=>[p[0]/1000,p[1]/1000]); // mm → m
      setPoly(P); ta.value=toText(o.poly.get());});};
  }
  bar.addEventListener('click',e=>{const x=e.target.dataset&&e.target.dataset.x;if(!x)return;
    if(x==='png'){const cvs=[...app.querySelectorAll('canvas')],h=Math.max(...cvs.map(c=>c.height)),w=cvs.reduce((s,c)=>s+c.width,0);
      const out=document.createElement('canvas');out.width=w;out.height=h;const g=out.getContext('2d');g.fillStyle='#151513';g.fillRect(0,0,w,h);let ox=0;cvs.forEach(c=>{g.drawImage(c,ox,0);ox+=c.width;});
      out.toBlob(b=>save(b,name+'.png'));}
    if(x==='csv'){const rows=[...app.querySelectorAll('.nls div')].map(d=>[d.querySelector('span').textContent,d.querySelector('b').textContent]);
      const st=o.state();rows.push(['',''],['입력값','']);Object.entries(st.P||{}).forEach(([k,v])=>rows.push([k,v]));
      if(o.poly) o.poly.get().forEach((p,i)=>rows.push(['대지 점 '+(i+1),p[0].toFixed(2)+' / '+(-p[1]).toFixed(2)]));
      save(new Blob(['﻿'+rows.map(r=>r.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\n')],{type:'text/csv'}),name+'.csv');}
    if(x==='dxf'){const ents=o.dxf();let d='0\nSECTION\n2\nENTITIES\n';
      ents.forEach(en=>{const p=en.pts,n=p.length,z=en.z||0;for(let i=0;i<(en.closed===false?n-1:n);i++){const a=p[i],b=p[(i+1)%n];
        d+=`0\nLINE\n8\n${en.layer}\n10\n${a[0].toFixed(3)}\n20\n${(-a[1]).toFixed(3)}\n30\n${(a[2]!==undefined?a[2]:z).toFixed(3)}\n11\n${b[0].toFixed(3)}\n21\n${(-b[1]).toFixed(3)}\n31\n${(b[2]!==undefined?b[2]:z).toFixed(3)}\n`;}});
      d+='0\nENDSEC\n0\nEOF\n'; save(new Blob([d],{type:'application/dxf'}),name+'.dxf');}
    if(x==='link'){const u=location.href.split('#')[0]+'#s='+btoa(unescape(encodeURIComponent(JSON.stringify(o.state()))));
      (navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(()=>flash(e.target,'복사됨'),()=>{prompt('이 링크를 복사하세요',u);});}
  });
  // 링크로 연 경우 조건 복원
  const m=location.hash.match(/s=([^&]+)/); if(m){try{o.load(JSON.parse(decodeURIComponent(escape(atob(m[1])))));}catch(e){}}
};
