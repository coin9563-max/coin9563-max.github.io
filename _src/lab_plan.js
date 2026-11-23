// LAB 01 — 평면 대안 생성기
// 실 6개를 슬라이싱(길로틴) 방식으로 대지에 나눠 넣고, 대안 N개를 만든 뒤
// 형태 · 채광 · 인접 · 현관 점수에 가중치를 곱해 합산 → 기준 점수 이상이면서 서로 충분히 다른 안만 골라낸다.
(function(){
  const root=document.getElementById('lab-plan'); if(!root) return;
  const ROOMS=[
    {n:'거실',a:28,l:1.0,c:'#d48f62'},
    {n:'부엌',a:14,l:0.5,c:'#d2ad78'},
    {n:'침실 1',a:14,l:0.8,c:'#a9b89a'},
    {n:'침실 2',a:11,l:0.7,c:'#9dccef'},
    {n:'욕실',a:6,l:0.0,c:'#b2c3cc'},
    {n:'현관',a:5,l:0.0,c:'#e3a3a0'},
  ];
  const ADJ=[[0,1,'거실–부엌'],[0,5,'거실–현관'],[2,4,'침실1–욕실'],[3,4,'침실2–욕실']];
  const P={N:300, ratio:1.4, w:{shape:1,light:1.5,adj:1.2,entry:0.6}, th:65, div:0.18, seed:7};
  const AREAS=ROOMS.map(r=>r.a);

  // ---------- 생성
  function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
  function slice(R,ids,rnd,out){
    if(ids.length===1){out[ids[0]]=R;return;}
    const k=1+Math.floor(rnd()*(ids.length-1)), A=ids.slice(0,k), B=ids.slice(k);
    const sa=A.reduce((s,i)=>s+AREAS[i],0), sb=B.reduce((s,i)=>s+AREAS[i],0), f=sa/(sa+sb);
    const vert = rnd()<0.75 ? R.w>=R.h : rnd()<0.5;   // 대체로 긴 변을 자른다
    if(vert){ slice({x:R.x,y:R.y,w:R.w*f,h:R.h},A,rnd,out); slice({x:R.x+R.w*f,y:R.y,w:R.w*(1-f),h:R.h},B,rnd,out); }
    else    { slice({x:R.x,y:R.y,w:R.w,h:R.h*f},A,rnd,out); slice({x:R.x,y:R.y+R.h*f,w:R.w,h:R.h*(1-f)},B,rnd,out); }
  }
  function generate(){
    const tot=AREAS.reduce((a,b)=>a+b,0), W=Math.sqrt(tot*P.ratio), H=tot/W, alts=[];
    for(let s=0;s<P.N;s++){
      const rnd=rng(P.seed*100003+s), ids=[0,1,2,3,4,5];
      for(let i=5;i>0;i--){const j=Math.floor(rnd()*(i+1));[ids[i],ids[j]]=[ids[j],ids[i]];}
      const r=[]; slice({x:0,y:0,w:W,h:H},ids,rnd,r);
      alts.push(score({r,W,H,id:s+1}));
    }
    return alts;
  }
  // ---------- 평가
  const E=1e-6;
  function shared(a,b){ // 두 실이 맞닿은 벽 길이
    if(Math.abs(a.x+a.w-b.x)<E||Math.abs(b.x+b.w-a.x)<E) return Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
    if(Math.abs(a.y+a.h-b.y)<E||Math.abs(b.y+b.h-a.y)<E) return Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x));
    return 0;
  }
  function score(alt){
    const {r,W,H}=alt;
    // 형태: 가로세로비 1.5 이하 만점, 3 이상 0점. 폭 1.8m 미만인 실은 0점
    const shape=r.reduce((s,q)=>{const m=Math.min(q.w,q.h),k=Math.max(q.w,q.h)/m;return s+(m<1.8?0:k<=1.5?1:Math.max(0,1-(k-1.5)/1.5));},0)/6;
    // 채광: 남쪽(아래) 외벽에 면한 길이 비율 × 실별 채광 요구도. 동서 외벽은 절반 인정
    let ln=0,ld=0; r.forEach((q,i)=>{const L=ROOMS[i].l; if(!L) return;
      const south=Math.abs(q.y+q.h-H)<E?q.w:0, side=(q.x<E?q.h:0)+(Math.abs(q.x+q.w-W)<E?q.h:0);
      ln+=L*Math.min(1,(south+0.4*side)/Math.max(q.w,q.h)); ld+=L;});
    const light=ld?ln/ld:1;
    // 인접: 필요한 짝이 0.9m 이상 벽을 맞대면 통과
    const adjOk=ADJ.map(([a,b])=>shared(r[a],r[b])>=0.9);
    const adj=adjOk.filter(Boolean).length/ADJ.length;
    // 현관: 북쪽(위) 외벽에 면하면 1, 동서면 0.5
    const e=r[5], entry=e.y<E?1:(e.x<E||Math.abs(e.x+e.w-W)<E)?0.5:0;
    const s={shape,light,adj,entry}, w=P.w, ws=w.shape+w.light+w.adj+w.entry||1;
    alt.s=s; alt.adjOk=adjOk;
    alt.total=100*(w.shape*shape+w.light*light+w.adj*adj+w.entry*entry)/ws;
    // 폭 1.5m도 안 되는 실이 있으면 쓸 수 없는 평면 → 감점
    if(r.some(q=>Math.min(q.w,q.h)<1.5)) alt.total*=0.6;
    alt.sig=r.map(q=>[(q.x+q.w/2)/W,(q.y+q.h/2)/H]);
    return alt;
  }
  function dist(a,b){let d=0;for(let i=0;i<6;i++)d+=Math.hypot(a.sig[i][0]-b.sig[i][0],a.sig[i][1]-b.sig[i][1]);return d/6;}
  function pick(alts){
    const sorted=[...alts].sort((a,b)=>b.total-a.total), picked=[];
    for(const a of sorted){ if(a.total<P.th) break; if(picked.every(p=>dist(a,p)>=P.div)) picked.push(a); if(picked.length>=6) break; }
    return {sorted,picked};
  }
  // ---------- 그리기
  function svg(alt,big){
    const {r,W,H}=alt, pad=big?1.4:0.25, vb=`${-pad} ${-pad} ${W+2*pad} ${H+2*pad+(big?1.2:0)}`;
    let g=r.map((q,i)=>`<rect x="${q.x}" y="${q.y}" width="${q.w}" height="${q.h}" fill="${ROOMS[i].c}" stroke="#1d1c1a" stroke-width="${big?0.08:0.12}"/>`+
      (big?`<text x="${q.x+q.w/2}" y="${q.y+q.h/2}" font-size="${Math.min(0.62,q.w/4)}" text-anchor="middle" dominant-baseline="middle">${ROOMS[i].n}<tspan x="${q.x+q.w/2}" dy="1.1em" font-size=".8em" opacity=".7">${(q.w*q.h).toFixed(1)}㎡</tspan></text>`:'')).join('');
    if(big){
      g+=`<rect x="0" y="0" width="${W}" height="${H}" fill="none" stroke="#1d1c1a" stroke-width="0.22"/>`;
      g+=`<text x="${W/2}" y="${H+0.9}" font-size="0.5" text-anchor="middle" fill="#86827b">S · 남쪽 ☀</text><text x="${W/2}" y="-0.5" font-size="0.5" text-anchor="middle" fill="#86827b">N · 진입</text>`;
    }
    return `<svg viewBox="${vb}" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
  }
  const $=s=>root.querySelector(s);
  function bars(a){
    const L=[['형태','shape'],['채광','light'],['인접','adj'],['현관','entry']];
    return L.map(([k,v])=>`<div class="bar"><span>${k}</span><i style="--v:${(a.s[v]*100).toFixed(0)}%"></i><b>${(a.s[v]*100).toFixed(0)}</b></div>`).join('')+
      `<p class="adjl">${ADJ.map(([,,n],i)=>`<span class="${a.adjOk[i]?'ok':'no'}">${a.adjOk[i]?'●':'○'} ${n}</span>`).join('')}</p>`;
  }
  function run(){
    const alts=generate(), {sorted,picked}=pick(alts), pass=sorted.filter(a=>a.total>=P.th).length;
    $('.lsum').innerHTML=`대안 <b>${P.N}</b>개 생성 → 기준 ${P.th}점 이상 <b>${pass}</b>개 → 서로 충분히 다른 안 <b>${picked.length}</b>개`;
    $('.lpick').innerHTML=picked.length?picked.map((a,k)=>`<figure><div class="lpv">${svg(a,true)}</div><figcaption><p class="sc"><b>${a.total.toFixed(1)}</b>점 <span>#${a.id} · 선택 ${k+1}</span></p>${bars(a)}</figcaption></figure>`).join('')
      :'<p class="none">기준을 넘는 안이 없어요. 기준 점수를 낮추거나 가중치를 바꿔 보세요.</p>';
    const pk=new Set(picked.map(a=>a.id));
    $('.lgrid').innerHTML=sorted.slice(0,96).map(a=>`<div class="t ${a.total>=P.th?'':'low'} ${pk.has(a.id)?'pk':''}" title="#${a.id} · ${a.total.toFixed(1)}점">${svg(a,false)}<span>${a.total.toFixed(0)}</span></div>`).join('');
    // 점수 분포
    const bins=new Array(20).fill(0); alts.forEach(a=>bins[Math.min(19,Math.floor(a.total/5))]++); const mx=Math.max(...bins);
    $('.lhist').innerHTML=bins.map((b,i)=>`<i class="${i*5>=P.th?'on':''}" style="height:${(b/mx*100).toFixed(1)}%" title="${i*5}–${i*5+5}점 · ${b}개"></i>`).join('')+`<em style="left:${P.th}%"></em>`;
  }
  // ---------- 입력
  const ctl=[
    ...ROOMS.map((r,i)=>({g:'면적 (㎡)',k:r.n,min:3,max:40,step:1,get:()=>AREAS[i],set:v=>AREAS[i]=v})),
    {g:'가중치',k:'형태',min:0,max:3,step:.1,get:()=>P.w.shape,set:v=>P.w.shape=v},
    {g:'가중치',k:'채광',min:0,max:3,step:.1,get:()=>P.w.light,set:v=>P.w.light=v},
    {g:'가중치',k:'인접',min:0,max:3,step:.1,get:()=>P.w.adj,set:v=>P.w.adj=v},
    {g:'가중치',k:'현관',min:0,max:3,step:.1,get:()=>P.w.entry,set:v=>P.w.entry=v},
    {g:'선택',k:'기준 점수',min:40,max:95,step:1,get:()=>P.th,set:v=>P.th=v},
    {g:'선택',k:'서로 다른 정도',min:0,max:.4,step:.01,get:()=>P.div,set:v=>P.div=v},
    {g:'선택',k:'대지 가로세로비',min:1,max:2.5,step:.05,get:()=>P.ratio,set:v=>P.ratio=v},
    {g:'선택',k:'대안 개수',min:50,max:1000,step:50,get:()=>P.N,set:v=>P.N=v},
  ];
  const groups={}; ctl.forEach(c=>(groups[c.g]=groups[c.g]||[]).push(c));
  $('.lctl').innerHTML=Object.entries(groups).map(([g,cs])=>`<fieldset><legend>${g}</legend>${cs.map(c=>`<label><span>${c.k}</span><input type="range" min="${c.min}" max="${c.max}" step="${c.step}" value="${c.get()}" data-k="${ctl.indexOf(c)}"><output>${c.get()}</output></label>`).join('')}</fieldset>`).join('')+
    `<button type="button" class="reroll">다시 뽑기 ↻</button>`;
  let tm=null;
  root.addEventListener('input',e=>{const i=e.target.dataset.k; if(i===undefined) return; const c=ctl[i], v=parseFloat(e.target.value); c.set(v); e.target.nextElementSibling.textContent=v; clearTimeout(tm); tm=setTimeout(run,60);});
  $('.reroll').onclick=()=>{P.seed=Math.floor(Math.random()*1e6); run();};
  run();
})();
