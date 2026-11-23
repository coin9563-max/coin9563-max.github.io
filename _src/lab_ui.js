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
