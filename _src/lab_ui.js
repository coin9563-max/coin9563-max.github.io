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
